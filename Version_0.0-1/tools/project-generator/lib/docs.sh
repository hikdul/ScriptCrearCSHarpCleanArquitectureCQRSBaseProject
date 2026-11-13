#!/usr/bin/env bash
# Copies the reusable documentation and creates the specifications guide.

configure_documentation() {
	copy_repo_directory_rendered "docs/architecture" "docs/architecture"
	copy_repo_directory_rendered "docs/workflows" "docs/workflows"

	render_file "$REPO_ROOT/docs/agents/agents-list.md" "$DEST/docs/agents/agents-list.md"
	render_file "$TEMPLATES_DIR/docs/agents/README.md" "$DEST/docs/agents/README.md"

	# The source guide is product-tuned in its specification examples. The
	# template keeps the method and replaces those examples with the clean
	# bootstrap specification.
	render_file "$TEMPLATES_DIR/docs/guides/agent-usage.md" "$DEST/docs/guides/agent-usage.md"

	render_file "$TEMPLATES_DIR/docs/README.md" "$DEST/docs/README.md"
	render_file "$TEMPLATES_DIR/docs/agent-runs/README.md" "$DEST/docs/agent-runs/README.md"
}

initialize_specifications() {
	render_file \
		"$TEMPLATES_DIR/docs/specifications/000-spec-example.md" \
		"$DEST/docs/specifications/000-spec-example.md"

	local specification_count
	specification_count="$(find "$DEST/docs/specifications" -type f -name '*.md' | wc -l | tr -d ' ')"
	[[ "$specification_count" == "1" ]] \
		|| die "The generated specifications directory must contain exactly one reference document."

	success "Created docs/specifications/000-spec-example.md."
}
