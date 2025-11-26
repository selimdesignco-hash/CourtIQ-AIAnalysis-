from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uuid
import random

app = FastAPI(title="CourtIQ Demo Analysis API")

# Allow your Base44 / frontend domain to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, restrict to your real domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """
    Simple health check endpoint so Render / Replit / you can see it's running.
    """
    return {
        "status": "ok",
        "message": "CourtIQ demo backend is running.",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    jersey_color: str = Form("royal-blue"),
    game_title: str = Form("Untitled Game"),
    opponent: str = Form("Unknown Opponent"),
):
    """
    DEMO ONLY:
    - Ignores the actual video.
    - Immediately returns a fake but realistic scouting report.
    - This is meant to power your Workspace UI until real CV is ready.
    """

    # Consume the upload so there's no error, but don't actually process it.
    _ = await file.read()

    # Use a UUID as a fake game_id
    game_id = str(uuid.uuid4())

    # Seed random with game_id so results are stable per game
    random.seed(game_id)

    possessions = random.randint(60, 80)
    pace_comment = random.choice(
        [
            "Medium pace, similar to a typical high school game.",
            "Fast-paced team that looks to run in transition.",
            "Slow, grind-it-out pace focused on half-court sets.",
        ]
    )

    offensive_styles = [
        "Heavy high pick-and-roll with primary guard as ball handler",
        "Spot-up shooters spaced in the corners",
        "Occasional Horns set out of timeouts",
    ]

    defensive_styles = [
        "Mostly man-to-man",
        "2–3 zone in stretches to protect the paint",
        "Soft full-court pressure after made baskets",
    ]

    # Fake players
    def fake_player(number: int, role: str):
        est_pts = random.randint(8, 22)
        fga = random.randint(6, 15)
        threes = random.randint(0, fga // 2)
        usage = round(random.uniform(0.18, 0.32), 2)
        tendencies_map = {
            "guard": [
                "Pull-up threes from the left wing",
                "Strong right-hand drives",
                "Likes high pick-and-roll as ball handler",
            ],
            "wing": [
                "Catches and shoots from corners",
                "Attacks closeouts with one-dribble pull-ups",
                "Cuts backdoor when overplayed",
            ],
            "big": [
                "Rolls hard out of ball screens",
                "Crashes offensive glass every time",
                "Prefers finishing over left shoulder",
            ],
        }
        return {
            "number": number,
            "name": f"{role.title()} #{number}",
            "estimated_points": est_pts,
            "fg_attempts": fga,
            "threes_attempted": threes,
            "usage_rate": usage,
            "tendencies": tendencies_map.get(role, []),
        }

    players = [
        fake_player(3, "guard"),
        fake_player(12, "wing"),
        fake_player(15, "big"),
    ]

    plays = [
        {
            "name": "High PnR",
            "frequency_estimate": "40% of half-court possessions",
            "description": "Primary guard uses a high screen from the big at the top. Big rolls hard; shooters are spaced in both corners.",
        },
        {
            "name": "Horns set",
            "frequency_estimate": "15% of half-court possessions",
            "description": "Both bigs start at the elbows. Guard chooses a side ball screen, weak-side shooter lifts to the slot.",
        },
        {
            "name": "Baseline out-of-bounds (BLOB – box)",
            "frequency_estimate": "Used on most baseline inbounds",
            "description": "Box alignment into screen-the-screener action for a corner three.",
        },
    ]

    defense = {
        "base_defense": "Man-to-man",
        "zone_usage": "2–3 zone roughly 20% of the time, usually after timeouts or late in games.",
        "pressure": "Soft full-court man pressure after makes; mostly to slow you down, not to trap.",
        "key_defenders": [
            "Primary guard heats up the ball in the backcourt.",
            "Big protects the rim but can be late on closeouts.",
        ],
    }

    notes_for_coach = [
        "Make their primary guard work on defense — attack him in switches to tire him out.",
        f"Force their creators toward their weaker hand and go under on ball screens unless they are hot from three.",
        "Use 5-out or pick-and-pop actions to pull their big away from the rim.",
    ]

    report = {
        "video_path": f"demo://{file.filename}",
        "jersey_color_analyzed": jersey_color,
        "game_title": game_title,
        "opponent": opponent,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "team_summary": {
            "estimated_possessions": possessions,
            "pace_comment": pace_comment,
            "offensive_style": offensive_styles,
            "defensive_style": defensive_styles,
        },
        "players": players,
        "plays": plays,
        "defense": defense,
        "notes_for_coach": notes_for_coach,
    }

    return JSONResponse({"game_id": game_id, "report": report})
