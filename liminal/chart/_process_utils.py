from logging import error, info
from subprocess import STDOUT, CalledProcessError, check_output


def custom_check_output(command: str):
    info(f"Running command: {command}")
    try:
        output = check_output(command.split(" "), stderr=STDOUT).decode("utf-8")
    except CalledProcessError as err:
        error(err.output.decode("utf-8"))
        raise err
    info(f"Output from command:\n{output}")
    return output