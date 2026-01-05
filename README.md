# HCM Rated Tracker (Home Assistant)

A generic "rated items" tracker you can add multiple times (Books / Films / Music / TV / Games / Other).

## Features
- Add multiple trackers (multiple config entries) — one for Books, one for Films, etc.
- For each tracker, enter:
  - Title
  - Extra field (auto-labeled by preset: Author/Director/Artist/Platform…)
  - Rating (1–10)
- Stores a persistent history (newest first)
- Generates AI recommendations using Home Assistant’s OpenAI integration (`openai_conversation.generate_content`):
  - Infers recent genre(s) from most recent items
  - Same-lane picks based on high-rated items
  - Different-genre picks still likely to match taste

## Install (HACS custom repository)
1. Create a public GitHub repo and upload this folder.
2. In Home Assistant: HACS → Integrations → ⋮ → Custom repositories → add your repo URL (Category: Integration).
3. Install and restart Home Assistant.
4. Settings → Devices & Services → Add Integration → **HCM Rated Tracker**
5. Open the integration **Options** and set your **OpenAI config_entry id**.

## UI
Add an Entities card (or Mushroom cards) with the entities under the device created for the tracker:
- Title, Extra, Rating
- Save button
- Recommendations + Log (optional, maybe on a separate view)
