/* ==========================================================================
   Modern Digital Archive - Core Single Page Application Logic (Vanilla JS)
   ========================================================================== */

// App State
let appConfig = {
  r2PublicUrl: "",
  dates: {} // Format: { "YYYYMMDD": ["HHMM", ...] }
};

let activeState = {
  date: "", // YYYYMMDD
  slot: "", // HHMM
  sites: [], // List of sites in active slot
  searchQuery: "",
  modalActiveIndex: -1 // For screenshot lightbox navigation
};

let calendarState = {
  year: new Date().getFullYear(),
  month: new Date().getMonth() // 0-indexed
};

// DOM Elements
const el = {
  themeToggle: document.getElementById("theme-toggle"),
  searchBar: document.getElementById("search-bar"),
  calLabel: document.getElementById("cal-label"),
  calGrid: document.getElementById("cal-grid"),
  calPrev: document.getElementById("cal-prev"),
  calNext: document.getElementById("cal-next"),
  slotContainer: document.getElementById("slot-container"),
  activeDateStr: document.getElementById("active-date-str"),
  activeSlotBadge: document.getElementById("active-slot-badge"),
  archiveStats: document.getElementById("archive-stats"),
  cardsContainer: document.getElementById("cards-container"),
  loadingOverlay: document.getElementById("loading-overlay"),
  modal: document.getElementById("screenshot-modal"),
  modalImg: document.getElementById("modal-img"),
  modalCloseBtn: document.getElementById("modal-close-btn"),
  modalPrevBtn: document.getElementById("modal-prev-btn"),
  modalNextBtn: document.getElementById("modal-next-btn")
};

// ==========================================================================
// 1. Theme Configuration (Dark / Light Mode Toggle)
// ==========================================================================
function initTheme() {
  const savedTheme = localStorage.getItem("theme");
  const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  
  if (savedTheme === "dark" || (!savedTheme && systemPrefersDark)) {
    document.documentElement.setAttribute("data-theme", "dark");
    el.themeToggle.innerHTML = '<i class="fa-solid fa-sun"></i>';
  } else {
    document.documentElement.setAttribute("data-theme", "light");
    el.themeToggle.innerHTML = '<i class="fa-solid fa-moon"></i>';
  }
}

el.themeToggle.addEventListener("click", () => {
  const currentTheme = document.documentElement.getAttribute("data-theme");
  if (currentTheme === "dark") {
    document.documentElement.setAttribute("data-theme", "light");
    localStorage.setItem("theme", "light");
    el.themeToggle.innerHTML = '<i class="fa-solid fa-moon"></i>';
  } else {
    document.documentElement.setAttribute("data-theme", "dark");
    localStorage.setItem("theme", "dark");
    el.themeToggle.innerHTML = '<i class="fa-solid fa-sun"></i>';
  }
});

// ==========================================================================
// 2. Loading Overlay Control
// ==========================================================================
function showLoading(show) {
  if (show) {
    el.loadingOverlay.classList.add("active");
  } else {
    el.loadingOverlay.classList.remove("active");
  }
}

// ==========================================================================
// 3. Calendar Widget Rendering
// ==========================================================================
function renderCalendar() {
  const year = calendarState.year;
  const month = calendarState.month;
  
  // Update Header Label (e.g. "2026年 05月")
  el.calLabel.textContent = `${year}年 ${String(month + 1).padStart(2, "0")}月`;
  
  // Clear Grid
  el.calGrid.innerHTML = "";
  
  // Render Weekdays Header
  const weekdays = ["日", "月", "火", "水", "木", "金", "土"];
  weekdays.forEach(day => {
    const dayEl = document.createElement("div");
    dayEl.className = "cal-weekday";
    dayEl.textContent = day;
    el.calGrid.appendChild(dayEl);
  });
  
  // Calculate Days details
  const firstDayIndex = new Date(year, month, 1).getDay();
  const totalDays = new Date(year, month + 1, 0).getDate();
  
  // Render Empty blocks for padding before first day
  for (let i = 0; i < firstDayIndex; i++) {
    const emptyEl = document.createElement("div");
    emptyEl.className = "cal-day empty";
    el.calGrid.appendChild(emptyEl);
  }
  
  // Render Days of Month
  const todayStr = getTodayJSTString();
  for (let d = 1; d <= totalDays; d++) {
    const dayKey = `${year}${String(month + 1).padStart(2, "0")}${String(d).padStart(2, "0")}`;
    const dayEl = document.createElement("div");
    dayEl.textContent = d;
    dayEl.className = "cal-day";
    
    // Check if archive date exists
    if (appConfig.dates[dayKey]) {
      dayEl.classList.add("active-date");
      
      // Highlight currently selected date
      if (dayKey === activeState.date) {
        dayEl.classList.add("current-date");
      }
      
      // On click, select date
      dayEl.addEventListener("click", () => {
        selectDate(dayKey);
      });
    }
    
    el.calGrid.appendChild(dayEl);
  }
}

function getTodayJSTString() {
  // Simple offset conversion for basic comparison if needed
  const d = new Date();
  const utc = d.getTime() + (d.getTimezoneOffset() * 60000);
  const jstDate = new Date(utc + (3600000 * 9));
  const y = jstDate.getFullYear();
  const m = String(jstDate.getMonth() + 1).padStart(2, "0");
  const day = String(jstDate.getDate()).padStart(2, "0");
  return `${y}${m}${day}`;
}

// Calendar Navigate buttons
el.calPrev.addEventListener("click", () => {
  if (calendarState.month === 0) {
    calendarState.year--;
    calendarState.month = 11;
  } else {
    calendarState.month--;
  }
  renderCalendar();
});

el.calNext.addEventListener("click", () => {
  if (calendarState.month === 11) {
    calendarState.year++;
    calendarState.month = 0;
  } else {
    calendarState.month++;
  }
  renderCalendar();
});

// ==========================================================================
// 4. Slots Panel Rendering
// ==========================================================================
function renderSlots(dateKey) {
  el.slotContainer.innerHTML = "";
  const slots = appConfig.dates[dateKey] || [];
  
  if (slots.length === 0) {
    el.slotContainer.innerHTML = '<p style="color: var(--text-muted); font-size: 0.85rem;">取得スロットはありません</p>';
    return;
  }
  
  slots.forEach(slot => {
    const btn = document.createElement("button");
    btn.className = "btn-slot";
    if (slot === activeState.slot) btn.classList.add("active");
    
    // Format "1900" -> "19:00"
    const formattedTime = `${slot.slice(0, 2)}:${slot.slice(2, 4)}`;
    btn.innerHTML = `
      <span>${formattedTime}</span>
      <i class="fa-solid fa-chevron-right" style="font-size: 0.75rem; opacity: 0.7;"></i>
    `;
    
    btn.addEventListener("click", () => {
      selectSlot(slot);
    });
    
    el.slotContainer.appendChild(btn);
  });
}

// ==========================================================================
// 5. Card Grid Rendering & Search Filter
// ==========================================================================
function renderCards() {
  const container = el.cardsContainer;
  container.innerHTML = "";
  
  const query = activeState.searchQuery.toLowerCase().trim();
  
  // Filter sites by query
  const filteredSites = activeState.sites.filter(site => {
    if (!query) return true;
    const nameMatch = site.name.toLowerCase().includes(query);
    const urlMatch = site.url.toLowerCase().includes(query);
    const ocrMatch = site.ocr_text && site.ocr_text.toLowerCase().includes(query);
    return nameMatch || urlMatch || ocrMatch;
  });
  
  if (filteredSites.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 48px; color: var(--text-muted);">
        <i class="fa-solid fa-magnifying-glass" style="font-size: 3rem; margin-bottom: 16px;"></i>
        <p>該当するサイトは見つかりませんでした。</p>
      </div>
    `;
    return;
  }
  
  filteredSites.forEach((site, index) => {
    const card = document.createElement("div");
    card.className = "archive-card";
    
    // R2 URLs for Assets
    const baseUrl = `${appConfig.r2PublicUrl}/${activeState.date}/${activeState.slot}`;
    const thumbUrl = `${baseUrl}/${activeState.date}_${site.name}_thumb.png`;
    const fullUrl = `${baseUrl}/${activeState.date}_${site.name}_full.png`;
    const htmlUrl = `${baseUrl}/${activeState.date}_${site.name}.html`;
    
    // Find index of this site in main activeState.sites array (for lightbox ordering)
    const originalIndex = activeState.sites.indexOf(site);
    
    card.innerHTML = `
      <div class="card-image-wrap" id="card-img-${index}">
        <img src="${thumbUrl}" alt="${site.name}のスクリーンショット" loading="lazy" 
             onerror="this.closest('.archive-card').style.display='none';">
        <span class="card-badge-lang">${site.lang}</span>
      </div>
      <div class="card-body">
        <h3 class="card-title">${site.name}</h3>
        <a href="${site.url}" target="_blank" rel="noopener noreferrer" class="card-url-link" title="元のサイトを開く">
          <i class="fa-solid fa-link"></i> ${site.url}
        </a>
        
        <div class="card-actions">
          ${site.has_screenshot ? `<button class="btn-card btn-card-primary" id="btn-view-ss-${index}"><i class="fa-solid fa-image"></i> スクショを表示</button>` : ""}
          ${site.has_html ? `<a href="${htmlUrl}" target="_blank" rel="noopener noreferrer" class="btn-card"><i class="fa-solid fa-code"></i> 保存HTML</a>` : ""}
          ${site.ocr_text ? `<button class="btn-card" id="btn-toggle-ocr-${index}"><i class="fa-solid fa-file-lines"></i> OCR表示</button>` : ""}
        </div>
      </div>
      
      ${site.ocr_text ? `
        <div class="card-ocr-expand" id="ocr-box-${index}">
          <h4>抽出テキスト (OCR)</h4>
          <div class="ocr-text-box">${escapeHTML(site.ocr_text)}</div>
        </div>
      ` : ""}
    `;
    
    // Add Click listener to Image and SS button to trigger Lightbox
    const triggerLightbox = () => {
      openLightbox(originalIndex);
    };
    
    const imgWrap = card.querySelector(`#card-img-${index}`);
    if (imgWrap) imgWrap.addEventListener("click", triggerLightbox);
    
    const ssBtn = card.querySelector(`#btn-view-ss-${index}`);
    if (ssBtn) ssBtn.addEventListener("click", triggerLightbox);
    
    // Add Click listener to OCR Toggle
    const ocrBtn = card.querySelector(`#btn-toggle-ocr-${index}`);
    const ocrBox = card.querySelector(`#ocr-box-${index}`);
    if (ocrBtn && ocrBox) {
      ocrBtn.addEventListener("click", () => {
        ocrBox.classList.toggle("open");
        ocrBtn.classList.toggle("active");
        if (ocrBox.classList.contains("open")) {
          ocrBtn.innerHTML = '<i class="fa-solid fa-chevron-up"></i> 閉じる';
        } else {
          ocrBtn.innerHTML = '<i class="fa-solid fa-file-lines"></i> OCR表示';
        }
      });
    }
    
    container.appendChild(card);
  });
}

function escapeHTML(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Search Input Listener
el.searchBar.addEventListener("input", (e) => {
  activeState.searchQuery = e.target.value;
  renderCards();
});

// ==========================================================================
// 6. Navigation and Loading Logic
// ==========================================================================
async function loadConfigAndInit() {
  showLoading(true);
  try {
    // Fetch available_dates.json config from docs directory
    const response = await fetch("available_dates.json");
    if (!response.ok) {
      throw new Error(`Failed to load date config. Status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Handle both old flat array and new nested object formats
    if (Array.isArray(data)) {
      appConfig.r2PublicUrl = ""; // fallback
      appConfig.dates = {};
      data.forEach(d => {
        appConfig.dates[d] = ["2215"]; // default slot fallback
      });
    } else {
      appConfig.r2PublicUrl = data.r2_public_url || "";
      appConfig.dates = data.dates || {};
    }
    
    // Determine initially selected date (from hash or latest)
    let initialDate = "";
    const hash = window.location.hash.substring(1);
    if (hash && appConfig.dates[hash]) {
      initialDate = hash;
    } else {
      const allDates = Object.keys(appConfig.dates).sort();
      if (allDates.length > 0) {
        initialDate = allDates[allDates.length - 1]; // latest
      }
    }
    
    if (initialDate) {
      // Set calendar viewing to matches selected date
      calendarState.year = parseInt(initialDate.slice(0, 4));
      calendarState.month = parseInt(initialDate.slice(4, 6)) - 1;
      
      await selectDate(initialDate, false); // select without reloading config
    } else {
      renderCalendar();
      showLoading(false);
    }
    
  } catch (error) {
    showLoading(false);
    console.error("Config initialization failed:", error);
    el.cardsContainer.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 48px; color: #dc2626;">
        <i class="fa-solid fa-circle-exclamation" style="font-size: 3rem; margin-bottom: 16px;"></i>
        <p>初期化エラー: 設定ファイル (available_dates.json) の読み込みに失敗しました。</p>
        <p style="font-size: 0.8rem; margin-top: 8px;">${error.message}</p>
      </div>
    `;
  }
}

async function selectDate(dateKey, refreshCalendar = true) {
  activeState.date = dateKey;
  
  // Set default slot (first one available)
  const slots = appConfig.dates[dateKey] || [];
  activeState.slot = slots.length > 0 ? slots[0] : "";
  
  // Update URL Hash without trigger window.onhashchange listener loop
  history.replaceState(null, null, `#${dateKey}`);
  
  // Refresh Calendar UI highlight
  if (refreshCalendar) {
    renderCalendar();
  }
  
  // Render Slot selector
  renderSlots(dateKey);
  
  // Fetch details for slot
  if (activeState.slot) {
    await fetchSlotMetadata(dateKey, activeState.slot);
  } else {
    clearDetails();
  }
}

async function selectSlot(slotKey) {
  activeState.slot = slotKey;
  
  // Update active state in Slot buttons list
  document.querySelectorAll(".btn-slot").forEach(btn => {
    btn.classList.remove("active");
  });
  renderSlots(activeState.date);
  
  // Fetch details for selected slot
  await fetchSlotMetadata(activeState.date, slotKey);
}

const FALLBACK_SITE_NAMES = [
  "yahoo","msn", "bing", "yahoo_realtime", "nikkei", "nikkei_marketdata", "weathernews", "tenkijp",
  "hatena", "note", "oricon", "qiita", "nikoniko",
  "eigacom", "booklog", "reuters", "afpbb", "amazon",
  "zozo", "uniqlo", "seveneleven", "lawson", "takashimaya", "maruetsu",
  "yodobashi", "rakuten", "mercari", "rikunabi_tokyo", "rikunabi_osaka",
  "mynavi_tokyo", "mynavi_osaka",
  "go_kantei",  "gov-online","go_cao", "go_digital", "go_mhlw", "go_mof",
  "google", "reddit", "chatgpt", "gemini", "claude"   
];

async function fetchSlotMetadata(dateKey, slotKey) {
  showLoading(true);
  try {
    const metaUrl = `${appConfig.r2PublicUrl}/${dateKey}/${slotKey}/metadata.json`;
    const response = await fetch(metaUrl);
    
    if (!response.ok) {
      throw new Error(`R2 metadata file loading failed: ${response.status}`);
    }
    
    const metadata = await response.json();
    activeState.sites = metadata.sites || [];
    
    // Update Banner Details
    const y = dateKey.slice(0, 4);
    const m = parseInt(dateKey.slice(4, 6));
    const d = parseInt(dateKey.slice(6, 8));
    el.activeDateStr.textContent = `${y}年${m}月${d}日`;
    
    const formattedTime = `${slotKey.slice(0, 2)}:${slotKey.slice(2, 4)}`;
    el.activeSlotBadge.textContent = formattedTime;
    el.activeSlotBadge.style.display = "inline-block";
    el.archiveStats.textContent = `取得サイト数: ${activeState.sites.length}件`;
    
    // Clear search query
    el.searchBar.value = "";
    activeState.searchQuery = "";
    
    // Render Card Grid
    renderCards();
    showLoading(false);
  } catch (error) {
    console.warn("Metadata file not found, using fallback site structure:", error);
    
    // Fallback: build basic structures from fallback list (for backward compatibility)
    activeState.sites = FALLBACK_SITE_NAMES.map(name => {
      const isEng = ["google", "reddit", "chatgpt", "gemini", "claude"].includes(name);
      return {
        name: name,
        url: "",
        lang: isEng ? "eng" : "jpn",
        ocr_text: "",
        has_screenshot: true,
        has_html: false
      };
    });
    
    // Update Banner Details
    const y = dateKey.slice(0, 4);
    const m = parseInt(dateKey.slice(4, 6));
    const d = parseInt(dateKey.slice(6, 8));
    el.activeDateStr.textContent = `${y}年${m}月${d}日`;
    
    const formattedTime = `${slotKey.slice(0, 2)}:${slotKey.slice(2, 4)}`;
    el.activeSlotBadge.textContent = formattedTime;
    el.activeSlotBadge.style.display = "inline-block";
    el.archiveStats.textContent = "過去のアーカイブ（互換表示モード）";
    
    // Clear search query
    el.searchBar.value = "";
    activeState.searchQuery = "";
    
    // Render Card Grid
    renderCards();
    showLoading(false);
  }
}

function clearDetails() {
  activeState.sites = [];
  el.activeDateStr.textContent = "日付未選択";
  el.activeSlotBadge.style.display = "none";
  el.archiveStats.textContent = "表示可能なアーカイブはありません";
  el.cardsContainer.innerHTML = `
    <div style="grid-column: 1/-1; text-align: center; padding: 48px; color: var(--text-muted);">
      <i class="fa-solid fa-box-open" style="font-size: 3rem; margin-bottom: 16px;"></i>
      <p>表示可能なスロットデータがありません。</p>
    </div>
  `;
}

// Watch hash change
window.addEventListener("hashchange", () => {
  const hash = window.location.hash.substring(1);
  if (hash && appConfig.dates[hash] && hash !== activeState.date) {
    calendarState.year = parseInt(hash.slice(0, 4));
    calendarState.month = parseInt(hash.slice(4, 6)) - 1;
    selectDate(hash);
  }
});

// ==========================================================================
// 7. Lightbox Modal Navigation (Zoom Screen View)
// ==========================================================================
function openLightbox(index) {
  activeState.modalActiveIndex = index;
  updateLightboxContent();
  el.modal.classList.add("open");
  document.body.style.overflow = "hidden"; // Prevent body scroll
}

function closeLightbox() {
  el.modal.classList.remove("open");
  el.modalImg.src = "";
  activeState.modalActiveIndex = -1;
  document.body.style.overflow = ""; // Enable body scroll
}

function updateLightboxContent() {
  const idx = activeState.modalActiveIndex;
  const site = activeState.sites[idx];
  if (!site) return;
  
  const baseUrl = `${appConfig.r2PublicUrl}/${activeState.date}/${activeState.slot}`;
  const fullUrl = `${baseUrl}/${activeState.date}_${site.name}_full.png`;
  
  showLoading(true);
  el.modalImg.onload = () => {
    showLoading(false);
  };
  el.modalImg.onerror = () => {
    showLoading(false);
    el.modalImg.src = "https://placehold.co/800x600/e2e8f0/64748b?text=Image+Load+Failed";
  };
  el.modalImg.src = fullUrl;
}

function navigateLightbox(direction) {
  const siteCount = activeState.sites.length;
  if (siteCount <= 1) return;
  
  // Find next index that has screenshot
  let nextIdx = activeState.modalActiveIndex;
  let attempts = 0;
  
  do {
    nextIdx = (nextIdx + direction + siteCount) % siteCount;
    attempts++;
  } while (!activeState.sites[nextIdx].has_screenshot && attempts < siteCount);
  
  if (activeState.sites[nextIdx].has_screenshot) {
    activeState.modalActiveIndex = nextIdx;
    updateLightboxContent();
  }
}

// Lightbox Listeners
el.modalCloseBtn.addEventListener("click", closeLightbox);
el.modalPrevBtn.addEventListener("click", () => navigateLightbox(-1));
el.modalNextBtn.addEventListener("click", () => navigateLightbox(1));

// Close modal when click background
el.modal.addEventListener("click", (e) => {
  if (e.target === el.modal || e.target.classList.contains("modal-content-wrap")) {
    closeLightbox();
  }
});

// Keyboard Accessibility
document.addEventListener("keydown", (e) => {
  if (!el.modal.classList.contains("open")) return;
  
  if (e.key === "Escape") {
    closeLightbox();
  } else if (e.key === "ArrowLeft") {
    navigateLightbox(-1);
  } else if (e.key === "ArrowRight") {
    navigateLightbox(1);
  }
});

// ==========================================================================
// 8. Application Bootstrap
// ==========================================================================
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  loadConfigAndInit();
});


// べた書きを削除して、初期化時に設定
document.getElementById("cal-label").textContent =
  calYear + "年 " + String(calMonth + 1).padStart(2, "0") + "月";