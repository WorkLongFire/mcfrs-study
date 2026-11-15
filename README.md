# Shift Ready

A TikTok-style study app for EMT and firefighter students. Swipe through short clips, get quizzed on what you watched, and turn your own Quizlet sets, notes and photos into clips and spaced-review quizzes.

It is a Progressive Web App: one static site that installs on iPhone and Mac, runs full screen, and works offline.

## Features

- **Home**: vertical clip feed with an EMT / Fire switch. Each clip plays as one continuous video: a single timeline with elapsed and total time, crossfading scenes, drag or arrow keys to seek, tap to pause, and read-aloud narration (🔊 Sound). A clip counts as watched, and unlocks its quiz, only when every scene has played through.
- **Quiz**: builder that defaults to what you've been studying, or up to 20 typed topics; 5 to 120 questions mixing multiple choice, matching and typed answers. Progress separates watched from proven (answered correctly).
- **Focused feed**: Home's Mixed/Focused button narrows For You to typed topics or chosen uploads. Tune on each clip: more, less, already know, review later.
- **Search**: by title, hashtag, term or text.
- **Create**: turn a flashcard deck into a teaching clip (narration, captions, visual suggestions), edit it, add a recorded or uploaded video, and post it. Videos are stored on the device. Also includes a free-form scene editor and flip-card study for every deck.
- **Learn (Upload & Learn)**: import a Quizlet export or pasted notes, or photos and screenshots read by the on-device text reader. Check the text, review flagged cards (unreadable, conflicting, or different from the built-in deck), pick EMT, Fire or your own topic, and get clips and quizzes built only from your material. Progress is tracked per card, missed cards come back sooner (10 min, 1, 3, 7, 21 days), and the Fix-it clip covers your weak spots. Every clip and question links back to its source.
- **Backup & share**: export everything to a file and import it on another device, or send one set to a friend.
- **Built-in content**: 24 handcrafted clips, plus 753 NREMT flashcards in 25 decks, which also feed 192 clips.
- **Squad**: on claude.ai, live chat and leaderboard. In this installed version: a crew leaderboard built from score links friends send each other, group-text messaging, and private notes on clips. Sharing falls back to text, email or copy when the phone has no share menu.

## Repository layout

| Path | What it is |
|---|---|
| `index.html` | The whole installable app (HTML, CSS, JS and study content). **Generated; do not edit by hand.** |
| `sw.js`, `manifest.webmanifest`, `version.json`, `icons/`, `.nojekyll` | Generated app shell: offline cache, install metadata, update check, icons. |
| `vendor/tesseract/` | On-device photo text reader (Tesseract.js 5.1.1, Apache-2.0). Downloaded by the app on the first photo, about 7 MB. |
| `source/shift-ready.artifact.html` | **The source of truth.** The same app as it runs on claude.ai. Edit this file. |
| `tools/build_pwa.py` | Builds the root app files from the source file. |
| `content/` | Study content as data: `emt.json` and `fire.json` (handcrafted clips), `nremt/*.json` (flashcard decks), `nremt-flashcards.tsv` (Quizlet/Anki import), `nremt-study-list.md`. |
| `tests/smoke.js`, `tests/fixtures/` | End-to-end browser test: offline install, Upload & Learn (text and photo), saved videos, backup export and restore, re-import without duplicates, bad-file rejection, Send to a friend, the continuous player and the update prompt. |

## Run it locally

```bash
python3 -m http.server 8765
```

Then open http://localhost:8765/. Service workers need `localhost` or HTTPS; opening `index.html` directly from disk works, but without offline caching.

## Deploy (GitHub Pages)

1. In the repository on GitHub, open **Settings → Pages**.
2. Under **Build and deployment**, choose **Deploy from a branch**, then branch **main** and folder **/ (root)**, then **Save**.
3. After about a minute the app is live at `https://worklongfire.github.io/mcfrs-study/`.

Every push to `main` redeploys automatically.

## Install

- **iPhone**: open the Pages link in **Safari**, tap **Share**, then **Add to Home Screen**.
- **Mac**: open the link in **Safari** and choose **File → Add to Dock** (macOS Sonoma or later). In **Chrome**, click the install icon in the address bar.

## Update the app

1. Edit `source/shift-ready.artifact.html`. Content changes can start from `content/`, but the app reads only what is embedded in the source file.
2. Rebuild the root files. This also writes a new build id to `version.json`, `index.html` and the cache name in `sw.js`:
   ```bash
   python3 tools/build_pwa.py
   ```
3. Test:
   ```bash
   python3 -m http.server 8765 &
   ```
   ```bash
   node tests/smoke.js
   ```
4. Commit and push to `main`. GitHub Pages redeploys, and installed apps load the new version the next time they open online. An app left open in the background shows **Update ready · tap to reload**.

With Claude: open a Claude Code session with this repository attached and describe the change. Claude follows the steps above.

## Data and privacy

- Everything you upload, create or score in the installed app stays on that device, in browser storage and IndexedDB. Nothing is sent to a server. The on-device photo reader runs locally.
- Data is not synced between devices automatically. Use **Learn → Export backup** and **Import file**. Videos stay on the device where they were made.
- The repository contains no accounts, keys or personal data.

## Content accuracy

The study content was researched and fact-checked against current NREMT, 2025 AHA and IFSTA/NFPA material. Some primary sources could not be reached during checking. Cards marked "per local protocol" vary by region. Always defer to your textbook, instructor, local protocols and medical direction.

## Third-party

- [Tesseract.js](https://github.com/naptha/tesseract.js) 5.1.1, tesseract.js-core 5.1.1 and the English `best_int` language data, Apache License 2.0 (see `vendor/tesseract/LICENSE`).
- Google Fonts (Barlow Condensed, Inter, JetBrains Mono), loaded online and cached for offline use.
