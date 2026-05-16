from PIL import Image
import pytesseract
import os
import platform
 
from sites import COMMON_SITES, UNCOMMON_SITES
from utils import today, save_dir, write_log
 
# ===== Tesseractパス（OS自動切り替え） =====
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
 
 
# ===== サムネイル生成 =====
def make_thumbnail(ss_name):
 
    full_path  = f"{save_dir}/{today}_{ss_name}_full.png"
    thumb_path = f"{save_dir}/{today}_{ss_name}_thumb.png"
 
    if not os.path.exists(full_path):
        write_log(f"{ss_name}: フル画像が見つかりません（スキップ）")
        return
 
    try:
        img = Image.open(full_path)
        width, height = img.size
        crop_height = min(800, height)
        thumb = img.crop((0, 0, width, crop_height))
        thumb.save(thumb_path)
        write_log(f"{ss_name}: サムネイル保存完了")
    except Exception as e:
        write_log(f"{ss_name}: サムネイル生成失敗: {e}")
 
 
# ===== OCR =====
def run_ocr(ss_name, ss_lang):
 
    full_path = f"{save_dir}/{today}_{ss_name}_full.png"
    text_path = f"{save_dir}/{today}_{ss_name}.txt"
 
    if not os.path.exists(full_path):
        write_log(f"{ss_name}: フル画像が見つかりません（OCRスキップ）")
        return
 
    write_log(f"{ss_name}: OCR開始")
    try:
        text = pytesseract.image_to_string(
            Image.open(full_path),
            lang=ss_lang
        )
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(text)
        write_log(f"{ss_name}: OCR完了")
    except Exception as e:
        write_log(f"{ss_name}: OCR失敗: {e}")
 
 
# ===== サイトリスト（共通＋個別を統合） =====
ALL_SITES = COMMON_SITES + UNCOMMON_SITES
 
 
# ===== メイン =====
def run_process():
    for site in ALL_SITES:
        ss_name = site["name"]
        ss_lang = site.get("lang", "jpn")
        make_thumbnail(ss_name)
        run_ocr(ss_name, ss_lang)
 
    write_log("サムネイル・OCR完了")
 
