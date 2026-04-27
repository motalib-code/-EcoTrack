# Production Deployment Checklist (20 Items)

## Infrastructure
- [ ] 1. Dockerize API service and model service.
- [ ] 2. Create Kubernetes manifests (or equivalent) for API, DB, workers.
- [ ] 3. Configure horizontal autoscaling for API and model workers.
- [ ] 4. Configure staging and production environments separately.

## Security and Secrets
- [ ] 5. Store secrets in a secure manager (not in repo).
- [ ] 6. Rotate JWT/API keys periodically.
- [ ] 7. Enforce HTTPS/TLS on all ingress paths.
- [ ] 8. Apply strict CORS and trusted origin policy.

## Authentication and Access
- [ ] 9. Enforce OAuth2 + JWT validation on protected routes.
- [ ] 10. Implement role-based access (admin queue, moderation actions).

## Data and Privacy
- [ ] 11. Use privacy-first EPIC lookup flow (no raw EPIC retention).
- [ ] 12. Add PII redaction for logs and error traces.
- [ ] 13. Define retention + purge policy for lookup audit logs.

## MLOps and Model Governance
- [ ] 14. Version models in a model registry.
- [ ] 15. Track model metrics (precision/recall/F1, drift).
- [ ] 16. Add fallback strategy if model service fails.

## Testing and Quality
- [ ] 17. Add unit tests for auth, misinfo scoring, and EPIC validation.
- [ ] 18. Add integration tests for full request flows.
- [ ] 19. Run load tests and validate p95 latency targets.

## Operations
- [ ] 20. Configure monitoring/alerts and on-call runbook with rollback steps.
