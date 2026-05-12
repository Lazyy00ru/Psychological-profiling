import json
import secrets
import httpx
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles


#  CONFIG
Username   = "admin"
OMDB_API_KEY = "f4445d74"


#  SETUP
DATA_DIR   = Path("data")
IMAGES_DIR = Path("images")
DATA_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)

app      = FastAPI()
security = HTTPBasic()

if Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")



#  AUTH
def require_auth(credentials: HTTPBasicCredentials = Depends(security)):
    ok_user = secrets.compare_digest(credentials.username, Username)
    ok_pass = secrets.compare_digest(credentials.password, Username)
    if not (ok_user and ok_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username



#  3RD PARTY HELPERS
async def fetch_movie(title: str) -> dict:
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        return r.json()


async def fetch_animal_image(animal: str) -> str:
    endpoints = {
        "dog":  "https://dog.ceo/api/breeds/image/random",
        "cat":  "https://api.thecatapi.com/v1/images/search",
        "duck": "https://random-d.uk/api/v2/random",
    }
    if animal not in endpoints:
        return ""

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        meta = await client.get(endpoints[animal])
        data = meta.json()

        if animal == "dog":
            img_url = data["message"]
        elif animal == "cat":
            img_url = data[0]["url"]
        else:
            img_url = data["url"]

        img_resp = await client.get(img_url)
        ext = img_url.split(".")[-1].split("?")[0][:4].lower()
        if ext not in ("jpg", "jpeg", "png", "gif", "webp"):
            ext = "jpg"
        filename = f"{animal}.{ext}"
        (IMAGES_DIR / filename).write_bytes(img_resp.content)
        return filename



#  BIG FIVE ANALYSIS ENGINE
def get_trait_scores(q: dict) -> dict:
    def s(key):
        try:
            return int(q.get(key, 3))
        except (ValueError, TypeError):
            return 3

    def r(key):
        return 6 - s(key)

    extraversion      = s("question1")  + s("question8")  + r("question14") + s("question20") + r("question6")
    agreeableness     = s("question4")  + r("question9")  + r("question17") + r("question18") + s("question7")
    conscientiousness = s("question2")  + r("question5")  + s("question10") + r("question12") + r("question15")
    neuroticism       = s("question13") + s("question16") + s("question19") + r("question6")  + r("question11")
    openness          = s("question3")  + s("question7")  + s("question11") + s("question16") + s("question19")

    def clamp(v):
        return max(5, min(25, v))

    return {
        "extraversion":      clamp(extraversion),
        "agreeableness":     clamp(agreeableness),
        "conscientiousness": clamp(conscientiousness),
        "neuroticism":       clamp(neuroticism),
        "openness":          clamp(openness),
    }


JOB_MOVIES = {
    "ceo":       ["The Social Network", "Margin Call", "Wall Street"],
    "astronaut": ["Interstellar", "The Martian", "Gravity"],
    "doctor":    ["Patch Adams", "Awakenings", "The Doctor"],
    "model":     ["The Devil Wears Prada", "Zoolander", "Gia"],
    "rockstar":  ["Bohemian Rhapsody", "Almost Famous", "School of Rock"],
    "garbage":   ["Billy Madison", "Office Space", "The Full Monty"],
}

JOB_VERDICT = {
    "ceo":       "You dream big and thrive on power — the boardroom is your natural habitat. Just don't forget the little people on the way up.",
    "astronaut": "You are drawn to the unknown and unafraid of vast emptiness — a born explorer with your head literally in the stars.",
    "doctor":    "You carry deep empathy and a drive to heal. Medicine is your calling, though perhaps avoid self-diagnosing on WebMD.",
    "model":     "You have an eye for aesthetics and carry yourself with presence. The runway was made for you.",
    "rockstar":  "You live for the stage and the roar of the crowd. Your energy is infectious — just protect your ears.",
    "garbage":   "Underrated and essential. You are the backbone of civilisation — someone has to keep the world clean, and you own it.",
}


def build_insights(traits: dict) -> list:
    insights = []
    e = traits["extraversion"]
    if e >= 18:
        insights.append("You are highly extraverted — energised by social interaction, talkative, and assertive. You light up any room you walk into.")
    elif e <= 10:
        insights.append("You lean introverted — thoughtful, preferring depth over breadth in your social life. You recharge best with quiet time.")
    else:
        insights.append("You are an ambivert — comfortable in social situations but equally happy with your own company. A rare and balanced trait.")

    a = traits["agreeableness"]
    if a >= 18:
        insights.append("Your high agreeableness shows warmth and cooperativeness. People trust you easily — you are a genuine team player.")
    elif a <= 10:
        insights.append("You are competitive and direct, sometimes coming across as blunt. You value honesty over diplomacy.")
    else:
        insights.append("You balance assertiveness with empathy — you can stand your ground without burning bridges.")

    c = traits["conscientiousness"]
    if c >= 18:
        insights.append("Highly conscientious — you are organised, dependable, and goal-oriented. Your to-do lists have to-do lists.")
    elif c <= 10:
        insights.append("You are spontaneous and flexible, but can struggle with deadlines. Structure is not your natural friend.")
    else:
        insights.append("Moderately conscientious — you can be organised when it matters, but you know how to go with the flow.")

    n = traits["neuroticism"]
    if n >= 18:
        insights.append("You experience emotions intensely and may worry more than average. Your sensitivity, however, makes you deeply perceptive.")
    elif n <= 10:
        insights.append("You are emotionally stable and cool under pressure — the kind of person others lean on in a crisis.")
    else:
        insights.append("Your emotional landscape is balanced — you feel things fully without being overwhelmed by them.")

    o = traits["openness"]
    if o >= 18:
        insights.append("Highly open to experience — creative, curious, and always hungry for new ideas. You probably have seventeen half-finished projects.")
    elif o <= 10:
        insights.append("You prefer the tried and tested — practical, conventional, and grounded in what you know works.")
    else:
        insights.append("Moderately open — you enjoy new experiences but also appreciate routine and familiarity.")

    return insights


def get_personality_type(traits: dict) -> str:
    e = traits["extraversion"]
    o = traits["openness"]
    c = traits["conscientiousness"]
    if e >= 18 and o >= 18:
        return "The Visionary Explorer"
    elif e >= 18 and c >= 18:
        return "The Dynamic Leader"
    elif e <= 10 and o >= 18:
        return "The Quiet Innovator"
    elif e <= 10 and c >= 18:
        return "The Meticulous Thinker"
    elif o >= 18 and c <= 10:
        return "The Creative Dreamer"
    elif c >= 18 and o <= 10:
        return "The Reliable Traditionalist"
    else:
        return "The Balanced Realist"


def compute_overall_score(traits: dict) -> int:
    total = sum(traits.values())
    return round((total / 125) * 100)


#  ROUTES
@app.get("/", response_class=HTMLResponse)
async def root(_: str = Depends(require_auth)):
    return Path("Frontend/index.html").read_text(encoding="utf-8")


@app.get("/form", response_class=HTMLResponse)
async def get_form(_: str = Depends(require_auth)):
    return Path("Frontend/psycho.html").read_text(encoding="utf-8")


@app.post("/submit")
async def submit_form(request: Request, _: str = Depends(require_auth)):
    raw = await request.form()
    data = {}
    pets = []
    for key, value in raw.multi_items():
        if key == "pets":
            pets.append(value)
        else:
            data[key] = value
    data["pets"] = pets
    (DATA_DIR / "form_data.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    name = data.get("name", "stranger")
    return JSONResponse({"status": "ok", "message": f"Thanks {name}! Your data has been saved."})


@app.post("/analyze")
async def analyze(_: str = Depends(require_auth)):
    fp = DATA_DIR / "form_data.json"
    if not fp.exists():
        raise HTTPException(status_code=400, detail="No form data found. Please submit the form first.")

    form = json.loads(fp.read_text(encoding="utf-8"))
    traits         = get_trait_scores(form)
    job            = form.get("job", "ceo")
    career_verdict = JOB_VERDICT.get(job, JOB_VERDICT["ceo"])
    movie_titles   = JOB_MOVIES.get(job, JOB_MOVIES["ceo"])

    movie_details = []
    for title in movie_titles:
        try:
            details = await fetch_movie(title)
            if details.get("Response") == "True":
                movie_details.append({
                    "title":  details.get("Title"),
                    "year":   details.get("Year"),
                    "plot":   details.get("Plot"),
                    "poster": details.get("Poster"),
                    "rating": details.get("imdbRating"),
                })
            else:
                movie_details.append({"title": title, "plot": "Details unavailable."})
        except Exception:
            movie_details.append({"title": title, "plot": "Could not fetch data."})

    pet_images = {}
    for pet in form.get("pets", []):
        pet_lower = pet.lower()
        if pet_lower in ("dog", "cat", "duck"):
            try:
                filename = await fetch_animal_image(pet_lower)
                if filename:
                    pet_images[pet_lower] = filename
            except Exception:
                pass

    profile = {
        **traits,
        "overall_score":    compute_overall_score(traits),
        "personality_type": get_personality_type(traits),
        "career_verdict":   career_verdict,
        "insights":         build_insights(traits),
        "movies_detail":    movie_details,
        "pet_images":       pet_images,
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save timestamped profile
    (DATA_DIR / f"profile_{timestamp}.json").write_text(
        json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    # Save latest profile
    (DATA_DIR / "profile.json").write_text(
        json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    # Save a timestamped copy of the input data linked to this profile
    (DATA_DIR / f"input_{timestamp}.json").write_text(
        json.dumps(form, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return JSONResponse({"status": "ok", "message": "Analysis complete! Your profile has been saved."})


@app.get("/view/input")
async def view_input(_: str = Depends(require_auth)):
    fp = DATA_DIR / "form_data.json"
    if not fp.exists():
        raise HTTPException(status_code=404, detail="No input data found. Submit the form first.")
    return JSONResponse(json.loads(fp.read_text(encoding="utf-8")))


@app.get("/view/inputs")
async def list_inputs(_: str = Depends(require_auth)):
    """Return a list of all saved timestamped input data files, newest first."""
    files = sorted(DATA_DIR.glob("input_*.json"), reverse=True)
    inputs = []
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        inputs.append({
            "filename":  f.name,
            "timestamp": f.name.replace("input_", "").replace(".json", ""),
            "name":      data.get("name", "—"),
            "job":       data.get("job", "—"),
        })
    return JSONResponse(inputs)


@app.get("/view/input/{filename}")
async def view_input_by_name(filename: str, _: str = Depends(require_auth)):
    safe_name = Path(filename).name
    fp = DATA_DIR / safe_name
    if not fp.exists():
        raise HTTPException(status_code=404, detail="Input data not found.")
    return JSONResponse(json.loads(fp.read_text(encoding="utf-8")))


@app.get("/view/profiles")
async def list_profiles(_: str = Depends(require_auth)):
    files = sorted(DATA_DIR.glob("profile_*.json"), reverse=True)
    profiles = []
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        profiles.append({
            "filename":         f.name,
            "timestamp":        f.name.replace("profile_", "").replace(".json", ""),
            "personality_type": data.get("personality_type", "—"),
            "overall_score":    data.get("overall_score", "—"),
        })
    return JSONResponse(profiles)


@app.get("/view/profile/{filename}")
async def view_profile_by_name(filename: str, _: str = Depends(require_auth)):
    safe_name = Path(filename).name
    fp = DATA_DIR / safe_name
    if not fp.exists():
        raise HTTPException(status_code=404, detail="Profile not found.")
    return JSONResponse(json.loads(fp.read_text(encoding="utf-8")))


@app.get("/view/profile")
async def view_profile(_: str = Depends(require_auth)):
    fp = DATA_DIR / "profile.json"
    if not fp.exists():
        raise HTTPException(status_code=404, detail="No profile found. Run the analysis first.")
    return JSONResponse(json.loads(fp.read_text(encoding="utf-8")))


@app.delete("/reset")
async def reset_data(_: str = Depends(require_auth)):
    deleted = []
    for f in DATA_DIR.glob("*.json"):
        f.unlink()
        deleted.append(f.name)
    return JSONResponse({"status": "ok", "message": f"Cleared {len(deleted)} file(s) successfully."})


@app.get("/images/{filename}")
async def serve_image(filename: str, _: str = Depends(require_auth)):
    safe_name = Path(filename).name
    path = IMAGES_DIR / safe_name
    if not path.exists():
        raise HTTPException(status_code=404, detail="Image not found.")
    return FileResponse(path)