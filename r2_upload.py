import boto3
import os
from utils import today, slot, save_dir, write_log

# ===== R2接続設定 =====
R2_ACCESS_KEY  = os.environ.get("R2_ACCESS_KEY")
R2_SECRET_KEY  = os.environ.get("R2_SECRET_KEY")
R2_BUCKET_NAME = os.environ.get("R2_BUCKET_NAME")
R2_ENDPOINT    = os.environ.get("R2_ENDPOINT")


def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
        region_name="auto"
    )


def upload_file(local_path, r2_key):
    """1ファイルをR2にアップロード"""
    try:
        client = get_r2_client()
        client.upload_file(local_path, R2_BUCKET_NAME, r2_key)
        write_log(f"R2アップロード完了: {r2_key}")
    except Exception as e:
        write_log(f"R2アップロード失敗: {r2_key} / {e}")


def upload_today():
    """本日分の画像をR2にアップロード"""

    # R2設定が未設定の場合はスキップ
    if not all([R2_ACCESS_KEY, R2_SECRET_KEY, R2_BUCKET_NAME, R2_ENDPOINT]):
        write_log("R2設定なし・スキップ")
        return

    write_log("R2アップロード開始")

    if not os.path.exists(save_dir):
        write_log(f"保存先フォルダが見つかりません: {save_dir}")
        return

    for filename in os.listdir(save_dir):

        # 画像ファイルのみアップロード
        if not filename.endswith(".png"):
            continue

        local_path = os.path.join(save_dir, filename)
        r2_key = f"{today}/{slot}/{filename}"

        upload_file(local_path, r2_key)

    write_log("R2アップロード完了")