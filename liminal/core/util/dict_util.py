#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import re
from collections import OrderedDict

from sqlalchemy.util import OrderedSet

from liminal.runners.airflow.config import standalone_variable_backend


def merge_dicts(dict1, dict2, recursive=False):
    """
    :returns dict1 enriched by dict2
    """
    if not recursive:
        return {**dict1, **dict2}

    return __merge_dicts(dict1, dict2)


def __merge_dicts(dict1, dict2):
    # recursive merge
    merged_dicts = OrderedDict()
    dict_1_keys = dict1.keys()
    dict_2_keys = dict2.keys()
    for k in OrderedSet(dict_1_keys).union(dict_2_keys):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                merged_dicts[k] = dict(__merge_dicts(dict1[k], dict2[k]))
            else:
                merged_dicts[k] = dict1[k]
        elif k in dict_1_keys:
            merged_dicts[k] = dict1[k]
        else:
            merged_dicts[k] = dict2[k]
    return merged_dicts


__PLACE_HOLDER_PATTERN = r"{{\s*([a-zA-Z0-9._-]+)\s*}}"


def replace_placeholders(dct, variables):
    """
    Replace all {{variable.key}} in dct with variable.value variable in variables
    """
    return dict(__replace_placeholders(dct, variables))


def replace_placholders_in_string(string_value, variables, pattern=__PLACE_HOLDER_PATTERN):
    print(f"string_value: {string_value}")
    print(f"pattern: {pattern}")
    return re.sub(pattern, lambda m: __repl(m, variables), string_value, flags=re.IGNORECASE)


def __replace_placeholders(dct, variables):
    dct_items = dct.items()
    for k, v in dct_items:
        if isinstance(v, str):
            yield k, replace_placholders_in_string(v, variables)
        elif isinstance(v, dict):
            yield k, dict(__replace_placeholders(v, variables))
        elif isinstance(v, list):
            yield k, list(__replace_placeholder_in_list(v, variables))
        else:
            yield k, v


def __replace_placeholder_in_list(lst, variables):
    for v in lst:
        if isinstance(v, str):
            yield replace_placholders_in_string(v, variables)
        elif isinstance(v, dict):
            yield dict(__replace_placeholders(v, variables))
        elif isinstance(v, list):
            yield __replace_placeholder_in_list(v, variables)
        else:
            yield v


def __repl(matched, variables):
    origin = matched.group(0)
    key = matched.group(1)
    return variables.get(key, __try_backend_variables(key, default=origin))


def __try_backend_variables(key, default):
    return standalone_variable_backend.get_variable(key, default)
