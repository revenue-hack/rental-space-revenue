# Public GitHub release checklist

Use this reference only when preparing the skill for public distribution.

## Required checks

- Keep `SKILL.md` at the repository root so the skill entrypoint is easy to discover.
- Keep runtime instructions in `SKILL.md`, conditional platform details in `references/`, and deterministic processing in `scripts/`. Do not include booking or settlement datasets, even as examples.
- Search the complete repository for email addresses, phone numbers, postal addresses, credentials, account IDs, real reservation IDs, raw message bodies, local filesystem paths, and generated financial output.
- Run `quick_validate.py` against the repository root.
- Run both helper scripts against temporary generic fixtures created outside the repository, and when available one private fixture that is never copied into the repository.
- Ensure `__pycache__`, temporary output, downloaded mail, statements, spreadsheets, and local environment files are ignored.
- Select a license intentionally before public release. Do not infer a license from repository visibility.

## Suggested publication sequence

1. Create an empty public GitHub repository only after the user explicitly requests publication.
2. Push this directory as the repository root, retaining its commit history when practical.
3. Verify the public file list and search the remote repository for sensitive strings.
4. Tag the first reviewed release, for example `v0.1.0`.

The skill does not require a GitHub Actions workflow. Add one only when automated validation provides clear value.
