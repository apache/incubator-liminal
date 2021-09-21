from typing import Dict, List, Optional
from collections import defaultdict
from hapi.chart.metadata_pb2 import Metadata
from logging import error, info
from pathlib import Path

import os, re, shutil, subprocess, codecs, yaml
 
from liminal.chart import repo
from liminal.chart.utils import get_helm_installations
from liminal.chart._process_utils import custom_check_output
from liminal.chart.values_yaml import Values


class ChartBuilder:
    """
    Main builder object. Accepts kubernetes objects and generates the helm chart
    structure. Can also perform the installation onto the server

    :param chart_info: Contains all chart metadata and dependency info
    :param kubernetes_objects: A list of kubernetes objects
    :param output_directory: A path to the directory in which to place the generated \
        chart
    :param keep_chart: Whether or not to keep the chart after installation
    :param namespace: The namespace in which all chart components should be installed \
        This allows the convenience of not passing the namespace option to both \
        install and uninstall
    """

    def __init__(
        self,
        keep_chart: bool = False,
        namespace: Optional[str] = None,
        values: Optional[Values] = None,
        output_directory: Optional[str] = None,
        repo_url: Optional[str] = None,
        chart: Optional[str] = None,
        nameOverride: Optional[str] = None,
    ):
        self.__keep_chart = keep_chart
        self.__values = values
        self.namespace = namespace
        self.output_directory = output_directory
        self.repo_url =  repo_url if repo_url is not None else 'https://charts.helm.sh/incubator'
        self.chart = chart if chart is not None else 'common'
        self.nameOverride = nameOverride if nameOverride is None else nameOverride

    def __delete_chart_directory(self):
        if os.path.exists(self.chart_info.name):
            shutil.rmtree(self.__templates_directory)

    @staticmethod
    def read_file(path):
        '''
        Open the file provided in `path` and strip any non-UTF8 characters.
        Return back the cleaned content
        '''
        with codecs.open(path, encoding='utf-8', errors='ignore') as fd:
            content = fd.read()
        return bytes(bytearray(content, encoding='utf-8'))


    def get_metadata(self):
        '''
        Process metadata
        '''
        # extract Chart.yaml to construct metadata
        chart_yaml = yaml.safe_load(ChartBuilder.read_file(os.path.join(self.__templates_directory, 'Chart.yaml')))

        if 'version' not in chart_yaml or \
           'name' not in chart_yaml:
           self._logger.error("Chart missing required fields")
           return

        default_chart_yaml = defaultdict(str, chart_yaml)

        # construct Metadata object
        return Metadata(
            apiVersion=default_chart_yaml['apiVersion'],
            description=default_chart_yaml['description'],
            name=default_chart_yaml['name'],
            version=str(default_chart_yaml['version']),
            appVersion=str(default_chart_yaml['appVersion'])
        )

    def generate_chart(self):
        """
        Generates the chart but does not install it on kubernetes

        :returns The template directory
        """
        self.__templates_directory = repo.from_repo(self.repo_url, self.chart, self.output_directory)
        self.chart_info = self.get_metadata()
        if (self.nameOverride):
            self.chart_info.name = self.nameOverride
        self.chart_folder_path = Path(self.__templates_directory)
        self.__chart_yaml = self.chart_folder_path / "Chart.yaml"
        self.__templates_directory = Path(self.__templates_directory)

        with open(
            self.__templates_directory / "values.yaml", "w"
        ) as values_file:
            values_file.write(self.__get_values_yaml())

        return self.__templates_directory

    def __get_values_yaml(self):
        values = {}
        if self.__values:
            values.update(self.__values.values)
        return yaml.dump(values)

    @staticmethod
    def __parse_options(options: Optional[Dict[str, Optional[str]]] = None):
        option_string = ""
        if options is None:
            return option_string
        for option in options:
            option_string += f" --{option}"

            # Add value after flag if one is given
            value = options[option]
            if value:
                option_string += f" {value}"
        return option_string

    def __get_helm_install_command(
        self, options: Optional[Dict[str, Optional[str]]] = None
    ):        
        command = (
            f"helm3 install {self.chart_info.name} {self.chart_folder_path.resolve()}"
        )
        return self.__handle_namespace(command) + self.__parse_options(options)

    def run_helm_install(self, options: Optional[Dict[str, Optional[str]]] = None):
        """
        Runs helm install on the chart

        :param options: A dictionary of command line arguments to pass to helm

        :Example:

        To run an install with updated dependencies and with verbose logging:

        >>> self.run_helm_install({"dependency_update": None, "v": "info"})
        """
        custom_check_output(self.__get_helm_install_command(options))

    def __handle_installation(self, options: Optional[Dict[str, Optional[str]]] = None):
        try:
            info(f"Installing helm chart {self.chart_info.name}...")
            self.run_helm_install(options)
        except subprocess.CalledProcessError as err:
            decoded = err.output.decode("utf-8")
            error = ErrorFactory(decoded).get_error()
            if error is not None:
                raise error
            if self.is_installed:
                self.uninstall_chart()
            raise post_uninstall_handle_error(decoded)

    def install_chart(self, options: Optional[Dict[str, Optional[str]]] = None):
        """
        Generates and installs the helm chart onto kubernetes and handles all failures.
        It will also add the repos of all listed dependencies.

        Note that the generated chart will be deleted if *keep_chart* is not set to
        true on ChartBuilder

        WARNING: If the helm chart installation fails, the chart will be uninstalled,
        so if working with an existing chart, please use upgrade_chart instead

        :param options: A dictionary of command line arguments to pass to helm

        For example, to run an install with updated dependencies and with verbose
        logging:
        >>> self.helm_install({"dependency_update": None, "v": "info"})
        """
        self.generate_chart()
        # self.add_dependency_repos()
        self.__handle_installation(options)
        if not self.__keep_chart:
            self.__delete_chart_directory()

    def __get_helm_uninstall_command(
        self, options: Optional[Dict[str, Optional[str]]] = None
    ):
        command = f"helm3 uninstall {self.chart}"
        return self.__handle_namespace(command) + self.__parse_options(options)

    def run_helm_uninstall(self, options: Optional[Dict[str, Optional[str]]] = None):
        """
        Runs helm uninstall

        :param options: A dictionary of command line arguments to pass to helm

        :Example:

        >>> self.run_helm_uninstall(
        >>>    {"dry-run": None,
        >>>    "description": "My uninstall description"
        >>>    }
        >>> )
        """
        info(f"Uninstalling chart {self.chart}")
        custom_check_output(self.__get_helm_uninstall_command(options))

    def __check_if_installed(self):
        info(f"Checking if helm chart {self.chart} is installed")
        if not self.is_installed:
            raise ChartNotInstalledError(
                f'Error: chart "{self.chart}" is not installed'
            )

    def __handle_uninstallation(
        self, options: Optional[Dict[str, Optional[str]]] = None
    ):
        self.__check_if_installed()
        self.run_helm_uninstall(options)

    def uninstall_chart(self, options: Optional[Dict[str, Optional[str]]] = None):
        """
        Uninstalls the chart if present, if not present, raises an error

        :param options: A dictionary of command line arguments to pass to helm

        :Example:

        >>> self.uninstall_chart(
        >>>    {"dry-run": None,
        >>>    "description": "My uninstall description"
        >>>    }
        >>> )
        """
        self.__handle_uninstallation(options)

    def __handle_namespace(self, command: str):
        if self.namespace is not None:
            return command + f" -n {self.namespace}"
        return command

    def __get_helm_upgrade_command(
        self, options: Optional[Dict[str, Optional[str]]] = None
    ):
        command = f"helm upgrade {self.chart_info.name} {self.chart_folder_path}"
        return self.__handle_namespace(command) + self.__parse_options(options)

    def __handle_upgrade(self, options: Optional[Dict[str, Optional[str]]] = None):
        try:
            self.run_helm_upgrade(options)
        except subprocess.CalledProcessError as err:
            decoded = err.output.decode("utf-8")
            error = ErrorFactory(decoded).get_error()
            if error is not None:
                raise error
            raise post_uninstall_handle_error(decoded)

    def run_helm_upgrade(self, options: Optional[Dict[str, Optional[str]]] = None):
        """
        Runs 'helm upgrade' on the chart

        :param options: A dictionary of command line arguments to pass to helm

        :Example:

        >>> self.run_helm_upgrade(options={"atomic": None, "version": "2.0"})
        """
        info(f"Upgrading helm chart {self.chart_info.name}")
        custom_check_output(self.__get_helm_upgrade_command(options))

    def upgrade_chart(self, options: Optional[Dict[str, Optional[str]]] = None):
        """
        Generates and upgrades the helm chart

        :param options: A dictionary of command line arguments to pass to helm

        :Example:

        >>> self.upgrade_chart(options={"atomic": None, "version": "2.0"})
        """
        self.__check_if_installed()
        self.generate_chart()
        self.__handle_upgrade(options)

    @property
    def is_installed(self):
        """
        :return: True if chart with the given name is already installed in the chart \
            builders namespace, else False
        """
        installations = get_helm_installations(self.namespace)
        if not installations:
            return False
        return self.chart in installations["NAME"]