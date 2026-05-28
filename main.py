from capture import run_capture
from build_ai_text import build_ai_texts
from process import run_process
from r2_upload import upload_today

print("スクショ処理開始")

run_capture()
run_process()
build_ai_texts()
upload_today()

print("スクショ処理終了")