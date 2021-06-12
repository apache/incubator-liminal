#!/bin/sh

echo 'Writing liminal output..'

EXIT=$1
USER_OUTPUT_DIR=$2
S3_TARGET_DIR=$3

if  [ "$S3_TARGET_DIR" != "" ] && [ "$USER_OUTPUT_DIR" != "" ] && [ -d "$USER_OUTPUT_DIR" ] ; then
    # shellcheck disable=SC2154
    ls "$USER_OUTPUT_DIR"
    echo pipenv run aws s3 cp "$USER_OUTPUT_DIR" "$S3_TARGET_DIR/$run_id" --recursive
    pipenv run aws s3 cp "$USER_OUTPUT_DIR" "$S3_TARGET_DIR/$run_id" --recursive
fi

exit "$EXIT"
