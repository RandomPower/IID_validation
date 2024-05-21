#!/bin/bash
# Regenerate the .venv reinstalling the base dependencies
set -e

# Add actual high-level dependencies here
DEPENDENCIES=("matplotlib" "numpy" "tqdm")

VENV_DIRECTORY=".venv"
REQUIREMENTS="requirements.txt"

if [ ! -d "$VENV_DIRECTORY" ]; then
    echo "$VENV_DIRECTORY does not exist."
    return 1
fi

if [[ "$VIRTUAL_ENV" != "" ]]; then
    deactivate
fi

rm -r "$VENV_DIRECTORY"

python3 -m venv "$VENV_DIRECTORY"

source "$(find $VENV_DIRECTORY -name activate)"

pip install "${DEPENDENCIES[@]}"

pip freeze > "$REQUIREMENTS"

echo "Activate the new venv with:"
echo "source $(find $VENV_DIRECTORY -name activate)"
