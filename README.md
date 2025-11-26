# CourtIQ — Demo AI Analysis Backend

This is a minimal FastAPI backend that supports your CourtIQ web app.

⚠️ DEMO MODE ONLY  
It **ignores** real video files and instantly returns a **fake scouting report**, so the  
Workspace page loads without freezing.

Perfect for Base44, Render, Replit, Netlify, or any external frontend.

---

## Endpoints

### `POST /analyze`
Form-data:

- `file`: video file  
- `jersey_color`: selected jersey color from UI  
- `game_title`
- `opponent`

Returns JSON:

