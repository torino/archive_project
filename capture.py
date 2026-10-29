from playwright.sync_api import sync_playwright
import os

from sites import COMMON_SITES
from utils import today, save_dir, write_log

# ===== GitHub Actions対応：環境変数でheadless切り替え =====
HEADLESS = os.environ.get("HEADLESS", "false").lower() == "true"

# ===== 遅延読み込み画像の読み込み促進 =====
def prepare_lazy_images(page):

    write_log("遅延読み込み画像の読み込み開始")

    for _ in range(10):
        page_height = page.evaluate(
            "document.documentElement.scrollHeight"
        )
        viewport_height = page.evaluate("window.innerHeight")

        # 画面の高さの約80%ずつスクロール
        step = max(1, int(viewport_height * 0.8))

        for y in range(0, page_height, step):
            page.evaluate(
                "(y) => window.scrollTo(0, y)", y
            )
            page.wait_for_timeout(300)

        # スクロールによる追加読み込みを待つ
        page.wait_for_timeout(3000)

        new_height = page.evaluate(
            "document.documentElement.scrollHeight"
        )

        # ページの高さが変わらなければ終了
        if new_height <= page_height:
            break

    # 撮影位置を先頭に戻す
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)

    write_log("遅延読み込み画像の読み込み促進完了")

# ===== フルスクショ + HTML保存 =====
def capture_page(page, ss_name):
    
    # 追加：撮影前に画像の読み込みを促す
    prepare_lazy_images(page)

    full_path = f"{save_dir}/{today}_{ss_name}_full.png"
    html_path = f"{save_dir}/{today}_{ss_name}.html"

    write_log(f"{ss_name}: スクショ開始")
    page.screenshot(path=full_path, full_page=True)
    write_log(f"{ss_name}: スクショ完了")

    try:
        html = page.content()
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        write_log(f"{ss_name}: HTML保存完了")
    except Exception as e:
        write_log(f"{ss_name}: HTML保存失敗: {e}")


# ===== 共通サイト取得 =====
def capture_site(browser, site):

    ss_name = site["name"]
    ss_url  = site["url"]

    page = browser.new_page()
    write_log(f"{ss_name}: アクセス開始: {ss_url}")

    try:
        page.goto(ss_url, timeout=60000)
        page.wait_for_timeout(3000)
        capture_page(page, ss_name)
    except Exception as e:
        write_log(f"{ss_name}: 取得失敗: {e}")
    finally:
        page.close()


# ===== 個別サイト：NHK =====
def capture_nhk(browser):

    ss_name = "nhk"
    ss_url  = "https://www3.nhk.or.jp/news/"

    page = browser.new_page()
    write_log(f"{ss_name}: アクセス開始: {ss_url}")

    try:
        page.goto(ss_url, timeout=60000)
        page.wait_for_timeout(3000)
        try:
            page.locator("text=サービスを利用しない").click(timeout=5000)
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
    ss_url  = "https://www.yahoo.co.jp/"

    page = browser.new_page()
    write_log(f"{ss_name}: アクセス開始: {ss_url}")

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
        page.goto(ss_url, timeout=90000)
        page.wait_for_timeout(5000)
        capture_page(page, ss_name)
    except Exception as e:
        write_log(f"{ss_name}: 取得失敗: {e}")
    finally:
        page.close()


# ===== メイン =====
def run_capture():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)

        # 共通サイト
        for site in COMMON_SITES:
            capture_site(browser, site)

        # 個別サイト
        # capture_nhk(browser)  # GitHub ActionsでIPブロックのため一時除外
        capture_yahoo(browser)
        capture_nikoniko(browser)

        browser.close()

    write_log("キャプチャ完了")