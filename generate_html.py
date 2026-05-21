"""
generate_html.py
R2上の画像を参照したHTMLを生成する。
出力先: docs/{date}.html + docs/index.html
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from sites import COMMON_SITES, UNCOMMON_SITES

# ===== 設定 =====
R2_PUBLIC_URL = os.environ.get("R2_PUBLIC_URL", "")
DOCS_DIR      = "docs"
DATES_JSON    = os.path.join(DOCS_DIR, "available_dates.json")

os.makedirs(DOCS_DIR, exist_ok=True)

# ===== 全サイトリスト =====
ALL_SITES = COMMON_SITES + UNCOMMON_SITES

# ===== ログ =====
def write_log(message):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {message}")

# ===== 利用可能日付リスト読み込み =====
if os.path.exists(DATES_JSON):
    with open(DATES_JSON, encoding="utf-8") as f:
        available_dates = json.load(f)
else:
    available_dates = []

# ===== data/以下からスロット一覧を取得 =====
def get_slots(date_key):
    date_dir = os.path.join("data", date_key)
    if not os.path.exists(date_dir):
        return []
    slots = sorted([
        d for d in os.listdir(date_dir)
        if os.path.isdir(os.path.join(date_dir, d)) and d.isdigit()
    ])
    return slots

# ===== サムネイルHTML生成 =====
def build_thumbnails(date_key, slot):
    html = ""
    for site in ALL_SITES:
        ss_name    = site["name"]
        thumb_url  = f"{R2_PUBLIC_URL}/{date_key}/{slot}/{date_key}_{ss_name}_thumb.png"
        full_url   = f"{R2_PUBLIC_URL}/{date_key}/{slot}/{date_key}_{ss_name}_full.png"
        html += f"""
        <div class="thumb-card" onclick="openModal('{full_url}')">
          <img src="{thumb_url}" alt="{ss_name}" loading="lazy"
               onerror="this.closest('.thumb-card').style.display='none'">
          <div class="thumb-label">{ss_name}</div>
        </div>"""
    return html

# ===== 1日分のHTML生成 =====
def generate_day_html(date_key):

    try:
        dt = datetime.strptime(date_key, "%Y%m%d")
        date_display = f"{dt.year}年{dt.month}月{dt.day}日"
    except Exception:
        date_display = date_key

    slots = get_slots(date_key)
    if not slots:
        write_log(f"{date_key}: スロットなし・スキップ")
        return

    # スロットタブHTML
    slot_tabs = ""
    slot_panels = ""
    for i, slot in enumerate(slots):
        active = "active" if i == 0 else ""
        slot_tabs += f'<button class="slot-tab {active}" onclick="switchSlot(\'{slot}\')" id="tab-{slot}">{slot[:2]}:{slot[2:]}</button>'
        thumbs = build_thumbnails(date_key, slot)
        display = "block" if i == 0 else "none"
        slot_panels += f'<div class="slot-panel" id="panel-{slot}" style="display:{display}"><div class="thumb-grid">{thumbs}</div></div>'

    # 前後日付
    idx       = available_dates.index(date_key) if date_key in available_dates else -1
    prev_date = available_dates[idx - 1] if idx > 0 else None
    next_date = available_dates[idx + 1] if idx >= 0 and idx < len(available_dates) - 1 else None

    prev_btn = f'<a class="nav-btn" href="{prev_date}.html">◀ 前の日</a>' if prev_date else '<span class="nav-btn disabled">◀ 前の日</span>'
    next_btn = f'<a class="nav-btn" href="{next_date}.html">次の日 ▶</a>' if next_date else '<span class="nav-btn disabled">次の日 ▶</span>'

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>あの日のトップページ - {date_display}</title>
</head>
<body>
<header>
  <h1>あの日のトップページ</h1>
  <p>web archive project</p>
</header>
<main>

  <div class="date-nav">
    {prev_btn}
    <span class="current-date">{date_display}</span>
    {next_btn}
  </div>

  <div class="calendar-wrap">
    <div class="calendar-header">
      <button onclick="calPrev()">◀</button>
      <span id="cal-label"></span>
      <button onclick="calNext()">▶</button>
    </div>
    <div class="calendar-grid" id="cal-grid"></div>
  </div>

  <div class="slot-tabs">{slot_tabs}</div>
  {slot_panels}

  <div class="meta">取得日: {date_display} ／ サイト数: {len(ALL_SITES)}</div>

</main>

<div class="modal" id="modal" onclick="closeModal(event)">
  <button class="modal-close" onclick="closeModalBtn()">✕</button>
  <img id="modal-img" src="" alt="">
</div>

<script>
  const CURRENT = "{date_key}";
  const DATES   = {json.dumps(sorted(available_dates))};

  function openModal(src) {{
    document.getElementById("modal-img").src = src;
    document.getElementById("modal").classList.add("open");
  }}
  function closeModal(e) {{ if (e.target === document.getElementById("modal")) closeModalBtn(); }}
  function closeModalBtn() {{
    document.getElementById("modal").classList.remove("open");
    document.getElementById("modal-img").src = "";
  }}
  document.addEventListener("keydown", e => {{ if (e.key === "Escape") closeModalBtn(); }});

  function switchSlot(slot) {{
    document.querySelectorAll(".slot-panel").forEach(p => p.style.display = "none");
    document.querySelectorAll(".slot-tab").forEach(t => t.classList.remove("active"));
    document.getElementById("panel-" + slot).style.display = "block";
    document.getElementById("tab-" + slot).classList.add("active");
  }}

  // カレンダー
  let calYear  = parseInt(CURRENT.slice(0,4));
  let calMonth = parseInt(CURRENT.slice(4,6)) - 1;
  const weekdays = ["日","月","火","水","木","金","土"];

  function renderCalendar() {{
    document.getElementById("cal-label").textContent = calYear + "年 " + (calMonth+1) + "月";
    const grid = document.getElementById("cal-grid");
    grid.innerHTML = "";
    weekdays.forEach(d => {{ const el = document.createElement("div"); el.className="cal-weekday"; el.textContent=d; grid.appendChild(el); }});
    const first = new Date(calYear, calMonth, 1).getDay();
    const days  = new Date(calYear, calMonth+1, 0).getDate();
    for (let i=0; i<first; i++) {{ const el=document.createElement("div"); el.className="cal-day empty"; grid.appendChild(el); }}
    for (let d=1; d<=days; d++) {{
      const key = calYear + String(calMonth+1).padStart(2,"0") + String(d).padStart(2,"0");
      const el  = document.createElement("div");
      el.textContent = d;
      if (key === CURRENT) {{ el.className="cal-day current"; }}
      else if (DATES.includes(key)) {{ el.className="cal-day"; el.onclick=()=>location.href=key+".html"; }}
      else {{ el.className="cal-day inactive"; }}
      grid.appendChild(el);
    }}
  }}
  function calPrev() {{ if(calMonth===0){{calYear--;calMonth=11;}}else{{calMonth--;}} renderCalendar(); }}
  function calNext() {{ if(calMonth===11){{calYear++;calMonth=0;}}else{{calMonth++;}} renderCalendar(); }}
  renderCalendar();
</script>
</body>
</html>"""

    out_path = os.path.join(DOCS_DIR, f"{date_key}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    write_log(f"HTML生成完了: {out_path}")

    if date_key not in available_dates:
        available_dates.append(date_key)


# ===== 全日付を処理 =====
def generate_html_all():
  data_dir = "data"
  date_dirs = sorted([
      d for d in os.listdir(data_dir)
      if os.path.isdir(os.path.join(data_dir, d)) and d.isdigit() and len(d) == 8
  ])

  for date_key in date_dirs:
      generate_day_html(date_key)

  # ===== available_dates.json更新 =====
  with open(DATES_JSON, "w", encoding="utf-8") as f:
      json.dump(sorted(available_dates), f, ensure_ascii=False, indent=2)
  write_log("available_dates.json 更新完了")

  # ===== index.html → 最新日にリダイレクト =====
  if available_dates:
      latest = sorted(available_dates)[-1]
      index_html = f"""<!DOCTYPE html>
  <html lang="ja">
  <head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url={latest}.html">
    <title>あの日のトップページ</title>
  </head>
  <body><p><a href="{latest}.html">最新の日付へ</a></p></body>
  </html>"""
      with open(os.path.join(DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
          f.write(index_html)
      write_log(f"index.html → {latest}.html")

  print("HTML生成完了")

if __name__ == "__main__":
    generate_html_all()