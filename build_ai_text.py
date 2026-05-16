from datetime import datetime
import os

from sites import COMMON_SITES
from sites import UNCOMMON_SITES
from utils import today, save_dir, write_log

# 日付取得
today = datetime.now().strftime("%Y%m%d")

# 保存先
save_dir = f"data/{today}"

# AI統合ファイル
ai_filename = f"{today}_ai.txt"
ai_path = f"{save_dir}/{ai_filename}"


# サイト単位の追記
def append_site_ai_text(site):

    ss_name = site["name"]
    ss_url = site["url"]
    ss_lang = site["lang"]

    # OCRファイル
    ocr_filename = f"{today}_{ss_name}.txt"
    ocr_path = f"{save_dir}/{ocr_filename}"

    # HTMLファイル
    html_filename = f"{today}_{ss_name}.html"
    html_path = f"{save_dir}/{html_filename}"

    write_log(f"{ss_name}: AIテキスト追記開始")

    try:

        # OCR読み込み
        with open(
            ocr_path,
            "r",
            encoding="utf-8"
        ) as f:

            ocr_text = f.read()

        # HTML読み込み
        with open(
            html_path,
            "r",
            encoding="utf-8"
        ) as f:

            html_text = f.read()

        # AI統合ファイルへ追記
        with open(
            ai_path,
            "a",
            encoding="utf-8"
        ) as f:

            f.write("\n")
            f.write("========================================\n")
            f.write(f"SITE: {ss_name}\n")
            f.write("========================================\n")

            # メタ情報
            f.write("\n===== METADATA =====\n")
            f.write(f"site: {ss_name}\n")
            f.write(f"url: {ss_url}\n")
            f.write(f"lang: {ss_lang}\n")
            f.write(f"date: {today}\n")

            # OCR
            f.write("\n===== OCR =====\n")
            f.write(ocr_text)

            # HTML
            f.write("\n\n===== HTML =====\n")
            f.write(html_text)

            f.write("\n\n")

        write_log(f"{ss_name}: AIテキスト追記完了")

    except Exception as e:

        write_log(f"{ss_name}: AIテキスト生成失敗: {e}")


# 全サイト統合
def build_ai_texts():

    write_log("AI統合テキスト生成開始")

    # 既存ファイル削除
    if os.path.exists(ai_path):
        os.remove(ai_path)

    # 共通サイト
    for site in COMMON_SITES:

        append_site_ai_text(site)

    # 個別サイト
    for site in UNCOMMON_SITES:

        append_site_ai_text(site)

    write_log("AI統合テキスト生成終了")