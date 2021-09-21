from liminal.yaml.yaml_handling import HelmYaml

class Values:
    """
    An abstraction on the Helm *values.yaml*.

    More information on *values.yaml* can be found
    `here <https://helm.sh/docs/chart_template_guide/values_files/>`__

    :param values: A dictionary specifying what should appear in *values.yaml*
    """

    def __init__(self, values: dict):
        self.values = values


class Value(HelmYaml):
    """
    Used to reference a value specified in :any:`Values`.

    :param value_reference: A reference string specifying a value in **values.yaml**
        using dot notation.

        For example,

        The string

        .. code-block:: python

            'is.my.value'

        would be translated in the yaml output to

        .. code-block:: python

            '{{ .Values.is.my.value }}'

        which in helm will retrieve the value specified in :any:`Values` at

        .. code-block:: python

            {"is":
                {"my":
                    {
                     "value": <some_value>
                    }
                }
            }
    """

    def __init__(self, value_reference: str):
        self.value_reference = value_reference

    def to_dict(self):
        return "{{" + f" .Values.{self.value_reference} " + "}}"