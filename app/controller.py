import json as js
import os
import time
from dataclasses import dataclass
from jsonschema import validate
from typing import Any

from .json_data import get_default_json_data, get_json_schema
#from json_data import get_default_json_data, get_json_schema
from icecream import ic


class JsonException(Exception):
    ...

@dataclass
class ElementData:
    category_name: str
    category_bytes: str
    is_input: bool
    group_name: str
    group_bytes: str
    element_name: str
    element_bytes: str
    is_num: str
    data: str | float
    widget: Any = None


class Controller:
    def __init__(self, parent) -> None:
        self.parent = parent
        self._json_data = self._get_data_from_json()
        self.validate_json()
        self._data = self.generate_data()
        self.table_bytes = self.get_table_bytes()

    def _get_data_from_json(self):
        filepath = os.path.join(os.getcwd(), 'data.json')
        with open(filepath, 'r', encoding='utf-8') as file:
            data = js.load(file)
        return data

    @staticmethod
    def generate_json():
        filepath = os.path.join(os.getcwd(), 'data.json')
        if os.path.isfile(filepath):
            os.rename(filepath, filepath + f'{time.time()}.bak')
        with open(filepath, 'w', encoding='utf-8') as file:
            json_data = get_default_json_data()
            js.dump(json_data, file, ensure_ascii=False, indent=4)

    def save_json(self):
        filepath = os.path.join(os.getcwd(), 'data.json')
        with open(filepath, 'w', encoding='utf-8') as file:
            js.dump(self._json_data, file, ensure_ascii=False, indent=4)

    def generate_data(self):
        data = []
        for category in self._json_data:
            for group in category['groups']:
                for element in group['elements']:
                    data.append(
                        ElementData(category['category_name'],
                                    category['category_bytes'],
                                    category['is_input'], 
                                    group['group_name'],
                                    group['group_bytes'],
                                    element['element_name'],
                                    element['element_bytes'],
                                    element['is_num'],
                                    element['default']))
        return data

    def get_category_datas(self):
        return self._data

    def get_category_names(self):
        return sorted({data.category_name for data in self._data})

    def get_group_datas(self, category_name):
        return [data for data in self._data if data.category_name == category_name]

    def get_group_names(self, category_name):
        return sorted({data.group_name for data in self.get_group_datas(category_name)})

    def get_element_datas(self, category_name, group_name):
        return [data for data in self.get_group_datas(category_name) if data.group_name == group_name]

    def get_element_names(self, category_name, group_name):
        return sorted({data.element_name for data in self.get_element_datas(category_name, group_name)})

    def get_element_data(self, category_name, group_name, element_name):
        return [data for data in self.get_element_datas(category_name, group_name) if data.element_name == element_name][0]

    # def set_new_fixed_bytes(self, new_bytes: str):
    #     try:
    #         for category in self._json_data:
    #             category['fixed_bytes'] = new_bytes
    #         self.save_json()
    #     except:
    #         raise JsonException

    def validate_json(self):
        schema = get_json_schema()
        validate(instance=self._json_data, schema=schema)

    @staticmethod
    def volts_to_int(volts):
        return round(float(volts) / 3.3 * 4096)

    @staticmethod
    def int_to_volts(num):
        return round(num * 3.3 / 4096, 2)

    @staticmethod
    def split_int_to_bytes(number):
        # Переводим число в двоичное представление и обрезаем "0b" в начале
        binary_representation = bin(number)[2:]

        # Дополняем нулями слева до достижения 16 бит
        binary_representation = binary_representation.zfill(16)

        # Берем первые 8 бит
        byte1 = int(binary_representation[:8], 2)

        # Берем следующие 8 бит
        byte2 = int(binary_representation[8:], 2)

        return [byte1, byte2]

    @staticmethod
    def date_to_int(date):
        if len(date) != 10:
            date = '00.00.0000'
        day, month, year = [int(i) for i in date.split('.')]
        result = ''
        result += bin(year % 100)[2:].zfill(7)[::-1][:7][::-1]
        result += bin(month)[2:].zfill(4)[::-1][:4][::-1]
        result += bin(day)[2:].zfill(5)[::-1][:5][::-1]
        byte1, byte2 = int(result[:8], 2), int(result[8:], 2)
        return [byte1, byte2]
    
    @staticmethod
    def category_bytes_to_intlist(category_bytes):
        first_num = int(category_bytes[:2], base=16)
        second_num = int(category_bytes[2:4], base=16)
        third_num = int(category_bytes[4:], base=16)
        return [first_num, second_num, third_num]

    def get_data_for_temp_memory(self, widget_datas):
        widget_datas = sorted(widget_datas, key=lambda x: (x.group_bytes, x.element_bytes))
        return [self.get_command(data) for data in widget_datas]

    def get_command(self, element):
        command_list = []
        command_list.extend(self.category_bytes_to_intlist(
            element.category_bytes
        ))
        command_list.append(
            int(element.group_bytes, base=16))
        command_list.append(
            int(element.element_bytes, base=16))
        if element.is_input:
            if element.is_num:
                command_list.extend(self.split_int_to_bytes(
                    self.volts_to_int(element.data)))
            else:
                command_list.extend(self.date_to_int(element.data))
        else:
            command_list.extend([0, 0])
            
        control_sum = sum(command_list) & 0xFF
        command_list.append(control_sum)
        result = bytes(command_list)
        return result

    def get_table_bytes(self):
        result = {}
        for category_data in self._json_data:
            category_name = category_data['category_name']
            result[category_name] = {'bytes': category_data['category_bytes']}
            for group in category_data['groups']:
                group_name = group['group_name']
                result[category_name][group_name] = {'bytes': group['group_bytes']}
                for element in group['elements']:
                    element_name = element['element_name']
                    result[category_name][group_name][element_name] = {
                        'bytes': element['element_bytes']}
        return result

    def get_apply_command(self):
        command = '53 08 14 50 50 00 00 0F'
        return bytes.fromhex(command)
    
    def get_element_from_answer(self, message):
        from random import choice, randint
        bytes = message.toHex().data().decode('utf-8').upper()
        main_bytes = bytes[:6]
        #TODO проверка контрольной суммы на 530841
        group_bytes = bytes[6:8]
        element_bytes = bytes[8:10]

        element = [i for i in self._data if i.group_bytes == group_bytes and i.element_bytes == element_bytes][0]

        element.data = randint(0, 25)
        return element


if __name__ == '__main__':
    controller = Controller(parent=None)
    category = controller.get_category_names()[5]
    group = controller.get_group_names(category)[0]
    element = controller.get_element_names(category, group)[0]
    print(controller.get_element_data(category, group, element))
