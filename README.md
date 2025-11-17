<img width="2619" height="680" alt="Screenshot from 2025-11-16 20-44-50" src="https://github.com/user-attachments/assets/a6119408-43e6-4f70-b3b4-de3facc3c26f" />

# Collalbum
_For when someone asks you "What's your music taste?"_

Collalbum generates aesthetic, semantically meaningful album-art collages from your Spotify listening history. Instead of sending someone a playlist link, you can share a single image that captures your music taste at a glance.

## Overview 
Collalbum is an BeaverHacks '25 project that:

- Connects to your Spotify account
- Fetches your listening history (e.g., top tracks/artists)
- Collects the corresponding album art and metadata
- Embeds albums into a semantic space so that “similar” albums live near each other
- Lays them out on a canvas to produce a single collage image you can download and share

## Architecture

This repo is split into two main parts:

- `collage_server/` – Python backend (“collage server”)
  - Exposes HTTP endpoints for:
    - Authenticating with Spotify (or accepting an access token)
    - Fetching and caching listening-history data
    - Generating collages from a set of album IDs
  - Handles:
    - Calls to the Spotify Web API
    - Embedding computation + dimensionality reduction
    - Image layout and rendering
  - Intended to be run with a modern async server (e.g., Uvicorn).

- Frontend (`src/`, `public/`, `dist/`, `index.html`, `vite.config.js`)
  - Vite-based single-page app.
  - Talks to the collage server via REST endpoints.
  - Implements the “log in with Spotify, generate collage, download image” flow.
  - `server.js` can be used to serve the built frontend and proxy to the Python backend in production.


## Extra
Check out our [Devpost](https://devpost.com/software/collalbum) submitted to BeaverHacks 2025. We can't deploy the project as we realized (too late) that Collalbum is against the [Spotify API terms of service](https://developer.spotify.com/terms). Feel free to fork to make your own collage!

<img width="613" height="492" alt="Screenshot from 2025-11-16 20-24-36" src="https://github.com/user-attachments/assets/ac922ed3-bbe1-43a5-bcbd-456e76de2969" />
