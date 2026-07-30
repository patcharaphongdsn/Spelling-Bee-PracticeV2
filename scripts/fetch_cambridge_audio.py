#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
BASE = "https://dictionary.cambridge.org"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0 Safari/537.36"
    ),
    "Accept-Language": "en-GB,en;q=0.9",
}

def load_words(html: str) -> tuple[list[dict], re.Match[str]]:
    match = re.search(r"const WORDS = (\[.*?\]);\nconst \$ =", html, flags=re.S)
    if not match:
        raise RuntimeError("WORDS array was not found in index.html")
    return json.loads(match.group(1)), match

def first_mp3(container) -> str:
    if not container:
        return ""
    source = container.select_one('source[type="audio/mpeg"]') or container.select_one("source")
    if not source:
        return ""
    src = source.get("src", "").strip()
    return urljoin(BASE, src) if src else ""

def extract_audio(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")

    # Current Cambridge structure: pronunciation blocks normally carry uk/us classes.
    uk = first_mp3(soup.select_one(".uk.dpron-i")) or first_mp3(soup.select_one(".uk"))
    us = first_mp3(soup.select_one(".us.dpron-i")) or first_mp3(soup.select_one(".us"))

    # Fallback: inspect each audio wrapper and its ancestors.
    if not uk or not us:
        for wrapper in soup.select("span.daud"):
            source = wrapper.select_one('source[type="audio/mpeg"]') or wrapper.select_one("source")
            if not source:
                continue
            src = source.get("src", "").strip()
            if not src:
                continue
            url = urljoin(BASE, src)
            ancestry = " ".join(
                " ".join(node.get("class", []))
                for node in [wrapper, wrapper.parent, getattr(wrapper.parent, "parent", None)]
                if node is not None
            ).lower()
            if " uk " in f" {ancestry} " and not uk:
                uk = url
            if " us " in f" {ancestry} " and not us:
                us = url

    return uk, us

def fetch_word(session: requests.Session, word: str) -> tuple[str, str, str]:
    urls = [
        f"{BASE}/pronunciation/english/{quote(word)}",
        f"{BASE}/dictionary/english/{quote(word)}",
    ]
    for url in urls:
        response = session.get(url, headers=HEADERS, timeout=25)
        if response.status_code == 200:
            uk, us = extract_audio(response.text)
            if uk or us:
                return uk, us, url
        time.sleep(0.4)
    return "", "", urls[0]

def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    words, match = load_words(html)
    session = requests.Session()

    found_uk = found_us = failed = 0
    total = len(words)

    for i, item in enumerate(words, start=1):
        word = item["word"]
        if item.get("audioUk") and item.get("audioUs"):
            print(f"[{i}/{total}] {word}: already complete")
            found_uk += 1
            found_us += 1
            continue

        try:
            uk, us, page = fetch_word(session, word)
        except requests.RequestException as exc:
            print(f"[{i}/{total}] {word}: request error: {exc}")
            failed += 1
            time.sleep(1.5)
            continue

        if uk:
            item["audioUk"] = uk
            found_uk += 1
        if us:
            item["audioUs"] = us
            found_us += 1
        item["cambridgeUrl"] = page

        status = f"UK={'yes' if uk else 'no'}, US={'yes' if us else 'no'}"
        print(f"[{i}/{total}] {word}: {status}")
        if not uk and not us:
            failed += 1

        # Be gentle with the public site.
        time.sleep(0.8)

    new_json = json.dumps(words, ensure_ascii=False, separators=(",", ":"))
    updated = html[:match.start(1)] + new_json + html[match.end(1):]
    INDEX.write_text(updated, encoding="utf-8")

    report = {
        "totalWords": total,
        "ukAudioFound": found_uk,
        "usAudioFound": found_us,
        "entriesWithoutAudio": failed,
    }
    (ROOT / "cambridge-audio-report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
