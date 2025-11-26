from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import uuid
import tempfile
import cv2
import numpy as np
from ultralytics import YOLO

app = FastAPI()

# Load YOLO model once at startup
yolo_model = YOLO("yolov8n.pt")  # small + fast, good for MVP

# Simple mapping of user color words -> approximate BGR values
COLOR_MAP = {
    "royal-blue": (180, 80, 30),
    "navy": (100, 40, 20),
    "red": (40, 40, 200),
    "green": (40, 150, 40),
    "black": (20, 20, 20),
    "white": (230, 230, 230),
    # ...extend as needed
}

def color_distance(c1, c2):
    c1 = np.array(c1, dtype=np.float32)
    c2 = np.array(c2, dtype=np.float32)
    return float(np.linalg.norm(c1 - c2))

def estimate_jersey_color(frame, bbox):
    """Take a player bbox and estimate average jersey color inside it."""
    x1, y1, x2, y2 = map(int, bbox)
    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        return None

    # Focus on middle vertical band (avoid shorts/shoes)
    h, w, _ = crop.shape
    mid = crop[int(h*0.2):int(h*0.7), int(w*0.2):int(w*0.8)]
    avg_bgr = mid.reshape(-1, 3).mean(axis=0)
    return tuple(avg_bgr.tolist())

def is_target_team(avg_bgr, target_color_name, threshold=80.0):
    if avg_bgr is None:
        return False
    target_bgr = COLOR_MAP.get(target_color_name)
    if target_bgr is None:
        return True  # if unknown, accept everyone (fallback)
    dist = color_distance(avg_bgr, target_bgr)
    return dist < threshold

def sample_frames(video_path, fps_target=5):
    """Yield frames at approx fps_target."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    step = max(int(round(fps / fps_target)), 1)
    frame_idx = 0
    out_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % step == 0:
            yield out_idx, frame
            out_idx += 1
        frame_idx += 1

    cap.release()

def analyze_video(video_path: str, jersey_color: str):
    """
    Core CV logic: run YOLO, filter players by jersey color, track simple stats.
    This is MVP logic – can be improved over time.
    """
    players_stats = {}  # key: track_id, value: dict of stats
    total_frames = 0

    for sample_idx, frame in sample_frames(video_path, fps_target=3):
        total_frames += 1

        # Run YOLO
        results = yolo_model(frame, verbose=False)[0]

        # YOLOv8: boxes.xyxy, boxes.cls, boxes.id (if using tracking)
        # For simple MVP, we don't track – we just approximate per-frame stats.
        for box in results.boxes:
            cls_id = int(box.cls)
            # 0 is 'person' for COCO
            if cls_id != 0:
                continue

            bbox = box.xyxy[0].tolist()
            avg_bgr = estimate_jersey_color(frame, bbox)
            if not is_target_team(avg_bgr, jersey_color):
                continue

            # For MVP, fake a track_id using bbox position
            x1, y1, x2, y2 = bbox
            center_x = (x1 + x2) / 2
            track_id = int(center_x // 50)  # VERY rough grouping

            stats = players_stats.setdefault(track_id, {
                "frames_seen": 0,
                "estimated_points": 0,
                "fg_attempts": 0,
                "threes_attempted": 0,
                "drives_left": 0,
                "drives_right": 0,
            })
            stats["frames_seen"] += 1

            # TODO: refine – here we could look at motion vectors over time
            # to approximate left/right drives, shot attempts, etc.

    # Turn raw stats into nicer report
    players_report = []
    for track_id, stats in players_stats.items():
        usage = stats["frames_seen"] / max(total_frames, 1)
        players_report.append({
            "number": track_id,  # placeholder until jersey OCR
            "name": f"Player #{track_id}",
            "estimated_points": int(stats["frames_seen"] * 0.15),
            "fg_attempts": int(stats["frames_seen"] * 0.1),
            "threes_attempted": int(stats["frames_seen"] * 0.03),
            "usage_rate": round(float(usage), 2),
            "tendencies": [
                "MVP v0 – tendencies are heuristic.",
                "Upgrade logic to use motion + ball tracking."
            ],
        })

    report = {
        "team_summary": {
            "estimated_possessions": int(total_frames * 0.5),
            "pace_comment": "Prototype CV estimate – refine with real event logic.",
            "offensive_style": [
                "Prototype: patterns not fully classified yet."
            ],
            "defensive_style": [
                "Prototype: base defense classification TBD."
            ]
        },
        "players": players_report,
        "plays": [],     # TODO: detect plays from patterns
        "defense": {},   # TODO: classify zones vs man
        "notes_for_coach": [
            "This is CourtIQ CV v0.",
            "Real tendencies & play types improve as models and heuristics are upgraded."
        ]
    }
    return report

@app.post("/analyze")
async def analyze_endpoint(
    file: UploadFile = File(...),
    jersey_color: str = Form("royal-blue")
):
    # Save temp video
    suffix = "." + (file.filename.split(".")[-1] if "." in file.filename else "mp4")
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        video_path = tmp.name
        content = await file.read()
        tmp.write(content)

    game_id = str(uuid.uuid4())
    report = analyze_video(video_path, jersey_color)

    return JSONResponse({
        "game_id": game_id,
        "report": report
    })
