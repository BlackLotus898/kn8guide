#!/usr/bin/env python3
"""
sync_instagram_announcements.py

Checks the official Kaiju No. 8 The Game Instagram account
(@kaijuno8_thegame_en) for new posts and appends them to
data/announcements.json as "game" type entries.

== WHY THIS IS EVEN MORE FRAGILE THAN THE X SCRIPT ==
Instagram has no free, official, no-login way to read a public account's
posts. This script uses Instagram's internal/unofficial web API endpoint
(the same one their own website's JavaScript calls when you visit a
profile page while logged out). This is NOT a public, documented,
or supported API — Instagram can and does change it without notice,
rate-limit it aggressively, or block requests that don't look like a
real browser. Because GitHub Actions runs from shared cloud IP ranges
that Instagram is known to rate-limit or block more readily than normal
residential traffic, there is a real chance this script simply stops
working entirely, or works inconsistently, through no fault of the code.

If this script fails, it exits cleanly without changing announcements.json
— same safety behavior as the X script. Treat any Instagram-sourced
content here as a bonus, not a guarantee.

== HOW IT WORKS ==
1. Request Instagram's public web profile JSON endpoint for the account.
2. Parse out the most recent posts (caption + timestamp + permalink).
3. Compare against existing entries in announcements.json (by post URL).
4. Add any new posts as "game" type announcements, tagged with
   source: "instagram" so they're distinguishable from X-sourced ones.
5. Write the file back out, sorted by date descending.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

IG_USERNAME = "kaijuno8_thegame_en"

CATEGORY_KEYWORDS = {
    "gacha": ["pickup gacha", "gacha", "pickup character", "pickup banner"],
    "event": ["special event", "event trailer", "large conquest", "conquest", "campaign", "rewards campaign"],
    "update": ["data update", "content schedule", "uniparts added", "training &", "patch notes"],
    "character": ["character skill showcase", "character trailer", "new character", "character voice clip", "skill showcase"],
}

def detect_category(title, summary):
    """Best-effort keyword match against post text. Returns None if no
    keyword matches, so callers can fall back to a generic 'news' bucket
    rather than guessing wrong."""
    text = f"{title} {summary}".lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return category
    return None
ANNOUNCEMENTS_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "announcements.json"

# Instagram's unofficial public web profile endpoint. This URL pattern
# has historically required these specific headers to return data while
# logged out. Both the URL and required headers have changed before and
# will likely change again — if this breaks, that's the first thing to
# check against current Instagram web traffic in a browser's dev tools.
PROFILE_URL = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={IG_USERNAME}"

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "X-IG-App-ID": "936619743392459",  # public web app ID used by instagram.com itself
    "Accept": "*/*",
}

REQUEST_TIMEOUT = 10
MAX_NEW_POSTS_PER_RUN = 5


def fetch_recent_posts():
    """Returns a list of recent post dicts, or None if the fetch failed."""
    try:
        resp = requests.get(PROFILE_URL, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

    if resp.status_code != 200:
        print(f"Instagram returned status {resp.status_code} — likely blocked or rate-limited.")
        return None

    try:
        data = resp.json()
        edges = data["data"]["user"]["edge_owner_to_timeline_media"]["edges"]
    except (KeyError, ValueError, TypeError) as e:
        print(f"Unexpected response shape (Instagram likely changed their API): {e}")
        return None

    posts = []
    for edge in edges:
        node = edge.get("node", {})
        caption_edges = node.get("edge_media_to_caption", {}).get("edges", [])
        caption = caption_edges[0]["node"]["text"] if caption_edges else ""
        shortcode = node.get("shortcode", "")
        timestamp = node.get("taken_at_timestamp")
        if not shortcode or not timestamp:
            continue
        posts.append({
            "caption": caption.strip(),
            "shortcode": shortcode,
            "link": f"https://www.instagram.com/p/{shortcode}/",
            "timestamp": timestamp,
            "image": node.get("display_url"),
        })
    return posts


def load_announcements():
    if not ANNOUNCEMENTS_PATH.exists():
        return {"lastUpdated": "", "announcements": []}
    with open(ANNOUNCEMENTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_announcements(data):
    data["announcements"].sort(key=lambda a: a["date"], reverse=True)
    data["lastUpdated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(ANNOUNCEMENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def slugify_id(date_str, text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:50]
    return f"{date_str}-ig-{slug}"


def main():
    posts = fetch_recent_posts()
    if posts is None:
        print("No usable Instagram data this run — exiting without changes.")
        sys.exit(0)

    if not posts:
        print("Fetch succeeded but returned zero posts — nothing to add.")
        sys.exit(0)

    data = load_announcements()
    existing_links = {a.get("sourceLink") for a in data["announcements"] if a.get("sourceLink")}

    new_count = 0
    for post in posts:
        if new_count >= MAX_NEW_POSTS_PER_RUN:
            break
        if post["link"] in existing_links:
            continue

        date_str = datetime.fromtimestamp(post["timestamp"], tz=timezone.utc).strftime("%Y-%m-%d")
        caption = post["caption"] or "New post from the official Instagram"
        title = caption if len(caption) <= 90 else caption[:87] + "..."
        # Collapse newlines so the card/list summary doesn't break layout
        summary = re.sub(r"\s+", " ", caption).strip()[:280]
        category = detect_category(title, summary)

        new_entry = {
            "id": slugify_id(date_str, caption or post["shortcode"]),
            "date": date_str,
            "type": "game",
            "title": title,
            "summary": summary,
            "link": post["link"],
            "sourceLink": post["link"],
            "source": "instagram",
            "autoAdded": True,
        }
        if post.get("image"):
            new_entry["image"] = post["image"]
        if category:
            new_entry["category"] = category

        data["announcements"].append(new_entry)
        existing_links.add(post["link"])
        new_count += 1
        print(f"Added new Instagram announcement: {title}")

    if new_count == 0:
        print("No new posts found — nothing to update.")
        sys.exit(0)

    save_announcements(data)
    print(f"Done. Added {new_count} new announcement(s).")


if __name__ == "__main__":
    main()
