#!/bin/bash

# Working under the assumption that a virtualenvironment exists with
# the proper python version
module load python/3.12.10
source ../.venv/bin/activate

# Check if pabutools is already installed
if ! python3 -c "import pabutools" &> /dev/null; then
    echo "PABUTools is not installed. Installing it now..."
    # Install PABUTools using pip
    pip install --user pabutools  # Use --user to install in user space on clusters
fi

# Check if pabutools is already installed
if ! python3 -c "import pandas" &> /dev/null; then
    echo "pandas is not installed. Installing it now..."
    # Install PABUTools using pip
    pip install --user pandas  # Use --user to install in user space on clusters
fi


# Folder containing files
FILES_DIR="../Data"

# Build a bash array of files
FILES=("$FILES_DIR"/*.pb)

# Pick the file corresponding to this array task
FILE="${FILES[$1]}"

echo "Running on file: $FILE"
echo "Array task ID: $1"

python "$2" "$FILE"