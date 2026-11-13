#!/usr/bin/env bash
# Reusable .NET project generator.
#
# Usage: ./create-project.sh [OPTIONS] [PROJECT_NAME]
# See tools/project-generator/README.md for the full guide.

set -Eeuo pipefail

SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
exec "$SCRIPT_DIR/tools/project-generator/lib/generate.sh" "$@"
