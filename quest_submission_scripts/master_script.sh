#!/bin/bash

# Working under the assumption that a virtualenvironment exists with
# the proper python version and pabutools and pandas installed
module load python/3.12.10
source ../.venv/bin/activate


# Folder containing files
FILES_DIR="../Data"

# Build a bash array of files
FILES=("$FILES_DIR"/*.pb)

# Pick the file corresponding to this array task
FILE="${FILES[$1]}"

echo "Running on file: $FILE"
echo "Array task ID: $1"

python "$2" "$FILE"