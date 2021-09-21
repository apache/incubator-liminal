from liminal.chart import ChartBuilder
from liminal.chart.values_yaml import Values

def create_helm_chart(helm_chart):
    values = Values({"my_value": "some_value", "my": {"nested": {"value": 0}}})
    chart = ChartBuilder(
        # output_directory='/Users/lidor.ettinger/Repos/incubator-liminal',
        nameOverride=helm_chart,
        keep_chart=True,
        values=values,
    )
    helm_install = chart.install_chart()

def delete_helm_chart(helm_chart):
    chart = ChartBuilder(
        chart=helm_chart,
        namespace='default'
    )
    chart.uninstall_chart()