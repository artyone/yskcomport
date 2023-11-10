import json as js
import os
import time
from icecream import ic


class JsonException(Exception):
    ...


class Controller:
    def __init__(self) -> None:
        self._json_data = self._get_data_from_json()

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
            json_data = [
                {
                    "name": "Опрос текущих пороговых значений АЦП",
                    "fixed_bytes": "530814",
                    "groups": [
                        {
                            "name": "Максильмальное значение",
                            "bytes": "0A",
                            "elements": [
                                {
                                    "name": "2.5(1) V  max",
                                    "bytes": "01",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "2.5(2) V  max",
                                    "bytes": "02",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "3.3 V МЦО max",
                                    "bytes": "03",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "1.25 V max",
                                    "bytes": "05",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "3.3V max",
                                    "bytes": "06",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "9 V max",
                                    "bytes": "07",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "5 V max",
                                    "bytes": "08",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "12 V max ",
                                    "bytes": "09",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "-12 V max ",
                                    "bytes": "0A",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "15 V max",
                                    "bytes": "0B",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "-15 V max",
                                    "bytes": "0C",
                                    "type": "uint16",
                                    "default": 6553
                                }
                            ]
                        },
                        {
                            "name": "Минимальное значение",
                            "bytes": "09",
                            "elements": [
                                {
                                    "name": "2.5(1) V  max",
                                    "bytes": "01",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "2.5(2) V  max",
                                    "bytes": "02",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "3.3 V МЦО max",
                                    "bytes": "03",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "1.25 V max",
                                    "bytes": "05",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "3.3V max",
                                    "bytes": "06",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "9 V max",
                                    "bytes": "07",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "5 V max",
                                    "bytes": "08",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "12 V max ",
                                    "bytes": "09",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "-12 V max ",
                                    "bytes": "0A",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "15 V max",
                                    "bytes": "0B",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "-15 V max",
                                    "bytes": "0C",
                                    "type": "uint16",
                                    "default": 6553
                                }
                            ]
                        },
                        {
                            "name": "Номинальное значение",
                            "bytes": "08",
                            "elements": [
                                {
                                    "name": "2.5(1) V  max",
                                    "bytes": "01",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "2.5(2) V  max",
                                    "bytes": "02",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "3.3 V МЦО max",
                                    "bytes": "03",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "1.25 V max",
                                    "bytes": "05",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "3.3V max",
                                    "bytes": "06",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "9 V max",
                                    "bytes": "07",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "5 V max",
                                    "bytes": "08",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "12 V max ",
                                    "bytes": "09",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "-12 V max ",
                                    "bytes": "0A",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "15 V max",
                                    "bytes": "0B",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "-15 V max",
                                    "bytes": "0C",
                                    "type": "uint16",
                                    "default": 6553
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "Ввод пороговых значений АЦП",
                    "fixed_bytes": "530814",
                    "groups": [
                        {
                            "name": "Максильмальное значение",
                            "bytes": "51",
                            "elements": [
                                {
                                    "name": "2.5(1) V  max",
                                    "bytes": "01",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "2.5(2) V  max",
                                    "bytes": "02",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "3.3 V МЦО max",
                                    "bytes": "03",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "1.25 V max",
                                    "bytes": "05",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "3.3V max",
                                    "bytes": "06",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "9 V max",
                                    "bytes": "07",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "5 V max",
                                    "bytes": "08",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "12 V max ",
                                    "bytes": "09",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "-12 V max ",
                                    "bytes": "0A",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "15 V max",
                                    "bytes": "0B",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "-15 V max",
                                    "bytes": "0C",
                                    "type": "uint16",
                                    "default": 6553
                                }
                            ]
                        },
                        {
                            "name": "Минимальное значение",
                            "bytes": "09",
                            "elements": [
                                {
                                    "name": "2.5(1) V  max",
                                    "bytes": "01",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "2.5(2) V  max",
                                    "bytes": "02",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "3.3 V МЦО max",
                                    "bytes": "03",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "1.25 V max",
                                    "bytes": "05",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "3.3V max",
                                    "bytes": "06",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "9 V max",
                                    "bytes": "07",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "5 V max",
                                    "bytes": "08",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "12 V max ",
                                    "bytes": "09",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "-12 V max ",
                                    "bytes": "0A",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "15 V max",
                                    "bytes": "0B",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "-15 V max",
                                    "bytes": "0C",
                                    "type": "uint16",
                                    "default": 6553
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "Информация о ПМО",
                    "fixed_bytes": "530814",
                    "groups": [
                        {
                            "name": "Ввод информации о ПМО",
                            "bytes": "53",
                            "elements": [
                                {
                                    "name": "Версия ПМО",
                                    "bytes": "01",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "Дата ПМО",
                                    "bytes": "02",
                                    "type": "date",
                                    "default": "12.12.2012"
                                },
                                {
                                    "name": "КС ПМО 1",
                                    "bytes": "03",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "КС ПМО 2",
                                    "bytes": "04",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "КС ПМО 3",
                                    "bytes": "05",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "КС ПМО 4",
                                    "bytes": "06",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "КС ПМО 5",
                                    "bytes": "07",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "КС ПМО 6",
                                    "bytes": "08",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "КС ПМО 7",
                                    "bytes": "09",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "КС ПМО 8",
                                    "bytes": "0A",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "Серийный №",
                                    "bytes": "0B",
                                    "type": "uint16",
                                    "default": 6553
                                }
                            ]
                        },
                        {
                            "name": "Опрос информации о ПМО",
                            "bytes": "54",
                            "elements": [
                                {
                                    "name": "Версия ПМО",
                                    "bytes": "01",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "Дата ПМО",
                                    "bytes": "02",
                                    "type": "date",
                                    "default": "12.12.2012"
                                },
                                {
                                    "name": "КС ПМО 1",
                                    "bytes": "03",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "КС ПМО 2",
                                    "bytes": "04",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "КС ПМО 3",
                                    "bytes": "05",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "КС ПМО 4",
                                    "bytes": "06",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "КС ПМО 5",
                                    "bytes": "07",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "КС ПМО 6",
                                    "bytes": "08",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "КС ПМО 7",
                                    "bytes": "09",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "КС ПМО 8",
                                    "bytes": "0A",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "Серийный №",
                                    "bytes": "0B",
                                    "type": "uint16",
                                    "default": 6553
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "Eeprom",
                    "fixed_bytes": "530814",
                    "groups": [
                        {
                            "name": "Cчитать текущее значение из eeprom",
                            "bytes": "50",
                            "elements": [
                                {
                                    "name": "Значение курса",
                                    "bytes": "55",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "Значение крена",
                                    "bytes": "56",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "Значение тангажа",
                                    "bytes": "57",
                                    "type": "uint16",
                                    "default": 6553
                                }
                            ]
                        },
                        {
                            "name": "Ввод поправок в eeprom",
                            "bytes": "55",
                            "elements": [
                                {
                                    "name": "Значение курса",
                                    "bytes": "55",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "Значение крена",
                                    "bytes": "56",
                                    "type": "uint16",
                                    "default": 6553
                                },
                                {
                                    "name": "Значение тангажа",
                                    "bytes": "57",
                                    "type": "uint16",
                                    "default": 6553
                                }
                            ]
                        }
                    ]
                }
            ]
            js.dump(json_data, file, ensure_ascii=False, indent=4)

    def save_json(self):
        filepath = os.path.join(os.getcwd(), 'data.json')
        with open(filepath, 'w', encoding='utf-8') as file:
            js.dump(self._json_data, file, ensure_ascii=False, indent=4)

    def get_categories_data(self):
        return self._json_data

    def get_category_names(self):
        if self._json_data is None:
            return []
        return [category['name'] for category in self._json_data]

    def get_groups_data(self, category_name):
        for category in self.get_categories_data():
            if category['name'] == category_name:
                return category['groups']
        return []

    def get_group_names(self, category_name):
        groups = self.get_groups_data(category_name)
        return [group['name'] for group in groups]

    def get_element_datas(self, category_name, group_name):
        for group in self.get_groups_data(category_name):
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

    def check_data(self):
        if not isinstance(self._json_data, dict):
            return False
        for category, c_data in self._json_data.items():
            if (not isinstance(category, str) or
                not isinstance(c_data, dict) or
                    not category):
                return False
            if 'fixed_bytes' not in c_data or 'groups' not in c_data:
                return False


if __name__ == '__main__':
    Controller.generate_json()
    ctrl = Controller()
    category = ctrl.get_category_names()[0]
    group = ctrl.get_group_names(category)[0]
    names = ctrl.get_element_names(category, group)[0]
    elem = ctrl.get_element_data(category, group, names)
    ic(elem)
