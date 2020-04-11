#!/bin/sh

echo 'Writing rainbow input..'

echo """$RAINBOW_INPUT""" > /rainbow_input.json

AIRFLOW_RETURN_FILE=/airflow/xcom/return.json

mkdir -p /airflow/xcom/

echo {} > $AIRFLOW_RETURN_FILE
