import json as js
import os
import time
from dataclasses import dataclass
from typing import Any

from jsonschema import validate

from .json_data import get_default_json_data, get_json_schema


class JsonException(Exception):
    ...


class AnswerException(Exception):
    ...


@dataclass
class ElementData:
    category_name: str
    category_bytes: str
    is_input: bool
    group_name: str
    group_bytes: str
    group_eeprom: str
    element_name: str
    element_bytes: str
    type: str
    tooltip: str
    data: Any
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
                        ElementData(
                            category['category_name'],
                            category['category_bytes'],
                            category['is_input'],
                            group['group_name'],
                            group['group_bytes'],
                            group['group_eeprom'],
                            element['element_name'],
                            element['element_bytes'],
                            element['type'],
                            element['tooltip'],
                            element['default']
                        ))
        return data

    def get_category_datas(self):
        return self._data

    def get_category_names(self):
        return list({data.category_name: 0 for data in self._data})

    def get_group_datas(self, category_name):
        return [data for data in self._data if data.category_name == category_name]

    def get_group_names(self, category_name):
        return list({data.group_name: 0 for data in self.get_group_datas(category_name)})

    def get_element_datas(self, category_name, group_name):
        return [data for data in self.get_group_datas(category_name) if data.group_name == group_name]

    def get_element_names(self, category_name, group_name):
        return [data.element_name for data in self.get_element_datas(category_name, group_name)]

    def get_element_data(self, category_name, group_name, element_name):
        return [data for data in self.get_element_datas(category_name, group_name) if data.element_name == element_name][0]
    
    def get_eeprom_command(self, category_name, group_name):
        lst = self.get_element_datas(category_name, group_name)
        if len(lst):
            return lst[0].group_eeprom
        return []

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
        if number > 65535:
            number = 65535
        byte1 = (number >> 8) & 0xFF
        byte2 = number & 0xFF
        return byte1, byte2

    @staticmethod
    def date_to_int(date):
        if len(date) != 8:
            date = '00.00.00'
        day, month, year = [int(i) for i in date.split('.')]
        result = f'{year:07b}{month:04b}{day:05b}'
        byte1, byte2 = int(result[:8], 2), int(result[8:], 2)
        return byte1, byte2

    @staticmethod
    def hex_to_date(bytes_data):
        if len(bytes_data) != 4:
            return '00.00.0000'

        bin_data = bin(int(bytes_data, 16))[2:].zfill(16)

        year = str(int(bin_data[:7], 2)).zfill(2)
        month = str(int(bin_data[7:11], 2)).zfill(2)
        day = str(int(bin_data[11:], 2)).zfill(2)
        return f'{day}.{month}.{year}'

    @staticmethod
    def category_bytes_to_intlist(category_bytes):
        first_num = int(category_bytes[:2], base=16)
        second_num = int(category_bytes[2:4], base=16)
        third_num = int(category_bytes[4:], base=16)
        return first_num, second_num, third_num

    def get_data_for_temp_memory(self, widget_datas):
        widget_datas = sorted(widget_datas, key=lambda x: (
            x.group_bytes, x.element_bytes))
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
            if element.type == 'volts':
                command_list.extend(self.split_int_to_bytes(
                    self.volts_to_int(element.data)))
            elif element.type == 'date':
                command_list.extend(self.date_to_int(element.data))
            else:
                command_list.extend(
                    [int(element.data[:2], base=16),
                     int(element.data[2:], base=16)])
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
                result[category_name][group_name] = {
                    'bytes': group['group_bytes']}
                for element in group['elements']:
                    element_name = element['element_name']
                    result[category_name][group_name][element_name] = {
                        'bytes': element['element_bytes']}
        return result

    @staticmethod
    def get_apply_command(command):
        return bytes.fromhex(command)

    def get_element_from_answer(self, message):
        bytes_data = message.toHex().data().decode('utf-8').upper()
        main_bytes = bytes_data[:6]
        if main_bytes != '530841':
            raise AnswerException(
                'Первые три байта в пакете должны быть 53 08 41')

        group_bytes = bytes_data[6:8]
        element_bytes = bytes_data[8:10]
        element_data = bytes_data[10:14]

        for element in self._data:
            if element.group_bytes == group_bytes and element.element_bytes == element_bytes:
                if element.type == 'volts':
                    element.data = self.int_to_volts(int(element_data, 16))
                elif element.type == 'date':
                    element.data = self.hex_to_date(element_data)
                else:
                    element.data = element_data
                return element.widget
        raise AnswerException('Не удалось распознать команду')
    
    @staticmethod
    def get_commands_debug(data):
        commands = []
        for val in data:
            commands.append(bytes([int(i, base=16) if i else 0 for i in val]))
        return commands


if __name__ == '__main__':
    controller = Controller(parent=None)
    category = controller.get_category_names()[5]
    group = controller.get_group_names(category)[0]
    element = controller.get_element_names(category, group)[0]
    print(controller.get_element_data(category, group, element))
