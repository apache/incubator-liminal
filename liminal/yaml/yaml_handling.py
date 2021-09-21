from copy import deepcopy
from datetime import datetime
import re
from typing import Optional, Union

from yaml import dump


def is_empty_yaml(value):
    # If value is None, [], {} do not include value
    return not value and not isinstance(value, (bool, str))


def is_private_var(key: str):
    if re.match(r"_+.*", key):
        return True
    return False


class HelmYaml:
    def __clean_nested(self, dictionary_or_list: Union[dict, list]):
        if isinstance(dictionary_or_list, list):
            cleaned_list = []
            for value in dictionary_or_list:
                if is_empty_yaml(value):
                    continue

                if isinstance(value, (dict, list)):
                    cleaned_dict_or_list = self.__clean_nested(value)

                    if cleaned_dict_or_list:
                        cleaned_list.append(self.__clean_nested(value))

                elif isinstance(value, HelmYaml):
                    cleaned_dict_or_list = value.to_dict()

                    if cleaned_dict_or_list:
                        cleaned_list.append(cleaned_dict_or_list)

                else:
                    cleaned_list.append(value)
            return cleaned_list

        elif isinstance(dictionary_or_list, dict):
            cleaned_dict = {}
            for key, value in dictionary_or_list.items():
                if is_private_var(key):
                    continue

                if is_empty_yaml(value):
                    continue

                elif isinstance(value, (dict, list)):
                    cleaned_dict_or_list = self.__clean_nested(value)

                    if cleaned_dict_or_list:
                        cleaned_dict[key] = cleaned_dict_or_list

                elif isinstance(value, HelmYaml):
                    cleaned_dict_or_list = value.to_dict()

                    if cleaned_dict_or_list:
                        cleaned_dict[key] = cleaned_dict_or_list
                else:
                    cleaned_dict[key] = value
            return cleaned_dict

    def __str__(self):
        return dump(self.to_dict())

    def to_dict(self):
        dictionary = deepcopy(self.__dict__)
        return self.__clean_nested(dictionary)

    @staticmethod
    def _get_kube_date_string(datetime_obj: Optional[datetime]):
        return (
            datetime_obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ%Z")
            if datetime_obj
            else datetime_obj
        )

    def __setitem__(self, key, value):
        self.__dict__[key] = value