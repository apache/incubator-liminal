from typing import Optional

from liminal.chart._process_utils import custom_check_output
from liminal.chart.helpers import parse_output_to_dict


def get_helm_installations(namespace: Optional[str] = None):
    command = "helm3 list"
    if namespace is not None:
        command += f" -n {namespace}"
    output = custom_check_output(command)
    return parse_output_to_dict(output)