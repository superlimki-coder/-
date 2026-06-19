import json
import math
import uuid
from datetime import datetime, timezone, timedelta
import requests
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="견적계산기",
    page_icon="🧾",
    layout="wide",
)

st.markdown(
    """
<style>
/* ── 기본 베이스 (70대도 읽기 편한 크기) ── */
html, body, [class*="css"] {
    font-size: 17px !important;
}

/* ── 레이아웃 ── */
.stApp, body, html,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    color: #111827 !important;
}
.block-container {
    background-color: #ffffff !important;
}
.main .block-container {
    max-width: 1800px !important;
    padding-left: 20px !important;
    padding-right: 20px !important;
}

/* ── 모바일 화면 꽉 채우기 ── */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: 8px !important;
        padding-right: 8px !important;
        padding-top: 8px !important;
        max-width: 100vw !important;
    }
    /* 상단 헤더 여백 제거 */
    [data-testid="stAppViewContainer"] {
        padding-top: 0 !important;
    }
    /* 사이드 여백 최소화 */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    /* 헤더 높이 줄이기 */
    [data-testid="stHeader"] {
        min-height: 0 !important;
    }
}

/* ── 라벨 ── */
label {
    font-size: 16px !important;
    font-weight: 700 !important;
}

/* ── input / textarea ── */
input, textarea {
    font-size: 17px !important;
    font-weight: 600 !important;
    background-color: #f8fafc !important;
    color: #111827 !important;
}
div[data-baseweb="input"] {
    background-color: #f8fafc !important;
    color: #111827 !important;
}
[data-testid="stNumberInput"] {
    min-width: 0 !important;
}

/* ── 셀렉트박스 ── */
div[data-baseweb="select"] > div {
    background-color: #f8fafc !important;
    color: #111827 !important;
    font-size: 16px !important;
    font-weight: 600 !important;
}
div[data-baseweb="select"] div {
    font-size: 16px !important;
    font-weight: 600 !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
}
div[data-baseweb="select"] input {
    font-size: 16px !important;
}

/* ── 드롭다운 메뉴 ── */
div[data-baseweb="popover"],
div[data-baseweb="popover"] div,
div[data-baseweb="menu"],
ul[role="listbox"],
li[role="option"] {
    background-color: #ffffff !important;
    color: #111827 !important;
}
li[role="option"] div,
li[role="option"] span {
    background-color: #ffffff !important;
    color: #111827 !important;
    font-size: 16px !important;
    font-weight: 600 !important;
}
li[aria-selected="true"],
li[role="option"]:hover,
li[role="option"][aria-selected="true"] {
    background-color: #f3f4f6 !important;
    color: #111827 !important;
}
[data-baseweb="select"] [role="listbox"],
[data-baseweb="select"] [role="option"],
[data-baseweb="select"] ul,
[data-baseweb="select"] li {
    background-color: #ffffff !important;
    color: #111827 !important;
}

/* ── 버튼 ── */
button {
    font-size: 16px !important;
    font-weight: 700 !important;
}
div[data-testid="stButton"] button {
    min-height: 46px !important;
}
.stDownloadButton button {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 2px solid #d1d5db !important;
    font-size: 16px !important;
}

/* ── 헤딩 ── */
h3 {
    font-size: 20px !important;
    font-weight: 800 !important;
}

/* ── 메트릭 ── */
[data-testid="stMetricValue"] {
    font-size: 26px !important;
    font-weight: 800 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 15px !important;
    font-weight: 700 !important;
}

/* ── 텍스트 색상 ── */
p, span, div, h1, h2, h3, h4, h5, h6, label {
    color: #111827 !important;
}

/* ── 커스텀 테이블 ── */
.custom-table {
    width: 100%;
    border-collapse: collapse;
    background-color: #ffffff !important;
    color: #111827 !important;
    font-size: 15px !important;
    border: 1px solid #d1d5db;
}
.custom-table th {
    background-color: #f3f4f6 !important;
    color: #111827 !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    padding: 10px 12px;
    border: 1px solid #d1d5db;
    text-align: left;
}
.custom-table td {
    background-color: #ffffff !important;
    color: #111827 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    padding: 10px 12px;
    border: 1px solid #d1d5db;
    text-align: left;
    word-break: keep-all;
    white-space: normal;
}

/* ── 발주서 목록 행 ── */
.order-header div,
.order-row div {
    font-size: 15px !important;
    line-height: 1.4 !important;
}
.order-row .item-main {
    font-size: 16px !important;
    font-weight: 800 !important;
    line-height: 1.4 !important;
}
.order-row .item-sub {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #6b7280 !important;
    line-height: 1.3 !important;
}
.order-row .num-cell {
    font-size: 15px !important;
    font-weight: 800 !important;
    text-align: right !important;
}
.order-row .total-cell {
    font-size: 16px !important;
    font-weight: 900 !important;
    text-align: right !important;
}

/* ── 탭 메뉴 글씨 크기 ── */
button[data-baseweb="tab"] {
    font-size: 17px !important;
    font-weight: 700 !important;
    padding: 12px 16px !important;
}
button[data-baseweb="tab"] p {
    font-size: 17px !important;
    font-weight: 700 !important;
}
[data-testid="stTabBar"] {
    gap: 2px !important;
}

/* ── 기타 ── */
div[data-testid="stVerticalBlock"] > div:has(h3) {
    margin-top: 0.3rem;
}
@media (max-width: 900px) {
    div[style*="grid-template-columns: repeat(5, 1fr)"] {
        grid-template-columns: 1fr !important;
    }
}
@media (max-width: 600px) {
    html, body, [class*="css"] { font-size: 17px !important; }
    label { font-size: 16px !important; }
    h3 { font-size: 19px !important; }
    [data-testid="stMetricValue"] { font-size: 24px !important; }
    [data-testid="stMetricLabel"] { font-size: 14px !important; }
    button { font-size: 16px !important; }
    input, textarea { font-size: 17px !important; }
    div[data-baseweb="select"] div { font-size: 16px !important; }
    .custom-table, .custom-table th, .custom-table td { font-size: 14px !important; padding: 8px !important; }
    /* 모바일 컬럼 가로 강제 유지 */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 4px !important;
    }
    [data-testid="stHorizontalBlock"] > div {
        min-width: 0 !important;
        flex-shrink: 1 !important;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

components.html(
    """
    <script>
    // 모바일 핀치줌 강제 허용
    (function fixViewport(){
        try {
            var doc = window.parent.document;
            // 기존 viewport meta 제거 후 재생성
            var old = doc.querySelector('meta[name="viewport"]');
            if(old) old.parentNode.removeChild(old);
            var m = doc.createElement('meta');
            m.name = 'viewport';
            m.content = 'width=device-width, initial-scale=1.0, maximum-scale=5.0, minimum-scale=1.0, user-scalable=yes';
            doc.head.appendChild(m);
        } catch(e){}
        // Streamlit이 다시 덮어쓸 수 있으므로 반복 적용
        setTimeout(fixViewport, 500);
        setTimeout(fixViewport, 1500);
        setTimeout(fixViewport, 3000);
    })();
    function attachSelectAll(){
        const doc = window.parent.document;
        const inputs = doc.querySelectorAll('input');
        inputs.forEach(function(input){
            if (input.dataset.selectAllAttached === "1") return;
            input.dataset.selectAllAttached = "1";
            input.addEventListener('focus', function(){
                setTimeout(function(){ input.select(); }, 20);
            });
            input.addEventListener('click', function(){
                setTimeout(function(){ input.select(); }, 20);
            });
        });
    }
    attachSelectAll();
    setInterval(attachSelectAll, 1000);
    </script>
    """,
    height=0,
)

# ──────────────────────────────────────────
# 한국 시간 (KST = UTC+9)
# ──────────────────────────────────────────

KST = timezone(timedelta(hours=9))

def now_kst():
    """현재 한국 시간 반환"""
    return datetime.now(KST)

def today_kst():
    """오늘 한국 날짜 반환"""
    return datetime.now(KST).date()


# ──────────────────────────────────────────
# 기본 데이터
# ──────────────────────────────────────────

MATERIALS = {
    "HDPE": {"density": 0.92, "extrusion": 600, "raw_price": 1600},
    "LDPE": {"density": 0.92, "extrusion": 600, "raw_price": 1650},
    "생분해": {"density": 1.10, "extrusion": 600, "raw_price": 3300},
    "PP": {"density": 0.90, "extrusion": 700, "raw_price": 1600},
}

PLATE_COST_LENGTH_TABLE = [
    (0, 13.4, 4.0),
    (13.4, 20, 3.0),
    (20, 40, 2.0),
    (40, 150, 1.0),
]

# ──────────────────────────────────────────
# Supabase 설정
# ──────────────────────────────────────────

SUPABASE_URL = "https://zdzvynatkpwdtfbobyew.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpkenZ5bmF0a3B3ZHRmYm9ieWV3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE3NzQxMDUsImV4cCI6MjA5NzM1MDEwNX0.QbxqlP6Y_fm-ePYa5nYF95MrQTKmM6KBZeB-gXkds-c"
SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_get(table, params=None):
    """Supabase에서 데이터 조회"""
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/{table}",
                         headers=SB_HEADERS, params=params, timeout=10)
        return r.json() if r.ok else []
    except Exception:
        return []

def sb_upsert(table, data):
    """Supabase에 데이터 삽입/업데이트"""
    try:
        headers = {**SB_HEADERS, "Prefer": "resolution=merge-duplicates,return=representation"}
        r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}",
                          headers=headers, json=data if isinstance(data, list) else [data], timeout=10)
        return r.ok
    except Exception:
        return False

def sb_delete(table, eq_col, eq_val):
    """Supabase에서 데이터 삭제"""
    try:
        r = requests.delete(f"{SUPABASE_URL}/rest/v1/{table}",
                            headers=SB_HEADERS,
                            params={eq_col: f"eq.{eq_val}"}, timeout=10)
        return r.ok
    except Exception:
        return False

def sb_patch(table, eq_col, eq_val, data):
    """Supabase 특정 행 업데이트"""
    try:
        r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}",
                           headers=SB_HEADERS,
                           params={eq_col: f"eq.{eq_val}"},
                           json=data, timeout=10)
        return r.ok
    except Exception:
        return False

DEFAULT_SUPPLIER = {
    "id": "default",
    "profile_name": "(주)대봉 기본",
    "supplier_name": "(주)대봉",
    "business_no": "231-81-02595",
    "ceo_name": "임권일",
    "supplier_manager": "",
    "supplier_address": "경기도 포천시 가산면 포천로912번길 175",
    "business_type": "제조업 도소매",
    "business_item": "합성수지",
    "supplier_tel": "031-544-0051",
    "supplier_fax": "010.6613.0051",
}

# ──────────────────────────────────────────
# 발주서 저장 / 불러오기
# ──────────────────────────────────────────

# ──────────────────────────────────────────
# 발주서 (Supabase)
# ──────────────────────────────────────────

@st.cache_data(ttl=300)
def load_orders():
    rows = sb_get("orders", {"select": "id,data", "order": "id.desc"})
    return [r["data"] for r in rows if r.get("data")]

def save_orders(orders):
    pass  # upsert_order / delete_order 로 개별 처리

def upsert_order(order):
    sb_upsert("orders", {"id": order["id"], "data": order})
    st.cache_data.clear()

def delete_order(order_id):
    sb_delete("orders", "id", order_id)
    st.cache_data.clear()

def load_order_to_session(order):
    for k, v in order.items():
        st.session_state[k] = v
    st.session_state["loaded_order_id"] = order.get("id")

def get_default(key, default):
    return st.session_state.get(key, default)

# ──────────────────────────────────────────
# 출고일지 (Supabase)
# ──────────────────────────────────────────

@st.cache_data(ttl=30)
def load_delivery_logs():
    rows = sb_get("delivery_logs", {"select": "*", "order": "date.desc,saved_at.desc"})
    return rows if rows else []

def save_delivery_logs(logs):
    pass  # 개별 append/delete로 처리

def append_delivery_log(log):
    sb_upsert("delivery_logs", log)
    st.cache_data.clear()

def update_delivery_log(log_id, data):
    sb_patch("delivery_logs", "id", log_id, data)
    st.cache_data.clear()

def delete_delivery_log(log_id):
    sb_delete("delivery_logs", "id", log_id)
    st.cache_data.clear()

# ──────────────────────────────────────────
# 기사 (Supabase)
# ──────────────────────────────────────────

@st.cache_data(ttl=600)
def load_drivers():
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/drivers",
            headers=SB_HEADERS,
            params={"select": "name", "order": "name.asc"},
            timeout=10,
        )
        if r.ok:
            return [row["name"] for row in r.json()]
        else:
            st.error(f"기사 목록 오류: {r.status_code} - {r.text[:100]}")
            return []
    except Exception as e:
        st.error(f"기사 목록 연결 오류: {e}")
        return []

def save_drivers(drivers):
    pass  # add/delete 개별 처리

def add_driver(name):
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/drivers",
            headers={**SB_HEADERS, "Prefer": "return=representation"},
            json={"name": name},
            timeout=10,
        )
        return r.ok
    except Exception:
        return False

def remove_driver(name):
    try:
        r = requests.delete(
            f"{SUPABASE_URL}/rest/v1/drivers",
            headers=SB_HEADERS,
            params={"name": f"eq.{name}"},
            timeout=10,
        )
        return r.ok
    except Exception:
        return False

def rename_driver(old_name, new_name):
    try:
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/drivers",
            headers=SB_HEADERS,
            params={"name": f"eq.{old_name}"},
            json={"name": new_name},
            timeout=10,
        )
        return r.ok
    except Exception:
        return False

# ──────────────────────────────────────────
# 거래처별 품목 (Supabase)
# ──────────────────────────────────────────

@st.cache_data(ttl=300)
def load_items():
    rows = sb_get("items", {"select": "*", "order": "updated_at.desc"})
    result = {}
    for r in rows:
        c = r.get("customer","")
        if c not in result:
            result[c] = []
        result[c].append({"name": r.get("name",""), "size": r.get("size",""), "qty": r.get("qty",0)})
    return result

def save_items(items):
    pass

def upsert_item(customer, item_name, item_size="", qty=0):
    if not customer.strip() or not item_name.strip():
        return
    # 기존 동일 품목 삭제 후 재삽입
    rows = sb_get("items", {"customer": f"eq.{customer}", "name": f"eq.{item_name}", "size": f"eq.{item_size}"})
    if rows:
        sb_delete("items", "id", rows[0]["id"])
    sb_upsert("items", {
        "customer": customer.strip(),
        "name": item_name.strip(),
        "size": item_size.strip(),
        "qty": int(qty),
        "updated_at": now_kst().strftime("%Y-%m-%d %H:%M:%S"),
    })

def delete_item(customer, item_name, item_size=""):
    rows = sb_get("items", {"customer": f"eq.{customer}", "name": f"eq.{item_name}", "size": f"eq.{item_size}"})
    for r in rows:
        sb_delete("items", "id", r["id"])

def get_customer_items(customer):
    rows = sb_get("items", {"customer": f"eq.{customer}", "select": "*", "order": "updated_at.desc", "limit": "20"})
    return [{"name": r.get("name",""), "size": r.get("size",""), "qty": r.get("qty",0)} for r in rows]

# ──────────────────────────────────────────
# 공급자 프로필 (Supabase)
# ──────────────────────────────────────────

@st.cache_data(ttl=300)
def load_suppliers():
    rows = sb_get("suppliers", {"select": "id,data"})
    result = [r["data"] for r in rows if r.get("data")]
    return result if result else [DEFAULT_SUPPLIER]

def save_suppliers(suppliers):
    pass

def upsert_supplier(supplier):
    sb_upsert("suppliers", {"id": supplier["id"], "data": supplier})

def delete_supplier(supplier_id):
    sb_delete("suppliers", "id", supplier_id)

# ──────────────────────────────────────────
# 최근 원료값 (Supabase)
# ──────────────────────────────────────────

@st.cache_data(ttl=300)
def load_last_raw_price():
    rows = sb_get("settings", {"key": "eq.raw_price", "select": "value"})
    if rows:
        try:
            return int(rows[0]["value"])
        except Exception:
            pass
    return 0

def save_last_raw_price(value):
    sb_upsert("settings", {"key": "raw_price", "value": str(int(value))})

# ──────────────────────────────────────────
# 거래처 (Supabase)
# ──────────────────────────────────────────

@st.cache_data(ttl=300)
def load_customers():
    rows = sb_get("customers", {"select": "*", "order": "company.asc"})
    return rows if rows else []

def save_customers(customers):
    pass

def upsert_customer(customer):
    sb_upsert("customers", customer)
    st.cache_data.clear()

def delete_customer(customer_id):
    sb_delete("customers", "id", customer_id)
    st.cache_data.clear()

# ──────────────────────────────────────────
# 유틸 함수
# ──────────────────────────────────────────

def lookup_factor(value, table, default=0):
    for low, high, factor in table:
        if value >= low and value < high:
            return factor
    return default

def roundup(value, digits=0):
    factor = 10**digits
    if digits >= 0:
        return math.ceil(value * factor) / factor
    factor = 10 ** (-digits)
    return math.ceil(value / factor) * factor

def rounddown(value, digits=0):
    factor = 10**digits
    if digits >= 0:
        return math.floor(value * factor) / factor
    factor = 10 ** (-digits)
    return math.floor(value / factor) * factor

def ceiling(value, significance=1):
    if significance == 0:
        return value
    return math.ceil(value / significance) * significance

def make_m_text(m_gusset_cm):
    return f"(M{m_gusset_cm:g})" if m_gusset_cm > 0 else ""

def show_white_table(df):
    html = df.to_html(index=False, escape=False, classes="custom-table")
    st.markdown(html, unsafe_allow_html=True)

def fmt_won(value, decimals=0):
    if decimals == 0:
        return f"{value:,.0f}"
    return f"{value:,.{decimals}f}"

def calc_quote(
    bag_type, thickness_um, roll_width_cm, m_gusset_cm, process_length_cm,
    roll_length_m, print_count_display, manual_print_cost_500m,
    manual_open_processing_cost_500m, adhesive_processing_cost_per_cm_ea,
    extra_processing_cost_500m, margin_percent, roll_count, manual_production_qty,
    raw_price, extrusion_cost, density,
):
    total_width_m = roll_width_cm / 100
    thickness_mm = thickness_um / 1000
    m_text = make_m_text(m_gusset_cm)

    actual_size_text = f"{thickness_mm:.3f} × {roll_width_cm:g}{m_text} × {process_length_cm:g}cm"
    roll_spec_text = f"{thickness_mm:.3f} × {roll_width_cm:g}{m_text} × {roll_length_m:g}m"

    weight_500m = density * (thickness_um * 0.001) * roll_width_cm * 500 * 2 / 100
    weight_roll = density * (thickness_um * 0.001) * roll_width_cm * roll_length_m * 2 / 100

    fabric_cost_500m = (raw_price + extrusion_cost) * weight_500m
    fabric_cost_roll = (raw_price + extrusion_cost) * weight_roll

    print_cost_500m = manual_print_cost_500m
    open_process_cost_500m = manual_open_processing_cost_500m
    adhesive_process_cost_ea = (
        process_length_cm * adhesive_processing_cost_per_cm_ea if bag_type == "택배봉투" else 0
    )

    plate_length_factor = lookup_factor(process_length_cm, PLATE_COST_LENGTH_TABLE)
    effective_width_for_plate = (
        (roll_width_cm - (m_gusset_cm * 2)) + 4
        if (roll_width_cm - (m_gusset_cm * 2)) >= 36
        else 40
    )
    plate_cost_per_color = roundup(
        process_length_cm * plate_length_factor * effective_width_for_plate * 50, -4
    )
    plate_cost_total = plate_cost_per_color * print_count_display

    open_before_500m = fabric_cost_500m + open_process_cost_500m + print_cost_500m + extra_processing_cost_500m
    adhesive_before_500m = fabric_cost_500m + print_cost_500m + extra_processing_cost_500m

    process_count_500m = rounddown(50000 / process_length_cm, -1) if process_length_cm else 0

    open_unit_cost = open_before_500m / process_count_500m if process_count_500m else 0
    adhesive_unit_cost = (
        (adhesive_before_500m / process_count_500m + adhesive_process_cost_ea)
        if process_count_500m else 0
    )

    open_bag_cost = roundup(open_unit_cost * 1.05, 2)
    adhesive_bag_cost = roundup(adhesive_unit_cost * 1.05, 2)

    selected_base = open_bag_cost if bag_type == "오픈봉투" else adhesive_bag_cost
    unit_quote = ceiling(selected_base * (1 + margin_percent / 100), 0.5)

    qty_per_roll = (
        rounddown((roll_length_m * 100) / process_length_cm, -2) if process_length_cm else 0
    )
    auto_production_qty = int(qty_per_roll * roll_count)
    production_qty = int(manual_production_qty) if manual_production_qty > 0 else auto_production_qty

    fabric_quote_per_roll = roundup(
        (fabric_cost_roll + (print_cost_500m * roll_length_m / 500)) * (1 + margin_percent / 100), -3,
    )

    supply_amount = unit_quote * production_qty
    vat_amount = supply_amount * 0.10
    total_with_vat = supply_amount + vat_amount + plate_cost_total
    total_amount = supply_amount + plate_cost_total

    return {
        "total_width_m": total_width_m,
        "actual_size_text": actual_size_text,
        "roll_spec_text": roll_spec_text,
        "weight_500m": weight_500m,
        "weight_roll": weight_roll,
        "fabric_cost_500m": fabric_cost_500m,
        "fabric_cost_roll": fabric_cost_roll,
        "fabric_quote_per_roll": fabric_quote_per_roll,
        "print_cost_500m": print_cost_500m,
        "open_process_cost_500m": open_process_cost_500m,
        "adhesive_process_cost_ea": adhesive_process_cost_ea,
        "extra_processing_cost_500m": extra_processing_cost_500m,
        "plate_cost_per_color": plate_cost_per_color,
        "plate_cost_total": plate_cost_total,
        "open_before_500m": open_before_500m,
        "adhesive_before_500m": adhesive_before_500m,
        "process_count_500m": process_count_500m,
        "open_unit_cost": open_unit_cost,
        "adhesive_unit_cost": adhesive_unit_cost,
        "open_bag_cost": open_bag_cost,
        "adhesive_bag_cost": adhesive_bag_cost,
        "unit_quote": unit_quote,
        "qty_per_roll": qty_per_roll,
        "auto_production_qty": auto_production_qty,
        "production_qty": production_qty,
        "supply_amount": supply_amount,
        "vat_amount": vat_amount,
        "plate_amount": plate_cost_total,
        "total_amount": total_amount,
        "total_with_vat": total_with_vat,
    }


# ──────────────────────────────────────────
# 기사 경비 (Supabase)
# ──────────────────────────────────────────

@st.cache_data(ttl=30)
def load_expenses():
    rows = sb_get("expenses", {"select": "*", "order": "date.desc,saved_at.desc"})
    return rows if rows else []

def save_expenses(expenses):
    pass  # append/delete 개별 처리

def append_expense(exp):
    sb_upsert("expenses", exp)
    st.cache_data.clear()

def delete_expense(exp_id):
    sb_delete("expenses", "id", exp_id)
    st.cache_data.clear()

# 경비 카테고리
EXPENSE_CATEGORIES = ["🍱 식사", "⛽ 주유", "🅿️ 주차", "🛣️ 통행료", "📦 기타"]


# ──────────────────────────────────────────
# UI
# ──────────────────────────────────────────

# 탭별 제목/아이콘 설정
_TAB_SUBTITLES = {
    "quote":    "📝 견적/발주 입력",
    "orders":   "📁 저장된 견적서",
    "delivery": "🚚 대봉 출고일지",
}
_BROWSER_TITLES = {
    "quote":    "견적/발주 입력 - 대봉",
    "orders":   "저장된 견적서 - 대봉",
    "delivery": "대봉 출고일지",
}
_cur_tab = st.session_state.get("current_tab", "delivery")
_subtitle = _TAB_SUBTITLES[_cur_tab]
_browser_title = _BROWSER_TITLES[_cur_tab]

# 브라우저 탭 타이틀 동적 변경
st.markdown(
    f"<script>window.parent.document.title = '{_browser_title}';</script>",
    unsafe_allow_html=True,
)

# 헤더: 대봉 토탈 시스템(크게) + 탭 제목(작게)
st.markdown(
    f"""
    <div style="margin-bottom:8px;">
        <div style="font-size:32px;font-weight:900;color:#111827;line-height:1.1;">
            🏭 대봉 토탈 시스템
        </div>
        <div style="font-size:20px;font-weight:700;color:#6b7280;margin-top:4px;">
            {_subtitle}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.divider()

tab_quote, tab_orders, tab_delivery = st.tabs(["📝 견적/발주 입력", "📁 저장된 견적서", "🚚 대봉 출고일지"])

# ══════════════════════════════════════════
# 탭: 저장된 견적서
# ══════════════════════════════════════════

with tab_orders:
    st.session_state["current_tab"] = "orders"
    if not st.session_state.get("orders_unlocked", False):
        _pw_in = st.text_input("🔒 비밀번호", type="password", key="orders_pw_input",
                               placeholder="비밀번호를 입력하세요", label_visibility="collapsed")
        if _pw_in == "7191":
            st.session_state["orders_unlocked"] = True
            st.rerun()
        elif _pw_in:
            st.error("비밀번호가 틀렸습니다.")
        else:
            st.markdown("<div style='text-align:center;padding:60px 0;'><div style='font-size:52px;'>🔒</div><div style='font-size:17px;font-weight:700;color:#6b7280;margin-top:10px;'>비밀번호를 입력하면 열립니다</div></div>", unsafe_allow_html=True)
    else:
        if st.button("🔓 잠금", key="lock_orders_btn"):
            st.session_state["orders_unlocked"] = False
            st.rerun()

        st.subheader("📋 견적서 조회")
        orders = load_orders()

        f1, f2, f3, f4, f5, f6 = st.columns([1, 1, 1, 1, 1, 4])
        with f1:
            st.button("전체", use_container_width=True, type="primary")
        with f2:
            st.button("결재중", use_container_width=True)
        with f3:
            st.button("미확인", use_container_width=True)
        with f4:
            st.button("확인", use_container_width=True)
        with f5:
            st.button("완료", use_container_width=True)

        s1, s2 = st.columns([4, 1])
        with s1:
            search_text = st.text_input(
                "검색", value="", placeholder="거래처명 / 품목명 / 비닐사이즈 검색",
                label_visibility="collapsed", key="order_search_text",
            )
        with s2:
            st.button("Search(F3)", use_container_width=True)

        if not orders:
            st.info("아직 저장된 발주서가 없습니다.")
        else:
            sorted_orders = sorted(orders, key=lambda x: x.get("saved_at", ""), reverse=True)

            if search_text.strip():
                q = search_text.strip().lower()
                sorted_orders = [
                    o for o in sorted_orders
                    if q in str(o.get("company", "")).lower()
                    or q in str(o.get("item_name", "")).lower()
                    or q in str(o.get("actual_size_text", "")).lower()
                    or q in str(o.get("saved_at", "")).lower()
                ]

            if not sorted_orders:
                st.warning("검색 결과가 없습니다.")
            else:
                selected_order_id = st.session_state.get("selected_order_id")
                if not selected_order_id or not any(o.get("id") == selected_order_id for o in sorted_orders):
                    selected_order_id = sorted_orders[0].get("id")
                    st.session_state["selected_order_id"] = selected_order_id

                st.markdown(
                    f'<div style="text-align:right; font-weight:700; margin:6px 0 8px 0;">총 {len(sorted_orders)}건</div>',
                    unsafe_allow_html=True,
                )

                h0,h1,h2,h3,h4,h5,h6,h7,h8,h9,h10 = st.columns([0.35,0.45,1.45,2.0,1.2,4.0,0.85,0.9,1.15,0.7,0.75])
                for col, label in zip(
                    [h0,h1,h2,h3,h4,h5,h6,h7,h8,h9,h10],
                    ["☑","No.","일자-No.","거래처명","담당명","품목명(요약)","장당가","수량","합계금액","상태","조회"]
                ):
                    col.markdown(f"<div class='order-header'><b>{label}</b></div>", unsafe_allow_html=True)
                st.divider()

                for idx, o in enumerate(sorted_orders):
                    oid = o.get("id", str(idx))
                    is_selected = oid == st.session_state.get("selected_order_id")

                    c0,c1,c2,c3,c4,c5,c6,c7,c8,c9,c10 = st.columns([0.35,0.45,1.45,2.0,1.2,4.0,0.85,0.9,1.15,0.7,0.75])

                    with c0:
                        checked = st.checkbox("", value=is_selected, key=f"row_check_{oid}")
                        if checked and not is_selected:
                            st.session_state["selected_order_id"] = oid
                            st.session_state["edit_panel_open"] = False
                            st.rerun()

                    c1.markdown(f"<div class='order-row' style='padding-top:6px; font-weight:700;'>{idx+1}</div>", unsafe_allow_html=True)
                    c2.markdown(f"<div class='order-row' style='padding-top:6px; font-weight:700;'>{o.get('saved_at','')}</div>", unsafe_allow_html=True)
                    c3.markdown(f"<div class='order-row' style='padding-top:6px; font-weight:700;'>{o.get('company') or '거래처 미입력'}</div>", unsafe_allow_html=True)
                    c4.markdown(f"<div class='order-row' style='padding-top:6px; font-weight:700;'>{o.get('person') or o.get('supplier_manager') or '-'}</div>", unsafe_allow_html=True)
                    c5.markdown(
                        f"<div class='order-row' style='padding-top:4px;'>"
                        f"<div class='item-main'>{o.get('item_name','-')}</div>"
                        f"<div class='item-sub'>{o.get('actual_size_text','')}</div></div>",
                        unsafe_allow_html=True,
                    )
                    c6.markdown(f"<div class='order-row num-cell' style='padding-top:6px;'>{o.get('unit_quote',0):,.1f}</div>", unsafe_allow_html=True)
                    c7.markdown(f"<div class='order-row num-cell' style='padding-top:6px;'>{o.get('production_qty',0):,}</div>", unsafe_allow_html=True)
                    c8.markdown(f"<div class='order-row total-cell' style='padding-top:6px;'>{o.get('total_amount',0):,.0f}</div>", unsafe_allow_html=True)
                    c9.markdown("<div class='order-row' style='font-weight:800; color:#1e3a8a; padding-top:6px;'>진행중</div>", unsafe_allow_html=True)

                    with c10:
                        if st.button("조회", key=f"row_view_{oid}", use_container_width=True):
                            st.session_state["selected_order_id"] = oid
                            st.session_state["edit_panel_open"] = False
                            st.rerun()

                    st.markdown("<hr style='margin:4px 0; border:0; border-top:1px solid #d1d5db;'>", unsafe_allow_html=True)

                selected_order = next(
                    (o for o in sorted_orders if o.get("id") == st.session_state.get("selected_order_id")),
                    sorted_orders[0],
                )

                st.divider()

                selected_items = selected_order.get("items") or []
                print_items = selected_items if selected_items else [{
                    "item_name": selected_order.get("item_name", ""),
                    "actual_size_text": selected_order.get("actual_size_text", ""),
                    "production_qty": selected_order.get("production_qty", 0),
                    "unit_quote": selected_order.get("unit_quote", 0),
                    "supply_amount": selected_order.get("supply_amount", 0),
                    "plate_amount": selected_order.get("plate_amount", 0),
                    "total_amount": selected_order.get("total_amount", 0),
                }]

                st.subheader("✅ 선택한 발주서")

                item_count_text = f" 외 {len(selected_items)-1}건" if len(selected_items) > 1 else ""
                summary_item_name = (
                    selected_items[0].get("item_name", selected_order.get("item_name", "")) + item_count_text
                    if selected_items else selected_order.get("item_name", "")
                )
                summary_size = "여러 품목" if len(selected_items) > 1 else selected_order.get("actual_size_text", "")

                st.markdown(
                    f"""
                    <div style="border:1px solid #d1d5db; border-radius:12px; padding:18px 22px; margin-bottom:14px; background:#ffffff;">
                        <div style="display:grid; grid-template-columns: repeat(5, 1fr); gap:16px;">
                            <div>
                                <div style="font-size:17px; color:#6b7280 !important; font-weight:700;">거래처</div>
                                <div style="font-size:20px; font-weight:900;">{selected_order.get('company') or '거래처 미입력'}</div>
                            </div>
                            <div>
                                <div style="font-size:17px; color:#6b7280 !important; font-weight:700;">담당자</div>
                                <div style="font-size:20px; font-weight:900;">{selected_order.get('person') or selected_order.get('supplier_manager') or '-'}</div>
                            </div>
                            <div>
                                <div style="font-size:17px; color:#6b7280 !important; font-weight:700;">품목</div>
                                <div style="font-size:20px; font-weight:900;">{summary_item_name}</div>
                                <div style="font-size:16px; color:#6b7280 !important; font-weight:700;">{summary_size}</div>
                            </div>
                            <div>
                                <div style="font-size:17px; color:#6b7280 !important; font-weight:700;">수량</div>
                                <div style="font-size:22px; font-weight:900;">{selected_order.get('production_qty',0):,} 장</div>
                            </div>
                            <div>
                                <div style="font-size:17px; color:#6b7280 !important; font-weight:700;">합계금액</div>
                                <div style="font-size:24px; font-weight:900;">{selected_order.get('total_amount',0):,.0f} 원</div>
                                <div style="font-size:16px; color:#6b7280 !important; font-weight:700;">VAT 별도</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if selected_order.get("items"):
                    with st.expander("📋 저장된 품목 상세 보기", expanded=False):
                        saved_item_rows = []
                        for idx, item in enumerate(selected_order.get("items", []), start=1):
                            saved_item_rows.append({
                                "순번": idx,
                                "품목명": item.get("item_name", ""),
                                "규격": item.get("actual_size_text", ""),
                                "수량": f"{item.get('production_qty',0):,}",
                                "장당가": f"{item.get('unit_quote',0):,.1f}",
                                "공급가액": f"{item.get('supply_amount',0):,.0f}",
                                "동판단가": f"{item.get('plate_unit', item.get('plate_amount',0)):,.0f}",
                                "동판수량": f"{item.get('plate_qty', 1 if item.get('plate_amount',0) else 0):,}",
                                "동판비": f"{item.get('plate_amount',0):,.0f}",
                                "합계": f"{item.get('total_amount',0):,.0f}",
                            })
                        show_white_table(pd.DataFrame(saved_item_rows))

                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button("✏️ 수정하기", use_container_width=True):
                        st.session_state["edit_panel_open"] = True
                        st.session_state["edit_order_id"] = selected_order.get("id")
                        st.rerun()
                with b2:
                    if st.button("📄 발주서 복사", use_container_width=True):
                        copied_order = dict(selected_order)
                        copied_order["id"] = str(uuid.uuid4())
                        copied_order["saved_at"] = now_kst().strftime("%Y-%m-%d %H:%M")
                        copied_order["quote_no"] = f"{now_kst().strftime('%Y/%m/%d')}-복사"
                        base_name = str(copied_order.get("item_name", "")).replace(" 복사본", "").strip()
                        copied_order["item_name"] = f"{base_name} 복사본".strip()
                        if copied_order.get("items"):
                            copied_items = []
                            for copied_item in copied_order["items"]:
                                copied_item = dict(copied_item)
                                item_base_name = str(copied_item.get("item_name", "")).replace(" 복사본", "").strip()
                                copied_item["id"] = str(uuid.uuid4())
                                copied_item["item_name"] = f"{item_base_name} 복사본".strip()
                                copied_items.append(copied_item)
                            copied_order["items"] = copied_items
                        upsert_order(copied_order)
                        st.session_state["selected_order_id"] = copied_order["id"]
                        st.session_state["edit_panel_open"] = True
                        st.session_state["edit_order_id"] = copied_order["id"]
                        st.success("복사본을 만들었습니다.")
                        st.rerun()
                with b3:
                    if st.button("🗑️ 선택삭제", use_container_width=True):
                        delete_order(selected_order.get("id"))
                        st.session_state.pop("selected_order_id", None)
                        st.session_state["edit_panel_open"] = False
                        st.success("삭제했습니다.")
                        st.rerun()

                if st.session_state.get("edit_panel_open"):
                    edit_order = next(
                        (o for o in load_orders() if o.get("id") == st.session_state.get("edit_order_id")),
                        selected_order,
                    )

                    st.divider()
                    st.subheader("✏️ 발주서 수정창")
                    st.caption("수정 후 저장하기를 누르면 기존 발주서에 덮어쓰기 됩니다.")

                    e1, e2 = st.columns(2)
                    with e1:
                        edit_company = st.text_input("거래처명", value=edit_order.get("company",""), key="edit_company")
                    with e2:
                        edit_person = st.text_input("담당자", value=edit_order.get("person",""), key="edit_person")

                    e3, e4 = st.columns(2)
                    with e3:
                        edit_item_name = st.text_input("품목명", value=edit_order.get("item_name",""), key="edit_item_name")
                    with e4:
                        material_options = list(MATERIALS.keys())
                        edit_material_default = edit_order.get("material", "HDPE")
                        edit_material_index = material_options.index(edit_material_default) if edit_material_default in material_options else 0
                        edit_material = st.selectbox("재질", material_options, index=edit_material_index, key="edit_material")

                    e5, e6 = st.columns(2)
                    with e5:
                        bag_options = ["오픈봉투", "택배봉투"]
                        edit_bag_default = edit_order.get("bag_type", "오픈봉투")
                        edit_bag_index = bag_options.index(edit_bag_default) if edit_bag_default in bag_options else 0
                        edit_bag_type = st.selectbox("봉투 형태", bag_options, index=edit_bag_index, key="edit_bag_type")
                    with e6:
                        edit_quote_no = st.text_input("일련번호", value=edit_order.get("quote_no",""), key="edit_quote_no")

                    e7, e8, e9 = st.columns(3)
                    with e7:
                        edit_thickness = st.number_input("원단두께 (㎛)", min_value=1, max_value=300, value=int(edit_order.get("thickness_um",25)), step=1, format="%d", key="edit_thickness")
                    with e8:
                        edit_roll_width = st.number_input("원단폭/총가로 (cm)", min_value=1, max_value=300, value=int(edit_order.get("roll_width_cm",44)), step=1, format="%d", key="edit_roll_width")
                    with e9:
                        edit_m_gusset = st.number_input("M가공 합계 (cm)", min_value=0.0, max_value=200.0, value=float(edit_order.get("m_gusset_cm",0.0)), step=0.5, format="%.1f", key="edit_m_gusset")

                    e10, e11, e12 = st.columns(3)
                    with e10:
                        edit_process_length = st.number_input("가공길이 (cm)", min_value=1, max_value=300, value=int(edit_order.get("process_length_cm",44)), step=1, format="%d", key="edit_process_length")
                    with e11:
                        edit_roll_length = st.number_input("원단길이 (m/롤)", min_value=1, max_value=10000, value=int(edit_order.get("roll_length_m",500)), step=10, format="%d", key="edit_roll_length")
                    with e12:
                        edit_qty = st.number_input("제작수량 (장)", min_value=1, max_value=100_000_000, value=int(edit_order.get("manual_production_qty", edit_order.get("production_qty",10000))), step=1000, key="edit_qty")

                    e13, e14, e15 = st.columns(3)
                    mat_default = MATERIALS[edit_material]
                    with e13:
                        edit_density = st.number_input("비중", min_value=0.1, max_value=2.0, value=float(edit_order.get("density", mat_default["density"])), step=0.01, format="%.2f", key="edit_density")
                    with e14:
                        edit_extrusion = st.number_input("압출비", min_value=0, max_value=10000, value=int(edit_order.get("extrusion_cost", mat_default["extrusion"])), step=50, key="edit_extrusion")
                    with e15:
                        edit_raw_price = st.number_input("원료값/kg", min_value=0, max_value=20000, value=int(edit_order.get("raw_price", mat_default["raw_price"])), step=50, key="edit_raw_price")

                    e16, e17, e18 = st.columns(3)
                    with e16:
                        edit_margin = st.number_input("마진 (%)", min_value=0, max_value=300, value=int(edit_order.get("margin_percent",15)), step=1, format="%d", key="edit_margin")
                    with e17:
                        edit_print_cost = st.number_input("인쇄비 (원/500m)", min_value=0, max_value=10_000_000, value=int(edit_order.get("manual_print_cost_500m",0)), step=1000, format="%d", key="edit_print_cost")
                    with e18:
                        edit_open_cost = st.number_input("오픈 가공비 (원/500m)", min_value=0, max_value=10_000_000, value=int(edit_order.get("manual_open_processing_cost_500m",0)), step=1000, format="%d", key="edit_open_cost")

                    e19, e20, e21 = st.columns(3)
                    with e19:
                        edit_print_count = st.number_input("인쇄도수 표시용", min_value=0, max_value=10, value=int(edit_order.get("print_count_display",0)), step=1, key="edit_print_count")
                    with e20:
                        edit_roll_count = st.number_input("원단롤수", min_value=1, max_value=1000, value=int(edit_order.get("roll_count",1)), step=1, key="edit_roll_count")
                    with e21:
                        edit_extra_cost = st.number_input("기타 추가가공비", min_value=0, max_value=10_000_000, value=int(edit_order.get("extra_processing_cost_500m",0)), step=1000, format="%d", key="edit_extra_cost")

                    if edit_bag_type == "택배봉투":
                        edit_adhesive_cost = st.number_input("접착 가공비 단가 (원/cm·장)", min_value=0.0, max_value=100.0, value=float(edit_order.get("adhesive_processing_cost_per_cm_ea",0.4)), step=0.05, format="%.2f", key="edit_adhesive_cost")
                    else:
                        edit_adhesive_cost = 0.0

                    edited_items_table = None
                    if edit_order.get("items"):
                        st.divider()
                        st.markdown("### 📋 품목별 숫자 빠른 수정")
                        edit_item_rows = []
                        for idx, item in enumerate(edit_order.get("items",[]), start=1):
                            plate_amount_now = float(item.get("plate_amount",0))
                            plate_unit_now = float(item.get("plate_unit", plate_amount_now))
                            plate_qty_now = int(item.get("plate_qty", 1 if plate_amount_now else 0))
                            edit_item_rows.append({
                                "순번": idx,
                                "품목명": item.get("item_name",""),
                                "규격": item.get("actual_size_text",""),
                                "수량": int(item.get("production_qty",0)),
                                "장당가": float(item.get("unit_quote",0)),
                                "동판단가": plate_unit_now,
                                "동판수량": plate_qty_now,
                            })

                        edited_items_table = st.data_editor(
                            pd.DataFrame(edit_item_rows),
                            use_container_width=True, hide_index=True,
                            disabled=["순번","품목명","규격"],
                            column_order=["순번","품목명","규격","수량","장당가","동판단가","동판수량"],
                            column_config={
                                "수량": st.column_config.NumberColumn("수량", min_value=0, step=100, format="%d"),
                                "장당가": st.column_config.NumberColumn("장당가", min_value=0.0, step=0.5, format="%.1f"),
                                "동판단가": st.column_config.NumberColumn("동판단가", min_value=0.0, step=1000, format="%.0f"),
                                "동판수량": st.column_config.SelectboxColumn("동판수량", options=[0,1,2,3,4,5,6,7,8,9,10], required=True),
                            },
                            key=f"edit_items_editor_{edit_order.get('id')}",
                        )

                        preview_rows = []
                        preview_total = 0
                        for _, row in edited_items_table.iterrows():
                            qty_preview = int(row["수량"])
                            unit_preview = float(row["장당가"])
                            plate_unit_preview = float(row["동판단가"])
                            plate_qty_preview = int(row["동판수량"])
                            supply_preview = qty_preview * unit_preview
                            plate_preview = plate_unit_preview * plate_qty_preview
                            total_preview = supply_preview + plate_preview
                            preview_total += total_preview
                            preview_rows.append({
                                "순번": int(row["순번"]),
                                "품목명": row["품목명"],
                                "수량": f"{qty_preview:,}",
                                "장당가": f"{unit_preview:,.1f}",
                                "공급가액": f"{supply_preview:,.0f}",
                                "동판단가": f"{plate_unit_preview:,.0f}",
                                "동판수량": f"{plate_qty_preview:,}",
                                "동판비": f"{plate_preview:,.0f}",
                                "합계": f"{total_preview:,.0f}",
                            })

                        show_white_table(pd.DataFrame(preview_rows))
                        st.metric("수정 후 총합계 (VAT 별도)", f"{preview_total:,.0f} 원")

                    bc1, bc2 = st.columns(2)
                    with bc1:
                        if st.button("💾 저장하기", use_container_width=True, type="primary"):
                            edit_result = calc_quote(
                                bag_type=edit_bag_type, thickness_um=edit_thickness, roll_width_cm=edit_roll_width,
                                m_gusset_cm=edit_m_gusset, process_length_cm=edit_process_length, roll_length_m=edit_roll_length,
                                print_count_display=edit_print_count, manual_print_cost_500m=edit_print_cost,
                                manual_open_processing_cost_500m=edit_open_cost, adhesive_processing_cost_per_cm_ea=edit_adhesive_cost,
                                extra_processing_cost_500m=edit_extra_cost, margin_percent=edit_margin,
                                roll_count=edit_roll_count, manual_production_qty=edit_qty,
                                raw_price=edit_raw_price, extrusion_cost=edit_extrusion, density=edit_density,
                            )

                            updated_order = dict(edit_order)

                            if edit_order.get("items") and edited_items_table is not None:
                                updated_items = []
                                original_items = edit_order.get("items", [])
                                for row_idx, row in edited_items_table.iterrows():
                                    base_item = dict(original_items[row_idx]) if row_idx < len(original_items) else {}
                                    qty = int(row["수량"])
                                    unit = float(row["장당가"])
                                    plate_unit = float(row["동판단가"])
                                    plate_qty = int(row["동판수량"])
                                    plate = plate_unit * plate_qty
                                    supply = qty * unit
                                    total = supply + plate
                                    base_item.update({
                                        "production_qty": qty, "unit_quote": unit,
                                        "supply_amount": supply, "plate_unit": plate_unit,
                                        "plate_qty": plate_qty, "plate_amount": plate, "total_amount": total,
                                    })
                                    updated_items.append(base_item)

                                total_qty = sum(int(i.get("production_qty",0)) for i in updated_items)
                                total_supply = sum(float(i.get("supply_amount",0)) for i in updated_items)
                                total_plate = sum(float(i.get("plate_amount",0)) for i in updated_items)
                                total_amount = sum(float(i.get("total_amount",0)) for i in updated_items)
                                first_item = updated_items[0] if updated_items else {}
                                summary_name = first_item.get("item_name", edit_item_name)
                                if len(updated_items) > 1:
                                    summary_name = f"{summary_name} 외 {len(updated_items)-1}건"

                                updated_order.update({
                                    "saved_at": now_kst().strftime("%Y-%m-%d %H:%M"),
                                    "quote_no": edit_quote_no, "company": edit_company, "person": edit_person,
                                    "item_name": summary_name, "material": edit_material, "bag_type": edit_bag_type,
                                    "thickness_um": edit_thickness, "roll_width_cm": edit_roll_width,
                                    "m_gusset_cm": edit_m_gusset, "process_length_cm": edit_process_length,
                                    "roll_length_m": edit_roll_length, "manual_production_qty": total_qty,
                                    "print_count_display": edit_print_count, "roll_count": edit_roll_count,
                                    "density": edit_density, "extrusion_cost": edit_extrusion, "raw_price": edit_raw_price,
                                    "margin_percent": edit_margin, "manual_print_cost_500m": edit_print_cost,
                                    "manual_open_processing_cost_500m": edit_open_cost,
                                    "adhesive_processing_cost_per_cm_ea": edit_adhesive_cost,
                                    "extra_processing_cost_500m": edit_extra_cost,
                                    "actual_size_text": "여러 품목" if len(updated_items) > 1 else first_item.get("actual_size_text", edit_result["actual_size_text"]),
                                    "roll_spec_text": first_item.get("roll_spec_text", edit_result["roll_spec_text"]),
                                    "unit_quote": 0 if len(updated_items) > 1 else first_item.get("unit_quote", edit_result["unit_quote"]),
                                    "production_qty": total_qty, "supply_amount": total_supply,
                                    "plate_amount": total_plate, "total_amount": total_amount, "items": updated_items,
                                })
                            else:
                                updated_order.update({
                                    "saved_at": now_kst().strftime("%Y-%m-%d %H:%M"),
                                    "quote_no": edit_quote_no, "company": edit_company, "person": edit_person,
                                    "item_name": edit_item_name, "material": edit_material, "bag_type": edit_bag_type,
                                    "thickness_um": edit_thickness, "roll_width_cm": edit_roll_width,
                                    "m_gusset_cm": edit_m_gusset, "process_length_cm": edit_process_length,
                                    "roll_length_m": edit_roll_length, "manual_production_qty": edit_qty,
                                    "print_count_display": edit_print_count, "roll_count": edit_roll_count,
                                    "density": edit_density, "extrusion_cost": edit_extrusion, "raw_price": edit_raw_price,
                                    "margin_percent": edit_margin, "manual_print_cost_500m": edit_print_cost,
                                    "manual_open_processing_cost_500m": edit_open_cost,
                                    "adhesive_processing_cost_per_cm_ea": edit_adhesive_cost,
                                    "extra_processing_cost_500m": edit_extra_cost,
                                    "actual_size_text": edit_result["actual_size_text"],
                                    "roll_spec_text": edit_result["roll_spec_text"],
                                    "unit_quote": edit_result["unit_quote"],
                                    "production_qty": edit_result["production_qty"],
                                    "supply_amount": edit_result["supply_amount"],
                                    "plate_amount": edit_result["plate_amount"],
                                    "total_amount": edit_result["total_amount"],
                                })

                            upsert_order(updated_order)
                            st.session_state["selected_order_id"] = updated_order["id"]
                            st.session_state["edit_panel_open"] = False
                            st.success("수정한 발주서를 저장했습니다.")
                            st.rerun()

                    with bc2:
                        if st.button("❌ 수정 취소", use_container_width=True):
                            st.session_state["edit_panel_open"] = False
                            st.rerun()

    # ══════════════════════════════════════════
    # 탭: 대봉 출고일지
    # ══════════════════════════════════════════

with tab_delivery:
    st.session_state["current_tab"] = "delivery"
    st.subheader("🚚 대봉 출고일지")
    delivery_logs = load_delivery_logs()
    drivers = load_drivers()

    # ── 기사 관리 ──
    with st.expander("👤 배송 기사 관리", expanded=False):
        nc1, nc2 = st.columns([4, 1])
        with nc1:
            new_drv = st.text_input("기사명", placeholder="이름 입력", label_visibility="collapsed", key="new_driver_input")
        with nc2:
            if st.button("추가", key="add_driver_btn", use_container_width=True):
                if new_drv.strip() and new_drv.strip() not in drivers:
                    r = requests.post(f"{SUPABASE_URL}/rest/v1/drivers",
                        headers={**SB_HEADERS, "Prefer": "return=representation"},
                        json={"name": new_drv.strip()}, timeout=10)
                    if r.ok:
                        st.success(f"'{new_drv.strip()}' 추가!")
                        st.rerun()
                    else:
                        st.error(f"오류: {r.text[:100]}")
                elif new_drv.strip() in drivers:
                    st.warning("이미 등록된 기사입니다.")

        if drivers:
            st.markdown(f"**등록 기사 {len(drivers)}명**")
            for di, drv in enumerate(sorted(drivers)):
                c1, c2, c3 = st.columns([5, 1, 1])
                c1.write(f"👤 {drv}")
                with c2:
                    if st.button("수정", key=f"edit_drv_{di}", use_container_width=True):
                        st.session_state[f"editing_drv_{di}"] = not st.session_state.get(f"editing_drv_{di}", False)
                        st.rerun()
                with c3:
                    if st.button("삭제", key=f"del_drv_{di}", use_container_width=True):
                        remove_driver(drv)
                        st.rerun()
                if st.session_state.get(f"editing_drv_{di}", False):
                    e1, e2, e3 = st.columns([4, 1, 1])
                    with e1:
                        new_name = st.text_input("이름", value=drv, key=f"edit_drv_name_{di}", label_visibility="collapsed")
                    with e2:
                        if st.button("저장", key=f"save_drv_{di}", use_container_width=True, type="primary"):
                            rename_driver(drv, new_name.strip())
                            st.session_state[f"editing_drv_{di}"] = False
                            st.rerun()
                    with e3:
                        if st.button("취소", key=f"cancel_drv_{di}", use_container_width=True):
                            st.session_state[f"editing_drv_{di}"] = False
                            st.rerun()
        else:
            st.info("기사를 추가해 주세요.")

    st.markdown("---")
    st.markdown("### 📥 출고 입력")

    if not drivers:
        st.warning("먼저 배송 기사를 추가해 주세요.")
    else:
        # 기사 / 날짜
        d1, d2 = st.columns(2)
        with d1:
            delivery_driver = st.selectbox("출고 기사", sorted(drivers), key="delivery_driver_select")
        with d2:
            delivery_date = st.date_input("출고일", value=today_kst(), key="delivery_date_input")

        # 저장 후 초기화
        if st.session_state.pop("_clear_customer_input", False):
            st.session_state["_cust_override"] = "— 거래처 선택 —"
            st.session_state["delivery_basket"] = []

        # 거래처명
        _all_customers_for_ac = load_customers()
        _company_list = sorted([c.get("company","") for c in _all_customers_for_ac if c.get("company")])
        _cust_opts = ["— 거래처 선택 —"] + _company_list
        # 거래처 관리에서 선택 시 override
        _override = st.session_state.pop("_cust_override", None)
        if _override and _override in _cust_opts:
            _default_idx = _cust_opts.index(_override)
        else:
            _prev = st.session_state.get("cust_all_dropdown", "— 거래처 선택 —")
            _default_idx = _cust_opts.index(_prev) if _prev in _cust_opts else 0
        _sel_cust = st.selectbox("거래처명", options=_cust_opts, index=_default_idx, key="cust_all_dropdown")
        delivery_customer = _sel_cust if _sel_cust != "— 거래처 선택 —" else ""

        # 거래처 관리
        with st.expander("🏢 거래처 관리", expanded=False):
            nc1, nc2 = st.columns(2)
            with nc1:
                new_cn = st.text_input("거래처명 *", key="new_del_cust_name", placeholder="필수")
                new_cp = st.text_input("담당자", key="new_del_cust_person")
            with nc2:
                new_ct = st.text_input("연락처", key="new_del_cust_tel")
                new_ca = st.text_input("주소", key="new_del_cust_addr")
            if st.button("💾 거래처 저장", key="save_new_del_cust_btn", use_container_width=True, type="primary"):
                if not new_cn.strip():
                    st.error("거래처명을 입력하세요.")
                else:
                    existing = next((c for c in _all_customers_for_ac if c.get("company") == new_cn.strip()), None)
                    upsert_customer({
                        "id": existing["id"] if existing else str(uuid.uuid4()),
                        "company": new_cn.strip(), "person": new_cp.strip(),
                        "customer_tel": new_ct.strip(), "address": new_ca.strip(),
                        "ref_text": "", "payment_terms": "",
                    })
                    st.success(f"'{new_cn.strip()}' 저장!")
                    st.rerun()

            st.markdown("---")
            dc_search = st.text_input("거래처 검색", key="delivery_cust_search",
                                      placeholder="검색", label_visibility="collapsed")
            _mgmt_custs = [c for c in _all_customers_for_ac
                           if dc_search.strip().lower() in c.get("company","").lower()]                           if dc_search.strip() else _all_customers_for_ac
            st.markdown(f"총 {len(_mgmt_custs)}개")
            with st.container(height=min(len(_mgmt_custs)*70, 300) if _mgmt_custs else None):
                for ci, c in enumerate(_mgmt_custs):
                    c1, c2, c3, c4 = st.columns([5, 1, 1, 1])
                    with c1:
                        _sub = " · ".join([x for x in [c.get("person",""), c.get("customer_tel","")] if x])
                        st.markdown(f"**{c.get('company','-')}**{'  ' + _sub if _sub else ''}")
                    with c2:
                        if st.button("선택", key=f"mgmt_sel_{ci}", use_container_width=True):
                            st.session_state["_cust_override"] = c.get("company","")
                            st.rerun()
                    with c3:
                        if st.button("수정", key=f"mgmt_edit_{ci}", use_container_width=True):
                            st.session_state[f"mgmt_editing_{ci}"] = not st.session_state.get(f"mgmt_editing_{ci}", False)
                            st.rerun()
                    with c4:
                        if st.button("삭제", key=f"mgmt_del_{ci}", use_container_width=True):
                            delete_customer(c.get("id",""))
                            st.rerun()
                    if st.session_state.get(f"mgmt_editing_{ci}", False):
                        e1, e2, e3 = st.columns([3, 2, 2])
                        with e1:
                            _en = st.text_input("거래처명", value=c.get("company",""), key=f"mgmt_cname_{ci}", label_visibility="collapsed")
                        with e2:
                            _ep = st.text_input("담당자", value=c.get("person",""), key=f"mgmt_cperson_{ci}", label_visibility="collapsed")
                        with e3:
                            _et = st.text_input("연락처", value=c.get("customer_tel",""), key=f"mgmt_ctel_{ci}", label_visibility="collapsed")
                        _ea = st.text_input("주소", value=c.get("address",""), key=f"mgmt_caddr_{ci}", label_visibility="collapsed")
                        s1, s2 = st.columns(2)
                        with s1:
                            if st.button("저장", key=f"mgmt_save_{ci}", use_container_width=True, type="primary"):
                                upsert_customer({"id": c.get("id", str(uuid.uuid4())),
                                    "company": _en.strip(), "person": _ep.strip(),
                                    "customer_tel": _et.strip(), "address": _ea.strip(),
                                    "ref_text": c.get("ref_text",""), "payment_terms": c.get("payment_terms","")})
                                st.session_state[f"mgmt_editing_{ci}"] = False
                                st.rerun()
                        with s2:
                            if st.button("취소", key=f"mgmt_cancel_{ci}", use_container_width=True):
                                st.session_state[f"mgmt_editing_{ci}"] = False
                                st.rerun()
                    st.divider()

        # ── 품목 선택 ──
        st.markdown("### 📦 품목 선택")

        # 바구니 초기화
        if "delivery_basket" not in st.session_state:
            st.session_state["delivery_basket"] = []
        if st.session_state.get("delivery_basket_customer","") != delivery_customer:
            st.session_state["delivery_basket"] = []
            st.session_state["delivery_basket_customer"] = delivery_customer

        if delivery_customer:
            cust_items = get_customer_items(delivery_customer)
            if cust_items:
                # 품목을 selectbox로 선택
                item_labels = [f"{i['name']} / {i['size']}" if i.get('size') else i['name'] for i in cust_items]
                sel_item_label = st.selectbox("품목 선택", ["— 선택 —"] + item_labels,
                                              key="item_select_box", label_visibility="collapsed")

                if sel_item_label != "— 선택 —":
                    sel_item = cust_items[item_labels.index(sel_item_label)]
                    add_qty = st.number_input("수량", value=int(sel_item.get("qty", 0)),
                                              min_value=0, step=100, key="item_qty_input")
                    a1, a2 = st.columns(2)
                    with a1:
                        if st.button("➕ 바구니 추가", key="add_to_basket", use_container_width=True, type="primary"):
                            st.session_state["delivery_basket"] = [
                                b for b in st.session_state["delivery_basket"]
                                if not (b["name"] == sel_item["name"] and b["size"] == sel_item.get("size",""))
                            ]
                            st.session_state["delivery_basket"].append({
                                "name": sel_item["name"], "size": sel_item.get("size",""), "qty": int(add_qty)
                            })
                            upsert_item(delivery_customer, sel_item["name"], sel_item.get("size",""), int(add_qty))
                            st.rerun()
                    with a2:
                        if st.button("🗑 품목 삭제", key="del_item_btn", use_container_width=True):
                            delete_item(delivery_customer, sel_item["name"], sel_item.get("size",""))
                            st.rerun()

            # 새 품목 추가
            if st.session_state.pop("_clear_pre_item", False):
                st.session_state["pre_item_name"] = ""
                st.session_state["pre_item_size"] = ""
                st.session_state["pre_item_qty"] = 0

            with st.expander("새 품목 추가", expanded=not bool(cust_items)):
                p1, p2, p3 = st.columns([3, 1, 1])
                with p1:
                    pre_name = st.text_input("품목명", key="pre_item_name", placeholder="품목명")
                with p2:
                    pre_size = st.text_input("규격", key="pre_item_size", placeholder="규격")
                with p3:
                    pre_qty = st.number_input("기본수량", key="pre_item_qty", min_value=0, value=0, step=100)
                if st.button("등록", key="add_pre_item_btn", use_container_width=True, type="primary"):
                    if pre_name.strip():
                        upsert_item(delivery_customer, pre_name.strip(), pre_size.strip(), pre_qty)
                        st.session_state["_clear_pre_item"] = True
                        st.rerun()
                    else:
                        st.warning("품목명을 입력하세요.")
        else:
            st.info("거래처를 먼저 선택하세요.")

        # ── 바구니 ──
        basket = st.session_state.get("delivery_basket", [])
        if basket:
            st.markdown("**🛒 선택된 품목**")
            _bdf = pd.DataFrame([{"품목": b["name"] + (f" / {b['size']}" if b.get("size") else ""),
                                   "수량": b["qty"]} for b in basket])
            st.dataframe(_bdf, use_container_width=True, hide_index=True)
            total_qty = sum(b["qty"] for b in basket)
            st.markdown(f"**총 {total_qty:,}개 · {len(basket)}품목**")
            if st.button("🗑 바구니 비우기", key="clear_basket", use_container_width=False):
                st.session_state["delivery_basket"] = []
                st.rerun()

        # ── 경비 입력 ──
        if st.session_state.pop("_clear_expense_inputs", False):
            for k in ["inline_meal_input", "inline_fuel_input", "inline_etc_input"]:
                st.session_state[k] = 0
            st.session_state["inline_etc_label"] = ""

        with st.expander("💰 경비 입력 (선택사항)", expanded=False):
            ex1, ex2, ex3 = st.columns(3)
            with ex1:
                meal_amount = st.number_input("🍱 식비", min_value=0, value=0, step=1000, key="inline_meal_input")
            with ex2:
                fuel_amount = st.number_input("⛽ 주유비", min_value=0, value=0, step=1000, key="inline_fuel_input")
            with ex3:
                etc_amount = st.number_input("📦 기타", min_value=0, value=0, step=1000, key="inline_etc_input")
            etc_label = st.text_input("기타 항목명", key="inline_etc_label", placeholder="예) 주차비")
            total_exp = meal_amount + fuel_amount + etc_amount
            if total_exp > 0:
                st.info(f"💰 경비 합계: {total_exp:,}원")

        # ── 명세표 첨부 ──
        st.markdown("**📎 거래명세표 첨부** (선택사항)")
        _attach_mode = st.radio("첨부방식", ["📁 갤러리", "📷 카메라"], horizontal=True,
                                key="attach_mode_radio", label_visibility="collapsed")
        delivery_attachment = None
        if _attach_mode == "📁 갤러리":
            _f = st.file_uploader("이미지 선택", type=["jpg","jpeg","png","webp"],
                                  key="delivery_attachment_input", label_visibility="collapsed")
            if _f:
                delivery_attachment = _f
                st.image(_f, width=200)
        else:
            import streamlit.components.v1 as _cam_components
            _b64_transfer = st.session_state.get("cam_b64_input","")
            _cam_components.html("""
<style>
#cw{width:100%;background:#000;border-radius:8px;overflow:hidden}
#cv{width:100%;display:block}
#bs{width:100%;padding:14px;font-size:20px;font-weight:900;background:#ef4444;color:#fff;border:none;cursor:pointer}
#prev{display:none;width:100%;border-radius:8px;margin-top:6px}
#br{display:none;gap:8px;margin-top:6px}
#bc{flex:1;padding:12px;font-size:18px;font-weight:800;background:#22c55e;color:#fff;border:none;border-radius:8px;cursor:pointer}
#brt{flex:1;padding:12px;font-size:16px;background:#6b7280;color:#fff;border:none;border-radius:8px;cursor:pointer}
</style>
<div id="cw"><video id="cv" autoplay playsinline></video></div>
<canvas id="can" style="display:none"></canvas>
<button id="bs" onclick="shoot()">📷 사진 찍기</button>
<img id="prev"/><div id="br"><button id="brt" onclick="retake()">↩ 다시</button><button id="bc" onclick="confirm()">✅ 확인</button></div>
<script>
var s,cap,v=document.getElementById('cv'),c=document.getElementById('can');
navigator.mediaDevices.getUserMedia({video:{facingMode:{ideal:'environment'}},audio:false}).then(function(st){s=st;v.srcObject=st;}).catch(function(e){document.getElementById('cw').innerHTML='<p style="color:red;padding:12px;">카메라 오류: '+e.message+'</p>';});
function shoot(){c.width=v.videoWidth;c.height=v.videoHeight;c.getContext('2d').drawImage(v,0,0);cap=c.toDataURL('image/jpeg',0.9);document.getElementById('prev').src=cap;document.getElementById('prev').style.display='block';document.getElementById('cw').style.display='none';document.getElementById('bs').style.display='none';document.getElementById('br').style.display='flex';}
function retake(){document.getElementById('prev').style.display='none';document.getElementById('cw').style.display='block';document.getElementById('bs').style.display='block';document.getElementById('br').style.display='none';cap=null;}
function confirm(){if(!cap)return;var doc=window.parent.document;var inp=doc.querySelector('input[aria-label="cam_b64_transfer"]');if(inp){var s=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;s.call(inp,cap.split(',')[1]);inp.dispatchEvent(new Event('input',{bubbles:true}));}document.getElementById('br').innerHTML='<p style="color:#22c55e;font-size:16px;font-weight:900;padding:8px">✅ 저장 완료! 아래 저장 버튼을 누르세요.</p>';}
</script>""", height=480)
            _b64_transfer = st.text_input("cam_b64_transfer", key="cam_b64_input", label_visibility="hidden")
            if _b64_transfer and len(_b64_transfer) > 100:
                import base64 as _b64m
                try:
                    _img_bytes = _b64m.b64decode(_b64_transfer)
                    from io import BytesIO as _BIO
                    _bio = _BIO(_img_bytes); _bio.name="camera.jpg"; _bio.type="image/jpeg"
                    delivery_attachment = _bio
                    st.image(_img_bytes, width=200)
                except: pass

        # ── 저장 버튼 ──
        if st.button("💾 출고일지 저장", use_container_width=True, key="save_delivery_btn", type="primary"):
            basket = st.session_state.get("delivery_basket", [])
            if not delivery_customer:
                st.error("거래처를 선택하세요.")
            elif not basket:
                st.error("품목을 1개 이상 추가하세요.")
            else:
                import base64
                att_b64 = att_mime = None
                if delivery_attachment:
                    att_b64 = base64.b64encode(delivery_attachment.read()).decode()
                    att_mime = getattr(delivery_attachment, "type", "image/jpeg") or "image/jpeg"
                for b in basket:
                    append_delivery_log({
                        "id": str(uuid.uuid4()), "driver": delivery_driver,
                        "date": delivery_date.strftime("%Y-%m-%d"),
                        "customer": delivery_customer, "item": b["name"],
                        "size": b.get("size",""), "quantity": int(b["qty"]),
                        "saved_at": now_kst().strftime("%Y-%m-%d %H:%M:%S"),
                        "attachment": att_b64, "attachment_mime": att_mime,
                    })
                    upsert_item(delivery_customer, b["name"], b.get("size",""), int(b["qty"]))
                # 경비 저장
                _exp_date = delivery_date.strftime("%Y-%m-%d")
                _exp_at = now_kst().strftime("%Y-%m-%d %H:%M:%S")
                if meal_amount > 0:
                    append_expense({"id": str(uuid.uuid4()), "driver": delivery_driver,
                        "date": _exp_date, "category": "🍱 식사", "amount": int(meal_amount), "memo": "", "saved_at": _exp_at})
                if fuel_amount > 0:
                    append_expense({"id": str(uuid.uuid4()), "driver": delivery_driver,
                        "date": _exp_date, "category": "⛽ 주유", "amount": int(fuel_amount), "memo": "", "saved_at": _exp_at})
                if etc_amount > 0:
                    append_expense({"id": str(uuid.uuid4()), "driver": delivery_driver,
                        "date": _exp_date, "category": f"📦 {etc_label or '기타'}", "amount": int(etc_amount), "memo": "", "saved_at": _exp_at})
                st.session_state["_clear_customer_input"] = True
                st.session_state["_clear_expense_inputs"] = True
                st.success(f"저장 완료! ({len(basket)}품목)")
                st.rerun()

    st.markdown("---")

    # ── 경비 현황 ──
    expenses = load_expenses()
    with st.expander("💰 기사 경비 현황", expanded=False):
        if expenses:
            _exp_drivers = sorted(set(e.get("driver","") for e in expenses))
            _exp_drv_filter = st.radio("기사", ["전체"] + _exp_drivers, horizontal=True, key="exp_driver_filter", label_visibility="collapsed")
            _exp_filtered = expenses if _exp_drv_filter == "전체" else [e for e in expenses if e.get("driver") == _exp_drv_filter]

            # 집계
            _cat_sum = {}
            for e in _exp_filtered:
                _cat_sum[e.get("category","-")] = _cat_sum.get(e.get("category","-"), 0) + int(e.get("amount",0))
            _total_exp = sum(_cat_sum.values())
            st.metric("합계", f"{_total_exp:,}원")

            # 목록
            _exp_df = pd.DataFrame([{"날짜": e.get("date",""), "기사": e.get("driver",""),
                "항목": e.get("category",""), "금액": e.get("amount",0), "메모": e.get("memo","")}
                for e in sorted(_exp_filtered, key=lambda x: x.get("date",""), reverse=True)])
            st.dataframe(_exp_df, use_container_width=True, hide_index=True, height=min(len(_exp_df)*35+40, 300))

            # 경비 등록
            st.markdown("**경비 추가**")
            ex1, ex2 = st.columns(2)
            with ex1:
                exp_drv = st.selectbox("기사", sorted(drivers) if drivers else ["기사없음"], key="exp_driver_select")
                exp_cat = st.selectbox("항목", ["🍱 식사","⛽ 주유","🅿️ 주차","🛣️ 통행료","📦 기타"], key="exp_category_select")
            with ex2:
                exp_date = st.date_input("날짜", value=today_kst(), key="exp_date_input")
                exp_amt = st.number_input("금액", min_value=0, value=0, step=1000, key="exp_amount_input")
            exp_memo = st.text_input("메모", key="exp_memo_input", placeholder="메모")
            if st.button("💾 경비 등록", key="save_expense_btn", use_container_width=True, type="primary"):
                if exp_amt > 0:
                    append_expense({"id": str(uuid.uuid4()), "driver": exp_drv,
                        "date": exp_date.strftime("%Y-%m-%d"), "category": exp_cat,
                        "amount": int(exp_amt), "memo": exp_memo.strip(),
                        "saved_at": now_kst().strftime("%Y-%m-%d %H:%M:%S")})
                    st.success("등록 완료!")
                    st.rerun()

            # 삭제
            if st.button("🗑 선택 항목 삭제", key="del_exp_btn", use_container_width=False):
                st.session_state["_show_exp_del"] = True
            if st.session_state.get("_show_exp_del", False):
                _del_opts = [f"{e.get('date','')} | {e.get('driver','')} | {e.get('category','')} | {e.get('amount',0):,}원"
                             for e in _exp_filtered]
                _del_sel = st.selectbox("삭제할 항목", _del_opts, key="del_exp_select", label_visibility="collapsed")
                if st.button("삭제 확인", key="confirm_del_exp", use_container_width=True):
                    _del_idx = _del_opts.index(_del_sel)
                    delete_expense(_exp_filtered[_del_idx].get("id",""))
                    st.session_state["_show_exp_del"] = False
                    st.rerun()

            # CSV 다운로드
            st.download_button("📥 CSV", data=_exp_df.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"expenses_{now_kst().strftime('%Y%m%d')}.csv", mime="text/csv")
        else:
            st.info("등록된 경비가 없습니다.")

    st.markdown("---")

    # ── 출고일지 조회 ──
    st.markdown("### 📋 출고일지 조회")

    if delivery_logs:
        # 기사 필터
        _all_drvs = sorted(set(l.get("driver","") for l in delivery_logs))
        selected_driver_filter = st.radio("기사", ["전체"] + _all_drvs, horizontal=True,
                                          key="driver_filter_radio", label_visibility="collapsed")
        filtered_logs = delivery_logs if selected_driver_filter == "전체" else             [l for l in delivery_logs if l.get("driver") == selected_driver_filter]

        # 날짜 필터
        from datetime import date
        import calendar
        _today = date.today()
        _this_m = _today.replace(day=1)
        _prev_m = _today.replace(month=_today.month-1, day=1) if _today.month > 1 else _today.replace(year=_today.year-1, month=12, day=1)
        _prev_m_end = _today.replace(month=_today.month-1, day=calendar.monthrange(_today.year, _today.month-1)[1]) if _today.month > 1 else _today.replace(year=_today.year-1, month=12, day=31)

        qb1, qb2, qb3 = st.columns(3)
        with qb1:
            if st.button(f"당월({_today.strftime('%m')}월)", key="btn_this_month", use_container_width=True):
                st.session_state["filter_date_from"] = _this_m
                st.session_state["filter_date_to"] = _today
                st.rerun()
        with qb2:
            if st.button(f"전월({_prev_m.strftime('%m')}월)", key="btn_last_month", use_container_width=True):
                st.session_state["filter_date_from"] = _prev_m
                st.session_state["filter_date_to"] = _prev_m_end
                st.rerun()
        with qb3:
            if st.button("전체", key="btn_all_period", use_container_width=True):
                st.session_state.pop("filter_date_from", None)
                st.session_state.pop("filter_date_to", None)
                st.rerun()

        dt1, dt2 = st.columns(2)
        with dt1:
            date_from = st.date_input("시작일", key="filter_date_from")
        with dt2:
            date_to = st.date_input("종료일", key="filter_date_to")

        if date_from:
            filtered_logs = [l for l in filtered_logs if l.get("date","") >= date_from.strftime("%Y-%m-%d")]
        if date_to:
            filtered_logs = [l for l in filtered_logs if l.get("date","") <= date_to.strftime("%Y-%m-%d")]

        st.markdown(f"**조회 결과: {len(filtered_logs)}건**")

        # 기사별 수량
        if selected_driver_filter == "전체" and filtered_logs:
            _drv_sum = {}
            for l in filtered_logs:
                _drv_sum[l.get("driver","-")] = _drv_sum.get(l.get("driver","-"), 0) + int(l.get("quantity",0))
            _cols = st.columns(min(len(_drv_sum), 4))
            for i, (drv, tot) in enumerate(_drv_sum.items()):
                _cols[i % 4].metric(drv, f"{tot:,}개")

        # 목록 dataframe
        if filtered_logs:
            _sorted = sorted(filtered_logs, key=lambda x: (x.get("date",""), x.get("saved_at","")), reverse=True)
            _df = pd.DataFrame([{
                "출고일": l.get("date",""),
                "기사": l.get("driver",""),
                "거래처": l.get("customer",""),
                "품목": l.get("item","") + (f" / {l.get('size','')}" if l.get("size") else ""),
                "수량": l.get("quantity",0),
                "명세표": "📷" if l.get("attachment") else "-",
            } for l in _sorted])
            st.dataframe(_df, use_container_width=True, hide_index=True,
                         height=min(len(_df)*35+40, 420))

            # 편집
            with st.expander("✏️ 편집 / 삭제", expanded=False):
                _edit_labels = [
                    f"{l.get('date','')} | {l.get('driver','')} | {l.get('customer','')} | {l.get('item','')} | {l.get('quantity',0):,}개"
                    for l in _sorted]
                _sel = st.selectbox("편집할 항목", ["— 선택 —"] + _edit_labels,
                                    key="log_edit_select", label_visibility="collapsed")
                if _sel != "— 선택 —":
                    import base64 as _b64
                    _ei = _edit_labels.index(_sel)
                    _log = _sorted[_ei]
                    _lid = _log.get("id","")
                    _has_att = bool(_log.get("attachment"))

                    e1, e2 = st.columns(2)
                    with e1:
                        _new_c = st.selectbox("거래처", ["— 변경없음 —"] + _company_list, key="edit_log_cust")
                    with e2:
                        _new_i = st.text_input("품목명", value=_log.get("item",""), key="edit_log_item", label_visibility="collapsed")
                    _new_q = st.number_input("수량", value=int(_log.get("quantity",0)), min_value=0, step=1, key="edit_log_qty", label_visibility="collapsed")

                    s1, s2 = st.columns(2)
                    with s1:
                        if st.button("저장", key="save_log_edit", use_container_width=True, type="primary"):
                            _upd = {"quantity": int(_new_q), "item": _new_i.strip() or _log.get("item","")}
                            if _new_c != "— 변경없음 —": _upd["customer"] = _new_c
                            update_delivery_log(_lid, _upd)
                            st.success("수정 완료!")
                            st.rerun()
                    with s2:
                        if st.button("🗑 삭제", key="del_log_btn", use_container_width=True):
                            delete_delivery_log(_lid)
                            st.rerun()

                    # 명세표
                    if _has_att:
                        _img = _b64.b64decode(_log["attachment"])
                        _mime = _log.get("attachment_mime","image/jpeg")
                        st.image(_img, use_container_width=True)
                        _ext = "jpg" if "jpeg" in _mime else _mime.split("/")[-1]
                        ba1, ba2 = st.columns(2)
                        with ba1:
                            st.download_button("⬇️ 다운로드", data=_img,
                                file_name=f"명세표_{_log.get('customer','')}_{_log.get('date','')}.{_ext}",
                                mime=_mime, key="dl_attach_btn", use_container_width=True)
                        with ba2:
                            if st.button("🗑 명세표 삭제", key="del_attach_btn", use_container_width=True):
                                update_delivery_log(_lid, {"attachment": None, "attachment_mime": None})
                                st.rerun()
                        _new_att = st.file_uploader("교체", type=["jpg","jpeg","png","webp"], key="replace_attach_btn", label_visibility="collapsed")
                        if _new_att and st.button("교체 저장", key="save_replace_btn", use_container_width=True):
                            update_delivery_log(_lid, {"attachment": _b64.b64encode(_new_att.read()).decode(), "attachment_mime": _new_att.type})
                            st.rerun()
                    else:
                        _new_up = st.file_uploader("📎 명세표 첨부", type=["jpg","jpeg","png","webp"], key="upload_attach_btn", label_visibility="collapsed")
                        if _new_up and st.button("📎 저장", key="save_attach_btn", use_container_width=True, type="primary"):
                            update_delivery_log(_lid, {"attachment": _b64.b64encode(_new_up.read()).decode(), "attachment_mime": _new_up.type})
                            st.rerun()

            # CSV
            st.download_button(
                f"📥 CSV 다운로드",
                data=_df.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"delivery_{now_kst().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True,
            )
    else:
        st.info("아직 저장된 출고일지가 없습니다.")

# ══════════════════════════════════════════
# 탭: 견적/발주 입력
# ══════════════════════════════════════════

with tab_quote:
    st.session_state["current_tab"] = "quote"
    if not st.session_state.get("quote_unlocked", False):
        _pw_in2 = st.text_input("🔒 비밀번호", type="password", key="quote_pw_input",
                                placeholder="비밀번호를 입력하세요", label_visibility="collapsed")
        if _pw_in2 == "7191":
            st.session_state["quote_unlocked"] = True
            st.rerun()
        elif _pw_in2:
            st.error("비밀번호가 틀렸습니다.")
        else:
            st.markdown("<div style='text-align:center;padding:60px 0;'><div style='font-size:52px;'>🔒</div><div style='font-size:17px;font-weight:700;color:#6b7280;margin-top:10px;'>비밀번호를 입력하면 열립니다</div></div>", unsafe_allow_html=True)
    else:
        if st.button("🔓 잠금", key="lock_quote_btn"):
            st.session_state["quote_unlocked"] = False
            st.rerun()

        st.subheader("📝 견적/발주 입력")
        st.caption("거래처정보, 제품규격, 재질단가, 인쇄/가공비를 한 화면에서 입력합니다.")

        st.markdown("### 📋 견적 기본정보")

        all_customers = load_customers()

        if all_customers:
            cw1, cw2 = st.columns([5, 1])
            with cw1:
                cust_search_val = st.text_input(
                    "거래처 검색", value="", placeholder="🔍 거래처명 또는 담당자 검색",
                    label_visibility="collapsed", key="customer_search_input",
                )
            with cw2:
                if "show_all_customers" not in st.session_state:
                    st.session_state["show_all_customers"] = False
                toggle_label = "📋 닫기" if st.session_state["show_all_customers"] else "📋 전체보기"
                if st.button(toggle_label, use_container_width=True, key="toggle_all_customers"):
                    st.session_state["show_all_customers"] = not st.session_state["show_all_customers"]
                    st.rerun()

            display_customers = all_customers
            if cust_search_val.strip():
                q_cs = cust_search_val.strip().lower()
                display_customers = [
                    c for c in all_customers
                    if q_cs in str(c.get("company","")).lower() or q_cs in str(c.get("person","")).lower()
                ]
                if not display_customers:
                    st.caption("검색 결과가 없습니다.")
                show_list = True
            else:
                show_list = st.session_state.get("show_all_customers", False)

            if show_list and display_customers:
                st.markdown(f"<div style='font-size:17px;color:#6b7280;font-weight:700;margin:4px 0 6px 0;'>총 {len(display_customers)}개</div>", unsafe_allow_html=True)

                with st.container():
                    for ridx, c in enumerate(display_customers):
                        person_text = c.get('person','')
                        tel_text = c.get('customer_tel','')
                        pay_text = c.get('payment_terms','')
                        sub_parts = [x for x in [person_text, tel_text, pay_text] if x]
                        sub_line = " · ".join(sub_parts)

                        col_info, col_btns = st.columns([6, 1])
                        with col_info:
                            st.markdown(
                                f"<div style='padding:5px 2px;'>"
                                f"<div style='font-size:17px;font-weight:800;color:#111827;'>{c.get('company','-')}</div>"
                                f"<div style='font-size:17px;color:#6b7280;margin-top:1px;'>{sub_line}</div>"
                                f"</div>",
                                unsafe_allow_html=True,
                            )
                        with col_btns:
                            if st.button("✅", key=f"sel_cust_{ridx}", use_container_width=True, help=f"{c.get('company','')} 선택"):
                                for f in ["company","person","customer_tel","ref_text","payment_terms"]:
                                    st.session_state[f] = c.get(f,"")
                                st.session_state["show_all_customers"] = False
                                st.rerun()
                            if st.button("🗑", key=f"del_cust_{ridx}", use_container_width=True, help=f"{c.get('company','')} 삭제"):
                                delete_customer(c.get("id",""))
                                st.rerun()

                        st.markdown("<hr style='margin:1px 0;border:0;border-top:1px solid #f3f4f6;'>", unsafe_allow_html=True)

        q1, q2 = st.columns(2)
        with q1:
            company = st.text_input("거래처명", value=get_default("company",""), placeholder="예) 주식회사 까사홀딩스", key="company")
        with q2:
            person = st.text_input("담당자", value=get_default("person",""), placeholder="예) 홍길동", key="person")

        q3, q4 = st.columns(2)
        with q3:
            customer_tel = st.text_input("거래처 TEL/FAX", value=get_default("customer_tel","/"), key="customer_tel")
        with q4:
            ref_text = st.text_input("참조", value=get_default("ref_text",""), key="ref_text")

        q5, q6, q7 = st.columns(3)
        with q5:
            quote_no = st.text_input("일련번호", value=get_default("quote_no", f"{now_kst().strftime('%Y/%m/%d')}-1"), key="quote_no")
        with q6:
            payment_terms = st.text_input("결제조건", value=get_default("payment_terms",""), key="payment_terms")
        with q7:
            valid_until = st.text_input("유효기간", value=get_default("valid_until",""), key="valid_until")

        sv_c1, sv_c2 = st.columns([5, 1])
        with sv_c1:
            st.caption("현재 입력한 거래처 정보를 저장하면 다음번에 바로 불러올 수 있습니다.")
        with sv_c2:
            if st.button("💾 거래처 저장", use_container_width=True, key="save_customer_btn"):
                cur_company = st.session_state.get("company","")
                if not cur_company.strip():
                    st.warning("거래처명을 먼저 입력해 주세요.")
                else:
                    existing = next(
                        (c for c in load_customers() if c.get("company")==cur_company and c.get("person")==st.session_state.get("person","")),
                        None,
                    )
                    new_c = {
                        "id": existing["id"] if existing else str(uuid.uuid4()),
                        "company": cur_company,
                        "person": st.session_state.get("person",""),
                        "customer_tel": st.session_state.get("customer_tel",""),
                        "ref_text": st.session_state.get("ref_text",""),
                        "payment_terms": st.session_state.get("payment_terms",""),
                    }
                    upsert_customer(new_c)
                    st.success(f"'{cur_company}' 저장 완료!")
                    st.rerun()

        with st.expander("공급자 정보 / 비고", expanded=False):
            all_suppliers = load_suppliers()
            supplier_labels = [s.get("profile_name", s.get("supplier_name","")) for s in all_suppliers]

            pr1, pr2, pr3 = st.columns([4,1,1])
            with pr1:
                selected_profile_label = st.selectbox(
                    "저장된 공급자 프로필", options=supplier_labels, index=0,
                    key="supplier_profile_select", label_visibility="collapsed",
                )
            with pr2:
                if st.button("📥 불러오기", use_container_width=True, key="load_supplier_btn"):
                    sel_idx = supplier_labels.index(selected_profile_label)
                    sel = all_suppliers[sel_idx]
                    for f in ["supplier_name","business_no","ceo_name","supplier_manager","supplier_address","business_type","business_item","supplier_tel","supplier_fax"]:
                        st.session_state[f] = sel.get(f,"")
                    st.success(f"'{selected_profile_label}' 불러왔습니다.")
                    st.rerun()
            with pr3:
                sel_idx_d = supplier_labels.index(selected_profile_label)
                sel_id_d = all_suppliers[sel_idx_d].get("id","")
                if sel_id_d != "default":
                    if st.button("🗑️ 삭제", use_container_width=True, key="del_supplier_btn"):
                        delete_supplier(sel_id_d)
                        st.success("삭제했습니다.")
                        st.rerun()
                else:
                    st.caption("기본 프로필")

            st.divider()

            s1, s2 = st.columns(2)
            with s1:
                supplier_name = st.text_input("회사명", value=get_default("supplier_name","(주)대봉"), key="supplier_name")
                business_no = st.text_input("사업자등록번호", value=get_default("business_no","231-81-02595"), key="business_no")
                ceo_name = st.text_input("대표", value=get_default("ceo_name","임권일"), key="ceo_name")
                supplier_manager = st.text_input("공급자 담당자", value=get_default("supplier_manager",""), key="supplier_manager")
            with s2:
                supplier_address = st.text_input("주소", value=get_default("supplier_address","경기도 포천시 가산면 포천로912번길 175"), key="supplier_address")
                business_type = st.text_input("업태", value=get_default("business_type","제조업 도소매"), key="business_type")
                business_item = st.text_input("종목", value=get_default("business_item","합성수지"), key="business_item")
                supplier_tel = st.text_input("TEL", value=get_default("supplier_tel","031-544-0051"), key="supplier_tel")
                supplier_fax = st.text_input("FAX", value=get_default("supplier_fax","010.6613.0051"), key="supplier_fax")

            st.divider()
            sv1, sv2 = st.columns([4,1])
            with sv1:
                new_profile_name = st.text_input(
                    "새 프로필 이름", value="", placeholder="프로필 이름 입력 후 저장",
                    key="new_supplier_profile_name", label_visibility="collapsed",
                )
            with sv2:
                if st.button("➕ 프로필 저장", use_container_width=True, key="save_supplier_btn", type="primary"):
                    if not new_profile_name.strip():
                        st.warning("프로필 이름을 입력해 주세요.")
                    else:
                        upsert_supplier({
                            "id": str(uuid.uuid4()),
                            "profile_name": new_profile_name.strip(),
                            "supplier_name": st.session_state.get("supplier_name",""),
                            "business_no": st.session_state.get("business_no",""),
                            "ceo_name": st.session_state.get("ceo_name",""),
                            "supplier_manager": st.session_state.get("supplier_manager",""),
                            "supplier_address": st.session_state.get("supplier_address",""),
                            "business_type": st.session_state.get("business_type",""),
                            "business_item": st.session_state.get("business_item",""),
                            "supplier_tel": st.session_state.get("supplier_tel",""),
                            "supplier_fax": st.session_state.get("supplier_fax",""),
                        })
                        st.success(f"'{new_profile_name}' 저장 완료!")
                        st.rerun()

            memo = st.text_area(
                "비고 / 안내문",
                value=get_default("memo","1. 귀사의 일익 번창하심을 기원합니다.\n2. 하기와 같이 견적드리오니 검토하기 바랍니다."),
                key="memo",
            )

        st.divider()
        st.markdown("### 📦 제품규격 / 단가")

        p1, p2 = st.columns(2)
        with p1:
            item_name = st.text_input("견적서 품목명", value=get_default("item_name","HDPE 오픈봉투"), key="item_name")
        with p2:
            material_options = list(MATERIALS.keys())
            loaded_material = get_default("material","HDPE")
            material_index = material_options.index(loaded_material) if loaded_material in material_options else 0
            material = st.selectbox("재질", material_options, index=material_index, key="material")

        p3, p4 = st.columns(2)
        with p3:
            bag_options = ["오픈봉투","택배봉투"]
            loaded_bag = get_default("bag_type","오픈봉투")
            bag_index = bag_options.index(loaded_bag) if loaded_bag in bag_options else 0
            bag_type = st.selectbox("봉투 형태", bag_options, index=bag_index, key="bag_type")
        with p4:
            st.info("원단폭은 M가공이 합쳐진 총가로 기준입니다.")

        p5, p6, p7 = st.columns(3)
        with p5:
            thickness_um = st.number_input("원단두께 (㎛)", min_value=1, max_value=300, value=int(get_default("thickness_um",25)), step=1, format="%d", key="thickness_um")
        with p6:
            roll_width_cm = st.number_input("원단폭/총가로 (cm)", min_value=1, max_value=300, value=int(get_default("roll_width_cm",44)), step=1, format="%d", key="roll_width_cm")
        with p7:
            m_gusset_cm = st.number_input("M가공 합계 (cm)", min_value=0.0, max_value=200.0, value=float(get_default("m_gusset_cm",0.0)), step=0.5, format="%.1f", key="m_gusset_cm")

        p8, p9, p10 = st.columns(3)
        with p8:
            process_length_cm = st.number_input("가공길이 (cm)", min_value=1, max_value=300, value=int(get_default("process_length_cm",44)), step=1, format="%d", key="process_length_cm")
        with p9:
            roll_length_m = st.number_input("원단길이 (m/롤)", min_value=1, max_value=10000, value=int(get_default("roll_length_m",500)), step=10, format="%d", key="roll_length_m")
        with p10:
            manual_production_qty = st.number_input("제작수량 (장)", min_value=1, max_value=100_000_000, value=int(get_default("manual_production_qty",10000)), step=1000, key="manual_production_qty")

        mat_default = MATERIALS[material]
        p11, p12, p13 = st.columns(3)
        with p11:
            density = st.number_input("비중", min_value=0.1, max_value=2.0, value=float(get_default("density", mat_default["density"])), step=0.01, format="%.2f", key="density")
        with p12:
            extrusion_cost = st.number_input("압출비", min_value=0, max_value=10000, value=int(get_default("extrusion_cost", mat_default["extrusion"])), step=50, key="extrusion_cost")
        with p13:
            raw_price = st.number_input("원료값/kg", min_value=0, max_value=20000, value=int(get_default("raw_price", load_last_raw_price())), step=50, key="raw_price")

        p14, p15, p16 = st.columns(3)
        with p14:
            margin_percent = st.number_input("마진 (%)", min_value=0, max_value=300, value=int(get_default("margin_percent",15)), step=1, format="%d", key="margin_percent")
        with p15:
            manual_print_cost_500m = st.number_input("인쇄비 (원/500m)", min_value=0, max_value=10_000_000, value=int(get_default("manual_print_cost_500m",0)), step=1000, format="%d", key="manual_print_cost_500m")
        with p16:
            manual_open_processing_cost_500m = st.number_input("오픈 가공비 (원/500m)", min_value=0, max_value=10_000_000, value=int(get_default("manual_open_processing_cost_500m",0)), step=1000, format="%d", key="manual_open_processing_cost_500m")

        p17, p18, p19 = st.columns(3)
        with p17:
            print_count_display = st.number_input("인쇄도수 표시용", min_value=0, max_value=10, value=int(get_default("print_count_display",0)), step=1, key="print_count_display")
        with p18:
            roll_count = st.number_input("원단롤수", min_value=1, max_value=1000, value=int(get_default("roll_count",1)), step=1, key="roll_count")
        with p19:
            extra_processing_cost_500m = st.number_input("기타 추가가공비", min_value=0, max_value=10_000_000, value=int(get_default("extra_processing_cost_500m",0)), step=1000, format="%d", key="extra_processing_cost_500m")

        if bag_type == "택배봉투":
            adhesive_processing_cost_per_cm_ea = st.number_input(
                "접착 가공비 단가 (원/cm·장)", min_value=0.0, max_value=100.0,
                value=float(get_default("adhesive_processing_cost_per_cm_ea",0.4)), step=0.05, format="%.2f", key="adhesive_processing_cost_per_cm_ea",
            )
            st.info(f"접착 가공비 청구 기준: {process_length_cm:g}cm × {adhesive_processing_cost_per_cm_ea:g}원/cm = {process_length_cm * adhesive_processing_cost_per_cm_ea:,.2f}원/장")
        else:
            adhesive_processing_cost_per_cm_ea = 0.0

        thickness_mm_preview = thickness_um / 1000
        m_text_preview = make_m_text(m_gusset_cm)
        actual_size_text = f"{thickness_mm_preview:.3f} × {roll_width_cm:g}{m_text_preview} × {process_length_cm:g}cm"
        roll_spec_text = f"{thickness_mm_preview:.3f} × {roll_width_cm:g}{m_text_preview} × {roll_length_m:g}m"
        weight_preview = density * (thickness_um * 0.001) * roll_width_cm * roll_length_m * 2 / 100
        qty_per_roll_preview = int(rounddown((roll_length_m * 100) / process_length_cm, -2)) if process_length_cm else 0

        preview_df = pd.DataFrame([
            ["실제 가공사이즈", actual_size_text],
            ["원단 규격", roll_spec_text],
            ["원단 중량", f"{weight_preview:,.2f} kg/롤"],
            ["1롤당 수량", f"{qty_per_roll_preview:,} 장"],
        ], columns=["항목","내용"])

        with st.expander("📏 실제 가공사이즈 / 원단 규격 보기", expanded=False):
            show_white_table(preview_df)

        st.caption("인쇄도수는 표시용 및 동판비 계산용입니다. 인쇄비는 수기입력 금액이 그대로 반영됩니다.")
        st.divider()

        if st.button("💰 견적 계산", use_container_width=True, type="primary"):
            save_last_raw_price(raw_price)
            r = calc_quote(
                bag_type=bag_type, thickness_um=thickness_um, roll_width_cm=roll_width_cm,
                m_gusset_cm=m_gusset_cm, process_length_cm=process_length_cm, roll_length_m=roll_length_m,
                print_count_display=print_count_display, manual_print_cost_500m=manual_print_cost_500m,
                manual_open_processing_cost_500m=manual_open_processing_cost_500m,
                adhesive_processing_cost_per_cm_ea=adhesive_processing_cost_per_cm_ea,
                extra_processing_cost_500m=extra_processing_cost_500m, margin_percent=margin_percent,
                roll_count=roll_count, manual_production_qty=manual_production_qty,
                raw_price=raw_price, extrusion_cost=extrusion_cost, density=density,
            )
            st.session_state["last_quote_result"] = r

            st.markdown(
                f"""
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
                    <span style="font-size:22px;font-weight:900;">📊 견적 결과</span>
                    <span style="font-size:17px;color:#6b7280;font-weight:600;">거래처: {company or '-'} &nbsp;|&nbsp; 담당자: {person or '-'} &nbsp;|&nbsp; {now_kst().strftime('%Y-%m-%d')}</span>
                </div>
                <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:10px 16px;margin-bottom:16px;font-size:16px;font-weight:700;color:#1d4ed8;">
                    📦 &nbsp;{r['actual_size_text']}
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px;">
                    <div style="border:1.5px solid #e5e7eb;border-radius:10px;padding:14px 18px;background:#f9fafb;">
                        <div style="font-size:16px;color:#6b7280;font-weight:700;margin-bottom:4px;">장당 견적가</div>
                        <div style="font-size:28px;font-weight:900;">{r['unit_quote']:,.1f} 원</div>
                    </div>
                    <div style="border:1.5px solid #e5e7eb;border-radius:10px;padding:14px 18px;background:#f9fafb;">
                        <div style="font-size:16px;color:#6b7280;font-weight:700;margin-bottom:4px;">제작 수량</div>
                        <div style="font-size:28px;font-weight:900;">{r['production_qty']:,} 장</div>
                    </div>
                </div>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:14px;">
                    <div style="border:1.5px solid #e5e7eb;border-radius:10px;padding:14px 18px;background:#fff;text-align:center;">
                        <div style="font-size:16px;color:#6b7280;font-weight:700;margin-bottom:6px;">공급가액</div>
                        <div style="font-size:22px;font-weight:900;">{r['supply_amount']:,.0f} 원</div>
                    </div>
                    <div style="border:1.5px solid #e5e7eb;border-radius:10px;padding:14px 18px;background:#fff;text-align:center;">
                        <div style="font-size:16px;color:#6b7280;font-weight:700;margin-bottom:6px;">동판비</div>
                        <div style="font-size:22px;font-weight:900;">{r['plate_amount']:,.0f} 원</div>
                    </div>
                    <div style="border:1.5px solid #3b82f6;border-radius:10px;padding:14px 18px;background:#eff6ff;text-align:center;">
                        <div style="font-size:16px;color:#2563eb;font-weight:700;margin-bottom:6px;">합계금액 (VAT 별도)</div>
                        <div style="font-size:26px;font-weight:900;color:#1d4ed8;">{r['total_amount']:,.0f} 원</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            detail_items = [
                ("재질", material), ("봉투 형태", bag_type),
                ("실제 가공사이즈", r["actual_size_text"]), ("원단 규격", r["roll_spec_text"]),
                ("원단 중량", f"{r['weight_roll']:,.3f} kg/롤"), ("1롤당 수량", f"{r['qty_per_roll']:,.0f} 장"),
                ("제작수량 입력값", f"{manual_production_qty:,} 장"), ("롤 기준 자동 제작수량", f"{r['auto_production_qty']:,} 장"),
                ("원단두께", f"{thickness_um:g} ㎛"), ("원단폭/총가로", f"{roll_width_cm:g} cm"),
                ("M가공 합계", f"{m_gusset_cm:g} cm"), ("가공길이", f"{process_length_cm:g} cm"),
                ("원단길이", f"{roll_length_m:g} m/롤"), ("인쇄도수 표시용", f"{print_count_display} 도"),
                ("원단롤수", f"{roll_count} 롤"), ("마진", f"{margin_percent:g} %"),
                ("인쇄비 수기입력/500m", f"{r['print_cost_500m']:,.0f} 원"),
                ("오픈 가공비 수기입력", f"{manual_open_processing_cost_500m:,.0f} 원/500m"),
                ("오픈 가공비 합계/500m", f"{r['open_process_cost_500m']:,.0f} 원"),
            ]
            if bag_type == "택배봉투":
                detail_items.extend([
                    ("접착 가공비 단가", f"{adhesive_processing_cost_per_cm_ea:,.2f} 원/cm·장"),
                    ("접착 가공비 합계/장", f"{r['adhesive_process_cost_ea']:,.2f} 원"),
                ])
            detail_items.extend([
                ("기타 추가가공비/500m", f"{extra_processing_cost_500m:,.0f} 원"),
                ("500m 환산 중량", f"{r['weight_500m']:,.3f} kg"),
                ("원단원가/500m", f"{r['fabric_cost_500m']:,.0f} 원"),
                ("원단원가/롤", f"{r['fabric_cost_roll']:,.0f} 원"),
                ("원단견적/롤", f"{r['fabric_quote_per_roll']:,.0f} 원"),
                ("인쇄 동판비/도", f"{r['plate_cost_per_color']:,.0f} 원"),
                ("인쇄 동판비 합계", f"{r['plate_cost_total']:,.0f} 원"),
                ("오픈가공전/500m", f"{r['open_before_500m']:,.0f} 원"),
                ("접착가공전/500m", f"{r['adhesive_before_500m']:,.0f} 원"),
                ("가공매수/500m", f"{r['process_count_500m']:,.0f} 장"),
                ("오픈장당원가", f"{r['open_unit_cost']:,.3f} 원"),
                ("접착장당원가", f"{r['adhesive_unit_cost']:,.3f} 원"),
                ("오픈봉투 기준가", f"{r['open_bag_cost']:,.2f} 원"),
                ("택배봉투 기준가", f"{r['adhesive_bag_cost']:,.2f} 원"),
                ("장당견적", f"{r['unit_quote']:,.1f} 원"),
                ("제작수량", f"{r['production_qty']:,} 장"),
                ("제품 공급가액", f"{r['supply_amount']:,.0f} 원"),
                ("동판비", f"{r['plate_amount']:,.0f} 원"),
                ("합계금액", f"{r['total_amount']:,.0f} 원"),
            ])

            detail_df = pd.DataFrame(detail_items, columns=["항목","내용"])

            with st.expander("상세 계산내역 보기", expanded=False):
                show_white_table(detail_df)

            quote_text = f"""대봉 비닐류 견적서\n\n거래처: {company or '-'}\n담당자: {person or '-'}\n작성일: {now_kst().strftime('%Y-%m-%d')}\n\n[제품]\n재질: {material}\n봉투 형태: {bag_type}\n실제 가공사이즈: {r['actual_size_text']}\n원단 규격: {r['roll_spec_text']}\n원단 중량: {r['weight_roll']:,.3f} kg/롤\n1롤당 수량: {r['qty_per_roll']:,.0f} 장\n\n[견적]\n장당견적: {r['unit_quote']:,.1f} 원\n제작수량: {r['production_qty']:,} 장\n제품 공급가액: {r['supply_amount']:,.0f} 원\n동판비: {r['plate_amount']:,.0f} 원\n합계금액: {r['total_amount']:,.0f} 원\n"""
            st.download_button("📥 견적서 TXT 다운로드", data=quote_text.encode("utf-8-sig"), file_name=f"daebong_quote_{now_kst().strftime('%Y%m%d')}.txt", mime="text/plain", use_container_width=True)
            st.download_button("📥 상세내역 CSV 다운로드", data=detail_df.to_csv(index=False).encode("utf-8-sig"), file_name=f"daebong_quote_detail_{now_kst().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)

        quote_result_for_items = st.session_state.get("last_quote_result")
        if "quote_items" not in st.session_state:
            st.session_state["quote_items"] = []

        if quote_result_for_items is not None:
            st.divider()
            st.subheader("📋 다품목 견적 목록")
            st.caption("견적 계산 후 현재 품목을 목록에 추가하면 한 견적서에 여러 품목을 넣을 수 있습니다.")

            add_item_data = {
                "id": str(uuid.uuid4()), "item_name": item_name, "material": material,
                "bag_type": bag_type, "actual_size_text": quote_result_for_items["actual_size_text"],
                "roll_spec_text": quote_result_for_items["roll_spec_text"],
                "unit_quote": quote_result_for_items["unit_quote"],
                "production_qty": quote_result_for_items["production_qty"],
                "supply_amount": quote_result_for_items["supply_amount"],
                "plate_unit": quote_result_for_items["plate_amount"],
                "plate_qty": 1 if quote_result_for_items["plate_amount"] > 0 else 0,
                "plate_amount": quote_result_for_items["plate_amount"],
                "total_amount": quote_result_for_items["total_amount"],
                "thickness_um": thickness_um, "roll_width_cm": roll_width_cm,
                "m_gusset_cm": m_gusset_cm, "process_length_cm": process_length_cm,
                "roll_length_m": roll_length_m, "manual_production_qty": manual_production_qty,
                "print_count_display": print_count_display, "roll_count": roll_count,
                "density": density, "extrusion_cost": extrusion_cost, "raw_price": raw_price,
                "margin_percent": margin_percent, "manual_print_cost_500m": manual_print_cost_500m,
                "manual_open_processing_cost_500m": manual_open_processing_cost_500m,
                "adhesive_processing_cost_per_cm_ea": adhesive_processing_cost_per_cm_ea,
                "extra_processing_cost_500m": extra_processing_cost_500m,
            }

            i1, i2, i3 = st.columns(3)
            with i1:
                if st.button("➕ 현재 품목을 견적목록에 추가", use_container_width=True):
                    st.session_state["quote_items"].append(add_item_data)
                    st.success("현재 품목을 견적목록에 추가했습니다.")
                    st.rerun()
            with i2:
                if st.button("🧹 품목 목록 전체 비우기", use_container_width=True):
                    st.session_state["quote_items"] = []
                    st.success("품목 목록을 비웠습니다.")
                    st.rerun()
            with i3:
                st.info(f"현재 목록: {len(st.session_state['quote_items'])}개")

        if st.session_state.get("quote_items"):
            item_rows = []
            for idx, item in enumerate(st.session_state["quote_items"], start=1):
                item_rows.append({
                    "순번": idx, "품목명": item.get("item_name",""),
                    "규격": item.get("actual_size_text",""),
                    "수량": f"{item.get('production_qty',0):,}",
                    "장당가": f"{item.get('unit_quote',0):,.1f}",
                    "공급가액": f"{item.get('supply_amount',0):,.0f}",
                    "동판비": f"{item.get('plate_amount',0):,.0f}",
                    "합계": f"{item.get('total_amount',0):,.0f}",
                })

            show_white_table(pd.DataFrame(item_rows))

            delete_options = [
                f"{idx+1}. {item.get('item_name','')} / {item.get('actual_size_text','')}"
                for idx, item in enumerate(st.session_state["quote_items"])
            ]
            d1, d2 = st.columns([3,1])
            with d1:
                delete_target = st.selectbox("삭제할 품목 선택", delete_options, key="delete_quote_item_select")
            with d2:
                if st.button("선택 품목 삭제", use_container_width=True):
                    del_idx = delete_options.index(delete_target)
                    st.session_state["quote_items"].pop(del_idx)
                    st.success("선택한 품목을 삭제했습니다.")
                    st.rerun()

            items_supply_sum = sum(float(item.get("supply_amount",0)) for item in st.session_state["quote_items"])
            items_plate_sum = sum(float(item.get("plate_amount",0)) for item in st.session_state["quote_items"])
            items_total_sum = sum(float(item.get("total_amount",0)) for item in st.session_state["quote_items"])
            items_qty_sum = sum(int(item.get("production_qty",0)) for item in st.session_state["quote_items"])

            m1,m2,m3,m4 = st.columns(4)
            m1.metric("총 품목수", f"{len(st.session_state['quote_items'])}개")
            m2.metric("총 수량", f"{items_qty_sum:,} 장")
            m3.metric("공급가액 합계", f"{items_supply_sum:,.0f} 원")
            m4.metric("전체 합계", f"{items_total_sum:,.0f} 원")

            multi_detail_df = pd.DataFrame(item_rows)
            st.download_button(
                "📥 다품목 견적 CSV 다운로드",
                data=multi_detail_df.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"daebong_multi_quote_{now_kst().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True,
            )

        quote_result = st.session_state.get("last_quote_result")
        quote_items_for_save = st.session_state.get("quote_items", [])

        if quote_result is not None or quote_items_for_save:
            if quote_items_for_save:
                first_item = quote_items_for_save[0]
                order_item_name = first_item.get("item_name","")
                if len(quote_items_for_save) > 1:
                    order_item_name = f"{order_item_name} 외 {len(quote_items_for_save)-1}건"
                order_actual_size = first_item.get("actual_size_text","")
                if len(quote_items_for_save) > 1:
                    order_actual_size = "여러 품목"
                order_unit_quote = 0
                order_qty = sum(int(item.get("production_qty",0)) for item in quote_items_for_save)
                order_supply = sum(float(item.get("supply_amount",0)) for item in quote_items_for_save)
                order_plate = sum(float(item.get("plate_amount",0)) for item in quote_items_for_save)
                order_total = sum(float(item.get("total_amount",0)) for item in quote_items_for_save)
                order_roll_spec = first_item.get("roll_spec_text","")
                order_items = quote_items_for_save
            else:
                order_item_name = item_name
                order_actual_size = quote_result["actual_size_text"]
                order_unit_quote = quote_result["unit_quote"]
                order_qty = quote_result["production_qty"]
                order_supply = quote_result["supply_amount"]
                order_plate = quote_result["plate_amount"]
                order_total = quote_result["total_amount"]
                order_roll_spec = quote_result["roll_spec_text"]
                order_items = [{
                    "id": str(uuid.uuid4()), "item_name": item_name, "material": material,
                    "bag_type": bag_type, "actual_size_text": quote_result["actual_size_text"],
                    "roll_spec_text": quote_result["roll_spec_text"],
                    "unit_quote": quote_result["unit_quote"],
                    "production_qty": quote_result["production_qty"],
                    "supply_amount": quote_result["supply_amount"],
                    "plate_unit": quote_result["plate_amount"],
                    "plate_qty": 1 if quote_result["plate_amount"] > 0 else 0,
                    "plate_amount": quote_result["plate_amount"],
                    "total_amount": quote_result["total_amount"],
                }]

            order_data = {
                "id": st.session_state.get("loaded_order_id", str(uuid.uuid4())),
                "saved_at": now_kst().strftime("%Y-%m-%d %H:%M"),
                "quote_no": quote_no, "company": company, "person": person,
                "customer_tel": customer_tel, "ref_text": ref_text,
                "payment_terms": payment_terms, "valid_until": valid_until, "memo": memo,
                "supplier_name": supplier_name, "business_no": business_no,
                "ceo_name": ceo_name, "supplier_manager": supplier_manager,
                "supplier_address": supplier_address, "business_type": business_type,
                "business_item": business_item, "supplier_tel": supplier_tel, "supplier_fax": supplier_fax,
                "material": material, "bag_type": bag_type, "thickness_um": thickness_um,
                "roll_width_cm": roll_width_cm, "m_gusset_cm": m_gusset_cm,
                "process_length_cm": process_length_cm, "roll_length_m": roll_length_m,
                "print_count_display": print_count_display, "roll_count": roll_count,
                "manual_production_qty": manual_production_qty, "item_name": order_item_name,
                "density": density, "extrusion_cost": extrusion_cost, "raw_price": raw_price,
                "margin_percent": margin_percent, "manual_print_cost_500m": manual_print_cost_500m,
                "manual_open_processing_cost_500m": manual_open_processing_cost_500m,
                "adhesive_processing_cost_per_cm_ea": adhesive_processing_cost_per_cm_ea,
                "extra_processing_cost_500m": extra_processing_cost_500m,
                "actual_size_text": order_actual_size, "roll_spec_text": order_roll_spec,
                "unit_quote": order_unit_quote, "production_qty": order_qty,
                "supply_amount": order_supply, "plate_amount": order_plate,
                "total_amount": order_total, "items": order_items,
            }

            save_caption = "✅ 다품목 발주서 확정 저장" if quote_items_for_save else "✅ 발주서 확정 저장"
            if st.button(save_caption, use_container_width=True, type="primary"):
                upsert_order(order_data)
                st.session_state["loaded_order_id"] = order_data["id"]
                st.success("발주서가 저장되었습니다. '저장된 견적서' 탭에서 확인할 수 있습니다.")
        else:
            st.info("먼저 견적 계산을 누르면 발주서 확정 저장 버튼이 나타납니다.")
