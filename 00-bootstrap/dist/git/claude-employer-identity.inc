# Claude commits in employer repos as the employer identity (I1; decision-claude-employer-surface).
# Included for every employer remote form, after the personal include (includeIf hasconfig in the
# Claude env overlay), so a repo with an employer remote never takes the personal identity.
# No remote URLs in this file (git forbids them inside hasconfig includes).
[user]
	useConfigOnly = true
	name = Sean Sands
	email = 271648271+sean-sands-centric@users.noreply.github.com
