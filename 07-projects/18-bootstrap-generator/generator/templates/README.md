# generator/templates/

The neutral workspace templates (the files `wsx init` lays down: `context/*.md`,
`frameworks/*.md`, `.gitignore`, `.obsidian/*`, etc.).

**v0 note:** these templates are currently **embedded as strings** in
[`../wsxlib/scaffold.py`](../wsxlib/scaffold.py) (`TEMPLATES` dict) so that `wsx init`
has zero external-file dependencies and is trivially reliable. Externalizing them
into real files under this directory — and rendering them with `core.render` — is a
planned follow-up once the scaffold set stabilizes. The placeholder syntax is `{{dotted.key}}`,
resolved against the profile plus `{{date}}`.
