#!/usr/bin/env python3
"""
sync_official_announcements.py

Checks the official KAIJU NO. 8 THE GAME news page (info.kj8-thegame.com)
for new posts and appends them to data/announcements.json as "game" type
entries, so they show up automatically on the K8GUIDE home page and
Announcements page.

== WHY THIS REPLACES THE X/NITTER AND INSTAGRAM SCRIPTS ==
sync_x_announcements.py depended on public Nitter-style RSS bridges, which
have all died. sync_instagram_announcements.py depended on Instagram's
unofficial API plus an RSS.app fallback -- and every hosted "social to RSS"
service we checked (RSS.app, FeedSpot) gates Instagram specifically behind
a paid subscription. Neither approach is viable for a volunteer fan site
with no budget.

This script instead scrapes the game's own first-party news page directly:
https://info.kj8-thegame.com/news/?language=en

That page is plain, server-rendered HTML -- no login, no CAPTCHA, no
anti-bot wall, no rate limiting encountered when this was written. It's
also strictly better data than the social posts ever were: most X/IG posts
just linked back to this same site for "details" anyway, so this is the
primary source, not a secondary mirror of one.

== HOW IT WORKS ==
1. Fetch the news list page and parse every
   <div class="ui-list-block js-each-content" data-content-id="...">
   block for its content ID, category label, and title.
2. Compare content IDs against data/.official_seen_ids.json (a small local
   cache of IDs we've already processed) to find genuinely new posts.
3. For each new ID, fetch https://info.kj8-thegame.com/news/<id>?language=en
   for the exact ISO timestamp, title, and body text.
4. Append new entries to data/announcements.json (type: "game",
   source: "official"), sorted by date descending, and update the
   seen-IDs cache.

== IF THIS BREAKS ==
Unlike the old scripts, there's no unofficial/rate-limited API here to
silently degrade against -- this is the game's own site. If parsing starts
returning zero items, that almost certainly means the site's markup
changed (class names, structure). Check the current HTML at the URLs above
against the CSS selectors below (SELECTOR NOTES section) and update them.
This script exits non-zero (fails loudly in the Actions tab) rather than
silently corrupting announcements.json, so a real markup change won't go
unnoticed.

== SELECTOR NOTES (as of 2026-09-11) ==
List page item block:
  <div data-content-id="1003710" data-url="../news/1003710?language=en"
       class="ui-list-block js-each-content">
    <div class="ui-list-block-bg">
      <p class="ui-list-category ui-update">Update</p>
      <div class="ui-list-content js-list-content js-clamp-text">Data Update &amp; Event Preview</div>
    </div>
  </div>
  (Note: pinned items appear twice in the raw HTML -- once in a "pinned"
  block, once in the normal list. We de-dupe by content-id per page load.)

Article page:
  <p class="ui-contents-header-date"><span class="nowrap js-datetime">2026-09-10T03:00:00Z</span></p>
  <div class="ui-contents-main js-detail-main" data-content-id="1003710">
    <h1>Data Update &amp; Event Preview</h1>
    <div class="ui-contents-main-detail js-detail-body">...full body HTML...</div>
  </div>
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

LIST_URL = "https://info.kj8-thegame.com/news/?language=en"
ARTICLE_URL_TMPL = "https://info.kj8-thegame.com/news/{id}?language=en"

ANNOUNCEMENTS_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "announcements.json"
SEEN_IDS_PATH = Path(__file__).resolve().parent.parent.parent / "data" / ".official_seen_ids.json"

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
}
REQUEST_TIMEOUT = 15
MAX_NEW_POSTS_PER_RUN = 8  # safety cap so one run can't flood the feed

# Official site category labels -> this site's own announcement category
# values. See announcements/index.html's filter buttons for the valid set
# (gacha, event, update, character). Anything not in this map (News,
# Important, Known Issue, Maintenance) is left uncategorized -- it still
# shows up under "All Categories", just without a category chip.
CATEGORY_MAP = {
    "Gacha": "gacha",
    "Event": "event",
    "Update": "update",
    "Character": "character",
}


def fetch_list_page():
    resp = requests.get(LIST_URL, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.text


def parse_list_items(html):
    """Returns a list of {id, category_label, title} dicts from the news
    list page, de-duplicated by content-id (pinned items render twice)."""
    soup = BeautifulSoup(html, "html.parser")
    items = []
    seen_this_page = set()
    for block in soup.select("div.ui-list-block.js-each-content[data-content-id]"):
        content_id = block.get("data-content-id")
        if not content_id or content_id in seen_this_page:
            continue
        seen_this_page.add(content_id)
        category_el = block.select_one("p.ui-list-category")
        title_el = block.select_one("div.ui-list-content")
        items.append({
            "id": content_id,
            "category_label": category_el.get_text(strip=True) if category_el else "",
            "title": title_el.get_text(strip=True) if title_el else "",
        })
    return items


def fetch_article(content_id):
    """Fetch a single article page and return {timestamp, title, summary, image, link}."""
    url = ARTICLE_URL_TMPL.format(id=content_id)
    resp = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    datetime_el = soup.select_one("span.js-datetime")
    timestamp = datetime_el.get_text(strip=True) if datetime_el else None

    title_el = soup.select_one("div.js-detail-main h1")
    title = title_el.get_text(strip=True) if title_el else None

    body_el = soup.select_one("div.js-detail-body")
    summary = ""
    image = None
    if body_el:
        text = body_el.get_text(separator=" ", strip=True)
        summary = re.sub(r"\s+", " ", text).strip()[:280]
        img_tag = body_el.find("img")
        if img_tag and img_tag.get("src"):
            image = img_tag["src"]

    return {
        "timestamp": timestamp,
        "title": title,
        "summary": summary,
        "image": image,
        "link": url,
    }


def load_json(path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def slugify_id(date_str, content_id, title):
    slug = re.sub(r"[^a-z0-9]+", "-", (title or "").lower()).strip("-")[:50]
    return f"{date_str}-official-{content_id}-{slug}"


def main():
    try:
        list_html = fetch_list_page()
    except requests.RequestException as e:
        print(f"Failed to fetch news list page: {e}")
        sys.exit(1)

    items = parse_list_items(list_html)
    if not items:
        print("Parsed zero items from the news list page -- the site's markup "
              "likely changed. See SELECTOR NOTES in this script's docstring. "
              "Exiting without changes.")
        sys.exit(1)
    print(f"Found {len(items)} items on the news list page.")

    seen_ids = set(load_json(SEEN_IDS_PATH, []))
    new_items = [it for it in items if it["id"] not in seen_ids]

    if not new_items:
        print("No new content IDs since last run -- nothing to add.")
        sys.exit(0)

    data = load_json(ANNOUNCEMENTS_PATH, {"lastUpdated": "", "announcements": []})
    existing_entry_ids = {a.get("id") for a in data["announcements"]}

    added = 0
    for item in new_items[:MAX_NEW_POSTS_PER_RUN]:
        try:
            article = fetch_article(item["id"])
        except requests.RequestException as e:
            print(f"Failed to fetch article {item['id']}: {e} -- skipping, will retry next run.")
            continue

        if not article["timestamp"]:
            print(f"Could not find a timestamp for article {item['id']} -- skipping, will retry next run.")
            continue

        date_str = article["timestamp"][:10]  # 'YYYY-MM-DD' prefix of the ISO timestamp
        title = article["title"] or item["title"] or f"News {item['id']}"
        entry_id = slugify_id(date_str, item["id"], title)

        if entry_id not in existing_entry_ids:
            new_entry = {
                "id": entry_id,
                "date": date_str,
                "type": "game",
                "title": title,
                "summary": article["summary"] or title,
                "link": article["link"],
                "sourceLink": article["link"],
                "source": "official",
                "autoAdded": True,
            }
            if article["image"]:
                new_entry["image"] = article["image"]
            category = CATEGORY_MAP.get(item["category_label"])
            if category:
                new_entry["category"] = category

            data["announcements"].append(new_entry)
            existing_entry_ids.add(entry_id)
            added += 1
            print(f"Added: [{item['category_label'] or 'News'}] {title}")

        seen_ids.add(item["id"])  # mark seen either way so we don't refetch it forever

    # Persist the seen-IDs cache regardless of whether anything was added,
    # so successfully-processed IDs (even ones that turned out to be
    # duplicates) aren't refetched next run.
    save_json(SEEN_IDS_PATH, sorted(seen_ids))

    if added == 0:
        print("No new announcements actually added this run.")
        sys.exit(0)

    data["announcements"].sort(key=lambda a: a["date"], reverse=True)
    data["lastUpdated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    save_json(ANNOUNCEMENTS_PATH, data)
    print(f"Done. Added {added} new announcement(s).")


if __name__ == "__main__":
    main()
