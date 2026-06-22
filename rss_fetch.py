import feedparser
import json
import os

from utils import today, save_dir, write_log

# ===== RSS対象リスト =====
RSS_SITES = [
    {"name": "nhk_rss",   "url": "https://www3.nhk.or.jp/rss/news/cat0.xml"},
    {"name": "yahoo_rss", "url": "https://news.yahoo.co.jp/rss/topics/top-picks.xml"},
]

# 前回取得分の記録ファイル（重複防止用）
SEEN_PATH = "data/rss_seen.json"


def load_seen():
    if os.path.exists(SEEN_PATH):
        with open(SEEN_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_seen(seen):
    with open(SEEN_PATH, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)


def fetch_rss(site, seen):

    ss_name = site["name"]
    ss_url  = site["url"]

    write_log(f"{ss_name}: RSS取得開始")

    try:
        feed = feedparser.parse(ss_url)

        if feed.bozo:
            write_log(f"{ss_name}: RSS解析エラー: {feed.bozo_exception}")
            return []

        seen_links = set(seen.get(ss_name, []))
        new_items  = []

        for entry in feed.entries:
            link = entry.get("link", "")
            if link and link not in seen_links:
                new_items.append({
                    "title":     entry.get("title", ""),
                    "link":      link,
                    "published": entry.get("published", ""),
                    "summary":   entry.get("summary", "")
                })
                seen_links.add(link)

        seen[ss_name] = list(seen_links)

        write_log(f"{ss_name}: 新規{len(new_items)}件取得")
        return new_items

    except Exception as e:
        write_log(f"{ss_name}: RSS取得失敗: {e}")
        return []


def run_rss_fetch():

    write_log("RSS取得開始")

    seen = load_seen()
    all_results = {}

    for site in RSS_SITES:
        new_items = fetch_rss(site, seen)
        all_results[site["name"]] = new_items

    # 本日分のRSS結果を保存
    out_path = f"{save_dir}/{today}_rss.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # 既読リンクを更新保存
    save_seen(seen)

    write_log(f"RSS取得完了: {out_path}")


if __name__ == "__main__":
    run_rss_fetch()