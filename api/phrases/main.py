# api/phrases/main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI(title="ASL Phrases API", version="1.0.0")

# ---------- Data Models ----------
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

# ---------- Phrase Library ----------
PHRASES: Dict[str, Phrase] = {
    # HELLO
    "PHRASE_HELLO": Phrase(
        key="PHRASE_HELLO",
        name="hello",
        steps=[
            Step(
                handshape="flat-hand",
                orientation="palm-out",
                location="near-temple",
                motion="small-outward-wave"
            )
        ],
        notes="Flat hand starts near temple and moves outward in a small wave motion."
    ),

    # HOW ARE YOU
    "PHRASE_HOW_ARE_YOU": Phrase(
        key="PHRASE_HOW_ARE_YOU",
        name="how are you",
        steps=[
            Step(
                handshape="curved-hands",
                orientation="palm-down",
                location="chest",
                motion="twist-together"
            ),
            Step(
                handshape="index-point",
                orientation="palm-forward",
                location="neutral-space",
                motion="none"
            )
        ],
        notes="Hands twist together for 'how', then point forward for 'you'."
    ),

    # DO YOU KNOW ASL
    "PHRASE_DO_YOU_KNOW_ASL": Phrase(
        key="PHRASE_DO_YOU_KNOW_ASL",
        name="do you know ASL",
        steps=[
            Step(
                handshape="flat-hand",
                orientation="palm-down",
                location="temple",
                motion="tap"
            ),
            Step(
                handshape="index-point",
                orientation="palm-forward",
                location="neutral-space",
                motion="none"
            ),
            Step(
                handshape="a-s-l-sequence",
                orientation="varies",
                location="neutral-space",
                motion="spell"
            )
        ],
        notes="Tap forehead for 'know', point forward for 'you', then spell A-S-L."
    ),

    # PLEASE
    "PHRASE_PLEASE": Phrase(
        key="PHRASE_PLEASE",
        name="please",
        steps=[
            Step(
                handshape="flat-hand",
                orientation="palm-in",
                location="chest",
                motion="circle-clockwise"
            )
        ],
        notes="Flat hand on chest, make circular motion clockwise."
    ),

    # THANK YOU
    "PHRASE_THANK_YOU": Phrase(
        key="PHRASE_THANK_YOU",
        name="thank you",
        steps=[
            Step(
                handshape="flat-hand",
                orientation="palm-in",
                location="chin",
                motion="move-forward"
            )
        ],
        notes="Flat hand from chin forward, palm up."
    ),

    # NICE TO MEET YOU
    "PHRASE_NICE_TO_MEET_YOU": Phrase(
        key="PHRASE_NICE_TO_MEET_YOU",
        name="nice to meet you",
        steps=[
            Step(
                handshape="flat-hands",
                orientation="palm-in",
                location="neutral-space",
                motion="slide-right"
            ),
            Step(
                handshape="index-up",
                orientation="palm-in",
                location="neutral-space",
                motion="hands-meet"
            )
        ],
        notes="Left palm stationary, right slides across it, then both index fingers meet upright."
    ),

    # SORRY
    "PHRASE_SORRY": Phrase(
        key="PHRASE_SORRY",
        name="sorry",
        steps=[
            Step(
                handshape="fist",
                orientation="palm-in",
                location="chest",
                motion="circle-clockwise"
            )
        ],
        notes="Fist over chest moves in small clockwise circles."
    ),

    # I LOVE YOU
    "PHRASE_I_LOVE_YOU": Phrase(
        key="PHRASE_I_LOVE_YOU",
        name="i love you",
        steps=[
            Step(
                handshape="i-love-you-shape",
                orientation="palm-forward",
                location="neutral-space",
                motion="none"
            )
        ],
        notes="Thumb, index, and pinky extended (I+L+Y)."
    ),
}

# ---------- Helpers ----------
def filter_phrases(q: Optional[str]) -> List[Phrase]:
    if not q:
        return list(PHRASES.values())
    ql = q.lower()
    out: List[Phrase] = []
    for p in PHRASES.values():
        if (
            ql in p.key.lower() or
            ql in p.name.lower() or
            (p.notes and ql in p.notes.lower())
        ):
            out.append(p)
    return out

# ---------- Endpoints ----------
@app.get("/", tags=["meta"])
def root():
    return {"service": "asl-phrases", "version": "1.0.0"}

@app.get("/health", tags=["meta"])
def health():
    return {"ok": True}

@app.get("/phrases", response_model=List[Phrase], tags=["phrases"])
def list_phrases(q: Optional[str] = Query(None, description="Search by name or notes")):
    return sorted(filter_phrases(q), key=lambda p: p.key)

@app.get("/phrases/{phrase_key}", response_model=Phrase, tags=["phrases"])
def get_phrase(phrase_key: str):
    key = phrase_key.upper()
    phrase = PHRASES.get(key)
    if not phrase:
        raise HTTPException(status_code=404, detail=f"Phrase '{phrase_key}' not found")
    return phrase

@app.get("/phrases/{phrase_key}/steps", response_model=List[Step], tags=["phrases"])
def get_phrase_steps(phrase_key: str):
    key = phrase_key.upper()
    phrase = PHRASES.get(key)
    if not phrase:
        raise HTTPException(status_code=404, detail=f"Phrase '{phrase_key}' not found")
    return phrase.steps
