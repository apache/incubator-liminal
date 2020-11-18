#!/bin/sh

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

export AIRFLOW__CORE__DAGS_FOLDER="$DIR/tests/runners/airflow/liminal/"

python -m unittest
