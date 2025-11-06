from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Literal

app = FastAPI(title="ASL Translate API", version="0.1.0")

# Reuse a tiny phrase/sign inventory (ideally reference your other services or a shared package)
KNOWN_SIGNS = {"HELLO", "YOU", "HOW", "KNOW", "PLEASE", "THANK-YOU", "SORRY", "NICE", "MEET", "ILY"}
KNOWN_PHRASES = {
    "hello": ["HELLO"],
    "how are you": ["HOW", "YOU"],
    "do you know asl": ["YOU", "KNOW", "A", "S", "L"],  # last three are fingerspelled
    "nice to meet you": ["NICE", "MEET", "YOU"],
    "please": ["PLEASE"],
    "thank you": ["THANK-YOU"],
    "sorry": ["SORRY"],
    "i love you": ["ILY"],
}

class TranslateRequest(BaseModel):
    text: str
    mode: Literal["best_match", "fingerspell_all"] = "best_match"

class PlanStep(BaseModel):
    type: Literal["sign", "fingerspell"]
    token: str
    hold_ms: int = 700

class TranslateResponse(BaseModel):
    tokens: List[PlanStep]
    total_ms: int

def to_steps_best_match(text: str) -> List[PlanStep]:
    s = text.strip().lower()
    if s in KNOWN_PHRASES:
        steps: List[PlanStep] = []
        for tok in KNOWN_PHRASES[s]:
            if len(tok) == 1 and tok.isalpha():
                steps.append(PlanStep(type="fingerspell", token=tok.upper(), hold_ms=300))
            else:
                steps.append(PlanStep(type="sign", token=tok, hold_ms=800))
        return steps

    # Otherwise: token-by-token – attempt known sign, else fingerspell the word
    steps: List[PlanStep] = []
    for word in s.split():
        up = word.upper()
        if up in KNOWN_SIGNS:
            steps.append(PlanStep(type="sign", token=up, hold_ms=800))
        else:
            for ch in up:
                if ch.isalpha():
                    steps.append(PlanStep(type="fingerspell", token=ch, hold_ms=300))
    return steps

def to_steps_fingerspell_all(text: str) -> List[PlanStep]:
    steps: List[PlanStep] = []
    for ch in text.upper():
        if ch.isalpha():
            steps.append(PlanStep(type="fingerspell", token=ch, hold_ms=250))
    return steps

@app.get("/")
def root():
    return {"service": "translate", "endpoints": ["/translate"]}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/translate", response_model=TranslateResponse)
def translate(req: TranslateRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text must not be empty.")

    if req.mode == "fingerspell_all":
        steps = to_steps_fingerspell_all(req.text)
    else:
        steps = to_steps_best_match(req.text)

    total = sum(s.hold_ms for s in steps)
    return TranslateResponse(tokens=steps, total_ms=total)
