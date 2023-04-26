#!/usr/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

if [ $# -eq 0 ]; then
    set --  tests/test_*.py
fi

PYTHONPATH="$SCRIPT_DIR/src/:PYTHONPATH" python -m coverage run --source src/ --omit src/unidecode_replace/replicas.py -m unittest "$@"
python -m coverage report
python -m coverage html
