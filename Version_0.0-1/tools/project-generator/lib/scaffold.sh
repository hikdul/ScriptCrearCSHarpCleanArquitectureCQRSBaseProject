#!/usr/bin/env bash
# Solution, project and test-project scaffolding.

dotnet_cli() {
	DOTNET_NOLOGO=1 \
		DOTNET_CLI_TELEMETRY_OPTOUT=1 \
		DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 \
		dotnet "$@"
}

initialize_repository() {
	if (( ! INITIALIZE_GIT )); then
		info "Git initialization skipped (--no-git)."
		return 0
	fi

	git init -q "$DEST"
	# Works with git versions that predate 'git init -b'.
	git -C "$DEST" symbolic-ref HEAD refs/heads/develop
	success "Initialized git repository on branch 'develop'."
}

render_root_configuration() {
	copy_repo_file_rendered ".editorconfig"
	copy_repo_file_rendered ".gitignore"
	copy_repo_file_rendered "docker-compose.yml"
	render_file "$TEMPLATES_DIR/root/README.md" "$DEST/README.md"
	render_file "$TEMPLATES_DIR/root/AGENTS.md" "$DEST/AGENTS.md"
}

copy_source_and_test_projects() {
	copy_tree_rendered "$TEMPLATES_DIR/src" "$DEST/src"
	copy_tree_rendered "$TEMPLATES_DIR/tests" "$DEST/tests"

	local generated_project
	for generated_project in "$DEST"/src/*/*.csproj "$DEST"/tests/*/*.csproj; do
		[[ -f "$generated_project" ]] || die "Expected project file was not generated: $generated_project"
	done
}

create_solution() {
	local solution="$DEST/$PROJECT_NAME.sln"
	(
		cd "$DEST"
		dotnet_cli new sln --name "$PROJECT_NAME" --output "$DEST" --format sln --no-update-check >/dev/null
	) || die "Failed to create the solution file."

	[[ -f "$solution" ]] || die "Solution file was not created: $solution"

	local projects=()
	local project
	while IFS= read -r -d '' project; do
		projects+=("$project")
	done < <(find "$DEST/src" "$DEST/tests" -name '*.csproj' -print0 | sort -z)

	(
		cd "$DEST"
		dotnet_cli sln "$solution" add "${projects[@]}" >/dev/null
	) || die "Failed to add projects to the solution."

	success "Created $PROJECT_NAME.sln with ${#projects[@]} projects."
}

scaffold_project() {
	render_root_configuration
	copy_source_and_test_projects
	create_solution
}
