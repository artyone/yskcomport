import json as js
import os
import time

from icecream import ic
from jsonschema import validate

from .json_data import get_default_json_data, get_json_schema


class JsonException(Exception):
    ...


class Controller:
    def __init__(self, parent) -> None:
        self.parent = parent
        self._json_data = self._get_data_from_json()
        self.validate_json()

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
        return round(volts / 3.3 * 4096)

    def send_data_to_temp_memory(self, widget_datas):
        for data in widget_datas:
            self.send_command(data)

    def send_command(self, data):
        pass