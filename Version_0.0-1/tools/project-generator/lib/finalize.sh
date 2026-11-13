#!/usr/bin/env bash
# Final structural verification, validation and reporting.

verify_generated_project() {
	local required=(
		"$PROJECT_NAME.sln"
		"AGENTS.md"
		"README.md"
		".editorconfig"
		".gitignore"
		"docker-compose.yml"
		".opencode/agents/orchestrator.md"
		".opencode/agents/validation.md"
		".opencode/commands/feature.md"
		".opencode/commands/validate.md"
		"docs/README.md"
		"docs/workflows/tdp-feature-workflow.md"
		"docs/architecture/architecture.md"
		"docs/architecture/001-clean-architecture.md"
		"docs/agents/agents-list.md"
		"docs/agents/README.md"
		"docs/guides/agent-usage.md"
		"docs/agent-runs/README.md"
		"docs/specifications/000-spec-example.md"
		"src/$PROJECT_NAME.Domain/AssemblyMarker.cs"
		"src/$PROJECT_NAME.Domain/Common/EntityId.cs"
		"src/$PROJECT_NAME.Application/AssemblyMarker.cs"
		"src/$PROJECT_NAME.Application/Mediator/SimpleMediator.cs"
		"src/$PROJECT_NAME.Application/Abstractions/IUnitOfWork.cs"
		"src/$PROJECT_NAME.Security/AssemblyMarker.cs"
		"src/$PROJECT_NAME.Infrastructure/Persistence/${PROJECT_NAME}DbContext.cs"
		"src/$PROJECT_NAME.Api/Program.cs"
		"tests/$PROJECT_NAME.Architecture.Tests/ArchitectureTests.cs"
		"tests/$PROJECT_NAME.TestSupport/SqliteDatabase.cs"
		"tests/$PROJECT_NAME.Domain.Tests/EntityIdTests.cs"
	)

	local path
	for path in "${required[@]}"; do
		[[ -f "$DEST/$path" ]] || die "Generated project is missing required file: $path"
	done

	local unexpected_specification
	unexpected_specification="$(find "$DEST/docs/specifications" -type f -name '*.md' ! -name '000-spec-example.md' -print -quit)"
	[[ -z "$unexpected_specification" ]] \
		|| die "Product specifications leaked into the generated project: $unexpected_specification"

	local excluded
	for excluded in \
		"$DEST/docs/guides/company-access-and-context.md" \
		"$DEST/docs/guides/firstCompany.md" \
		"$DEST/docs/guides/time-policy.md" \
		"$DEST/docs/guides/user-action-log.md"; do
		[[ ! -e "$excluded" ]] || die "Product documentation leaked into the generated project: $excluded"
	done

	if find "$DEST/docs/agent-runs" -type f -name '*.md' ! -name 'README.md' -print -quit | grep -q .; then
		die "Product agent-run records leaked into the generated project."
	fi

	# The generator must not leave the original product identity behind. A user
	# may deliberately choose a name containing the original identifier, in
	# which case those occurrences are legitimate.
	if [[ "${PROJECT_NAME,,}" != *asispass* ]]; then
		local leak_report
		leak_report="$(grep -rIl -E 'Asispass|ASISPASS|asispass' "$DEST" \
			--exclude-dir=.git --exclude-dir=bin --exclude-dir=obj 2>/dev/null || true)"
		if [[ -n "$leak_report" ]]; then
			warn "The generated project still contains the original product identifier:"
			printf '%s\n' "$leak_report" >&2
			die "Product identity leaked into the generated project."
		fi
	fi

	success "Verified the generated structure and the absence of product-specific content."
}

validate_generated_project() {
	if (( ! RUN_VALIDATION )); then
		warn "Validation skipped (--skip-validation). The project has not been built or tested."
		return 0
	fi

	VALIDATION_STARTED=1
	local solution="$DEST/$PROJECT_NAME.sln"

	info "Restoring, building, testing and format-checking the generated solution."
	run_checked "dotnet build" dotnet_cli build "$solution" --nologo --verbosity minimal \
		|| die "The generated project does not build. The directory was kept for inspection: $DEST"
	run_checked "dotnet test" dotnet_cli test "$solution" --nologo --verbosity minimal \
		|| die "The generated project's tests fail. The directory was kept for inspection: $DEST"
	run_checked "dotnet format --verify-no-changes" dotnet_cli format "$solution" --verify-no-changes --verbosity minimal \
		|| die "The generated project does not satisfy the formatting contract. The directory was kept for inspection: $DEST"

	success "The generated solution builds, its tests pass, and formatting is clean."
}

commit_generated_project() {
	if (( ! INITIALIZE_GIT )); then
		return 0
	fi

	local git_name git_email
	git_name="$(git config --get user.name || true)"
	git_email="$(git config --get user.email || true)"

	git -C "$DEST" add --all
	git -C "$DEST" \
		-c user.name="${git_name:-Project Generator}" \
		-c user.email="${git_email:-project-generator@localhost}" \
		commit -q -m "chore: bootstrap $PROJECT_NAME from the project generator"
	success "Created the initial commit on 'develop'."
}

report_result() {
	local agent_count command_count
	agent_count="$(find "$DEST/.opencode/agents" -type f -name '*.md' | wc -l | tr -d ' ')"
	command_count="$(find "$DEST/.opencode/commands" -type f -name '*.md' | wc -l | tr -d ' ')"

	printf '\n%s\n\n' "$(color '0;32' 'Project successfully created!')"
	printf '  Destination : %s\n' "$DEST"
	printf '  Solution    : %s.sln\n' "$PROJECT_NAME"
	printf '  Branch      : %s\n' "$( (( INITIALIZE_GIT )) && printf 'develop' || printf '(git disabled)')"
	printf '  OpenCode    : %s agents, %s commands\n' "$agent_count" "$command_count"
	printf '  Validation  : %s\n' "$( (( RUN_VALIDATION )) && printf 'build, test and format passed' || printf 'skipped')"
	printf '\nNext steps:\n'
	printf '  cd %s\n' "$DEST"
	printf '  export %s_SQLSERVER_CONNECTION_STRING="Server=localhost;Database=%s;User Id=sa;Password=<password>;Encrypt=True;TrustServerCertificate=True"\n' \
		"$PROJECT_NAME_UPPER" "$PROJECT_NAME_LOWER"
	if (( INITIALIZE_GIT )); then
		printf '  git status\n'
	fi
	printf '  dotnet run --project src/%s.Api\n' "$PROJECT_NAME"
	printf '\nThen start the first feature from OpenCode:\n'
	printf '  /feature "describe the first capability"\n'
	printf '\nRead AGENTS.md and docs/guides/agent-usage.md before writing code.\n\n'
}
