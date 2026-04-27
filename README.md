# VoteGuide AI (VoteWise AI)

VoteGuide AI bridges the gap between Election Commission resources and everyday citizens by consolidating fragmented election information into one intuitive AI-powered platform.

When people know how, where, and why to vote, democratic participation improves. This project is built to turn passive observers into active, informed voters.

## Real-World Impact
- Reduces friction in first-time voting journeys.
- Improves access for rural and low-bandwidth users.
- Provides multilingual civic education in a conversational format.
- Helps fight misinformation through layered verification.

## Solution Overview
VoteGuide AI is an apolitical, interactive platform that supports citizens at every stage of election participation.

| Feature | Description |
|---|---|
| AI Assistant | Gemini/Groq compatible assistant for election Q and A in real time. |
| ECI Map and Booth Finder | Polling booth discovery through map and lookup integrations. |
| EVM Demo Simulator | Virtual EVM flow to demystify voting procedures. |
| Gamified Election Quiz | Civic learning with score-based engagement and badges. |
| Structured Learning Modules | Guided lessons on registration, institutions, and first-time voting. |
| Multilingual Accessibility | English, Hindi, and optional translation to additional Indian languages. |

## Innovation Highlights
- Zero-dependency SPA-style interaction for fast transitions in the frontend experience.
- Immersive visual layer support for modern civic-tech UX.
- Mobile-first layouts optimized for low-cost phones and large screens.
- Serverless AI proxy pattern to keep provider keys secure.

## Architecture
- Frontend layer: HTML5/CSS3/JS modules and Streamlit interface.
- Backend layer: FastAPI services for auth, voting flows, and misinformation checks.
- AI layer: Provider-agnostic connectors (Gemini, Groq, Claude-compatible prompts).
- Data layer: MongoDB optional, in-memory fallback for local runs.
- Auth layer: OAuth2 password flow + JWT.

## Project Structure
- [main.py](main.py): FastAPI backend
- [streamlit_app.py](streamlit_app.py): Streamlit UI
- [ElectionAssistant.py](ElectionAssistant.py): assistant logic
- [dataset_pipeline.md](dataset_pipeline.md): dataset schema and collection flow
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md): production rollout checklist
- [master_prompt.txt](master_prompt.txt): prompt templates
- [requirements.txt](requirements.txt): Python dependencies

## Local Setup
1. Create and activate virtual environment.
2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Create env file.

```bash
copy .env.example .env
```

4. Run backend.

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

5. Run frontend.

```bash
streamlit run streamlit_app.py
```

## API Integrations (Secure Configuration)
Store all credentials in environment variables. Do not hardcode keys in code, docs, or commits.

Recommended variables:
- GEMINI_API_KEY=
- GROQ_API_KEY=
- XAI_API_KEY=
- POLLINATIONS_API_KEY=
- GOOGLE_VO3_API_KEY=
- GOOGLE_TTS_API_KEY=
- YOUTUBE_DATA_API_KEY=
- NEWS_API_KEY=

Optional local-only file:
- client_secrets.json for YouTube OAuth desktop flow (never commit this file).

## Suggested Install for Extended Tooling
If you are enabling trend research, YouTube upload, and extra generation tools, install:

```bash
pip install groq google-api-python-client google-auth-oauthlib google-auth-httplib2 pytrends gtts requests
```

## Security Notice
- Any previously exposed API key should be considered compromised.
- Rotate all keys immediately in provider dashboards.
- Add local secrets to .gitignore and keep only placeholders in tracked files.
- Keep EPIC and other PII out of logs and analytics events.

## Key API Endpoints
- POST /token
- POST /detect_misinfo
- POST /eci_proxy/lookup
- POST /simulate_vote
- GET /simulate_vote/results
- GET /moderation/queue
- GET /prompts/templates
- GET /health

## Roadmap
1. Baseline misinformation model: TF-IDF + Logistic Regression.
2. Upgrade: XLM-R multilingual fine-tuning for Hindi + English.
3. Add evidence-grounded explainability and moderation workflows.
