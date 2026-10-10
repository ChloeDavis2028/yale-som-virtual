# Yale SOM Virtual: Evans Hall, Floor 2

A first-person walk-through of the 2nd floor of Edward P. Evans Hall (Yale School of Management), built with React, Vite, three.js, and @react-three/fiber.

It includes the blue classroom drums you can walk into, the curvy glass cloister around the courtyard, Ross Library on the west side, the Beinecke Terrace Room and its outdoor terrace on the east side, the small glass meeting rooms, and paintings above the stairwells.

**Walk it in your browser:** https://zlisto.github.io/yale_som_virtual/

## Run it locally

```bash
npm install
npm run dev
```

Open http://localhost:5173 and click **Click to walk in**.

**Keyboard + mouse** (works like a PC shooter):

| Key | Action |
| --- | --- |
| W A S D / arrows | walk |
| Mouse | look |
| Shift | sprint |
| Space | jump |
| C | crouch |
| M | toggle map |
| Esc | pause |

**Phone / tablet:** tap **Tap to walk in**. The left-thumb joystick walks (push it all the way to sprint), dragging anywhere else looks around, and there are on-screen jump and pause buttons. On a laptop, click **Use on-screen joystick** to try the phone controls. WASD still works in that mode.

## Talk to people (backend)

Walk into **classroom 2200**, aim the crosshair at the **AI avatar of Prof. Tauhid Zaman** (dressed as Princess Leia in a pink royal wedding gown), and click. A chat opens on the right and the avatar turns to face you. Every avatar is clearly an AI avatar and never pretends to be the real person.

The backend is FastAPI (`backend/`). Each avatar is a PydanticAI agent whose instructions combine a persona file with course facts from `data/yale_som.db`.

**Run it** (Windows, from this folder):

```bash
py -3.13 -m venv backend/.venv
backend/.venv/Scripts/python -m pip install -r backend/requirements.txt
backend/.venv/Scripts/python backend/seed_course_material.py
backend/.venv/Scripts/python -m uvicorn main:app --app-dir backend --port 8000
```

Then `npm run dev` in another terminal. Vite proxies `/api` to `http://127.0.0.1:8000`. To point the chat somewhere else, set `VITE_API_URL`. The GitHub Pages site has no backend: the game still works and the chat says it can't reach the backend.

**Keys:** put `PORTKEY_API_KEY=...` in `backend/.env` (or this folder, or one or two folders up). The model is `gpt-6-luna` through Portkey; set `OPENAI_MODEL` to change it. `.env` is git-ignored: never commit a real key.

**Routes**

| Route | Returns |
| --- | --- |
| `GET /api/health` | `{ok, model, people}` |
| `GET /api/people` | `[{id, name, title, room, course}]` |
| `POST /api/people/{person_id}/chat` with `{message, session_id}` | `{reply, session_id}` (404 unknown person, 502 model failure) |

Conversations are kept on the server per `(person, session)`: at most 200 sessions and about 40 messages each.

**Avatar tools:** `search_courses` and `course_info` read the course catalog (read-only, PhD courses skipped, never emails). `search_course_material` and `course_material_topics` read course questions and answers from `data/course_material.db` (statistics, regression, the central limit theorem, variance, confidence intervals, hypothesis tests, AI agents). Add rows in `backend/seed_course_material.py` and re-run it to teach the avatars more.

**Add an avatar:** write `backend/prompts/<id>.md`, add a `Person` to `PEOPLE` in `backend/people.py`, add an entry to `PEOPLE_INFO` in `src/talk.js`, and put a `Professor` preset in a classroom (`src/Professor.jsx`, `src/Faculty.jsx`).

Dev helper: `document.body.dataset.talk = "zaman"` in the console opens the chat without pointer lock.

## How it's built

- `src/layout.js`: the floor plan in meters (+x east, -z north). It holds the drums, library, Beinecke, stairs, meeting rooms, wall colliders, and room lookup. Each classroom faces the courtyard, with the whiteboard and podium on the inner side and stadium-seating rows (32 cm risers) stepping up toward the outer wall; its two doors are at the front corners. You climb the center-aisle steps one riser at a time.
- `src/World.jsx`: all the meshes. Walls use instanced boxes and the drums use partial cylinders.
- `src/textures.js`: procedural canvas textures (carpet, navy drum glass, wood slats, mural, signs, stairwell paintings).
- `src/Player.jsx`: walking (pointer lock or touch), jump/crouch, circle-vs-wall collision.
- `src/TouchControls.jsx`: on-screen joystick, drag-to-look, jump and pause buttons.
- `src/Minimap.jsx`: the black-and-pink map in the corner.
- `src/Labubu.jsx`: a customizable Labubu built from primitives: `fur`, `expression` (grin / happy / surprised / sleepy / mischief), `shirt` ('yale', 'stripes', or any color), `pants`, `overalls`, `hat`, `sitting`, `anim`.
- `src/LabubuParty.jsx`: the crew playing in the courtyard plus Labubus in meetings in every glass room.
- `src/slides.js`: lecture slides for eight Fall 2026 MBA courses (MGT 409, 404, 403, 887, 402, 538, 800, 541) on the classroom screens and meeting-room monitors.
- `src/LabubuCrowd.jsx`: 30 seated Labubu students per classroom, drawn with shared instanced meshes.
- `src/Professor.jsx` + `src/Faculty.jsx`: cartoon Hogwarts professors teaching each class (Dumbledore, McGonagall, Trelawney, Slughorn, Snape, Lockhart, Moody, Flitwick), plus Hagrid in the courtyard.
- `src/HandsomeDan.jsx`: Handsome Dan touring a loop of 1000 randomly chosen classrooms (blue dot on the map).

The layout is estimated from the wayfinding plan posted on the floor, so room sizes are approximate. The Stair G painting comes from a photo; the other stairwell paintings are made up.

Made for MGT 409: AI Foundations for Managers, Lecture 13.
