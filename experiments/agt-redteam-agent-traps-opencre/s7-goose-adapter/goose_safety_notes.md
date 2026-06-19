# Goose Safety Notes

- Do not run Goose with real provider credentials in this experiment.
- Use mock tools before any live-agent adapter.
- Capture normalized traces only; no raw secrets or live external effects.
- Treat live behavioural evaluation as a later SLO runbook with explicit gates.
