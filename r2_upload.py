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
    """1ファイルをR2にアップロード（適切なContentTypeを設定）"""
    try:
        client = get_r2_client()
        extra_args = {}
        
        # 拡張子からContent-Typeを判定
        ext = os.path.splitext(local_path)[1].lower()
        if ext == ".png":
            extra_args["ContentType"] = "image/png"
        elif ext == ".html":
            extra_args["ContentType"] = "text/html"
        elif ext in [".txt", ".log"]:
            extra_args["ContentType"] = "text/plain; charset=utf-8"
        elif ext == ".json":
            extra_args["ContentType"] = "application/json"

        client.upload_file(local_path, R2_BUCKET_NAME, r2_key, ExtraArgs=extra_args)
        write_log(f"R2アップロード完了: {r2_key}")
    except Exception as e:
        write_log(f"R2アップロード失敗: {r2_key} / {e}")


def upload_today():
    """本日分のファイル（画像・HTML・テキスト・メタデータ）をR2にアップロード"""

    # R2設定が未設定の場合はスキップ
    if not all([R2_ACCESS_KEY, R2_SECRET_KEY, R2_BUCKET_NAME, R2_ENDPOINT]):
        write_log("R2設定なし・スキップ")
        return

    write_log("R2アップロード開始")

    if not os.path.exists(save_dir):
        write_log(f"保存先フォルダが見つかりません: {save_dir}")
        return

    for filename in os.listdir(save_dir):
        ext = os.path.splitext(filename)[1].lower()
        # アップロード対象の拡張子のみをフィルタリング
        if ext not in [".png", ".html", ".txt", ".json", ".log"]:
            continue

        local_path = os.path.join(save_dir, filename)
        r2_key = f"{today}/{slot}/{filename}"

        upload_file(local_path, r2_key)

    write_log("R2アップロード処理終了")


def get_r2_archive_structure():
    """R2からアップロード済みの {date: [slots]} 構造を取得する"""
    if not all([R2_ACCESS_KEY, R2_SECRET_KEY, R2_BUCKET_NAME, R2_ENDPOINT]):
        write_log("R2設定なし・構造取得スキップ")
        return {}

    try:
        client = get_r2_client()
        dates = []
        
        # トップレベルの仮想フォルダ（日付：YYYYMMDD）を取得
        result = client.list_objects_v2(Bucket=R2_BUCKET_NAME, Delimiter='/')
        for prefix in result.get('CommonPrefixes', []):
            date_key = prefix['Prefix'].strip('/')
            if date_key.isdigit() and len(date_key) == 8:
                dates.append(date_key)
        
        structure = {}
        for date_key in sorted(dates):
            # 各日付の下の仮想フォルダ（スロット：HHMM）を取得
            slots_result = client.list_objects_v2(
                Bucket=R2_BUCKET_NAME, 
                Prefix=f"{date_key}/", 
                Delimiter='/'
            )
            slots = []
            for slot_prefix in slots_result.get('CommonPrefixes', []):
                slot_name = slot_prefix['Prefix'].split('/')[-2]
                if slot_name.isdigit() and len(slot_name) == 4:
                    slots.append(slot_name)
            if slots:
                structure[date_key] = sorted(slots)
        
        write_log(f"R2から構造取得成功 (計 {len(structure)} 日分)")
        return structure
    except Exception as e:
        write_log(f"R2構造取得失敗: {e}")
        return {}