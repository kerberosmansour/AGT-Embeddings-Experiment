# Security Policy

This repository contains research artifacts, validators, and documentation for
an AGT prompt-injection embeddings experiment. It does not ship a production
security control.

## Supported Scope

Please report:

- accidental publication of raw secrets, live credentials, customer data, or
  private prompts;
- vulnerabilities in scripts or Rust tools that could corrupt validation output
  or hide failed checks;
- supply-chain issues in dependencies used by the validators or baseline runner;
- provenance or manifest bugs that make a committed artifact unverifiable.

The following are not security vulnerabilities in this repository:

- false positives or false negatives already visible in the claims ledger;
- disagreement with the experimental method;
- requests to promote the embedding signal into default blocking behaviour;
- missing production hardening for a detector this repository does not ship.

## Reporting

Use GitHub private vulnerability reporting if it is enabled for the repository.
If it is not enabled, open a public issue with a minimal description and avoid
including secrets, private prompts, or raw sensitive data.

For methodology gaps, open a normal GitHub issue and link the relevant artifact,
validator, or claims-ledger row.

## Disclosure Expectations

Maintainers will triage reports against the research scope above. Fixes should
prefer reproducible validators, manifest checks, and narrow documentation
corrections over broad claims.
