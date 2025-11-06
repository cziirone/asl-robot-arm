from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Literal, Optional

app = FastAPI(title="ASL Phrases API", version="0.1.0")

class Step(BaseModel):
    type: Literal["sign", "fingerspell"]
    token: str                  # e.g., "HELLO" or a letter "A"
    hold_ms: int = 700          # simple timing default

class Phrase(BaseModel):
    key: str                    # slug/id
    text: str                   # English text
    gloss: str                  # ASL gloss (simple)
    sequence: List[Step]        # ordered steps
    notes: Optional[str] = None

PHRASES: Dict[str, Phrase] = {
    "hello": Phrase(
        key="hello",
        text="Hello",
        gloss="HELLO",
        sequence=[Step(type="sign", token="HELLO", hold_ms=700)],
        notes="Flat hand near temple moves outward."
    ),
    "how-are-you": Phrase(
        key="how-are-you",
        text="How are you?",
        gloss="HOW YOU",
        sequence=[
            Step(type="sign", token="HOW", hold_ms=900),
            Step(type="sign", token="YOU", hold_ms=700),
        ],
        notes="Arched hands roll for HOW; point for YOU."
    ),
    "do-you-know-asl": Phrase(
        key="do-you-know-asl",
        text="Do you know ASL?",
        gloss="YOU KNOW ASL (QUESTION)",
        sequence=[
            Step(type="sign", token="YOU", hold_ms=600),
            Step(type="sign", token="KNOW", hold_ms=800),
            Step(type="fingerspell", token="A", hold_ms=300),
            Step(type="fingerspell", token="S", hold_ms=300),
            Step(type="fingerspell", token="L", hold_ms=300),
        ],
        notes="Eyebrows up for yes/no question."
    ),
    "please": Phrase(
        key="please", text="Please", gloss="PLEASE",
        sequence=[Step(type="sign", token="PLEASE", hold_ms=900)]
    ),
    "thank-you": Phrase(
        key="thank-you", text="Thank you", gloss="THANK-YOU",
        sequence=[Step(type="sign", token="THANK-YOU", hold_ms=900)]
    ),
    "nice-to-meet-you": Phrase(
        key="nice-to-meet-you", text="Nice to meet you", gloss="NICE MEET YOU",
        sequence=[
            Step(type="sign", token="NICE", hold_ms=700),
            Step(type="sign", token="MEET", hold_ms=900),
            Step(type="sign", token="YOU", hold_ms=600),
        ],
    ),
    "sorry": Phrase(
        key="sorry", text="Sorry", gloss="SORRY",
        sequence=[Step(type="sign", token="SORRY", hold_ms=900)]
    ),
    "i-love-you": Phrase(
        key="i-love-you", text="I love you", gloss="ILY",
        sequence=[Step(type="sign", token="ILY", hold_ms=1000)]
    ),
}

@app.get("/")
def root():
    return {"service": "phrases", "endpoints": ["/phrases", "/phrases/{key}", "/phrases/{key}/plan"]}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/phrases", response_model=List[Phrase])
def list_phrases():
    return list(PHRASES.values())

@app.get("/phrases/{key}", response_model=Phrase)
def get_phrase(key: str):
    k = key.strip().lower()
    if k not in PHRASES:
        raise HTTPException(status_code=404, detail=f"Phrase '{key}' not found")
    return PHRASES[k]

@app.get("/phrases/{key}/plan")
def compile_phrase_to_plan(key: str):
    """
    Returns a simple 'animation plan' you can later map to robot joint targets.
    """
    phrase = get_phrase(key)
    plan = []
    t_ms = 0
    for step in phrase.sequence:
        plan.append({
            "time_ms_start": t_ms,
            "time_ms_end": t_ms + step.hold_ms,
            "action": step.type,
            "token": step.token
        })
        t_ms += step.hold_ms
    return {"key": phrase.key, "total_ms": t_ms, "plan": plan}
