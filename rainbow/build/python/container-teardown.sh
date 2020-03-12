#!/bin/bash

USER_CONFIG_OUTPUT_FILE=$1
if [ "$USER_CONFIG_OUTPUT_FILE" != "" ]; then
    cp ${USER_CONFIG_OUTPUT_FILE} /airflow/xcom/return.json
fi
