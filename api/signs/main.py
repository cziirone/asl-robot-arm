from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional

app = FastAPI(title="ASL Signs API", version="0.1.0")

# --- minimal sign dictionary (expand anytime) ---
# Each entry can later map to Webots/CoppeliaSim joint targets.
class Pose(BaseModel):
    handshape: str          # quick label (e.g., "A", "B", "C", "Flat-hand")
    dominant: bool = True   # dominant hand?
    orientation: str        # e.g., "palm out", "palm in"
    location: str           # e.g., "chin", "neutral space"
    motion: Optional[str] = None  # short motion description

class Sign(BaseModel):
    key: str                # "A"..."Z"
    name: str               # "Letter A"
    description: str
    poses: List[Pose]       # 1+ poses; later map to joint angles
    category: str = "alphabet"

SIGNS: Dict[str, Sign] = {
    "A": Sign(
        key="A",
        name="Letter A",
        description="Closed fist with thumb along the side; palm forward or to the side.",
        poses=[Pose(handshape="A", orientation="palm out", location="neutral space", motion=None)]
    ),
    "B": Sign(
        key="B",
        name="Letter B",
        description="Flat hand, fingers together and extended, thumb tucked across palm.",
        poses=[Pose(handshape="B", orientation="palm out", location="neutral space", motion=None)]
    ),
    "C": Sign(
        key="C",
        name="Letter C",
        description="Curve hand into a 'C' shape as if holding a cup.",
        poses=[Pose(handshape="C", orientation="palm out", location="neutral space", motion=None)]
    ),
    "D": Sign(
        key="D",
        name="Letter D",
        description="Index finger up, thumb touches middle finger; other fingers curled.",
        poses=[Pose(handshape="D", orientation="palm out", location="neutral space", motion=None)]
    ),
    "E": Sign(
        key="E",
        name="Letter E",
        description="Fingertips curl down toward palm; thumb across fingertips.",
        poses=[Pose(handshape="E", orientation="palm out", location="neutral space", motion=None)]
    ),
    # ... add remaining letters F–Z similarly ...
    "I": Sign(
        key="I",
        name="Letter I",
        description="Little finger extended, other fingers closed; thumb over fingers.",
        poses=[Pose(handshape="I", orientation="palm out", location="neutral space")]
    ),
    "L": Sign(
        key="L",
        name="Letter L",
        description="Index finger and thumb form an 'L', other fingers closed.",
        poses=[Pose(handshape="L", orientation="palm out", location="neutral space")]
    ),
    "Y": Sign(
        key="Y",
        name="Letter Y",
        description="Thumb and little finger extended (shaka), other fingers closed.",
        poses=[Pose(handshape="Y", orientation="palm out", location="neutral space")]
    ),
}

@app.get("/")
def root():
    return {"service": "signs", "endpoints": ["/signs", "/signs/{letter}", "/signs/{letter}/pose"]}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/signs", response_model=List[Sign])
def list_signs(q: Optional[str] = Query(None, description="Filter by letter/name/category")):
    items = list(SIGNS.values())
    if q:
        ql = q.lower()
        items = [s for s in items if ql in s.key.lower() or ql in s.name.lower() or ql in s.category.lower()]
    return items

@app.get("/signs/{letter}", response_model=Sign)
def get_sign(letter: str):
    key = letter.strip().upper()
    if key not in SIGNS:
        raise HTTPException(status_code=404, detail=f"Sign '{letter}' not found")
    return SIGNS[key]

@app.get("/signs/{letter}/pose", response_model=List[Pose])
def get_sign_pose(letter: str):
    key = letter.strip().upper()
    if key not in SIGNS:
        raise HTTPException(status_code=404, detail=f"Sign '{letter}' not found")
    return SIGNS[key].poses
