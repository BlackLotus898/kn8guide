# K8GUIDE — Internal Update Log

This is a running internal log of every batch of changes pushed to the site, for Lotus's own tracking. It is NOT shown publicly — it's a reference for deciding what's worth promoting to the public Announcements feed (`data/announcements.json`).

Format: most recent entry at the top. Each entry lists the date and a plain-language summary of what changed.

---

## 2026-06-19

**Unlocked Potential page corrections**
- Removed incorrect claim that UP requires max Ascension (unconfirmed/disproven via direct testing on Isao)
- Removed unverified claim about material/Spec-Ops Rank requirements
- Added Mina Ashiro (Off the Scale) and Soshiro Hoshina (Hoshina-Style Sword-Slay Technique) to the confirmed UP character list

**Announcements link fix**
- Fixed a 404 bug: announcement links used relative paths that only worked from one page depth, breaking on the home page banner and "What's New" cards
- Fixed by switching to root-relative paths in the data file, with the dedicated Announcements page adjusting depth at render time

**Banners page fixes**
- Gen Narumi (SPB) moved from Past Banners back to Active — his banner is still live through Jun 20, was incorrectly marked ENDED
- Added Chester Lochburn's signature weapon (AR-Anollococ) to his active banner card

**Sagan Shinomiya (RC) character page**
- Filled in confirmed pre-release kit data: role (Supporter), attack type (Blunt/Fire), Ultimate (Ardent Command), Combat Skill (Vanguard Initiative), full Passive Skill (Hidden Thermal Surge), and Ascension nodes 1–2
- Normal Attack, Follow-Up Skill, remaining ascensions, weapon, and uniparts intentionally left pending — not revealed pre-release
- NOT yet added to roster/tracker/squad maker (waiting on full release June 20 for art + remaining kit)

**Started this internal update log** (you're reading it)

---

## 2026-06-18 (and earlier — backfilled from memory, may be incomplete)

- Built Rin Shinonome (Cross-Forged Refinement) full character page + site-wide integration
- Built Tier List Maker (later rebuilt from drag-and-drop to modal-based "Manage Tier" system after mobile usability issues)
- Built Announcements system (home page banner + cards, dedicated page, GitHub Action auto-scrapers for X and Instagram)
- Fixed nav.js hardcoded base path bug (was breaking staging/test repo clones)
- Cleaned up auto-scraped announcement entries (stripped decorative characters, HTML tags from X/Nitter post text)
- Added image support to auto-scraped announcements
- Fixed Soichiro Hoshina (KOWJ) weapons, exploit medal, removed incorrect Limited tag
- Added Unlocked Potential as a new Game Guide section + page
- Renamed "Achievements" to "Unknown Achievements" site-wide
- Fixed Gen Narumi (SPB) exploit medal, removed Stats-by-Slot box, added to Limited/Banners pages with real photo
- Added 5 new Special Status entries (Fury, Prestige, Pride, Refinement, Sass) + Mind's Eye (found missing from Soichiro's kit)
- Site-wide link casing audit (`/Characters/` vs `/characters/`)
- Deleted stray leftover HTML file using old site structure

---

## Notes on using this log

- When something here feels "announcement-worthy" for visitors, add a clean entry to `data/announcements.json` with `"type": "site"`
- This log can stay messy/shorthand — it's just for you, not public-facing
- Going forward, every batch of changes should get an entry here before being marked done
