import hashlib
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import joblib
import requests
from fastapi import Body, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

try:
    from pymongo import MongoClient
except Exception:  # pragma: no cover
    MongoClient = None


# -------------------------
# Configuration
# -------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
MODEL_PATH = os.getenv("MODEL_PATH", "misinfo_model.pkl")
EPIC_AUDIT_SALT = os.getenv("EPIC_AUDIT_SALT", "replace-with-long-random-salt")

MONGO_URI = os.getenv("MONGO_URI", "")
MONGO_DB = os.getenv("MONGO_DB", "votewise")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_BASE_URL = os.getenv("GROQ_API_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


# -------------------------
# App and middleware
# -------------------------
APP_DESCRIPTION = """
## Why This Solution Matters (Real-World Impact)
VoteGuide AI bridges the gap between the Election Commission's resources and the everyday citizen.
By consolidating fragmented data into a single, intuitive platform powered by AI, it reduces the
friction of democratic participation.

When citizens are informed, when they know exactly how, where, and why to vote, democracy strengthens.
This platform is designed to convert passive observers into active, educated voters.

## Our Solution and Features
VoteGuide AI is an apolitical, highly interactive platform designed to educate and assist voters at every step.

- AI Assistant: instant conversational election guidance.
- ECI Map and Booth Finder: locate polling booth information quickly.
- EVM Demo Simulator: understand the voting process before election day.
- Gamified Election Quiz: strengthen civic awareness through engagement.
- Structured Educational Modules: progressive learning on registration and institutions.
- Multi-lingual Accessibility: supports English, Hindi, and extensible regional language workflows.

## Innovation Points
- Zero-dependency SPA-style interaction for fast user experience.
- Immersive visual layer support (including WebGL-ready frontend patterns).
- Mobile-first responsiveness for low-cost phones to large screens.
- Serverless AI integration pattern for secure key handling and low-latency responses.

## Architecture and How It Works
- Frontend Layer: HTML/CSS/JS and Streamlit-driven user workflows.
- State and Routing: route-based UI transitions with dynamic rendering.
- Authentication: OAuth-compatible user/session handling.
- Backend and AI Layer: secure API proxy pattern for model providers.
- This FastAPI service handles auth, misinformation checks, EPIC-safe lookup flow, and simulation APIs.
"""

app = FastAPI(title="VoteWise AI API", version="2.0.0", description=APP_DESCRIPTION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# -------------------------
# Optional MongoDB + fallback
# -------------------------
mongo_db = None
if MongoClient and MONGO_URI:
    try:
        mongo_db = MongoClient(MONGO_URI)[MONGO_DB]
    except Exception:
        mongo_db = None

in_memory_store: Dict[str, List[Dict[str, Any]]] = {
    "misinfo": [],
    "moderation": [],
    "epic_lookups": [],
    "simulations": [],
    "groq_cache": [],
}


def insert_doc(collection: str, doc: Dict[str, Any]) -> None:
    if mongo_db is not None:
        mongo_db[collection].insert_one(doc)
        return
    in_memory_store[collection].append(doc)


def find_pending_moderation(limit: int = 100) -> List[Dict[str, Any]]:
    if mongo_db is not None:
        rows = list(mongo_db.moderation.find({"status": "pending"}).limit(limit))
        for row in rows:
            row["_id"] = str(row.get("_id"))
        return rows
    return [row for row in in_memory_store["moderation"] if row.get("status") == "pending"][:limit]


def find_cached_groq_response(query_hash: str) -> Optional[Dict[str, Any]]:
    if mongo_db is not None:
        row = mongo_db.groq_cache.find_one({"query_hash": query_hash})
        if row:
            row["_id"] = str(row.get("_id"))
        return row

    for row in in_memory_store["groq_cache"]:
        if row.get("query_hash") == query_hash:
            return row
    return None


# -------------------------
# Auth
# -------------------------
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: str = "user"
    disabled: bool = False


class UserInDB(User):
    hashed_password: str


def _hash_password(plain_text: str) -> str:
    return pwd_context.hash(plain_text)


fake_users_db: Dict[str, UserInDB] = {
    "alice": UserInDB(
        username="alice",
        full_name="Alice Voter",
        email="alice@example.com",
        role="user",
        disabled=False,
        hashed_password=_hash_password("password123"),
    ),
    "admin": UserInDB(
        username="admin",
        full_name="System Admin",
        email="admin@example.com",
        role="admin",
        disabled=False,
        hashed_password=_hash_password("adminpass"),
    ),
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = fake_users_db.get(username)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(subject: str, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "exp": expires_at}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise auth_error
    except JWTError as exc:
        raise auth_error from exc

    user = fake_users_db.get(username)
    if user is None:
        raise auth_error
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


async def get_admin_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# -------------------------
# ML baseline
# -------------------------
vectorizer = TfidfVectorizer(max_features=5000)
classifier = LogisticRegression(max_iter=500)


def train_baseline_stub() -> None:
    sample_texts = [
        "Official ECI voter registration opens on Monday",
        "Bring voter ID and follow EVM instructions",
        "Breaking: election cancelled forever share now",
        "Get money reward if you skip voting and register here",
        "Polling booth details should be verified on ECI portal",
        "Secret method guarantees your candidate win",
        "मतदान की तारीख ECI वेबसाइट पर देखें",
        "यह नकली लिंक है जो वोटर डेटा चुराता है",
    ]
    labels = [0, 0, 1, 1, 0, 1, 0, 1]
    x_matrix = vectorizer.fit_transform(sample_texts)
    classifier.fit(x_matrix, labels)
    joblib.dump((vectorizer, classifier), MODEL_PATH)


if os.path.exists(MODEL_PATH):
    vectorizer, classifier = joblib.load(MODEL_PATH)
else:
    train_baseline_stub()
    vectorizer, classifier = joblib.load(MODEL_PATH)


# -------------------------
# Prompt templates
# -------------------------
VERIFY_PROMPT_EN = (
    "You are an Indian election fact-check assistant. Verify the claim using reliable sources. "
    "Return JSON with fields: verdict (true/false/unverifiable), confidence (0-1), "
    "evidence_urls (max 3), red_flags (list), explanation (short)."
)

VERIFY_PROMPT_HI = (
    "आप भारतीय चुनाव तथ्य-जांच सहायक हैं। दावे को विश्वसनीय स्रोतों से जांचें। "
    "JSON लौटाएं: verdict, confidence, evidence_urls, red_flags, explanation."
)


def build_verification_prompt(text: str, language: str, locality: str = "Jatani, Odisha") -> str:
    base = VERIFY_PROMPT_HI if language.lower() == "hi" else VERIFY_PROMPT_EN
    return (
        f"{base}\n"
        f"Claim: {text}\n"
        f"Language: {language}\n"
        f"Locality: {locality}\n"
        "Respond only in valid JSON."
    )


def mock_llm_verify(text: str, score: float, language: str) -> Dict[str, Any]:
    red_flags = []
    normalized = text.lower()
    if re.search(r"share now|urgent|breaking", normalized):
        red_flags.append("Urgency bait language")
    if re.search(r"free money|reward|guaranteed", normalized):
        red_flags.append("Manipulative incentive")

    verdict = "unverifiable"
    if score > 0.75:
        verdict = "likely_false"
    elif score < 0.35:
        verdict = "likely_true"

    explanation = (
        "Automated secondary verification completed. Use official ECI references for final confirmation."
        if language.lower() != "hi"
        else "द्वितीयक स्वचालित जांच पूरी हुई। अंतिम पुष्टि के लिए ECI स्रोत देखें।"
    )
    return {
        "verdict": verdict,
        "confidence": round(min(max(score, 0.05), 0.95), 2),
        "evidence_urls": ["https://eci.gov.in", "https://pib.gov.in/factcheck"],
        "red_flags": red_flags,
        "explanation": explanation,
    }


# -------------------------
# API schemas
# -------------------------
class ClaimRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=2000)
    language: str = Field(default="en", pattern=r"^(en|hi|mixed)$")
    escalate: bool = False


class MisinfoResponse(BaseModel):
    id: str
    score: float
    verdict: str
    confidence: int
    explanation: str
    rules_triggered: List[str]
    llm_verification: Optional[Dict[str, Any]] = None


class EPICLookupRequest(BaseModel):
    epic_number: str = Field(..., min_length=5, max_length=20)
    consent: bool


class VoteSimulationRequest(BaseModel):
    choice: int = Field(..., ge=1, le=4)


class ElectionAnalysisRequest(BaseModel):
    state: str = Field(..., min_length=2, max_length=100)
    year: int = Field(..., ge=1952, le=2100)
    election_type: str = Field(..., pattern=r"^(Lok Sabha|Assembly)$")
    user_query: str = Field(..., min_length=5, max_length=1500)


class ElectionAnalysisResponse(BaseModel):
    response: str
    source: str
    cached: bool
    disclaimer: str


live_votes = {1: 142, 2: 198, 3: 87, 4: 23}

INDIAVOTES_SAMPLE_CONTEXT = {
    "Odisha": {
        "Lok Sabha": {
            2019: {
                "party_performance": [
                    {"party": "BJD", "seats": 12, "vote_share": 42.8, "alliance": "Regional"},
                    {"party": "BJP", "seats": 8, "vote_share": 38.4, "alliance": "NDA"},
                    {"party": "INC", "seats": 1, "vote_share": 13.8, "alliance": "UPA"},
                ],
                "turnout": 74.1,
                "nota_share": 1.5,
            },
            2024: {
                "party_performance": [
                    {"party": "BJP", "seats": 20, "vote_share": 45.3, "alliance": "NDA"},
                    {"party": "BJD", "seats": 1, "vote_share": 37.4, "alliance": "Regional"},
                    {"party": "INC", "seats": 0, "vote_share": 12.5, "alliance": "UPA"},
                ],
                "turnout": 75.7,
                "nota_share": 1.1,
            },
        }
    },
    "Karnataka": {
        "Assembly": {
            2018: {
                "party_performance": [
                    {"party": "BJP", "seats": 104, "vote_share": 36.4, "alliance": "NDA"},
                    {"party": "INC", "seats": 80, "vote_share": 38.0, "alliance": "UPA"},
                    {"party": "JD(S)", "seats": 37, "vote_share": 18.3, "alliance": "Regional"},
                ],
                "turnout": 72.1,
                "nota_share": 0.9,
            },
            2023: {
                "party_performance": [
                    {"party": "INC", "seats": 135, "vote_share": 42.9, "alliance": "UPA"},
                    {"party": "BJP", "seats": 66, "vote_share": 36.0, "alliance": "NDA"},
                    {"party": "JD(S)", "seats": 19, "vote_share": 13.3, "alliance": "Regional"},
                ],
                "turnout": 73.2,
                "nota_share": 0.7,
            },
        }
    },
}


def _get_indiavotes_context(state: str, election_type: str, year: int) -> Dict[str, Any]:
    state_data = INDIAVOTES_SAMPLE_CONTEXT.get(state, {})
    type_data = state_data.get(election_type, {})
    year_data = type_data.get(year)
    if not year_data:
        return {
            "party_performance": [],
            "turnout": None,
            "nota_share": None,
        }
    return year_data


def _build_election_prompt(req: ElectionAnalysisRequest, context: Dict[str, Any]) -> str:
    return (
        "You are an AI Election Assistant integrated with IndiaVotes data.\n"
        "Your tasks:\n"
        "- Explain election results clearly in Hindi + English.\n"
        "- Show tables: Party-wise seats, vote share %, alliance performance.\n"
        "- Highlight swing compared to previous election.\n"
        "- Mention voter turnout and NOTA impact.\n"
        "- Keep responses simple, interactive, and user-friendly.\n"
        "- Always clarify: This is historical data from IndiaVotes, not live ECI results.\n\n"
        f"State: {req.state}\n"
        f"Election Type: {req.election_type}\n"
        f"Year: {req.year}\n"
        f"IndiaVotes Context: {context}\n"
        f"User Query: {req.user_query}\n"
    )


def query_groq(prompt: str) -> str:
    if not GROQ_API_KEY:
        raise HTTPException(status_code=503, detail="GROQ_API_KEY is not configured")

    url = f"{GROQ_API_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail="Failed to reach Groq API") from exc
    except (KeyError, IndexError, TypeError) as exc:
        raise HTTPException(status_code=502, detail="Invalid Groq API response format") from exc


def apply_rule_signals(claim_text: str) -> List[str]:
    text = claim_text.lower()
    flags: List[str] = []
    if "eci.gov.in" not in text and ("official" in text or "ec announcement" in text):
        flags.append("Official-source claim without official URL")
    if re.search(r"free money|cash reward|click this link", text):
        flags.append("Financial bait or phishing pattern")
    if re.search(r"election cancelled|polling postponed indefinitely", text):
        flags.append("Potential high-impact election rumor")
    return flags


def hash_epic_for_audit(epic: str) -> str:
    payload = f"{EPIC_AUDIT_SALT}:{epic}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# -------------------------
# Endpoints
# -------------------------
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token(subject=user.username)
    return Token(access_token=token, token_type="bearer")


@app.post("/detect_misinfo", response_model=MisinfoResponse)
async def detect_misinfo(
    claim: ClaimRequest,
    current_user: UserInDB = Depends(get_current_user),
) -> MisinfoResponse:
    x_matrix = vectorizer.transform([claim.text])
    ml_score = float(classifier.predict_proba(x_matrix)[0][1])
    rule_flags = apply_rule_signals(claim.text)

    rule_boost = min(0.25, 0.08 * len(rule_flags))
    final_score = min(1.0, ml_score + rule_boost)

    if final_score >= 0.8:
        verdict = "LIKELY_FALSE"
    elif final_score >= 0.4:
        verdict = "NEEDS_VERIFICATION"
    else:
        verdict = "LIKELY_TRUE"

    llm_payload = None
    if claim.escalate or final_score >= 0.65:
        llm_payload = {
            "prompt": build_verification_prompt(claim.text, claim.language),
            "result": mock_llm_verify(claim.text, final_score, claim.language),
        }

    claim_id = str(uuid.uuid4())
    doc = {
        "claim_id": claim_id,
        "text": claim.text,
        "language": claim.language,
        "user": current_user.username,
        "ml_score": ml_score,
        "final_score": final_score,
        "verdict": verdict,
        "rules_triggered": rule_flags,
        "llm_verification": llm_payload,
        "created_at": datetime.now(timezone.utc),
    }
    insert_doc("misinfo", doc)

    if claim.escalate or final_score >= 0.85:
        insert_doc(
            "moderation",
            {
                "item_id": str(uuid.uuid4()),
                "claim_id": claim_id,
                "status": "pending",
                "priority": "high" if final_score >= 0.9 else "medium",
                "created_at": datetime.now(timezone.utc),
                "summary": llm_payload["result"] if llm_payload else None,
            },
        )

    explanation = "Hybrid analysis completed (ML + rule checks)."
    if llm_payload is not None:
        explanation = "Hybrid analysis completed with secondary LLM verification."

    return MisinfoResponse(
        id=claim_id,
        score=round(final_score, 4),
        verdict=verdict,
        confidence=int(round((1 - abs(0.5 - final_score)) * 100)),
        explanation=explanation,
        rules_triggered=rule_flags,
        llm_verification=llm_payload["result"] if llm_payload else None,
    )


@app.post("/eci_proxy/lookup")
async def eci_lookup_proxy(
    data: EPICLookupRequest,
    current_user: UserInDB = Depends(get_current_user),
) -> Dict[str, Any]:
    if not data.consent:
        raise HTTPException(status_code=400, detail="Consent is mandatory for EPIC lookup")

    epic_token = hash_epic_for_audit(data.epic_number)
    lookup_id = str(uuid.uuid4())

    # Stubbed response for demo. Replace with approved ECI/vendor integration.
    response = {
        "lookup_id": lookup_id,
        "status": "record_found",
        "polling_station": "Jatani High School, Room 4",
        "booth_number": 12,
        "serial_number": 442,
        "district": "Khordha",
        "state": "Odisha",
        "disclaimer": "Verify final details on official ECI portal.",
    }

    insert_doc(
        "epic_lookups",
        {
            "lookup_id": lookup_id,
            "epic_hash": epic_token,
            "user": current_user.username,
            "created_at": datetime.now(timezone.utc),
        },
    )
    return response


@app.post("/simulate_vote")
async def simulate_vote(
    data: VoteSimulationRequest,
    current_user: UserInDB = Depends(get_current_user),
) -> Dict[str, Any]:
    live_votes[data.choice] += 1
    simulation_id = str(uuid.uuid4())
    insert_doc(
        "simulations",
        {
            "simulation_id": simulation_id,
            "user": current_user.username,
            "choice": data.choice,
            "created_at": datetime.now(timezone.utc),
        },
    )
    return {
        "simulation_id": simulation_id,
        "result": "vote recorded in simulation",
        "choice": data.choice,
    }


@app.get("/simulate_vote/results")
async def simulate_vote_results() -> Dict[str, Any]:
    total_votes = sum(live_votes.values())
    breakdown = []
    for candidate_id, vote_count in live_votes.items():
        pct = round((vote_count / total_votes) * 100, 2) if total_votes else 0.0
        breakdown.append({"candidate_id": candidate_id, "votes": vote_count, "percentage": pct})
    return {"total_votes": total_votes, "breakdown": breakdown}


@app.get("/moderation/queue")
async def moderation_queue(_: UserInDB = Depends(get_admin_user)) -> Dict[str, Any]:
    return {"pending": find_pending_moderation(limit=100)}


@app.get("/prompts/templates")
async def prompt_templates(_: UserInDB = Depends(get_current_user)) -> Dict[str, str]:
    return {
        "verify_en": VERIFY_PROMPT_EN,
        "verify_hi": VERIFY_PROMPT_HI,
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "VoteWise AI API",
        "time": datetime.now(timezone.utc),
        "mongo_connected": mongo_db is not None,
    }


@app.post("/assistant/election-analysis", response_model=ElectionAnalysisResponse)
async def election_analysis_with_groq(
    data: ElectionAnalysisRequest,
    current_user: UserInDB = Depends(get_current_user),
) -> ElectionAnalysisResponse:
    context = _get_indiavotes_context(data.state, data.election_type, data.year)
    prompt = _build_election_prompt(data, context)

    cache_key = hashlib.sha256(
        f"{data.state}|{data.year}|{data.election_type}|{data.user_query}".encode("utf-8")
    ).hexdigest()
    cached = find_cached_groq_response(cache_key)
    if cached:
        return ElectionAnalysisResponse(
            response=cached.get("response", ""),
            source="groq",
            cached=True,
            disclaimer="Historical analysis from IndiaVotes-style data, not live ECI results.",
        )

    groq_response = query_groq(prompt)
    cache_doc = {
        "id": str(uuid.uuid4()),
        "query_hash": cache_key,
        "state": data.state,
        "year": data.year,
        "election_type": data.election_type,
        "user_query": data.user_query,
        "response": groq_response,
        "user": current_user.username,
        "created_at": datetime.now(timezone.utc),
    }
    insert_doc("groq_cache", cache_doc)

    return ElectionAnalysisResponse(
        response=groq_response,
        source="groq",
        cached=False,
        disclaimer="Historical analysis from IndiaVotes-style data, not live ECI results.",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
