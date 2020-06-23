#!/bin/sh

echo 'Writing liminal input..'

echo """$LIMINAL_INPUT""" > /liminal_input.json

AIRFLOW_RETURN_FILE=/airflow/xcom/return.json

mkdir -p /airflow/xcom/

echo {} > $AIRFLOW_RETURN_FILE
