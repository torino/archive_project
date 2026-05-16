from playwright.sync_api import sync_playwright
import os
 
from sites import COMMON_SITES
from utils import today, save_dir, write_log
 
# ===== GitHub Actions対応：環境変数でheadless切り替え =====
HEADLESS = os.environ.get("HEADLESS", "false").lower() == "true"
 
 
# ===== フルスクショ + HTML保存 =====
def capture_page(page, ss_name):
 
    full_path = f"{save_dir}/{today}_{ss_name}_full.png"
    html_path = f"{save_dir}/{today}_{ss_name}.html"
 
    # フルページスクショ
    write_log(f"{ss_name}: スクショ開始")
    page.screenshot(path=full_path, full_page=True)
    write_log(f"{ss_name}: スクショ完了")
 
    # HTML保存
    try:
        html = page.content()
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        write_log(f"{ss_name}: HTML保存完了")
    except Exception as e:
        write_log(f"{ss_name}: HTML保存失敗: {e}")
 
 
# ===== 個別サイト：NHK =====
def capture_nhk(browser):
    ss_name = "nhk"
    ss_url = "https://www3.nhk.or.jp/news/"
 
    page = browser.new_page()
    write_log(f"{ss_name}: アクセス開始: {ss_url}")
    page.goto(ss_url)
    page.wait_for_timeout(3000)
 
    try:
        page.goto(ss_url, timeout=60000)
        page.wait_for_timeout(3000)
        try:
            page.locator("text=サービスを利用しない").click()
        except Exception as e:
            write_log(f"{ss_name}: popup close failed: {e}")
        capture_page(page, ss_name)
    except Exception as e:
        write_log(f"{ss_name}: 取得失敗: {e}")
    finally:
        page.close()
 
# ===== 個別サイト：Yahoo =====
def capture_yahoo(browser):
    ss_name = "yahoo"
    ss_url = "https://www.yahoo.co.jp/"
 
    page = browser.new_page()
    write_log(f"{ss_name}: アクセス開始: {ss_url}")
    page.goto(ss_url)
    page.wait_for_timeout(3000)
 
    try:
        page.goto(ss_url, timeout=60000)
        page.wait_for_timeout(3000)
        try:
            page.locator("a[data-cl-params*='close']").click(timeout=5000)
        except Exception as e:
            write_log(f"{ss_name}: popup close failed: {e}")
        capture_page(page, ss_name)
    except Exception as e:
        write_log(f"{ss_name}: 取得失敗: {e}")
    finally:
        page.close()


 # ===== 個別サイト：ニコニコ動画 =====
def capture_nikoniko(browser):
 
    ss_name = "nikoniko"
    ss_url  = "https://www.nicovideo.jp/"
 
    page = browser.new_page()
    write_log(f"{ss_name}: アクセス開始: {ss_url}")
 
    try:
        page.goto(ss_url, timeout=90000)  # 重いサイトのため長めに設定
        page.wait_for_timeout(5000)        # 読み込み待ちも長めに
        capture_page(page, ss_name)
    except Exception as e:
        write_log(f"{ss_name}: 取得失敗: {e}")
    finally:
        page.close()
 

# ===== 共通サイト取得 =====
def capture_site(browser, site):
    ss_name = site["name"]
    ss_url = site["url"]
 
    page = browser.new_page()
    write_log(f"{ss_name}: アクセス開始: {ss_url}")
    page.goto(ss_url)
    page.wait_for_timeout(3000)
 
    capture_page(page, ss_name)
    page.close()
 
 
# ===== メイン =====
def run_capture():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
 
        # 共通サイト
        for site in COMMON_SITES:
            capture_site(browser, site)
 
        # 個別サイト
        capture_nhk(browser)
        capture_yahoo(browser)
        capture_nikoniko(browser)
        
        browser.close()
 
    write_log("キャプチャ完了")
 