# 5 Stack

A Counter-Strike (CS:GO / CS2) take on [82-0](https://82-0.com) and [Ultimate 11](https://ultimate11.com).

Each round the game rolls a random **nationality** and **year** — you draft a player who fits.
Build a 5-stack (IGL, AWP, Pack Rifler, 2× Anchor), then simulate a Major run:
Stage 1 → Stage 2 → Stage 3 → Quarters → Semis → Final.

The whole game is a single self-contained `index.html` with the dataset inlined.
No build step, no dependencies, no tracking.

## Running it in dev mode

You just need a static file server with live reload so that edits in VS Code refresh the browser.

### Option A — VS Code Live Server extension (recommended)

1. Install the extension: **Live Server** by Ritwick Dey (`ritwickdey.LiveServer`).
2. Open this folder in VS Code.
3. Right-click `index.html` → **Open with Live Server** (or click **Go Live** in the status bar).
4. The browser opens at `http://127.0.0.1:5500/index.html` and reloads on every save.

### Option B — `npx live-server` (no extension)

Requires Node.js. From the project root:

```bash
npx live-server --port=5500 --open=index.html
```

Edits to `index.html` trigger a browser refresh.

### Option C — plain Python server (no live reload)

Fine for a quick look; you'll need to hit refresh yourself.

```bash
python3 -m http.server 5500
```

Then open <http://localhost:5500/>.

## Deploying

It's a single static file. Drop `index.html` anywhere that serves static content
(personal site, GitHub Pages, Netlify, S3, etc.). No build step required.

## Swapping in your own player data

Open `index.html` and find the `PLAYERS_CSV` template literal near the top of the
`<script>` block. Replace its contents with your own CSV. The columns are:

```
name,nationality,year,rating,roles
```

- `roles` is pipe-separated, e.g. `AWP|Pack Rifler`. Players may have 1 or 2 roles.
- Valid roles: `IGL`, `AWP`, `Pack Rifler`, `Anchor`.
- If you add a new nationality, add a flag emoji for it in the `FLAG` map below the CSV.

## Tuning the simulation

In `index.html`, the `STAGES` array defines per-stage difficulty thresholds, and
`finishDraftAndSimulate` uses a sigmoid (`k = 15`) to map (team avg rating − stage
difficulty) to a pass probability. Raise `k` for a sharper skill curve, lower it for
more variance. Raise the thresholds to make the Major harder.
