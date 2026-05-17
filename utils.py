import os
from datetime import datetime
 
# 日付
today = datetime.now().strftime("%Y%m%d")
slot  = datetime.now().strftime("%H%M")

# 保存先
save_dir = f"data/{today}/{slot}"
os.makedirs(save_dir, exist_ok=True)
 
# ログファイルパス
log_path = f"{save_dir}/capture.log"
 
 
def write_log(message):
    now = datetime.now().strftime("%H:%M:%S")
    log_message = f"[{now}] {message}"
    print(log_message)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")
 
