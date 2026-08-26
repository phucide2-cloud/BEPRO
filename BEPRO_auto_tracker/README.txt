# BEPRO ERP automatic slot tracker

This tracker watches the BEPRO Editor Registration Tracking page.

Behavior:
- Checks every 10 seconds.
- Looks for white/clickable slots.
- Prefers Mode 1.0 over Mode 0.5.
- Checks all Mode 1.0/0.5 slots currently rendered on the Tracking page.
- Sends a browser notification and Windows beep.
- Clicks the available slot automatically.
- Clicks Submit automatically.
- Keeps a persistent browser profile, so you normally only need to log in once.

## First-time setup on Windows

1. Install Python 3.10+.
2. Open Command Prompt in this folder.
3. Run:

   pip install -r requirements.txt
   playwright install chromium

4. Start it:

   python bepro_tracker.py

5. A Chromium browser opens.
6. Log in to BEPRO manually if needed.
7. Leave the browser open. The script checks every 10 seconds.

## Important

The script uses the page's visible "Mode 1.0"/"Mode 0.5" text and the slot's computed background/clickability rather than relying on BEPRO's generated CSS class names.

Because BEPRO can change its frontend, test it once before relying on it for an important registration. The script will click Submit automatically when it detects a qualifying slot.

To stop it, press Ctrl+C in the Command Prompt.

The browser profile is saved in:
    bepro_browser_profile/

Do not share that folder: it can contain your logged-in browser session.
