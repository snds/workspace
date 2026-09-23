# Claude surfaces are personal-only (06-context/memory/feedback-credential-scoping.md).
# Included for repos with an snds/* remote (includeIf hasconfig in the Claude env overlay).
# A repo that also has an employer remote gets a later no-identity include, so this
# identity never applies there. No remote URLs in this file (git forbids them inside
# hasconfig includes).
[user]
	name = Sean Sands
	email = 570874+snds@users.noreply.github.com
