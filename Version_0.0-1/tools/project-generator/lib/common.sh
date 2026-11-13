#!/usr/bin/env bash
# Shared helpers for the .NET project generator.
# Sourced by tools/project-generator/lib/generate.sh. Do not execute directly.

set -Eeuo pipefail

# Resolve the directory that contains this file, following symlinks.
resolve_script_dir() {
	local source="${BASH_SOURCE[0]}"
	while [[ -L "$source" ]]; do
		local directory
		directory="$(cd -P "$(dirname "$source")" >/dev/null 2>&1 && pwd)"
		source="$(readlink "$source")"
		[[ "$source" != /* ]] && source="$directory/$source"
	done
	cd -P "$(dirname "$source")" >/dev/null 2>&1 && pwd
}

GENERATOR_LIB_DIR="$(resolve_script_dir)"
GENERATOR_ROOT="$(cd "$GENERATOR_LIB_DIR/.." && pwd)"
# Two levels up from tools/project-generator is the repository root when the
# generator runs in place. Elsewhere this is simply the parent of the tool.
REPO_ROOT="$(cd "$GENERATOR_ROOT/../.." 2>/dev/null && pwd || printf '%s' "$GENERATOR_ROOT")"
TEMPLATES_DIR="$GENERATOR_ROOT/templates"
CONFIG_DIR="$GENERATOR_ROOT/config"
SNAPSHOT_ROOT="$GENERATOR_ROOT/snapshot"

GENERATOR_VERSION="1.0.0"

IN_PLACE=0
if [[ -d "$REPO_ROOT/.git" && "$GENERATOR_ROOT" == "$REPO_ROOT/tools/project-generator" ]]; then
	IN_PLACE=1
fi

# Resolve the reusable assets. Precedence:
#   --source / GENERATOR_SOURCE_ROOT  (explicit)
#   the live repository, when running in place
#   the bundled snapshot, when the tool was copied elsewhere
resolve_reusable_root() {
	local candidate
	for candidate in "${SOURCE_OVERRIDE:-}" "${GENERATOR_SOURCE_ROOT:-}"; do
		[[ -n "$candidate" ]] || continue
		[[ -d "$candidate" ]] || die "Reusable source directory does not exist: $candidate"
		(cd -P "$candidate" >/dev/null 2>&1 && pwd)
		return 0
	done

	if (( IN_PLACE )); then
		printf '%s' "$REPO_ROOT"
		return 0
	fi

	if [[ -d "$SNAPSHOT_ROOT/.opencode/agents" && -d "$SNAPSHOT_ROOT/docs/architecture" ]]; then
		printf '%s' "$SNAPSHOT_ROOT"
		return 0
	fi

	# Nothing usable: emit an empty value and let the prerequisite check fail
	# with a clear message.
	printf ''
}

# The tree the generated project must never be written inside.
tree_root_for_guard() {
	if (( IN_PLACE )); then
		printf '%s' "$REPO_ROOT"
	else
		dirname "$GENERATOR_ROOT"
	fi
}

TARGET_FRAMEWORK="${GENERATOR_TFM:-net10.0}"
PROJECT_NAME="${PROJECT_NAME:-}"
INITIALIZE_GIT=1
RUN_VALIDATION=1

PROJECT_NAME_LOWER=""
PROJECT_NAME_UPPER=""
DEST=""
DEST_CREATED=0
VALIDATION_STARTED=0
TEMP_DIR=""
REUSABLE_ROOT=""
SOURCE_OVERRIDE=""
COLOR_ENABLED=1

if [[ -n "${NO_COLOR:-}" || -n "${PROJECT_GENERATOR_NO_COLOR:-}" || ! -t 1 ]]; then
	COLOR_ENABLED=0
fi

color() {
	local code="$1"
	shift
	if (( COLOR_ENABLED )); then
		printf '\033[%sm%s\033[0m' "$code" "$*"
	else
		printf '%s' "$*"
	fi
}

info() { printf '%s %s\n' "$(color '0;36' '·')" "$*"; }
success() { printf '%s %s\n' "$(color '0;32' '✔')" "$*"; }
warn() { printf '%s %s\n' "$(color '0;33' '!')" "$*" >&2; }
die() {
	printf '%s %s\n' "$(color '0;31' '✘')" "$*" >&2
	exit 1
}

step() {
	local number="$1" total="$2" message="$3"
	printf '\n%s %s\n' "$(color '0;34' "[$number/$total]")" "$message"
}

banner() {
	printf '\n%s\n' "$(color '0;36' '========================================')"
	printf '       .NET PROJECT GENERATOR\n'
	printf '%s\n\n' "$(color '0;36' '========================================')"
}

default_output_root() {
	if (( IN_PLACE )); then
		dirname "$REPO_ROOT"
		return 0
	fi

	local current
	current="$(pwd -P)"
	local guard
	guard="$(tree_root_for_guard)"
	if path_is_inside "$current" "$guard"; then
		dirname "$guard"
	else
		printf '%s' "$current"
	fi
}

usage() {
	cat <<EOF
.NET Project Generator v$GENERATOR_VERSION

Usage:
  ./create-project.sh [OPTIONS] [PROJECT_NAME]

Creates a new Clean Architecture .NET solution that carries the reusable
engineering practices of this repository: layered architecture, the TDP
workflow, OpenCode agents and commands, the two-tier testing strategy, and
the architecture tests. It does not copy business logic or specifications.

Options:
  -n, --name NAME        Project name. Prompted for when omitted.
  -o, --output DIR       Parent directory in which the project folder is created.
                         Default: $(default_output_root)
      --source DIR       Reusable assets to copy (default: the live repository
                         when present, otherwise the bundled snapshot).
      --no-git           Do not initialize a git repository on develop.
      --skip-validation  Do not build, test or format-check the generated project.
  -h, --help             Show this help.
      --version          Show the generator version.

Environment:
  GENERATOR_TFM          Target framework (default: net10.0).
  GENERATOR_OUTPUT_ROOT  Same as --output.
  GENERATOR_SOURCE_ROOT  Same as --source.
  KEEP_PARTIAL=1         Keep the destination directory if generation fails
                         before validation.
  NO_COLOR=1             Disable ANSI colour.

The tool is self-contained: when it is copied away from its source repository
it uses the reusable snapshot bundled inside it. Run
tools/project-generator/sync-snapshot.sh from the source repository to refresh
that snapshot.

Project names must be PascalCase identifiers: a letter followed by letters or
digits, for example MyNewProject. An existing destination is never overwritten.
EOF
}

# Renders {{PLACEHOLDERS}} and the legacy product identifiers in a text stream.
render_string() {
	local input="$1"
	printf '%s' "$input" | sed \
		-e "s|{{PROJECT_NAME_UPPER}}|${PROJECT_NAME_UPPER}|g" \
		-e "s|{{PROJECT_NAME_LOWER}}|${PROJECT_NAME_LOWER}|g" \
		-e "s|{{PROJECT_NAME}}|${PROJECT_NAME}|g" \
		-e "s|{{TARGET_FRAMEWORK}}|${TARGET_FRAMEWORK}|g" \
		-e "s|ASISPASS|${PROJECT_NAME_UPPER}|g" \
		-e "s|Asispass|${PROJECT_NAME}|g" \
		-e "s|asispass|${PROJECT_NAME_LOWER}|g" \
		-e "s|PostgreSQL|SQL Server|g"
}

# Renders one text file into a new destination file.
render_file() {
	local source="$1" destination="$2"
	[[ -f "$source" ]] || die "Template file not found: $source"
	mkdir -p "$(dirname "$destination")"
	{
		render_string "$(cat "$source")"
		printf '\n'
	} >"$destination"
}

# Copies a directory tree, rendering placeholders in both paths and contents.
copy_tree_rendered() {
	local source_root="$1" destination_root="$2"
	[[ -d "$source_root" ]] || die "Template directory not found: $source_root"

	local source relative rendered_relative
	while IFS= read -r -d '' source; do
		relative="${source#"$source_root"/}"
		rendered_relative="$(render_string "$relative")"
		if [[ -d "$source" ]]; then
			mkdir -p "$destination_root/$rendered_relative"
		else
			render_file "$source" "$destination_root/$rendered_relative"
		fi
	done < <(find "$source_root" -mindepth 1 -print0)
}

# Renders a single whitelisted source file from the reusable tree.
copy_reusable_file() {
	local relative="$1"
	render_file "$REUSABLE_ROOT/$relative" "$DEST/$relative"
}

# Copies every regular file under a reusable directory, optionally skipping
# paths listed one per line in an exclude file.
copy_reusable_directory() {
	local relative_source="$1" relative_destination="$2" exclude_file="${3:-}"
	local source_root="$REUSABLE_ROOT/$relative_source"
	[[ -d "$source_root" ]] || die "Source directory not found: $source_root"

	local source relative skip
	while IFS= read -r -d '' source; do
		relative="${source#"$source_root"/}"
		skip=0
		if [[ -n "$exclude_file" && -f "$exclude_file" ]]; then
			grep -Fxq -- "$relative_source/$relative" "$exclude_file" && skip=1
		fi
		(( skip )) && continue
		render_file "$source" "$DEST/$relative_destination/$relative"
	done < <(find "$source_root" -type f -print0)
}

normalize_path() {
	local path="$1"
	local parent
	parent="$(cd -P "$(dirname "$path")" >/dev/null 2>&1 && pwd)" \
		|| die "Cannot resolve directory of: $path"
	printf '%s/%s' "$parent" "$(basename "$path")"
}

path_is_inside() {
	local child="$1" parent="$2"
	case "$child" in
	"$parent" | "$parent"/*) return 0 ;;
	*) return 1 ;;
	esac
}

# Runs a command, capturing its output. On failure the log is shown and kept.
run_checked() {
	local label="$1"
	shift
	local log="$TEMP_DIR/$(printf '%s' "$label" | tr ' /' '__').log"
	if "$@" >"$log" 2>&1; then
		info "$label: OK"
		return 0
	fi
	{
		printf '\n'
		warn "$label failed. Output follows:"
		printf '\n'
		cat "$log"
		printf '\n'
	} >&2
	return 1
}

cleanup() {
	local status=$?
	if [[ -n "$TEMP_DIR" && -d "$TEMP_DIR" ]]; then
		rm -rf -- "$TEMP_DIR"
	fi
	if (( status != 0 && DEST_CREATED == 1 && VALIDATION_STARTED == 0 )) \
		&& [[ "${KEEP_PARTIAL:-0}" != "1" ]]; then
		warn "Removing the partially created directory: $DEST"
		warn "Set KEEP_PARTIAL=1 to keep it for inspection."
		rm -rf -- "$DEST"
	fi
	return "$status"
}
