# api/translate/main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import os
import re
from functools import lru_cache

app = FastAPI(title="ASL Translate API", version="1.0.0")

# Configure where the other APIs live. Defaults assume:
# - Signs API on :8001
# - Phrases API on :8002
SIGNS_BASE_URL = os.getenv("SIGNS_BASE_URL", "http://127.0.0.1:8001")
PHRASES_BASE_URL = os.getenv("PHRASES_BASE_URL", "http://127.0.0.1:8002")

# ---------------------------
# Models
# ---------------------------
class Step(BaseModel):
    handshape: str
    orientation: str
    location: str
    motion: str = "none"

class Phrase(BaseModel):
    key: str
    name: str
    steps: List[Step]
    notes: Optional[str] = None

class LetterShape(BaseModel):
    letter: str
    handshape: str
    orientation: str
    location: str
    motion: str = "none"

class Action(BaseModel):
    """One unit of translated output."""
    type: str  # "phrase" or "letter"
    label: str
    steps: List[Step]

class TranslationRequest(BaseModel):
    text: str

class TranslationResponse(BaseModel):
    normalized_text: str
    path: List[Action]   # ordered actions to perform
    source: str          # "phrases" | "spelling" | "mixed"
    warnings: List[str] = []

# ---------------------------
# Helpers
# ---------------------------
_clean_re = re.compile(r"[^a-z0-9\s]+")

def normalize(text: str) -> str:
    return _clean_re.sub("", text.lower()).strip()

@lru_cache(maxsize=2048)
def is_phrase_available() -> bool:
    try:
        with httpx.Client(timeout=2.0) as c:
            r = c.get(f"{PHRASES_BASE_URL}/phrases")
            return r.status_code == 200
    except Exception:
        return False

@lru_cache(maxsize=2048)
def is_signs_available() -> bool:
    try:
        with httpx.Client(timeout=2.0) as c:
            r = c.get(f"{SIGNS_BASE_URL}/signs/A")
            return r.status_code == 200
    except Exception:
        return False

# Tiny local fallback so demos work without the other services running
LOCAL_PHRASES: Dict[str, Phrase] = {
    "hello": Phrase(
        key="PHRASE_HELLO",
        name="hello",
        steps=[Step(handshape="flat-hand", orientation="palm-out", location="near-temple", motion="small-outward-wave")],
        notes="Fallback phrase"
    ),
    "how are you": Phrase(
        key="PHRASE_HOW_ARE_YOU",
        name="how are you",
        steps=[
            Step(handshape="curved-hands", orientation="palm-down", location="chest", motion="twist-together"),
            Step(handshape="index-point", orientation="palm-forward", location="neutral-space", motion="none"),
        ],
        notes="Fallback phrase"
    ),
    "do you know asl": Phrase(
        key="PHRASE_DO_YOU_KNOW_ASL",
        name="do you know asl",
        steps=[
            Step(handshape="flat-hand", orientation="palm-down", location="temple", motion="tap"),
            Step(handshape="index-point", orientation="palm-forward", location="neutral-space", motion="none"),
            Step(handshape="a-s-l-sequence", orientation="varies", location="neutral-space", motion="spell"),
        ],
        notes="Fallback phrase"
    ),
    "thank you": Phrase(
        key="PHRASE_THANK_YOU",
        name="thank you",
        steps=[Step(handshape="flat-hand", orientation="palm-in", location="chin", motion="move-forward")],
        notes="Fallback phrase"
    ),
}

# Minimal fallback letter shapes for a few letters (you can expand or rely on Signs API)
LOCAL_SIGNS: Dict[str, LetterShape] = {
    "a": LetterShape(letter="A", handshape="fist", orientation="palm-out", location="neutral-space", motion="none"),
    "b": LetterShape(letter="B", handshape="flat-hand-thumb-in", orientation="palm-out", location="neutral-space", motion="none"),
    "c": LetterShape(letter="C", handshape="curved-C", orientation="palm-out", location="neutral-space", motion="none"),
    "i": LetterShape(letter="I", handshape="pinky-extended", orientation="palm-out", location="neutral-space", motion="none"),
    "l": LetterShape(letter="L", handshape="L-shape", orientation="palm-out", location="neutral-space", motion="none"),
    "y": LetterShape(letter="Y", handshape="thumb-pinky-out", orientation="palm-out", location="neutral-space", motion="shake-small"),
}

# ---------------------------
# Remote fetchers
# ---------------------------
def fetch_phrase_by_best_match(norm_text: str) -> Optional[Phrase]:
    """
    Try exact match first (e.g., 'how are you'),
    else search the list for a phrase whose name equals the normalized text.
    """
    if is_phrase_available():
        try:
            with httpx.Client(timeout=3.0) as c:
                # Pull all phrases and try a name match client-side (keeps API simple)
                r = c.get(f"{PHRASES_BASE_URL}/phrases")
                r.raise_for_status()
                phrases = [Phrase(**p) for p in r.json()]
                for p in phrases:
                    if normalize(p.name) == norm_text:
                        return p
        except Exception:
            pass
    # fallback
    return LOCAL_PHRASES.get(norm_text)

def fetch_sign(letter: str) -> Optional[LetterShape]:
    key = letter.upper()
    if is_signs_available():
        try:
            with httpx.Client(timeout=2.0) as c:
                r = c.get(f"{SIGNS_BASE_URL}/signs/{key}")
                if r.status_code == 200:
                    data = r.json()
                    return LetterShape(
                        letter=key,
                        handshape=data["handshape"],
                        orientation=data["orientation"],
                        location=data["location"],
                        motion=data.get("motion", "none"),
                    )
        except Exception:
            pass
    # fallback
    return LOCAL_SIGNS.get(letter.lower())

# ---------------------------
# Translation core
# ---------------------------
def build_action_from_phrase(p: Phrase) -> Action:
    return Action(type="phrase", label=p.name, steps=p.steps)

def build_action_from_letter(ls: LetterShape) -> Action:
    step = Step(handshape=ls.handshape, orientation=ls.orientation, location=ls.location, motion=ls.motion)
    return Action(type="letter", label=ls.letter, steps=[step])

def translate_text_to_actions(text: str) -> TranslationResponse:
    warnings: List[str] = []
    norm = normalize(text)

    # 1) Try to match a complete phrase
    phrase = fetch_phrase_by_best_match(norm)
    if phrase:
        return TranslationResponse(
            normalized_text=norm,
            path=[build_action_from_phrase(phrase)],
            source="phrases",
            warnings=warnings
        )

    # 2) Spell it letter-by-letter (skip spaces)
    actions: List[Action] = []
    missing_letters: List[str] = []
    for ch in norm:
        if ch == " ":
            continue
        if not ch.isalpha():
            # We only handle letters here; numerals/punct could be extended later
            warnings.append(f"Character '{ch}' not supported; skipped.")
            continue
        sign = fetch_sign(ch)
        if sign:
            actions.append(build_action_from_letter(sign))
        else:
            missing_letters.append(ch)

    if not actions:
        raise HTTPException(status_code=422, detail="Could not translate input (no phrases matched and no letters available).")

    if missing_letters:
        warnings.append(f"No sign data for: {', '.join(sorted(set(missing_letters)))} (consider expanding the Signs API).")

    return TranslationResponse(
        normalized_text=norm,
        path=actions,
        source="spelling",
        warnings=warnings
    )

# ---------------------------
# Endpoints
# ---------------------------
@app.get("/", tags=["meta"])
def root():
    return {"service": "asl-translate", "version": "1.0.0"}

@app.get("/health", tags=["meta"])
def health():
    return {
        "ok": True,
        "phrases_api": is_phrase_available(),
        "signs_api": is_signs_available(),
    }

@app.get("/translate", response_model=TranslationResponse, tags=["translate"])
def translate_get(text: str = Query(..., min_length=1, description="Plain text to translate into ASL actions")):
    return translate_text_to_actions(text)

@app.post("/translate", response_model=TranslationResponse, tags=["translate"])
def translate_post(req: TranslationRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    return translate_text_to_actions(req.text)
