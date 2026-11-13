#!/usr/bin/env bash
# Input validation and prerequisite checks.

validate_project_name() {
	local name="$1"

	[[ -n "$name" ]] || die "The project name cannot be empty."

	if [[ ${#name} -gt 100 ]]; then
		die "The project name must be 100 characters or fewer."
	fi

	if [[ ! "$name" =~ ^[A-Z][A-Za-z0-9]*$ ]]; then
		die "Invalid project name: '$name'. Use PascalCase letters and digits, starting with a capital letter (for example MyNewProject)."
	fi

	case "${name,,}" in
	con | prn | aux | nul | com[1-9] | lpt[1-9])
		die "'$name' is a reserved device name and cannot be used as a project name."
		;;
	esac

	PROJECT_NAME="$name"
	PROJECT_NAME_LOWER="${name,,}"
	PROJECT_NAME_UPPER="${name^^}"
}

prompt_for_project_name() {
	[[ -t 0 ]] || die "No project name was supplied and standard input is not interactive. Pass the name as an argument or with --name."

	local answer=""
	while true; do
		printf 'Enter the new project name: '
		IFS= read -r answer || die "No project name was supplied."
		answer="${answer#"${answer%%[![:space:]]*}"}"
		answer="${answer%"${answer##*[![:space:]]}"}"
		if [[ -n "$answer" ]]; then
			break
		fi
		warn "A project name is required."
	done
	printf '\n'
	validate_project_name "$answer"
}

check_prerequisites() {
	command -v dotnet >/dev/null 2>&1 \
		|| die "The .NET SDK is required but 'dotnet' was not found on PATH."

	local sdk_version sdk_major required_major
	sdk_version="$(dotnet --version 2>/dev/null || true)"
	[[ -n "$sdk_version" ]] || die "The .NET SDK is installed but 'dotnet --version' failed."

	sdk_major="${sdk_version%%.*}"
	required_major="$(printf '%s' "$TARGET_FRAMEWORK" | sed -E 's/^net([0-9]+).*/\1/')"
	if [[ ! "$required_major" =~ ^[0-9]+$ ]]; then
		die "Unsupported target framework '$TARGET_FRAMEWORK'. Set GENERATOR_TFM to a value such as net10.0."
	fi
	if (( sdk_major < required_major )); then
		die "This generator targets $TARGET_FRAMEWORK, but the installed .NET SDK is $sdk_version. Install the .NET $required_major SDK or set GENERATOR_TFM."
	fi

	if (( INITIALIZE_GIT )); then
		command -v git >/dev/null 2>&1 \
			|| die "git is required to initialize the repository. Pass --no-git to skip it."
	fi

	local required
	for required in find sed grep cat cp mkdir rm tr mktemp; do
		command -v "$required" >/dev/null 2>&1 \
			|| die "Required command not found: $required"
	done
}

# Verifies that the reusable assets are reachable and complete.
check_reusable_assets() {
	[[ -n "$REUSABLE_ROOT" && -d "$REUSABLE_ROOT" ]] || die \
		"No reusable assets are available. Run inside the source repository, run 'tools/project-generator/sync-snapshot.sh' from the source repository, or pass --source DIR."

	[[ -d "$TEMPLATES_DIR" ]] || die "Generator templates are missing: $TEMPLATES_DIR"

	local required
	for required in \
		".opencode/agents" \
		".opencode/commands" \
		"docs/architecture" \
		"docs/workflows/tdp-feature-workflow.md" \
		"docs/agents/agents-list.md" \
		".editorconfig" \
		".gitignore" \
		"docker-compose.yml"; do
		[[ -e "$REUSABLE_ROOT/$required" ]] \
			|| die "Reusable asset is missing: $required (looked in $REUSABLE_ROOT)"
	done
}

prepare_destination() {
	mkdir -p "$OUTPUT_ROOT" || die "Cannot create output directory: $OUTPUT_ROOT"

	local output_root_real
	output_root_real="$(cd -P "$OUTPUT_ROOT" >/dev/null 2>&1 && pwd)" \
		|| die "Cannot resolve output directory: $OUTPUT_ROOT"

	DEST="$output_root_real/$PROJECT_NAME"
	DEST="$(normalize_path "$DEST")"

	if [[ "$DEST" == "/" ]]; then
		die "Refusing to use the filesystem root as the destination."
	fi

	if path_is_inside "$DEST" "$(tree_root_for_guard)"; then
		die "The destination '$DEST' is inside the generator's source tree ($(tree_root_for_guard)). Choose an output directory outside it."
	fi

	if [[ -e "$DEST" ]]; then
		die "Destination already exists: $DEST. The generator never overwrites an existing directory."
	fi

	mkdir -p "$DEST" || die "Cannot create destination directory: $DEST"
	DEST_CREATED=1
}

parse_arguments() {
	local positional_name=""
	local name_from_option=""
	local allow_skip_validation=1

	while (( $# > 0 )); do
		case "$1" in
		-n | --name)
			[[ $# -ge 2 ]] || die "Option $1 requires a value."
			name_from_option="$2"
			shift 2
			;;
		-o | --output)
			[[ $# -ge 2 ]] || die "Option $1 requires a value."
			OUTPUT_ROOT="$2"
			shift 2
			;;
		--source)
			[[ $# -ge 2 ]] || die "Option $1 requires a value."
			SOURCE_OVERRIDE="$2"
			shift 2
			;;
		--no-git)
			INITIALIZE_GIT=0
			shift
			;;
		--skip-validation)
			RUN_VALIDATION=0
			allow_skip_validation=0
			shift
			;;
		-h | --help)
			usage
			exit 0
			;;
		--version)
			printf '%s\n' "$GENERATOR_VERSION"
			exit 0
			;;
		--)
			shift
			if (( $# > 0 )); then
				positional_name="$1"
				shift
			fi
			;;
		-*)
			die "Unknown option: $1 (use --help)"
			;;
		*)
			[[ -z "$positional_name" ]] || die "Only one project name may be supplied."
			positional_name="$1"
			shift
			;;
		esac
	done

	(( allow_skip_validation )) || true

	if [[ -n "$name_from_option" && -n "$positional_name" ]]; then
		die "The project name was supplied twice (positional and --name)."
	fi

	if [[ -n "${SOURCE_OVERRIDE:-}" ]]; then
		[[ -d "$SOURCE_OVERRIDE" ]] || die "The --source directory does not exist: $SOURCE_OVERRIDE"
		REUSABLE_ROOT="$(cd -P "$SOURCE_OVERRIDE" >/dev/null 2>&1 && pwd)"
	fi

	local chosen_name="${name_from_option:-$positional_name}"
	if [[ -n "$chosen_name" ]]; then
		validate_project_name "$chosen_name"
	fi
}
