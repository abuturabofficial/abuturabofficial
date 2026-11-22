#!/usr/bin/env python3
"""Refresh the blog table in README.md from the site's RSS feed (stdlib only)."""
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

FEED_URL = "https://sajidmahmood.com/index.xml"
README = Path("README.md")
MAX_POSTS = 8
START, END = "<!-- BLOG-POST-LIST:START -->", "<!-- BLOG-POST-LIST:END -->"


def fetch_posts():
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "readme-blog-updater"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        root = ET.fromstring(resp.read())
    posts = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = item.findtext("pubDate")
        if not (title and link.startswith("https://")):
            continue
        try:
            date = parsedate_to_datetime(pub).strftime("%b %d, %Y")
        except (TypeError, ValueError):
            date = ""
        posts.append((date, title.replace("|", "\\|"), link))
    return posts[:MAX_POSTS]


def main():
    posts = fetch_posts()
    if not posts:
        sys.exit("No posts parsed from feed; leaving README untouched.")
    rows = ["| Date | Post |", "|------|------|"]
    rows += [f"| {d} | [{t}]({u}) |" for d, t, u in posts]
    block = f"{START}\n" + "\n".join(rows) + f"\n{END}"

    text = README.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        sys.exit("Markers not found in README.md")
    new = pattern.sub(lambda _: block, text)
    if new != text:
        README.write_text(new, encoding="utf-8")
        print("README updated.")
    else:
        print("No changes.")


if __name__ == "__main__":
    main()
