# Clean fixture (synthetic owners only)

Owner-level tokens pass: acme-corp, acme-bb, Acme, acmeapp.
Placeholders pass: acme-corp/*, acme-corp/<repo>, ~/Projects/acme-corp/**, ~/Projects/*acmeapp*/**.
Allowlisted slug form passes: acme-corp/acmeapp.
Personal and third-party owners pass: pat-sample/sample-tool, oss-upstream/lib/src/x.py.
A personal PR URL passes: https://github.com/pat-sample/tool/pull/1
Vault paths pass: 07-projects/05-ACMEAPP/SESSION-STATE.md
Bare mail-domain mentions pass: acme-mail.example, `email_domains: ["acme-mail.example"]`, @acme-mail.example.

> a quote with no employer anchor nearby
