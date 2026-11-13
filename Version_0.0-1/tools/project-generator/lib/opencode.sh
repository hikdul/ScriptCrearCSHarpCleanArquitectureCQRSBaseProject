#!/usr/bin/env bash
# Copies the reusable OpenCode configuration from the source repository.

configure_opencode() {
	local exclude_file="$CONFIG_DIR/opencode-exclude.txt"

	copy_repo_directory_rendered ".opencode/agents" ".opencode/agents" "$exclude_file"
	copy_repo_directory_rendered ".opencode/commands" ".opencode/commands"

	local agent_count command_count
	agent_count="$(find "$DEST/.opencode/agents" -type f -name '*.md' | wc -l | tr -d ' ')"
	command_count="$(find "$DEST/.opencode/commands" -type f -name '*.md' | wc -l | tr -d ' ')"

	(( agent_count > 0 )) || die "No OpenCode agents were copied."
	(( command_count > 0 )) || die "No OpenCode commands were copied."

	success "Configured OpenCode with $agent_count agents and $command_count commands."
}
