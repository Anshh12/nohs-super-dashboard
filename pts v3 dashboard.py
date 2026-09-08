"""
North Delhi Household Listing — Analytics Dashboard
====================================================
Comprehensive 9-tab Streamlit dashboard for REDCap household-listing data,
styled to match the OralHealth Analytics Pro design language
(dark sidebar, Inter + Playfair Display, KPI cards with accent borders).

Run with:  streamlit run app.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# ── PAGE CONFIG ──
st.set_page_config(page_title="HouseholdListing Analytics Pro", page_icon="🏘️",
                   layout="wide", initial_sidebar_state="expanded")

# ── CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:#f8fafc;}
[data-testid="stSidebar"]{background:linear-gradient(160deg,#0f172a 0%,#1e293b 100%);border-right:none;}
[data-testid="stSidebar"] *{color:#cbd5e1 !important;}
[data-testid="stSidebar"] .stSelectbox label,[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stDateInput label,[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3{
color:#64748b !important;font-size:.72rem !important;text-transform:uppercase !important;letter-spacing:.08em !important;font-weight:600 !important;}
.kpi{background:white;border-radius:14px;padding:18px 22px;box-shadow:0 1px 3px rgba(0,0,0,.05);border-left:4px solid #3b82f6;margin-bottom:6px;}
.kpi.g{border-left-color:#10b981}.kpi.p{border-left-color:#8b5cf6}.kpi.o{border-left-color:#f59e0b}.kpi.r{border-left-color:#ef4444}.kpi.c{border-left-color:#06b6d4}
.kpi-l{font-size:.7rem;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:#64748b;margin-bottom:4px;}
.kpi-v{font-family:'Playfair Display',serif;font-size:2rem;color:#0f172a;line-height:1;}
.kpi-d{font-size:.75rem;color:#94a3b8;margin-top:3px;}
.sec{font-family:'Playfair Display',serif;font-size:1.25rem;color:#0f172a;margin:24px 0 12px;padding-bottom:6px;border-bottom:2px solid #e2e8f0;}
.stTabs [data-baseweb="tab-list"]{gap:2px;background:#e2e8f0;padding:3px;border-radius:10px;}
.stTabs [data-baseweb="tab"]{border-radius:8px;padding:6px 14px;font-weight:500;font-size:.8rem;}
.stTabs [aria-selected="true"]{background:white !important;box-shadow:0 1px 4px rgba(0,0,0,.08);}
hr{border-color:#e2e8f0;margin:16px 0;}
.alert-r{background:#fef2f2;border-left:4px solid #ef4444;padding:10px 14px;border-radius:6px;color:#7f1d1d;font-size:.85rem;margin:8px 0;}
.alert-o{background:#fffbeb;border-left:4px solid #f59e0b;padding:10px 14px;border-radius:6px;color:#78350f;font-size:.85rem;margin:8px 0;}
.alert-g{background:#f0fdf4;border-left:4px solid #10b981;padding:10px 14px;border-radius:6px;color:#14532d;font-size:.85rem;margin:8px 0;}
</style>""", unsafe_allow_html=True)

# ── HELPERS ──
C = ["#3b82f6","#10b981","#8b5cf6","#f59e0b","#ef4444","#06b6d4","#ec4899","#14b8a6","#f97316","#6366f1"]
LY = dict(paper_bgcolor="white",plot_bgcolor="white",
          font=dict(family="Inter",size=11,color="#334155"),
          margin=dict(l=10,r=10,t=40,b=10))

def kpi(l, v, c="", d=""):
    st.markdown(
        f'<div class="kpi {c}"><div class="kpi-l">{l}</div><div class="kpi-v">{v}</div>'
        f'{"<div class=kpi-d>"+d+"</div>" if d else ""}</div>',
        unsafe_allow_html=True,
    )

def sec(t):
    st.markdown(f'<div class="sec">{t}</div>', unsafe_allow_html=True)

def alert(msg, kind="r"):
    st.markdown(f'<div class="alert-{kind}">{msg}</div>', unsafe_allow_html=True)

def pie(s, t, h=320):
    vc = s.value_counts().reset_index(); vc.columns = ["l","c"]
    f = px.pie(vc, names="l", values="c", title=t, color_discrete_sequence=C, hole=.45)
    f.update_traces(textposition="outside", textinfo="percent+label")
    f.update_layout(**LY, title_font_size=13, showlegend=False, height=h)
    return f

def bar(s, t, o="v", clr="#3b82f6", h=320):
    vc = s.value_counts().reset_index(); vc.columns = ["l","c"]
    if o == "h":
        vc = vc.sort_values("c")
        f = px.bar(vc, x="c", y="l", orientation="h", title=t, color_discrete_sequence=[clr])
    else:
        f = px.bar(vc, x="l", y="c", title=t, color_discrete_sequence=[clr])
    f.update_layout(**LY, title_font_size=13, height=h,
                    xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#f1f5f9"))
    f.update_traces(marker_line_width=0)
    return f

def grp_bar(df, x, color, t, h=340):
    ct = pd.crosstab(df[x], df[color]); fig = go.Figure()
    for i, col in enumerate(ct.columns):
        fig.add_trace(go.Bar(name=str(col), x=ct.index.astype(str), y=ct[col],
                             marker_color=C[i % len(C)], marker_line_width=0))
    fig.update_layout(**LY, barmode="group", height=h, title=t, title_font_size=13,
                      xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f1f5f9"),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02))
    return fig

def clean_cluster_val(v):
    if v in ("Non-Identified", "(missing)"): return v
    try:
        f = float(v)
        if f == int(f): return str(int(f))
    except (ValueError, TypeError):
        pass
    return str(v)

def find_col(keywords, cols):
    for c in cols:
        for kw in keywords:
            if kw.lower() in c.lower(): return c
    return None

# ── SIDEBAR ──
with st.sidebar:
    st.markdown(
        '<div style="padding:14px 0 18px;">'
        '<div style="font-family:Playfair Display,serif;font-size:1.3rem;color:white;">🏘️ HouseholdListing Pro</div>'
        '<div style="font-size:.7rem;color:#64748b;margin-top:2px;">North Delhi · Comprehensive Analytics</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
    st.markdown("---")

if not uploaded:
    st.markdown(
        '<div style="font-family:Playfair Display,serif;font-size:2.2rem;color:#0f172a;">🏘️ HouseholdListing Analytics Pro</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="color:#64748b;margin-bottom:20px;">Upload your REDCap CSV (DATA LABELS export) from the sidebar to begin comprehensive analysis.</div>',
        unsafe_allow_html=True,
    )
    st.info("📁 Upload `NorthDelhiHouseholdL_DATA_LABELS_*.csv` to unlock all 10 analysis tabs.")
    st.markdown("""
#### What you'll get
- **Overview KPIs** — households, members, completion %, GPS capture %, substitution %
- **Cluster-wise analysis** — scorecards, completion & GPS rates, status × cluster heatmap
- **Enumerator performance** — productivity, scorecards, daily activity lines
- **Daily progress** — listing curve, cumulative households, weekday productivity
- **Enumerator work hours** — daily duration, consistency, start/end times (if timestamps exist)
- **Member demographics** — gender, age pyramid, occupation, education
- **Sampling coverage** — NDOHS 4 age groups (4–6, 12–15, 35–44, 65–74)
- **GPS & Tablet location audit** — which tablet/enumerator/cluster has missing GPS
- **Data quality flags** — 8 automated checks with downloads
- **Drill-down** — search any household, view full member list + GPS + substitution chain
    """)
    st.stop()

# ── LOAD DATA ──
@st.cache_data(show_spinner="Loading…")
def load(f):
    return pd.read_csv(f, low_memory=False)

raw = load(uploaded)

# ── SPLIT HOUSEHOLD vs MEMBER ROWS ──
ri_col = "Repeat Instrument"
if ri_col not in raw.columns:
    st.error("❌ CSV must contain a 'Repeat Instrument' column. Re-export from REDCap with labels.")
    st.stop()

hh_all = raw[raw[ri_col].isna() | (raw[ri_col].astype(str).str.strip() == "")].copy()
mbr_all = raw[raw[ri_col].astype(str).str.strip() == "Household Member"].copy()

# ── COLUMN AUTO-DETECT ──
col_id       = find_col(["Record ID", "record_id"], raw.columns) or raw.columns[0]
col_cluster  = find_col(["Cluster Code", "cluster_code", "cluster"], raw.columns)
col_date     = find_col(["Listing Date", "listing_date"], raw.columns)
col_enum     = find_col(["Enumerator Username/number", "Enumerator", "enumerator"], raw.columns)
col_hh_num   = find_col(["Household Number", "household_number"], raw.columns)
col_samp_num = find_col(["Sample Number", "sample_number"], raw.columns)
col_substituted = find_col(["Is this household a substitution", "is_substituted"], raw.columns)
col_sub_from = find_col(["Substituted From", "substituted_from"], raw.columns)
col_sub_reason = find_col(["Reason for Substitution", "substitution_reason"], raw.columns)
col_hh_status = find_col(["Household Status", "household_status"], raw.columns)
col_lat       = find_col(["Latitude (Auto", "gps_latitude", "Latitude"], raw.columns)
col_lon       = find_col(["Longitude (Auto", "gps_longitude", "Longitude"], raw.columns)
col_acc       = find_col(["GPS Accuracy", "gps_accuracy"], raw.columns)
col_maps      = find_col(["Google Maps", "maps_link", "gps_maps_link"], raw.columns)

col_mname    = find_col(["Member Name", "member_name"], raw.columns)
col_mage     = find_col(["Member Age", "member_age"], raw.columns)
col_mgender  = find_col(["Member Gender", "member_gender"], raw.columns)
col_mocc     = find_col(["Member Occupation", "member_occupation"], raw.columns)
col_medu     = find_col(["Member Education", "member_education"], raw.columns)
col_msamp    = find_col(["Member Sampling Group", "member_sampling_group"], raw.columns)
col_msel     = find_col(["Selected for sampling", "member_selected"], raw.columns)
col_minst    = find_col(["Repeat Instance"], raw.columns)

# ── PREPROCESS ──
hh_all["_date"] = pd.to_datetime(hh_all[col_date], errors="coerce") if col_date else pd.NaT
for c in (col_cluster, col_enum, col_samp_num):
    if c and c in hh_all.columns:
        hh_all[c] = pd.to_numeric(hh_all[c], errors="coerce").astype("Int64")

if col_cluster and col_cluster in hh_all.columns:
    hh_all["_cluster"] = hh_all[col_cluster].astype(str).apply(clean_cluster_val).replace({"<NA>": "(missing)", "nan": "(missing)"})
else:
    hh_all["_cluster"] = "(missing)"

if col_mage and col_mage in mbr_all.columns:
    mbr_all[col_mage] = pd.to_numeric(mbr_all[col_mage], errors="coerce")

# ── SIDEBAR FILTERS ──
with st.sidebar:
    st.markdown("### Filters")

    if hh_all["_date"].notna().any():
        mn, mx = hh_all["_date"].min().date(), hh_all["_date"].max().date()
        dr = st.date_input("Date Range", value=(mn, mx), min_value=mn, max_value=mx)
        if isinstance(dr, (list, tuple)) and len(dr) == 2:
            hh_all = hh_all[((hh_all["_date"].dt.date >= dr[0]) & (hh_all["_date"].dt.date <= dr[1])) | hh_all["_date"].isna()]

    clusters = sorted(hh_all["_cluster"].dropna().unique(), key=lambda x: (x == "(missing)", str(x)))
    sel_clusters = st.multiselect("Cluster", clusters, default=clusters)

    enums = sorted(e for e in hh_all[col_enum].dropna().unique()) if col_enum else []
    sel_enums = st.multiselect("Enumerator", enums, default=enums) if enums else []

    statuses = list(hh_all[col_hh_status].dropna().unique()) if col_hh_status else []
    sel_status = st.multiselect("Household Status", statuses, default=statuses) if statuses else []

    mask = hh_all["_cluster"].isin(sel_clusters)
    if sel_enums: mask &= hh_all[col_enum].isin(sel_enums)
    if sel_status: mask &= hh_all[col_hh_status].isin(sel_status)
    hh = hh_all[mask].copy()
    record_ids = hh[col_id].unique()
    mbr = mbr_all[mbr_all[col_id].isin(record_ids)].copy()

    st.markdown("---")
    st.markdown(
        f'<div style="font-size:.72rem;color:#64748b;">📊 {len(hh)} households · {len(mbr)} members</div>',
        unsafe_allow_html=True,
    )

# ── HEADER ──
st.markdown(
    '<div style="font-family:Playfair Display,serif;font-size:1.9rem;color:#0f172a;">🏘️ HouseholdListing Analytics Pro</div>',
    unsafe_allow_html=True,
)
date_window = ""
if hh["_date"].notna().any():
    date_window = (f"{hh['_date'].min().strftime('%d %b %Y')} – "
                   f"{hh['_date'].max().strftime('%d %b %Y')} "
                   f"({(hh['_date'].max() - hh['_date'].min()).days + 1} days) · ")
st.markdown(
    f'<div style="color:#64748b;font-size:.85rem;margin-bottom:20px;">North Delhi Household Listing · {date_window}{datetime.now().strftime("%d %b %Y, %I:%M %p")}</div>',
    unsafe_allow_html=True,
)

# ── KPI ROW ──
completed = (hh[col_hh_status] == "Completed").sum() if col_hh_status else 0
completion_pct = completed / len(hh) * 100 if len(hh) else 0
gps_captured = hh[col_lat].notna().sum() if col_lat else 0
gps_pct = gps_captured / len(hh) * 100 if len(hh) else 0
substituted = (hh[col_substituted] == "Yes").sum() if col_substituted else 0
sub_pct = substituted / len(hh) * 100 if len(hh) else 0

k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1: kpi("Households", f"{len(hh):,}")
with k2: kpi("Members", f"{len(mbr):,}", "g")
with k3: kpi("Clusters", f"{hh['_cluster'].nunique()}", "p")
with k4: kpi("Completed", f"{completed}", "g", f"{completion_pct:.0f}%")
with k5: kpi("GPS Captured", f"{gps_captured}", "c" if gps_pct >= 90 else "r", f"{gps_pct:.0f}%")
with k6: kpi("Substituted", f"{substituted}", "o", f"{sub_pct:.0f}%")
st.markdown("")

# ── TABS (10 tabs now) ──
tabs = st.tabs([
    "📊 Overview", "🗺️ Cluster", "👥 Enumerator", "📈 Progress",
    "⏱️ Work Hours",  # <-- new tab inserted here
    "👨‍👩‍👧 Demographics", "🎯 Sampling", "📍 GPS & Tablet",
    "🔍 Data Quality", "🔎 Drill-down",
])

# ═══ TAB 0: OVERVIEW ═══
with tabs[0]:
    sec("Survey Composition")
    c1, c2 = st.columns(2)
    with c1:
        if col_hh_status and hh[col_hh_status].notna().any():
            st.plotly_chart(pie(hh[col_hh_status].dropna(), "Household Status", 360), use_container_width=True)
    with c2:
        cl_counts = hh["_cluster"].value_counts().reset_index()
        cl_counts.columns = ["Cluster", "Households"]
        cl_counts = cl_counts.sort_values("Cluster")
        fig = px.bar(cl_counts, x="Cluster", y="Households", text="Households",
                     color="Households", color_continuous_scale="Blues", title="Households per Cluster")
        fig.update_layout(**LY, title_font_size=13, coloraxis_showscale=False, height=360,
                          xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f1f5f9"))
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    sec("Household Size")
    mbr_per_hh = mbr.groupby(col_id).size()
    if len(mbr_per_hh):
        b1, b2, b3 = st.columns(3)
        with b1: kpi("Avg members / HH", f"{mbr_per_hh.mean():.1f}", "g")
        with b2: kpi("Median members / HH", f"{mbr_per_hh.median():.0f}", "p")
        with b3: kpi("Max members / HH", f"{mbr_per_hh.max()}", "o")

        fig = px.histogram(mbr_per_hh.reset_index(name="Members"), x="Members",
                           nbins=int(mbr_per_hh.max()), color_discrete_sequence=["#3b82f6"],
                           title="Distribution of household sizes")
        fig.add_vline(x=mbr_per_hh.mean(), line_dash="dash", line_color="#ef4444",
                      annotation_text=f"Mean = {mbr_per_hh.mean():.1f}")
        fig.update_layout(**LY, title_font_size=13, height=320, bargap=0.05,
                          xaxis=dict(showgrid=False, title="Members per household"),
                          yaxis=dict(gridcolor="#f1f5f9", title="Households"))
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

# ═══ TAB 1: CLUSTER ═══
with tabs[1]:
    sec("Cluster-wise Scorecard")
    rows = []
    for cl, g in hh.groupby("_cluster"):
        ids = g[col_id].unique()
        gm = mbr[mbr[col_id].isin(ids)]
        rows.append({
            "Cluster": cl,
            "Households": len(g),
            "Members": len(gm),
            "Avg HH size": round(len(gm) / max(len(g), 1), 1),
            "Completed": int((g[col_hh_status] == "Completed").sum()) if col_hh_status else 0,
            "Completion %": round((g[col_hh_status] == "Completed").mean() * 100, 1) if col_hh_status else 0,
            "GPS captured": int(g[col_lat].notna().sum()) if col_lat else 0,
            "GPS %": round(g[col_lat].notna().mean() * 100, 1) if col_lat else 0,
            "Substituted": int((g[col_substituted] == "Yes").sum()) if col_substituted else 0,
            "Sub %": round((g[col_substituted] == "Yes").mean() * 100, 1) if col_substituted else 0,
        })
    cl_df = pd.DataFrame(rows).sort_values("Cluster")
    st.dataframe(cl_df, hide_index=True, use_container_width=True)

    sec("Completion & GPS rates per cluster")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(cl_df, x="Cluster", y="Completion %", text="Completion %",
                     color="Completion %", color_continuous_scale="RdYlGn", range_color=[0,100],
                     title="Completion rate by cluster")
        fig.update_traces(texttemplate="%{text}%", textposition="outside", marker_line_width=0)
        fig.update_layout(**LY, title_font_size=13, height=320, coloraxis_showscale=False,
                          xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f1f5f9"))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(cl_df, x="Cluster", y="GPS %", text="GPS %",
                     color="GPS %", color_continuous_scale="Blues", range_color=[0,100],
                     title="GPS capture rate by cluster")
        fig.update_traces(texttemplate="%{text}%", textposition="outside", marker_line_width=0)
        fig.update_layout(**LY, title_font_size=13, height=320, coloraxis_showscale=False,
                          xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f1f5f9"))
        st.plotly_chart(fig, use_container_width=True)

    if col_hh_status:
        sec("Household status × Cluster")
        st.plotly_chart(
            grp_bar(hh.dropna(subset=[col_hh_status]), "_cluster", col_hh_status,
                    "Status distribution per cluster", 380),
            use_container_width=True,
        )

# ═══ TAB 2: ENUMERATOR ═══
with tabs[2]:
    sec("Enumerator Scorecard")
    if not col_enum or hh[col_enum].dropna().empty:
        st.warning("No enumerator column detected.")
    else:
        rows = []
        for ex, g in hh.groupby(col_enum):
            ids = g[col_id].unique()
            gm = mbr[mbr[col_id].isin(ids)]
            days = g["_date"].dt.date.nunique() if g["_date"].notna().any() else 0
            rows.append({
                "Enumerator": str(ex),
                "Households": len(g),
                "Members": len(gm),
                "Avg HH size": round(len(gm) / max(len(g), 1), 1),
                "Days active": days,
                "Avg/day": round(len(g) / max(days, 1), 1) if days else len(g),
                "Completed": int((g[col_hh_status] == "Completed").sum()) if col_hh_status else 0,
                "Completion %": round((g[col_hh_status] == "Completed").mean() * 100, 1) if col_hh_status else 0,
                "GPS %": round(g[col_lat].notna().mean() * 100, 1) if col_lat else 0,
                "Substituted": int((g[col_substituted] == "Yes").sum()) if col_substituted else 0,
                "Clusters covered": g["_cluster"].nunique(),
            })
        en_df = pd.DataFrame(rows).sort_values("Households", ascending=False)
        st.dataframe(en_df, hide_index=True, use_container_width=True)

        top = en_df.iloc[0]
        e1, e2, e3, e4 = st.columns(4)
        with e1: kpi("Most active", top["Enumerator"], "g", f'{top["Households"]} HH')
        with e2: kpi("Top productivity", f'{en_df["Avg/day"].max():.1f}', "p", "HH per day")
        worst_gps = en_df.sort_values("GPS %").iloc[0]
        with e3: kpi("Worst GPS rate", f'{worst_gps["GPS %"]:.0f}%', "r", f'Enum {worst_gps["Enumerator"]}')
        with e4: kpi("Total clusters", f'{hh["_cluster"].nunique()}', "")

        sec("Productivity & GPS capture")
        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(en_df, x="Enumerator", y="Households", text="Households",
                         color="Enumerator", color_discrete_sequence=C, title="Households per enumerator")
            fig.update_traces(marker_line_width=0)
            fig.update_layout(**LY, title_font_size=13, height=320, showlegend=False,
                              xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f1f5f9"))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = px.bar(en_df, x="Enumerator", y="GPS %", text="GPS %",
                         color="GPS %", color_continuous_scale="RdYlGn", range_color=[0,100],
                         title="GPS capture rate per enumerator")
            fig.update_traces(texttemplate="%{text}%", textposition="outside", marker_line_width=0)
            fig.update_layout(**LY, title_font_size=13, height=320, coloraxis_showscale=False,
                              xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f1f5f9"))
            st.plotly_chart(fig, use_container_width=True)

        if hh["_date"].notna().any():
            sec("Daily activity per enumerator")
            daily = hh.dropna(subset=["_date", col_enum]).copy()
            daily["Date"] = daily["_date"].dt.date
            agg = daily.groupby(["Date", col_enum]).size().reset_index(name="Households")
            agg[col_enum] = agg[col_enum].astype(str)
            fig = px.line(agg, x="Date", y="Households", color=col_enum, markers=True,
                          color_discrete_sequence=C, title="Daily households per enumerator")
            fig.update_layout(**LY, title_font_size=13, height=340,
                              xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f1f5f9"),
                              legend=dict(orientation="h", yanchor="bottom", y=1.02))
            st.plotly_chart(fig, use_container_width=True)

# ═══ TAB 3: PROGRESS ═══
with tabs[3]:
    sec("Daily Progress")
    if hh["_date"].notna().any():
        daily = hh.dropna(subset=["_date"]).copy()
        daily["Date"] = daily["_date"].dt.date
        daily_hh = daily.groupby("Date").size().reset_index(name="Households")
        daily_hh["Cumulative"] = daily_hh["Households"].cumsum()

        mwd = mbr.merge(hh[[col_id, "_date"]], on=col_id)
        mwd["Date"] = mwd["_date"].dt.date
        daily_mbr = mwd.dropna(subset=["Date"]).groupby("Date").size().reset_index(name="Members")

        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(daily_hh, x="Date", y="Households", text="Households",
                         color_discrete_sequence=["#3b82f6"], title="Households listed per day")
            fig.update_traces(marker_line_width=0)
            fig.update_layout(**LY, title_font_size=13, height=320,
                              xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f1f5f9"))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = px.area(daily_hh, x="Date", y="Cumulative", color_discrete_sequence=["#10b981"],
                          title="Cumulative households over time")
            fig.update_traces(line_width=2, fill="tozeroy", fillcolor="rgba(16,185,129,.15)")
            fig.update_layout(**LY, title_font_size=13, height=320,
                              xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f1f5f9"))
            st.plotly_chart(fig, use_container_width=True)

        sec("Members listed per day")
        fig = px.bar(daily_mbr, x="Date", y="Members", text="Members",
                     color_discrete_sequence=["#f59e0b"], title="Members listed per day")
        fig.update_traces(marker_line_width=0)
        fig.update_layout(**LY, title_font_size=13, height=300,
                          xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f1f5f9"))
        st.plotly_chart(fig, use_container_width=True)

        sec("Productivity by weekday")
        wk = daily.copy()
        wk["Weekday"] = wk["_date"].dt.day_name()
        wk_counts = (wk["Weekday"].value_counts()
                       .reindex(["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
                       .fillna(0).reset_index())
        wk_counts.columns = ["Weekday", "Households"]
        fig = px.bar(wk_counts, x="Weekday", y="Households", text="Households",
                     color="Households", color_continuous_scale="Teal",
                     title="Households per weekday")
        fig.update_traces(marker_line_width=0)
        fig.update_layout(**LY, title_font_size=13, height=300, coloraxis_showscale=False,
                          xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f1f5f9"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No valid listing dates in the filtered selection.")

# ═══ TAB 4: WORK HOURS (NEW) ═══
with tabs[4]:
    sec("⏱️ Enumerator Work Hours & Day-wise Consistency")

    if not col_enum or hh[col_enum].dropna().empty:
        st.warning("No enumerator column found — cannot compute work hours.")
    elif hh["_date"].notna().sum() == 0:
        st.warning("No valid listing dates with timestamps — cannot compute work hours.")
    else:
        # Check if _date contains time information
        # We look at the hour component: if all hours are 0, likely only dates
        has_time = hh["_date"].dt.hour.sum() > 0
        if not has_time:
            st.warning("The Listing Date column appears to contain only dates (no time information). "
                       "Work duration cannot be computed, but day‑wise household counts are shown below.")

        wh = hh.dropna(subset=[col_enum, "_date"]).copy()
        wh["_day"] = wh["_date"].dt.date

        daily_rows = []
        for (en, day), grp in wh.groupby([col_enum, "_day"]):
            first_t = grp["_date"].min()
            last_t = grp["_date"].max()
            n_hh = len(grp)
            if has_time:
                dur_hr = (last_t - first_t).total_seconds() / 3600
                avg_gap_min = (dur_hr * 60 / (n_hh - 1)) if n_hh > 1 else np.nan
            else:
                dur_hr = np.nan
                avg_gap_min = np.nan
            daily_rows.append({
                "Enumerator": en,
                "Date": day,
                "First Listing": first_t,
                "Last Listing": last_t,
                "Households": n_hh,
                "Work Duration (hrs)": round(dur_hr, 2) if has_time else None,
                "Avg Time/HH (min)": round(avg_gap_min, 1) if has_time and pd.notna(avg_gap_min) else None,
                "First Time": first_t.strftime("%H:%M") if has_time else "",
                "Last Time": last_t.strftime("%H:%M") if has_time else "",
            })
        daily_log = pd.DataFrame(daily_rows)

        if len(daily_log) == 0:
            st.info("No enumerator-day data available.")
        else:
            daily_log = daily_log.sort_values(["Enumerator", "Date"])
            if has_time:
                daily_log["_start_dec"] = daily_log["First Listing"].apply(
                    lambda t: t.hour + t.minute/60 + t.second/3600
                )
                daily_log["_end_dec"] = daily_log["Last Listing"].apply(
                    lambda t: t.hour + t.minute/60 + t.second/3600
                )

            # KPI row
            if has_time:
                cons = daily_log.groupby("Enumerator")["Work Duration (hrs)"].agg(["mean", "std", "count"]).reset_index()
                cons_multi = cons[cons["count"] >= 2].copy()
                k1, k2, k3, k4 = st.columns(4)
                with k1: kpi("Enumerator-Days", f"{len(daily_log)}", "")
                with k2: kpi("Avg Work Duration", f"{daily_log['Work Duration (hrs)'].mean():.1f} hrs", "c")
                if len(cons_multi) > 0:
                    cons_multi["CV %"] = cons_multi["std"] / cons_multi["mean"].replace(0, np.nan) * 100
                    most_c = cons_multi.sort_values("CV %").iloc[0]
                    least_c = cons_multi.sort_values("CV %", ascending=False).iloc[0]
                    with k3: kpi("Most Consistent", f"Enum {most_c['Enumerator']}", "g", f"CV: {most_c['CV %']:.1f}%")
                    with k4: kpi("Least Consistent", f"Enum {least_c['Enumerator']}", "r", f"CV: {least_c['CV %']:.1f}%")
                else:
                    with k3: kpi("Enumerators", f"{daily_log['Enumerator'].nunique()}", "g")
                    with k4: kpi("Days", f"{daily_log['Date'].nunique()}", "o")
            else:
                # No time info – show counts only
                k1, k2, k3 = st.columns(3)
                with k1: kpi("Enumerator-Days", f"{len(daily_log)}", "")
                with k2: kpi("Enumerators", f"{daily_log['Enumerator'].nunique()}", "g")
                with k3: kpi("Total Households", f"{daily_log['Households'].sum()}", "p")

            # ── Timeline (Gantt) ── only if has_time
            if has_time:
                sec("📅 Daily Work Session Timeline")
                tl = daily_log.copy()
                # if first and last same, add a small dummy duration for visibility
                tl["_disp_end"] = tl.apply(
                    lambda r: r["Last Listing"] + pd.Timedelta(minutes=15)
                    if r["First Listing"] == r["Last Listing"]
                    else r["Last Listing"],
                    axis=1
                )
                tl["Enumerator Label"] = "Enumerator " + tl["Enumerator"].astype(str)
                fig_tl = px.timeline(
                    tl, x_start="First Listing", x_end="_disp_end", y="Enumerator Label",
                    color="Enumerator Label", color_discrete_sequence=C,
                    hover_data=["Households", "Work Duration (hrs)", "First Time", "Last Time"]
                )
                fig_tl.update_yaxes(title="", categoryorder="category descending")
                fig_tl.update_layout(
                    **LY,
                    height=max(tl["Enumerator Label"].nunique() * 70 + 100, 300),
                    showlegend=False,
                    xaxis=dict(showgrid=True, gridcolor="#f1f5f9", title="Date & Time")
                )
                st.plotly_chart(fig_tl, use_container_width=True)
                st.caption("Each bar spans one enumerator's working window on a given day — from first to last household listing timestamp.")

                # ── Day-wise work duration ──
                sec("📆 Work Duration by Day (Enumerator-wise)")
                fig_day = go.Figure()
                for i, ex in enumerate(sorted(daily_log["Enumerator"].unique())):
                    sub = daily_log[daily_log["Enumerator"] == ex].sort_values("Date")
                    fig_day.add_trace(go.Bar(
                        name=f"Enum {ex}",
                        x=sub["Date"].astype(str),
                        y=sub["Work Duration (hrs)"],
                        marker_color=C[i % len(C)],
                        marker_line_width=0
                    ))
                fig_day.update_layout(
                    **LY, barmode="group", height=360,
                    title="Daily Work Duration per Enumerator",
                    xaxis=dict(showgrid=False, title="Date"),
                    yaxis=dict(gridcolor="#f1f5f9", title="Hours"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02)
                )
                st.plotly_chart(fig_day, use_container_width=True)

                # ── Start / End time consistency ──
                sec("⏰ Start & End Time Consistency")
                b1, b2 = st.columns(2)
                with b1:
                    fig_start = px.box(
                        daily_log, x="Enumerator", y="_start_dec",
                        color="Enumerator", points="all",
                        title="Daily Start Time Spread", color_discrete_sequence=C
                    )
                    fig_start.update_layout(
                        **LY, height=340, showlegend=False,
                        xaxis=dict(showgrid=False, title="Enumerator"),
                        yaxis=dict(gridcolor="#f1f5f9", title="Start Hour (24h)")
                    )
                    st.plotly_chart(fig_start, use_container_width=True)
                with b2:
                    fig_dur = px.box(
                        daily_log, x="Enumerator", y="Work Duration (hrs)",
                        color="Enumerator", points="all",
                        title="Daily Work Duration Spread", color_discrete_sequence=C
                    )
                    fig_dur.update_layout(
                        **LY, height=340, showlegend=False,
                        xaxis=dict(showgrid=False, title="Enumerator"),
                        yaxis=dict(gridcolor="#f1f5f9", title="Hours")
                    )
                    st.plotly_chart(fig_dur, use_container_width=True)

            # ── Daily log table ──
            sec("📋 Daily Timing Log")
            display_cols = ["Enumerator", "Date", "First Time", "Last Time",
                            "Work Duration (hrs)", "Households", "Avg Time/HH (min)"]
            if not has_time:
                display_cols = ["Enumerator", "Date", "Households"]
            display_log = daily_log[display_cols].sort_values(["Date", "Enumerator"])
            st.dataframe(display_log, use_container_width=True, hide_index=True)

            # ── Consistency summary (only if has_time) ──
            if has_time:
                sec("📊 Enumerator Consistency Summary")
                summary_rows = []
                for ex, g in daily_log.groupby("Enumerator"):
                    days_worked = g["Date"].nunique()
                    avg_dur = round(g["Work Duration (hrs)"].mean(), 2)
                    std_dur = round(g["Work Duration (hrs)"].std(), 2) if days_worked > 1 else None
                    cv = round(std_dur / avg_dur * 100, 1) if (std_dur is not None and avg_dur > 0) else None
                    summary_rows.append({
                        "Enumerator": ex,
                        "Days Worked": days_worked,
                        "Total Households": int(g["Households"].sum()),
                        "Avg HH/Day": round(g["Households"].mean(), 1),
                        "Avg Start Time": f"{int(g['_start_dec'].mean()):02d}:{int((g['_start_dec'].mean() % 1) * 60):02d}",
                        "Avg End Time": f"{int(g['_end_dec'].mean()):02d}:{int((g['_end_dec'].mean() % 1) * 60):02d}",
                        "Avg Duration (hrs)": avg_dur,
                        "Std Dev Duration (hrs)": std_dur,
                        "Consistency CV %": cv,
                    })
                summary_df = pd.DataFrame(summary_rows).sort_values("Consistency CV %", na_position="last")
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
                st.caption("Lower Consistency CV % = steadier day‑to‑day work duration. Blank CV means only 1 day logged.")

                # ── Download reports ──
                sec("📥 Download Reports")
                dl1, dl2 = st.columns(2)
                with dl1:
                    csv_log = display_log.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "📥 Download Daily Timing Log CSV",
                        csv_log, "enumerator_daily_timing_log.csv", "text/csv",
                        use_container_width=True
                    )
                with dl2:
                    csv_summary = summary_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "📥 Download Consistency Summary CSV",
                        csv_summary, "enumerator_consistency_summary.csv", "text/csv",
                        use_container_width=True
                    )
            else:
                # If no time, still allow download of daily counts
                sec("📥 Download Daily Counts")
                csv_log = display_log.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Download Daily Household Counts CSV",
                    csv_log, "enumerator_daily_counts.csv", "text/csv",
                    use_container_width=True
                )

# ═══ TAB 5: DEMOGRAPHICS ═══
with tabs[5]:
    sec("Member Demographics")
    if len(mbr) == 0:
        st.info("No member rows in filter.")
    else:
        c1, c2 = st.columns(2)
        if col_mgender:
            with c1: st.plotly_chart(pie(mbr[col_mgender].dropna(), "Gender Distribution", 340), use_container_width=True)
        if col_mage:
            ages = mbr[col_mage].dropna()
            if len(ages):
                with c2:
                    fig = px.histogram(ages, nbins=20, color_discrete_sequence=["#3b82f6"],
                                       title="Age Distribution")
                    fig.add_vline(x=ages.mean(), line_dash="dash", line_color="#ef4444",
                                  annotation_text=f"Mean {ages.mean():.1f}")
                    fig.add_vline(x=ages.median(), line_dash="dot", line_color="#10b981",
                                  annotation_text=f"Median {ages.median():.0f}")
                    fig.update_traces(marker_line_width=0)
                    fig.update_layout(**LY, title_font_size=13, height=340, bargap=0.05,
                                      xaxis=dict(showgrid=False, title="Age (years)"),
                                      yaxis=dict(gridcolor="#f1f5f9", title="Members"),
                                      showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

        if col_mage and col_mgender:
            sec("Age × Gender Pyramid")
            md = mbr.dropna(subset=[col_mage, col_mgender]).copy()
            bins = list(range(0, 91, 5))
            labels = [f"{b}-{b+4}" for b in bins[:-1]]
            md["AgeBand"] = pd.cut(md[col_mage], bins=bins, labels=labels, include_lowest=True)
            py = md.groupby(["AgeBand", col_mgender], observed=True).size().reset_index(name="Count")
            male = py[py[col_mgender] == "Male"].copy()
            female = py[py[col_mgender] == "Female"].copy()
            male["Count"] = -male["Count"]
            fig = go.Figure()
            fig.add_bar(y=male["AgeBand"].astype(str), x=male["Count"], orientation="h",
                        name="Male", marker_color="#3b82f6")
            fig.add_bar(y=female["AgeBand"].astype(str), x=female["Count"], orientation="h",
                        name="Female", marker_color="#ec4899")
            fig.update_layout(**LY, barmode="overlay", bargap=0.05, height=460,
                              title="Age × Gender pyramid (5-year bands)", title_font_size=13,
                              xaxis=dict(title="Members (Male ◀ | ▶ Female)", showgrid=False,
                                         tickvals=[-100,-50,0,50,100], ticktext=["100","50","0","50","100"]),
                              yaxis=dict(title="Age band", gridcolor="#f1f5f9"))
            st.plotly_chart(fig, use_container_width=True)

        c3, c4 = st.columns(2)
        if col_mocc:
            with c3:
                vc = mbr[col_mocc].value_counts().reset_index(); vc.columns=["Occupation","Count"]
                vc = vc.sort_values("Count")
                fig = px.bar(vc, x="Count", y="Occupation", orientation="h", text="Count",
                             color="Count", color_continuous_scale="Viridis", title="Occupation")
                fig.update_traces(marker_line_width=0)
                fig.update_layout(**LY, title_font_size=13, height=380, coloraxis_showscale=False,
                                  xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
                                  yaxis=dict(showgrid=False))
                st.plotly_chart(fig, use_container_width=True)
        if col_medu:
            with c4:
                vc = mbr[col_medu].value_counts().reset_index(); vc.columns=["Education","Count"]
                vc = vc.sort_values("Count")
                fig = px.bar(vc, x="Count", y="Education", orientation="h", text="Count",
                             color="Count", color_continuous_scale="Cividis", title="Education")
                fig.update_traces(marker_line_width=0)
                fig.update_layout(**LY, title_font_size=13, height=380, coloraxis_showscale=False,
                                  xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
                                  yaxis=dict(showgrid=False))
                st.plotly_chart(fig, use_container_width=True)

# ═══ TAB 6: SAMPLING ═══
with tabs[6]:
    sec("NDOHS Sampling Coverage")
    if not col_msamp or len(mbr) == 0:
        st.info("No sampling group data available.")
    else:
        eligible = mbr[mbr[col_msamp] != "Not Applicable"]
        selected_yes = (mbr[col_msel] == "Yes").sum() if col_msel else 0

        s1, s2, s3 = st.columns(3)
        with s1: kpi("Total members", f"{len(mbr):,}")
        with s2: kpi("Eligible (4 groups)", f"{len(eligible):,}", "g",
                     f"{len(eligible)/len(mbr)*100:.0f}% of members" if len(mbr) else "")
        with s3: kpi("Selected for sampling", f"{selected_yes:,}", "p",
                     f"{selected_yes/max(len(eligible),1)*100:.0f}% of eligible")

        sec("Sampling group distribution")
        st.plotly_chart(bar(mbr[col_msamp].dropna(), "Members per sampling group", "h",
                            "#8b5cf6", 320), use_container_width=True)

        sec("Eligible members per cluster — by age group")
        ewc = eligible.merge(hh[[col_id, "_cluster"]], on=col_id)
        ewc = ewc.dropna(subset=[col_msamp])
        pivot = ewc.groupby(["_cluster", col_msamp]).size().reset_index(name="Count")
        fig = px.bar(pivot, x="_cluster", y="Count", color=col_msamp, text="Count",
                     barmode="group", color_discrete_sequence=C, title="Eligible × Age Group × Cluster")
        fig.update_traces(marker_line_width=0)
        fig.update_layout(**LY, title_font_size=13, height=380,
                          xaxis=dict(showgrid=False, title="Cluster"),
                          yaxis=dict(gridcolor="#f1f5f9", title="Eligible members"))
        st.plotly_chart(fig, use_container_width=True)

        if col_msel:
            sec("Selected vs Not-selected (within eligible)")
            sp = eligible.groupby([col_msamp, col_msel]).size().reset_index(name="Count")
            fig = px.bar(sp, x=col_msamp, y="Count", color=col_msel, text="Count",
                         barmode="stack",
                         color_discrete_map={"Yes": "#10b981", "No": "#94a3b8"},
                         title="Selection result per age group")
            fig.update_traces(marker_line_width=0)
            fig.update_layout(**LY, title_font_size=13, height=320,
                              xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f1f5f9"))
            st.plotly_chart(fig, use_container_width=True)

# ═══ TAB 7: GPS & TABLET LOCATION ═══
with tabs[7]:
    sec("📍 GPS Capture Status")
    if not col_lat:
        st.warning("No GPS latitude column found.")
    else:
        gps_ok = hh.dropna(subset=[col_lat, col_lon]).copy() if col_lon else hh.dropna(subset=[col_lat]).copy()
        gps_missing = hh[hh[col_lat].isna()].copy()

        g1, g2, g3 = st.columns(3)
        with g1: kpi("GPS captured", f"{len(gps_ok)}", "g",
                     f"{len(gps_ok)/max(len(hh),1)*100:.0f}% of households")
        with g2: kpi("GPS missing", f"{len(gps_missing)}", "r",
                     f"{len(gps_missing)/max(len(hh),1)*100:.0f}% of households")
        if col_acc and hh[col_acc].notna().any():
            avg_acc = hh[col_acc].mean()
            with g3: kpi("Avg accuracy", f"{avg_acc:.0f} m", "c", "Lower is better")

        if len(gps_ok):
            sec("Map of captured GPS locations")
            mapped = gps_ok.copy()
            mapped["lat"] = pd.to_numeric(mapped[col_lat], errors="coerce")
            mapped["lon"] = pd.to_numeric(mapped[col_lon], errors="coerce")
            mapped = mapped.dropna(subset=["lat","lon"])
            hover = {col_id: True, "_cluster": False, "lat": ":.5f", "lon": ":.5f"}
            if col_enum: hover[col_enum] = True
            if col_hh_status: hover[col_hh_status] = True
            fig = px.scatter_mapbox(
                mapped, lat="lat", lon="lon", color="_cluster",
                hover_name=col_hh_num if col_hh_num else col_id,
                hover_data=hover,
                zoom=11, height=520, color_discrete_sequence=C,
            )
            fig.update_layout(mapbox_style="open-street-map",
                              margin=dict(t=10, b=10, l=0, r=0),
                              legend_title="Cluster", font=dict(family="Inter", size=11))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        sec("🚨 Missing GPS — Tablet (Enumerator) Audit")
        if len(gps_missing) == 0:
            alert("✅ All households in the current filter have GPS captured.", "g")
        else:
            alert(
                f"⚠️ {len(gps_missing)} households ({len(gps_missing)/max(len(hh),1)*100:.0f}%) "
                "have NO GPS coordinates / Google Maps link. The breakdown below pinpoints "
                "which tablet/enumerator and cluster these records came from.",
                "r",
            )

            c1, c2, c3 = st.columns(3)
            with c1:
                if col_enum:
                    miss_en = gps_missing[col_enum].value_counts(dropna=False).reset_index()
                    miss_en.columns = ["Enumerator", "Missing"]
                    miss_en["Enumerator"] = miss_en["Enumerator"].astype(str).replace({"nan":"(missing)","<NA>":"(missing)"})
                    tot_en = hh[col_enum].value_counts(dropna=False).reset_index()
                    tot_en.columns = ["Enumerator", "Total"]
                    tot_en["Enumerator"] = tot_en["Enumerator"].astype(str).replace({"nan":"(missing)","<NA>":"(missing)"})
                    miss_en = miss_en.merge(tot_en, on="Enumerator", how="left")
                    miss_en["Rate %"] = (miss_en["Missing"] / miss_en["Total"] * 100).round(1)
                    fig = px.bar(miss_en, x="Enumerator", y="Missing", text="Missing",
                                 color="Rate %", color_continuous_scale="Reds",
                                 title="By Enumerator (Tablet)",
                                 hover_data=["Total","Rate %"])
                    fig.update_traces(marker_line_width=0)
                    fig.update_layout(**LY, title_font_size=12, height=300, coloraxis_showscale=False,
                                      xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f1f5f9"))
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(miss_en, hide_index=True, use_container_width=True)

            with c2:
                miss_cl = gps_missing["_cluster"].value_counts(dropna=False).reset_index()
                miss_cl.columns = ["Cluster", "Missing"]
                tot_cl = hh["_cluster"].value_counts().reset_index()
                tot_cl.columns = ["Cluster", "Total"]
                miss_cl = miss_cl.merge(tot_cl, on="Cluster", how="left")
                miss_cl["Rate %"] = (miss_cl["Missing"] / miss_cl["Total"] * 100).round(1)
                fig = px.bar(miss_cl, x="Cluster", y="Missing", text="Missing",
                             color="Rate %", color_continuous_scale="Oranges",
                             title="By Cluster", hover_data=["Total","Rate %"])
                fig.update_traces(marker_line_width=0)
                fig.update_layout(**LY, title_font_size=12, height=300, coloraxis_showscale=False,
                                  xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f1f5f9"))
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(miss_cl, hide_index=True, use_container_width=True)

            with c3:
                if col_hh_status:
                    miss_st = gps_missing[col_hh_status].value_counts(dropna=False).reset_index()
                    miss_st.columns = ["Status", "Missing"]
                    miss_st["Status"] = miss_st["Status"].fillna("(missing)")
                    fig = px.bar(miss_st, x="Status", y="Missing", text="Missing",
                                 color="Missing", color_continuous_scale="Greys",
                                 title="By Household Status")
                    fig.update_traces(marker_line_width=0)
                    fig.update_layout(**LY, title_font_size=12, height=300, coloraxis_showscale=False,
                                      xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f1f5f9"))
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(miss_st, hide_index=True, use_container_width=True)

            sec("📋 Follow-up list — records with missing GPS")
            follow_cols = [c for c in [col_id, "_cluster", col_hh_num, col_enum, col_date,
                                       col_hh_status, col_substituted, col_maps]
                           if c and c in gps_missing.columns]
            fu = gps_missing[follow_cols].rename(columns={"_cluster": "Cluster"})
            sort_keys = [k for k in [col_enum, "Cluster"] if k in fu.columns]
            if sort_keys: fu = fu.sort_values(sort_keys)
            st.dataframe(fu, hide_index=True, use_container_width=True, height=340)
            csv_bytes = fu.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download missing-GPS follow-up list (CSV)",
                               data=csv_bytes, file_name="missing_gps_followup.csv",
                               mime="text/csv")

        if col_acc and hh[col_acc].notna().any():
            st.markdown("---")
            sec("GPS Accuracy Distribution")
            acc = hh[col_acc].dropna()
            fig = px.histogram(acc, nbins=30, color_discrete_sequence=["#06b6d4"],
                               title="GPS accuracy distribution (metres)")
            fig.add_vline(x=acc.median(), line_dash="dash", line_color="#ef4444",
                          annotation_text=f"Median = {acc.median():.0f} m")
            fig.update_traces(marker_line_width=0)
            fig.update_layout(**LY, title_font_size=13, height=300, bargap=0.05,
                              xaxis=dict(showgrid=False, title="Accuracy (m)"),
                              yaxis=dict(gridcolor="#f1f5f9", title="Count"),
                              showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

# ═══ TAB 8: DATA QUALITY ═══
with tabs[8]:
    sec("🔍 Automated Quality Checks")

    issues = []
    hh_no_mbr_ids = set(hh[col_id]) - set(mbr[col_id])
    if hh_no_mbr_ids:
        cols = [c for c in [col_id, "_cluster", col_hh_num, col_enum, col_hh_status]
                if c and c in hh.columns]
        issues.append(("Households with NO members listed", len(hh_no_mbr_ids),
                       hh[hh[col_id].isin(hh_no_mbr_ids)][cols].rename(columns={"_cluster":"Cluster"})))

    if col_mage:
        m_no_age = mbr[mbr[col_mage].isna()]
        if len(m_no_age):
            cols = [c for c in [col_id, col_minst, col_mname, col_mgender, col_medu]
                    if c and c in m_no_age.columns]
            issues.append(("Members with missing Age", len(m_no_age), m_no_age[cols]))

    if col_mgender:
        m_no_gen = mbr[mbr[col_mgender].isna()]
        if len(m_no_gen):
            cols = [c for c in [col_id, col_minst, col_mname, col_mage] if c and c in m_no_gen.columns]
            issues.append(("Members with missing Gender", len(m_no_gen), m_no_gen[cols]))

    if col_hh_status and col_lat:
        comp_no_gps = hh[(hh[col_hh_status] == "Completed") & (hh[col_lat].isna())]
        if len(comp_no_gps):
            cols = [c for c in [col_id, "_cluster", col_hh_num, col_enum, col_date]
                    if c and c in comp_no_gps.columns]
            issues.append(("'Completed' households with NO GPS captured", len(comp_no_gps),
                           comp_no_gps[cols].rename(columns={"_cluster":"Cluster"})))

    if col_hh_status:
        comp_no_mbr = hh[(hh[col_hh_status] == "Completed") & (hh[col_id].isin(hh_no_mbr_ids))]
        if len(comp_no_mbr):
            cols = [c for c in [col_id, "_cluster", col_hh_num, col_enum]
                    if c and c in comp_no_mbr.columns]
            issues.append(("'Completed' households with NO members listed", len(comp_no_mbr),
                           comp_no_mbr[cols].rename(columns={"_cluster":"Cluster"})))

    if col_lat and col_lon:
        latn = pd.to_numeric(hh[col_lat], errors="coerce")
        lonn = pd.to_numeric(hh[col_lon], errors="coerce")
        out = hh[latn.notna() & ((latn < 28.4) | (latn > 28.95) | (lonn < 76.8) | (lonn > 77.4))]
        if len(out):
            cols = [c for c in [col_id, "_cluster", col_hh_num, col_lat, col_lon, col_enum]
                    if c and c in out.columns]
            issues.append(("GPS coordinates outside Delhi bounding box (sanity-check)",
                           len(out), out[cols].rename(columns={"_cluster":"Cluster"})))

    if col_hh_num:
        dups = hh.dropna(subset=["_cluster", col_hh_num]).groupby(["_cluster", col_hh_num]).size().reset_index(name="Count")
        dups = dups[dups["Count"] > 1].rename(columns={"_cluster":"Cluster"})
        if len(dups):
            issues.append(("Duplicate Household Numbers within same cluster", len(dups), dups))

    if col_substituted and col_sub_reason:
        sub_no_reason = hh[(hh[col_substituted] == "Yes") & (hh[col_sub_reason].isna())]
        if len(sub_no_reason):
            cols = [c for c in [col_id, "_cluster", col_hh_num, col_sub_from, col_enum]
                    if c and c in sub_no_reason.columns]
            issues.append(("Substituted households with NO reason recorded", len(sub_no_reason),
                           sub_no_reason[cols].rename(columns={"_cluster":"Cluster"})))

    if not issues:
        alert("✅ No data-quality issues detected in the current filter selection.", "g")
    else:
        total_records = sum(c for _, c, _ in issues)
        alert(
            f"⚠️ Found <strong>{len(issues)} types of issues</strong> affecting "
            f"<strong>{total_records} records</strong>. Expand each to inspect and download.",
            "o",
        )
        for title, count, dfi in issues:
            with st.expander(f"❗ {title}  —  {count} record(s)", expanded=False):
                st.dataframe(dfi, hide_index=True, use_container_width=True)
                csv = dfi.to_csv(index=False).encode("utf-8")
                st.download_button(
                    f"⬇️ Download CSV", data=csv,
                    file_name=f"quality_{title.lower().replace(' ','_')[:50]}.csv",
                    mime="text/csv", key=title,
                )

# ═══ TAB 9: DRILL-DOWN ═══
with tabs[9]:
    sec("🔎 Household Drill-down")
    st.caption("Search any household by Record ID or Household Number to view its full details + member list.")

    search = st.text_input("Search", placeholder="e.g. 4 or H19", label_visibility="collapsed")

    if search:
        mask = pd.Series([False] * len(hh), index=hh.index)
        try:
            si = int(search)
            mask |= (hh[col_id] == si)
        except ValueError:
            pass
        if col_hh_num:
            mask |= hh[col_hh_num].astype(str).str.contains(search, case=False, na=False)

        matches = hh[mask]
        if len(matches) == 0:
            st.warning(f"No households found matching '{search}'.")
        else:
            for _, h in matches.iterrows():
                with st.container(border=True):
                    title = f"Record `{h[col_id]}`"
                    if col_hh_num and pd.notna(h[col_hh_num]):
                        title += f" · Household `{h[col_hh_num]}`"
                    st.markdown(f"### {title}")

                    cA, cB, cC, cD = st.columns(4)
                    with cA: kpi("Cluster", str(h["_cluster"]))
                    with cB:
                        if col_enum: kpi("Enumerator", str(h[col_enum]), "p")
                    with cC:
                        if col_hh_status: kpi("Status",
                                              str(h[col_hh_status]) if pd.notna(h[col_hh_status]) else "—",
                                              "g" if h.get(col_hh_status) == "Completed" else "o")
                    with cD:
                        if col_date and pd.notna(h.get("_date")):
                            kpi("Listed", h["_date"].strftime("%d %b %Y"), "c")

                    if col_lat and pd.notna(h.get(col_lat)):
                        st.markdown(
                            f"📍 **GPS**: {h[col_lat]:.5f}, {h[col_lon]:.5f} "
                            f"(accuracy: {h.get(col_acc, '—')} m) — "
                            f"[Open in Maps]({h.get(col_maps, '#')})"
                        )
                    else:
                        alert("📍 GPS not captured for this household", "r")

                    if col_substituted and h.get(col_substituted) == "Yes":
                        alert(
                            f"🔄 Substituted from <strong>{h.get(col_sub_from, '?')}</strong> · "
                            f"reason: {h.get(col_sub_reason, '—')}",
                            "o",
                        )

                    members = mbr[mbr[col_id] == h[col_id]]
                    sec(f"Members ({len(members)})")
                    if len(members):
                        show = [c for c in [col_minst, col_mname, col_mage, col_mgender,
                                            col_mocc, col_medu, col_msamp, col_msel]
                                if c and c in members.columns]
                        st.dataframe(members[show], hide_index=True, use_container_width=True)
                    else:
                        st.info("No members listed for this household.")
    else:
        st.info("👆 Type a Record ID or Household Number above to drill down.")

    st.markdown("---")
    sec("📥 Export filtered data")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("⬇️ Households CSV",
                           data=hh.to_csv(index=False).encode("utf-8"),
                           file_name="filtered_households.csv", mime="text/csv")
    with c2:
        st.download_button("⬇️ Members CSV",
                           data=mbr.to_csv(index=False).encode("utf-8"),
                           file_name="filtered_members.csv", mime="text/csv")

# ── FOOTER ──
st.markdown("---")
st.markdown(
    f'<div style="color:#94a3b8;font-size:.75rem;text-align:center;padding:10px 0;">'
    f'HouseholdListing Analytics Pro · Built for the North Delhi REDCap project · '
    f'Generated {datetime.now().strftime("%d %b %Y %H:%M")}'
    f'</div>',
    unsafe_allow_html=True,
)