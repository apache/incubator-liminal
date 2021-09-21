import re
from subprocess import CalledProcessError
from typing import Any, List, Optional, Tuple

from liminal.chart._process_utils import custom_check_output

def _space_split(output_line: str):
    return [
        value
        for value in re.split(r"(\t|  +)", output_line)
        if not re.match(r"^\s*$", value)
    ]

def _get_name_locations(names: List[str], name_string: str):
    locs: List[Any] = []
    last_pos = 0
    for name in names:
        last_pos = name_string.find(name, last_pos)
        locs.append(last_pos)
    for i, loc in enumerate(locs):
        if i + 1 < len(locs):
            locs[i] = (loc, locs[i + 1])
            continue
        locs[i] = (loc, len(name_string))
    return locs

def _split_using_locations(locations: List[Tuple[int, int]], values_string: str):
    vals = []
    for i, loc in enumerate(locations):
        start = loc[0]
        end = loc[1]
        if i == len(locations) - 1:
            vals.append(values_string[start:].strip())
            continue
        vals.append(values_string[start:end].strip())
    return vals

def parse_output_to_dict(output: str):
    output_lines = output.split("\n")
    names = _space_split(output_lines[0])
    value_locations = _get_name_locations(names, output_lines[0])
    value_rows = []
    for line in output_lines[1:]:
        if line.strip():
            values = _split_using_locations(value_locations, line)
            value_rows.append(values)
    return {names[i]: row for i, row in enumerate(zip(*value_rows))}

class KubectlGetException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

def kubectl_get(resource: str, namespace: Optional[str] = None, wide: bool = False):
    try:
        command = f"kubectl get {resource}"
        if namespace:
            command += f" -n {namespace}"
        if wide:
            command += " -o wide"
        return parse_output_to_dict(custom_check_output(command))
    except CalledProcessError as err:
        raise KubectlGetException(err.output)