#!/usr/bin/env python3
"""
sync_x_announcements.py

Checks the official Kaiju No. 8 The Game X account (@kj8_TheGame_EN) for
new posts and appends them to data/announcements.json as "game" type
entries, so they show up automatically on the K8GUIDE home page and
Announcements page.

== WHY THIS IS FRAGILE ==
X (formerly Twitter) does not offer a free, reliable, official way to read
a public account's posts anymore — the official API requires a paid plan.
This script instead relies on a public Nitter-style RSS bridge, which is
an unofficial, community-run mirror of X. These bridges:
  - Can go down entirely with no warning
  - Can get rate-limited or IP-blocked
  - May change their URL structure without notice

If this script starts failing, that is the most likely reason — not a
problem with the rest of the site. The job will fail silently (the
workflow run will show a non-zero exit and skip the commit step) rather
than corrupt announcements.json with bad data.

== HOW IT WORKS ==
1. Try a list of known Nitter-style RSS bridge instances for the account.
2. Parse the RSS feed for the most recent posts.
3. Compare against existing entries in announcements.json (by post ID/URL).
4. Add any new posts as "game" type announcements.
5. Write the file back out, sorted by date descending.

If ALL bridge instances fail, the script exits cleanly without making
any changes — it will simply try again on the next scheduled run.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import requests

X_USERNAME = "kj8_TheGame_EN"
ANNOUNCEMENTS_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "announcements.json"

# Known public Nitter-style RSS bridge instances. This list will likely
# need maintenance over time as instances go up/down — that's expected.
# Add or remove instances here as needed; the script tries each in order
# and uses the first one that returns a valid feed.
BRIDGE_INSTANCES = [
    "https://rss.xcancel.com/{user}/rss",
    "https://xcancel.com/{user}/rss",
    "https://nitter.poast.org/{user}/rss",
    "https://nitter.privacyredirect.com/{user}/rss",
    "https://nitter.tiekoetter.com/{user}/rss",
    "https://nitter.net/{user}/rss",
]

REQUEST_TIMEOUT = 10
MAX_NEW_POSTS_PER_RUN = 5  # safety cap so one run can't flood the feed


def fetch_feed():
    """Try each bridge instance until one works. Returns parsed feed or None."""
    for template in BRIDGE_INSTANCES:
        url = template.format(user=X_USERNAME)
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            })
            if resp.status_code == 200 and resp.text.strip():
                parsed = feedparser.parse(resp.text)
                if parsed.entries:
                    print(f"Successfully fetched feed from {url}")
                    newest = parsed.entries[0]
                    newest_title = newest.get("title", "(no title)")[:80]
                    newest_date = newest.get("published", newest.get("updated", "(no date)"))
                    print(f"Newest entry in feed: [{newest_date}] {newest_title}")
                    return parsed
        except requests.RequestException as e:
            print(f"Bridge {url} failed: {e}")
            continue
    print("All bridge instances failed or returned empty feeds.")
    return None


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


def slugify_id(date_str, title):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:50]
    return f"{date_str}-x-{slug}"


def extract_image_url(entry):
    """
    Try several common places an RSS/Nitter entry might carry a post image:
    - media_content / media_thumbnail (standard RSS media extensions)
    - an <img> tag embedded directly in the summary/description HTML
    Returns None if nothing usable is found.
    """
    # Standard media RSS fields, when the bridge provides them
    media_content = entry.get("media_content")
    if media_content:
        url = media_content[0].get("url")
        if url:
            return url

    media_thumbnail = entry.get("media_thumbnail")
    if media_thumbnail:
        url = media_thumbnail[0].get("url")
        if url:
            return url

    # Nitter commonly embeds the image as an <img src="..."> inside the
    # summary HTML instead of a dedicated media field.
    summary_html = entry.get("summary", "")
    match = re.search(r'<img[^>]+src="([^"]+)"', summary_html)
    if match:
        return match.group(1)

    return None


def clean_html_summary(raw_html):
    """Strip HTML tags down to plain text for the summary field, so the
    site doesn't render raw <a>/<img> markup inside the card/list text."""
    text = re.sub(r"<[^>]+>", " ", raw_html)
    text = re.sub(r"\s+", " ", text).strip()
    return text


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


def main():
    feed = fetch_feed()
    if feed is None:
        print("No feed available this run — exiting without changes.")
        sys.exit(0)

    data = load_announcements()
    existing_links = {a.get("sourceLink") for a in data["announcements"] if a.get("sourceLink")}

    new_count = 0
    for entry in feed.entries:
        if new_count >= MAX_NEW_POSTS_PER_RUN:
            break

        link = entry.get("link", "")
        if not link or link in existing_links:
            continue

        try:
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            date_str = datetime(*published[:6]).strftime("%Y-%m-%d") if published else \
                datetime.now(timezone.utc).strftime("%Y-%m-%d")
        except Exception:
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        raw_title = entry.get("title", "").strip()
        if not raw_title:
            continue

        # Trim to a reasonable headline length; full text stays in summary
        title = raw_title if len(raw_title) <= 90 else raw_title[:87] + "..."
        raw_summary = entry.get("summary", raw_title)
        summary = clean_html_summary(raw_summary)
        image_url = extract_image_url(entry)

        category = detect_category(title, summary)

        new_entry = {
            "id": slugify_id(date_str, raw_title),
            "date": date_str,
            "type": "game",
            "title": title,
            "summary": summary[:280],
            "link": link,
            "sourceLink": link,
            "autoAdded": True,
        }
        if image_url:
            new_entry["image"] = image_url
        if category:
            new_entry["category"] = category

        data["announcements"].append(new_entry)
        existing_links.add(link)
        new_count += 1
        print(f"Added new announcement: {title}")

    if new_count == 0:
        print("No new posts found — nothing to update.")
        sys.exit(0)

    save_announcements(data)
    print(f"Done. Added {new_count} new announcement(s).")


if __name__ == "__main__":
    main()
