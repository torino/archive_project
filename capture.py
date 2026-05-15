from playwright.sync_api import sync_playwright
from datetime import datetime
from PIL import Image
import pytesseract
import os

from sites import COMMON_SITES

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


#日付取得処理
today = datetime.now().strftime("%Y%m%d")

#保存先フォルダ作成
save_dir = f"data/{today}"
os.makedirs(save_dir, exist_ok=True)


# ログファイルパス
log_path = f"{save_dir}/capture.log"


# 共通ログ出力
def write_log(message):

    now = datetime.now().strftime("%H:%M:%S")

    log_message = f"[{now}] {message}"

    # コンソール表示
    print(log_message)

    # ファイル保存
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")


# OCR処理
def run_ocr(image_path, text_path, ss_name, ss_lang):

    write_log(f"{ss_name}: OCR開始")

    try:

        text = pytesseract.image_to_string(
            Image.open(image_path),
            lang=ss_lang
        )

        with open(text_path, "w", encoding="utf-8") as f:
            f.write(text)

        write_log(f"{ss_name}: OCR保存完了")

    except Exception as e:

        write_log(f"{ss_name}: OCR failed: {e}")

# 共通キャプチャ処理
def capture_page(page, ss_name, ss_lang):

    # フル画像
    full_filename = f"{today}_{ss_name}_full.png"
    full_path = f"{save_dir}/{full_filename}"

    # サムネイル画像
    thumb_filename = f"{today}_{ss_name}_thumb.png"
    thumb_path = f"{save_dir}/{thumb_filename}"

    # OCRテキスト
    text_filename = f"{today}_{ss_name}.txt"
    text_path = f"{save_dir}/{text_filename}"
    
    # HTML
    html_filename = f"{today}_{ss_name}.html"
    html_path = f"{save_dir}/{html_filename}"

    write_log(f"{ss_name}: スクショ保存開始")

    # フルページ保存
    page.screenshot(
        path=full_path,
        full_page=True
    )
    write_log(f"{ss_name}: フル画像保存完了")

    # サムネイル生成
    try:
        img = Image.open(full_path)
        width, height = img.size
        crop_height = min(800, height)
        thumb = img.crop((0, 0, width, crop_height))
        thumb.save(thumb_path)
        write_log(f"{ss_name}: サムネイル保存完了")

    except Exception as e:
        write_log(f"{ss_name}: thumb failed: {e}")

    # HTML保存
    try:

        html = page.content()

        with open(
            html_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(html)

        write_log(
            f"{ss_name}: HTML保存完了"
        )

    except Exception as e:

        write_log(
            f"{ss_name}: HTML save failed: {e}"
        )
    
    # OCR実行
    run_ocr(full_path, text_path, ss_name, ss_lang)



# ===== 個別サイト取得　- NHK =====
def capture_nhk(browser):

    ss_name = "nhk"
    ss_url = "https://www3.nhk.or.jp/news/"
    ss_lang = "jpn"

    page = browser.new_page()

    write_log(f"{ss_name}: アクセス開始: {ss_url}")
    page.goto(ss_url)
    page.wait_for_timeout(3000)

    try:
        page.locator("text=サービスを利用しない").click()
    except Exception as e:
        write_log(f"{ss_name}: popup close failed: {e}")
    
    capture_page(page, ss_name, ss_lang)
    
    page.close()

# ===== 共通サイト取得 =====
def capture_site(browser, site):

    ss_name = site["name"]
    ss_url = site["url"]
    ss_lang = site["lang"]
    
    page = browser.new_page()

    write_log(f"{ss_name}: アクセス開始: url: {ss_url}")
    page.goto(ss_url)
    page.wait_for_timeout(3000)
    
    capture_page(page, ss_name, ss_lang)

    page.close()


# ===== 個別サイト取得　-  Yahoo =====
def capture_yahoo(browser):
    ss_name = "yahoo"
    ss_url = "https://www.yahoo.co.jp/"
    ss_lang = "jpn"
    
    page = browser.new_page()

    write_log(f"{ss_name}: アクセス開始: url: {ss_url}")
    page.goto(ss_url)
    page.wait_for_timeout(3000)

    try:
        page.locator("a[data-cl-params*='close']").click()
    except Exception as e:
        write_log(f"{ss_name}: popup close failed: {e}")
    
    capture_page(page, ss_name, ss_lang)

    page.close()


#スクリーンショット取得
def run_capture():
    with sync_playwright() as p:

        # スクリーンショット取得の前処理
        browser = p.chromium.launch(headless=True)

        # 共有処理
        for site in COMMON_SITES:
            capture_site(browser,site)
        
        # 個別処理
        capture_nhk(browser)
        capture_yahoo(browser)
        
        # スクリーンショット取得の後処理
        browser.close()

    write_log("スクショ完了")