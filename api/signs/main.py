# api/signs/main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional

app = FastAPI(title="ASL Signs API", version="1.0.0")

# ---------- Data Models ----------
class Pose(BaseModel):
    handshape: str          # e.g., "fist", "flat-hand", "c-shape"
    orientation: str        # e.g., "palm-out", "palm-in", "palm-left", "palm-right", "thumb-up"
    location: str           # e.g., "neutral-space", "chin", "mouth", "forehead"
    motion: str = "none"    # e.g., "none", "trace-j", "trace-z", "tap", "twist"

class Sign(BaseModel):
    key: str                # "A", "B", ..., "Z"
    name: str               # same as key for letters
    poses: List[Pose]       # one or more poses (J and Z are multi-step)
    notes: Optional[str] = None

# ---------- Catalog (A–Z) ----------
# These are concise, standard ASL fingerspelling descriptions intended for simulation.
SIGNS: Dict[str, Sign] = {
    # A: Closed fist, thumb alongside index (not over), palm out or sideways
    "A": Sign(key="A", name="A", poses=[
        Pose(handshape="fist", orientation="palm-out", location="neutral-space", motion="none")
    ], notes="Closed fist; thumb rests along side of index (not tucked inside)."),

    # B: Flat hand, fingers together, thumb across palm, palm out
    "B": Sign(key="B", name="B", poses=[
        Pose(handshape="flat-hand", orientation="palm-out", location="neutral-space", motion="none")
    ], notes="Flat hand, fingers together, thumb folded across palm."),

    # C: Curved hand like the letter C
    "C": Sign(key="C", name="C", poses=[
        Pose(handshape="c-shape", orientation="palm-right", location="neutral-space", motion="none")
    ], notes="Curve fingers and thumb to form a 'C'."),

    # D: Index up, other fingers touching thumb to form a circle
    "D": Sign(key="D", name="D", poses=[
        Pose(handshape="index-up-thumb-circle", orientation="palm-out", location="neutral-space", motion="none")
    ], notes="Index up; thumb touches middle/ring/pinky to make a circle."),

    # E: All fingertips touch thumb, palm out/in (neutral)
    "E": Sign(key="E", name="E", poses=[
        Pose(handshape="claw-thumb-tips", orientation="palm-out", location="neutral-space", motion="none")
    ], notes="Fingertips curl toward thumb; keep knuckles visible."),

    # F: Thumb and index make a circle; other fingers extended
    "F": Sign(key="F", name="F", poses=[
        Pose(handshape="ok-circle", orientation="palm-out", location="neutral-space", motion="none")
    ], notes="Thumb-index circle ('OK'); other fingers up and together."),

    # G: Index and thumb parallel, sideways
    "G": Sign(key="G", name="G", poses=[
        Pose(handshape="index-thumb-parallel", orientation="palm-left", location="neutral-space", motion="none")
    ], notes="Index points sideways; thumb parallel to index."),

    # H: Index and middle extended together, sideways
    "H": Sign(key="H", name="H", poses=[
        Pose(handshape="index-middle-extended", orientation="palm-left", location="neutral-space", motion="none")
    ], notes="Index and middle together, palm faces down/left."),

    # I: Pinky up, other fingers in fist, palm out/in
    "I": Sign(key="I", name="I", poses=[
        Pose(handshape="pinky-up", orientation="palm-in", location="neutral-space", motion="none")
    ], notes="Pinky up; thumb across fist."),

    # J: Draw a 'J' in the air with pinky
    "J": Sign(key="J", name="J", poses=[
        Pose(handshape="pinky-up", orientation="palm-in", location="neutral-space", motion="trace-j")
    ], notes="Start from 'I' handshape and trace a 'J' with pinky."),

    # K: Index and middle form a 'V', thumb touches middle at base, palm out
    "K": Sign(key="K", name="K", poses=[
        Pose(handshape="k-shape", orientation="palm-out", location="neutral-space", motion="none")
    ], notes="Index and middle spread; thumb contacts middle finger base."),

    # L: Index and thumb at 90 degrees (like 'L'), palm out
    "L": Sign(key="L", name="L", poses=[
        Pose(handshape="l-shape", orientation="palm-out", location="neutral-space", motion="none")
    ], notes="Index points up; thumb points sideways."),

    # M: Thumb under first three fingers (index/middle/ring)
    "M": Sign(key="M", name="M", poses=[
        Pose(handshape="m-shape", orientation="palm-in", location="neutral-space", motion="none")
    ], notes="Thumb tucked under index/middle/ring; pinky outside."),

    # N: Thumb under first two fingers (index/middle)
    "N": Sign(key="N", name="N", poses=[
        Pose(handshape="n-shape", orientation="palm-in", location="neutral-space", motion="none")
    ], notes="Thumb tucked under index/middle; ring/pinky outside."),

    # O: Touch fingertips to thumb making an 'O'
    "O": Sign(key="O", name="O", poses=[
        Pose(handshape="o-shape", orientation="palm-out", location="neutral-space", motion="none")
    ], notes="All fingertips meet thumb."),

    # P: Like 'K' but palm down (tilted)
    "P": Sign(key="P", name="P", poses=[
        Pose(handshape="k-shape", orientation="palm-down", location="neutral-space", motion="none")
    ], notes="Same handshape as K; rotate so palm faces down (tilt forward)."),

    # Q: Like 'G' but palm down (pointing downward)
    "Q": Sign(key="Q", name="Q", poses=[
        Pose(handshape="index-thumb-parallel", orientation="palm-down", location="neutral-space", motion="none")
    ], notes="Like G but point down."),

    # R: Index and middle crossed, palm out
    "R": Sign(key="R", name="R", poses=[
        Pose(handshape="r-shape", orientation="palm-out", location="neutral-space", motion="none")
    ], notes="Cross index and middle; other fingers curled."),

    # S: Fist with thumb across the front
    "S": Sign(key="S", name="S", poses=[
        Pose(handshape="fist-thumb-front", orientation="palm-out", location="neutral-space", motion="none")
    ], notes="Closed fist; thumb crosses in front of fingers."),

    # T: Fist with thumb between index and middle
    "T": Sign(key="T", name="T", poses=[
        Pose(handshape="t-shape", orientation="palm-out", location="neutral-space", motion="none")
    ], notes="Thumb tucked between index and middle fingers."),

    # U: Index and middle together, pointing up (like two)
    "U": Sign(key="U", name="U", poses=[
        Pose(handshape="u-shape", orientation="palm-out", location="neutral-space", motion="none")
    ], notes="Index/middle together; other fingers curled."),

    # V: Index and middle spread (peace sign), palm out
    "V": Sign(key="V", name="V", poses=[
        Pose(handshape="v-shape", orientation="palm-out", location="neutral-space", motion="none")
    ], notes="Index/middle spread into a V."),

    # W: Index, middle, ring extended/spread (three), palm out
    "W": Sign(key="W", name="W", poses=[
        Pose(handshape="w-shape", orientation="palm-out", location="neutral-space", motion="none")
    ], notes="Index/middle/ring up; pinky curled; thumb out."),

    # X: Hooked index (as if making a small claw), palm out/in
    "X": Sign(key="X", name="X", poses=[
        Pose(handshape="hook-index", orientation="palm-out", location="neutral-space", motion="none")
    ], notes="Index bent like a hook; other fingers curled."),

    # Y: Thumb and pinky extended (shaka), palm in/out
    "Y": Sign(key="Y", name="Y", poses=[
        Pose(handshape="y-shape", orientation="palm-in", location="neutral-space", motion="none")
    ], notes="Thumb and pinky out; other fingers curled."),

    # Z: Draw a 'Z' with index finger
    "Z": Sign(key="Z", name="Z", poses=[
        Pose(handshape="index-up", orientation="palm-out", location="neutral-space", motion="trace-z")
    ], notes="Use index finger to trace a 'Z' in the air.")
}

# ---------- Helpers ----------
def filter_signs(q: Optional[str]) -> List[Sign]:
    if not q:
        return list(SIGNS.values())
    ql = q.lower()
    out: List[Sign] = []
    for s in SIGNS.values():
        if (
            ql in s.key.lower() or
            ql in s.name.lower() or
            (s.notes and ql in s.notes.lower())
        ):
            out.append(s)
    return out

# ---------- Endpoints ----------
@app.get("/", tags=["meta"])
def root():
    return {"service": "asl-signs", "version": "1.0.0"}

@app.get("/health", tags=["meta"])
def health():
    return {"ok": True}

@app.get("/signs", response_model=List[Sign], tags=["signs"])
def list_signs(q: Optional[str] = Query(None, description="Search by letter/name/notes")):
    return sorted(filter_signs(q), key=lambda s: s.key)

@app.get("/signs/{letter}", response_model=Sign, tags=["signs"])
def get_sign(letter: str):
    L = letter.upper()
    sign = SIGNS.get(L)
    if not sign:
        raise HTTPException(status_code=404, detail=f"Sign '{letter}' not found")
    return sign

@app.get("/signs/{letter}/pose", response_model=List[Pose], tags=["signs"])
def get_sign_pose(letter: str):
    L = letter.upper()
    sign = SIGNS.get(L)
    if not sign:
        raise HTTPException(status_code=404, detail=f"Sign '{letter}' not found")
    return sign.poses
