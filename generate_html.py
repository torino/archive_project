"""
generate_html.py
R2上の画像・テキストを参照するためのメタデータ available_dates.json を生成する。
SPA (Single Page Application) で動的に読み込む設定ファイルとなります。
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

# r2_uploadモジュールから構造取得関数をインポート
from r2_upload import get_r2_archive_structure

# ===== 設定 =====
R2_PUBLIC_URL = os.environ.get("R2_PUBLIC_URL", "")
DOCS_DIR      = "docs"
DATES_JSON    = os.path.join(DOCS_DIR, "available_dates.json")

os.makedirs(DOCS_DIR, exist_ok=True)


def generate_available_dates_json():
    print("available_dates.json の生成を開始します...")
    
    # 1. R2からアップロード済みの {日付: [スロットリスト]} 構造を取得 (API経由)
    archive_structure = get_r2_archive_structure()
    
    # 2. ローカルの data/ フォルダも走査してマージ (GitHub Actionsカレント実行分やローカル開発用)
    if os.path.exists("data"):
        for date_key in os.listdir("data"):
            date_dir = os.path.join("data", date_key)
            if os.path.isdir(date_dir) and date_key.isdigit() and len(date_key) == 8:
                slots = []
                for slot in os.listdir(date_dir):
                    if os.path.isdir(os.path.join(date_dir, slot)) and slot.isdigit():
                        slots.append(slot)
                
                if slots:
                    if date_key in archive_structure:
                        # R2の既存データとローカル取得分をマージして重複排除
                        merged_slots = list(set(archive_structure[date_key] + slots))
                        archive_structure[date_key] = sorted(merged_slots)
                    else:
                        archive_structure[date_key] = sorted(slots)
                        
    # 3. 構造を保存用のデータ辞書に整形
    data = {
        "r2_public_url": R2_PUBLIC_URL,
        "dates": archive_structure
    }
    
    # 4. JSONとして書き出し
    with open(DATES_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"available_dates.json を更新しました: {DATES_JSON}")
    print(f"R2 Public URL: {R2_PUBLIC_URL}")
    print(f"合計収録日数: {len(archive_structure)} 日")
    for date_key, slots in sorted(archive_structure.items())[-5:]:
        print(f"  - {date_key}: {slots}")


if __name__ == "__main__":
    generate_available_dates_json()