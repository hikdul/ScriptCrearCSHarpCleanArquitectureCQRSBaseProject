#!/usr/bin/env bash
# Entry point for the reusable .NET project generator.

# shellcheck source=lib/common.sh
source "$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"
# shellcheck source=lib/validate.sh
source "$GENERATOR_LIB_DIR/validate.sh"
# shellcheck source=lib/scaffold.sh
source "$GENERATOR_LIB_DIR/scaffold.sh"
# shellcheck source=lib/opencode.sh
source "$GENERATOR_LIB_DIR/opencode.sh"
# shellcheck source=lib/docs.sh
source "$GENERATOR_LIB_DIR/docs.sh"
# shellcheck source=lib/finalize.sh
source "$GENERATOR_LIB_DIR/finalize.sh"

main() {
	parse_arguments "$@"
	trap cleanup EXIT

	banner

	if [[ -z "$PROJECT_NAME" ]]; then
		prompt_for_project_name
	fi

	check_prerequisites
	prepare_destination
	TEMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/project-generator.XXXXXX")"

	printf 'Creating project: %s\n' "$PROJECT_NAME"

	step 1 5 "Preparing project structure..."
	initialize_repository
	render_root_configuration

	step 2 5 "Copying reusable architecture..."
	copy_source_and_test_projects
	create_solution

	step 3 5 "Configuring OpenCode..."
	configure_opencode
	configure_documentation

	step 4 5 "Creating specifications template..."
	initialize_specifications

	step 5 5 "Finalizing project..."
	verify_generated_project
	validate_generated_project
	commit_generated_project
	report_result
}

main "$@"
