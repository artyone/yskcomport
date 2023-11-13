import json as js
import os
import time

from jsonschema import validate

from .json_data import get_default_json_data, get_json_schema


class JsonException(Exception):
    ...


class Controller:
    def __init__(self, parent) -> None:
        self.parent = parent
        self._json_data = self._get_data_from_json()
        self.validate_json()
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

    def get_category_datas(self):
        return self._json_data

    def get_category_names(self):
        if self._json_data is None:
            return []
        return [category['name'] for category in self._json_data]

    def get_group_datas(self, category_name):
        for category in self.get_category_datas():
            if category['name'] == category_name:
                return category['groups']
        return []

    def get_group_names(self, category_name):
        groups = self.get_group_datas(category_name)
        return [group['name'] for group in groups]

    def get_element_datas(self, category_name, group_name):
        for group in self.get_group_datas(category_name):
            if group['name'] == group_name:
                return group['elements']
        return []

    def get_element_names(self, category_name, group_name):
        elements = self.get_element_datas(category_name, group_name)
        return [element['name'] for element in elements]

    def get_element_data(self, category_name, group_name, element_name):
        for element in self.get_element_datas(category_name, group_name):
            if element['name'] == element_name:
                return element
        return {}

    def set_new_fixed_bytes(self, new_bytes: str):
        try:
            for category in self._json_data:
                category['fixed_bytes'] = new_bytes
            self.save_json()
        except:
            raise JsonException

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
        day, month, year = [int(i) for i in date.split('.')]
        result = ''
        result += bin(year % 100)[2:].zfill(7)[::-1][:7][::-1]
        result += bin(month)[2:].zfill(4)[::-1][:4][::-1]
        result += bin(day)[2:].zfill(5)[::-1][:5][::-1]
        byte1, byte2 = int(result[:8], 2), int(result[8:], 2)
        return [byte1, byte2]

    def get_data_for_temp_memory(self, widget_datas):
        return [self.get_command(data) for data in widget_datas]

    def get_command(self, data):
        command_list = []
        command_list.append(
            int(self.table_bytes[data.category]['bytes'][:2], base=16))
        command_list.append(
            int(self.table_bytes[data.category]['bytes'][2:4], base=16))
        command_list.append(
            int(self.table_bytes[data.category]['bytes'][4:], base=16))
        command_list.append(
            int(self.table_bytes[data.category][data.group]['bytes'], base=16))
        command_list.append(
            int(self.table_bytes[data.category][data.group][data.element]['bytes'], base=16))
        if data.type == 'date':
            command_list.extend(self.date_to_int(data.data))
        else:
            command_list.extend(self.split_int_to_bytes(
                self.volts_to_int(data.data)))
        control_sum = sum(command_list) & 0xFF
        command_list.append(control_sum)
        result = bytes(command_list)
        return result

    def get_table_bytes(self):
        result = {}
        for category_data in self._json_data:
            category_name = category_data['name']
            result[category_name] = {'bytes': category_data['fixed_bytes']}
            for group in category_data['groups']:
                group_name = group['name']
                result[category_name][group_name] = {'bytes': group['bytes']}
                for element in group['elements']:
                    element_name = element['name']
                    result[category_name][group_name][element_name] = {
                        'bytes': element['bytes']}
        return result

    def get_apply_command(self):
        command = '53 08 14 50 50 00 00 0F'
        return bytes.fromhex(command)
