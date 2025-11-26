# CourtIQ Demo Backend

This is a minimal FastAPI backend that powers the **CourtIQ** demo
AI scouting report. It ignores the actual video for now and returns
a realistic-looking JSON report so the frontend Workspace can load
instantly.

## Endpoints

### `GET /`

Health check. Returns status and timestamp.

### `POST /analyze`

Form-data:

- `file`: video file (MP4, MOV, etc.)
- `jersey_color`: string (e.g. "royal-blue")
- `game_title`: string
- `opponent`: string

Returns:

```json
{
  "game_id": "...",
  "report": {
    "team_summary": {...},
    "players": [...],
    "plays": [...],
    "defense": {...},
    "notes_for_coach": [...]
  }
}
