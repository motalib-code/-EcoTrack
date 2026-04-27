# Labelled Dataset + ECI/SVEEP Integration Plan

## 1. Dataset Goal
Build a bilingual election-claim dataset for India (English + Hindi) with labels:
- true
- misleading
- false
- unverifiable

Target use case:
- First-time voters in Jatani, Odisha
- Misinformation triage for local election stakeholders

## 2. Row Schema (One Claim)
| Field | Type | Description |
|---|---|---|
| id | string (UUID) | Unique claim id |
| claim_text_en | string | English version of claim |
| claim_text_hi | string | Hindi (Devanagari) version |
| language | enum | en / hi / mixed |
| source_type | enum | claimreview / news / social / whatsapp / telegram |
| source_url | string | Original URL or source marker |
| collected_at | datetime | Collection timestamp |
| locality | string | Example: Jatani, Khordha |
| label | enum | true / misleading / false / unverifiable |
| evidence_urls | list[string] | Supporting links |
| evidence_snippets | list[string] | Exact supporting/contradicting lines |
| claimreview_id | string | If available |
| annotator_id | string | Human annotator code |
| annotator_confidence | float | 0.0 - 1.0 |
| notes | string | Brief reason for label |

## 3. Labeling Policy
- true: matches official ECI/SVEEP/authoritative source
- misleading: partially true but context altered
- false: contradicted by verified evidence
- unverifiable: no reliable evidence available

## 4. Collection Sources
- ClaimReview feeds and Google Fact Check API
- Official ECI/SVEEP announcements
- Regional Odisha news portals
- Opt-in community forwards (WhatsApp/Telegram)

## 5. Collection Pipeline
1. Ingest source feeds on schedule (hourly/daily).
2. Extract and normalize claim sentence.
3. Detect language and create bilingual normalization fields.
4. Deduplicate via embedding similarity.
5. Auto-prioritize with rules (date mismatch, suspicious URL, urgency bait).
6. Human annotation for final label.
7. Adjudication for disagreements.
8. Export versioned dataset to JSONL/CSV.

## 6. Quality Control
- Use 2 annotators minimum per claim.
- Use 3 annotators for high-impact claims.
- Monitor Cohen's Kappa, target >= 0.70.
- Weekly audit for label drift.

## 7. Milestone Targets
- Seed dataset: 5,000 claims
- Hindi share: at least 33%
- Gold set: 1,000 claims with strong agreement

## 8. ECI + SVEEP Integration Plan
### Surface in Product
- EPIC status lookup (with consent)
- Polling booth information (minimal output)
- Election timeline cards
- EVM/VVPAT education content
- Local BLO contact and helpline references

### Privacy-First EPIC Flow
1. User gives consent.
2. Client submits EPIC securely.
3. Server queries ECI/vendor.
4. Return minimal data: status, booth, last-updated.
5. Log only hashed lookup token for audit.

### Low-Bandwidth Support
- Text-first guides
- Small images only
- Downloadable PDF one-pagers
- Cached official links with last-updated timestamp

## 9. Compliance Checklist (Data)
- Collect only necessary fields.
- Avoid storing personal identifiers in analytics logs.
- Encrypt data in transit and at rest.
- Define retention period and purge policy.
- Add human escalation for legal/high-impact claims.
