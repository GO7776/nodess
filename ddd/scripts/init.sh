#!/bin/bash
set -euo pipefail

PROJECT_ROOT=${1:-myapp}
python generate_full_stack.py -o "$PROJECT_ROOT"
