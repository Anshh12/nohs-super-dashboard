"""
Comprehensive Oral Health Survey Analytics Dashboard
Central Delhi Dental Health Study — Full A-Z Analysis
v2 (2026-03-16) — Updated with Household Status & Oral Submucous Fibrosis
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
from io import BytesIO

# ── PAGE CONFIG ──
st.set_page_config(page_title="OralHealth Analytics Pro", page_icon="🦷", layout="wide", initial_sidebar_state="expanded")

# ── CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:#f8fafc;}
[data-testid="stSidebar"]{background:linear-gradient(160deg,#0f172a 0%,#1e293b 100%);border-right:none;}
[data-testid="stSidebar"] *{color:#cbd5e1 !important;}
[data-testid="stSidebar"] .stSelectbox label,[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stDateInput label,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3{
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
</style>""", unsafe_allow_html=True)

# ── HELPERS ──
C = ["#3b82f6","#10b981","#8b5cf6","#f59e0b","#ef4444","#06b6d4","#ec4899","#14b8a6","#f97316","#6366f1"]
LY = dict(paper_bgcolor="white",plot_bgcolor="white",font=dict(family="Inter",size=11,color="#334155"),margin=dict(l=10,r=10,t=40,b=10))

def kpi(l,v,c="",d=""):
    st.markdown(f'<div class="kpi {c}"><div class="kpi-l">{l}</div><div class="kpi-v">{v}</div>{"<div class=kpi-d>"+d+"</div>" if d else ""}</div>',unsafe_allow_html=True)

def sec(t):
    st.markdown(f'<div class="sec">{t}</div>',unsafe_allow_html=True)

def pie(s,t,h=320):
    vc=s.value_counts().reset_index();vc.columns=["l","c"]
    f=px.pie(vc,names="l",values="c",title=t,color_discrete_sequence=C,hole=.45)
    f.update_traces(textposition="outside",textinfo="percent+label")
    f.update_layout(**LY,title_font_size=13,showlegend=False,height=h);return f

def bar(s,t,o="v",clr="#3b82f6",h=320):
    vc=s.value_counts().reset_index();vc.columns=["l","c"]
    if o=="h":vc=vc.sort_values("c");f=px.bar(vc,x="c",y="l",orientation="h",title=t,color_discrete_sequence=[clr])
    else:f=px.bar(vc,x="l",y="c",title=t,color_discrete_sequence=[clr])
    f.update_layout(**LY,title_font_size=13,height=h,xaxis=dict(showgrid=False),yaxis=dict(showgrid=True,gridcolor="#f1f5f9"))
    f.update_traces(marker_line_width=0);return f

def grp_bar(df,x,color,t,h=340):
    ct=pd.crosstab(df[x],df[color]);fig=go.Figure()
    for i,col in enumerate(ct.columns):
        fig.add_trace(go.Bar(name=str(col),x=ct.index.astype(str),y=ct[col],marker_color=C[i%len(C)],marker_line_width=0))
    fig.update_layout(**LY,barmode="group",height=h,title=t,title_font_size=13,
        xaxis=dict(showgrid=False),yaxis=dict(gridcolor="#f1f5f9"),legend=dict(orientation="h",yanchor="bottom",y=1.02))
    return fig

# ── SIDEBAR ──
with st.sidebar:
    st.markdown('<div style="padding:14px 0 18px;"><div style="font-family:Playfair Display,serif;font-size:1.3rem;color:white;">🦷 OralHealth Pro</div><div style="font-size:.7rem;color:#64748b;margin-top:2px;">Comprehensive Analytics</div></div>',unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload CSV",type=["csv"],label_visibility="collapsed")
    st.markdown("---")

if not uploaded:
    st.markdown('<div style="font-family:Playfair Display,serif;font-size:2.2rem;color:#0f172a;">🦷 OralHealth Analytics Pro</div>',unsafe_allow_html=True)
    st.markdown('<div style="color:#64748b;margin-bottom:20px;">Upload your survey CSV from the sidebar to begin comprehensive analysis.</div>',unsafe_allow_html=True)
    st.info("📁 Upload `CentralDelhi1_DATA_LABELS_*.csv` to get started with all 11 analysis modules.")
    st.stop()

# ── LOAD DATA ──
@st.cache_data
def load_csv(file_bytes):
    return pd.read_csv(BytesIO(file_bytes),low_memory=False)

try:
    raw = load_csv(uploaded.getvalue())
except Exception as exc:
    st.error(f"Could not read the uploaded CSV: {exc}")
    st.stop()

# ── SEPARATE HOUSEHOLD vs PARTICIPANT ──
ri_col = "Repeat Instrument"
has_ri = ri_col in raw.columns
if has_ri:
    hh = raw[raw[ri_col].isna() | (raw[ri_col].astype(str).str.strip()=="")].copy()
    pt = raw[raw[ri_col].astype(str).str.strip()=="Participant"].copy()
else:
    hh = pd.DataFrame(); pt = raw.copy()

# ── COLUMN AUTO-DETECT ──
def find_col(keywords, cols):
    for c in cols:
        for kw in keywords:
            if kw.lower() in c.lower(): return c
    return None

col_id = find_col(["record_id","patient_id","Record ID"],raw.columns) or raw.columns[0]
col_age = find_col(["Age (years)","age_years"],raw.columns)
col_ag = find_col(["Age group","age_group"],raw.columns)
col_gender = find_col(["Gender","sex"],raw.columns)
col_date = find_col(["Consent date","consent_date"],raw.columns)
col_exam = find_col(["Examiner Number","Examiner","participant_suffix"],raw.columns)
col_cluster = find_col(["cluster code","cluster"],raw.columns)
col_consent = find_col(["Consent obtained","consent"],raw.columns)
col_hh_num = find_col(["Household Number","household"],raw.columns)
col_hh_status = find_col(["household_status","Household Status","Household status"],raw.columns)
col_water = find_col(["drinking water","water"],raw.columns)
col_roof = find_col(["roof material","roof"],raw.columns)
col_fuel = find_col(["cooking fuel","fuel"],raw.columns)
col_toilet = find_col(["toilet facility","toilet"],raw.columns)
col_tobacco = find_col(["currently using any form of tobacco","current_tobacco"],raw.columns)
col_alcohol = find_col(["currently consuming alcohol","current_alcohol"],raw.columns)
col_cleaning = find_col(["How did you clean","cleaning_mode"],raw.columns)
col_brush_freq = find_col(["How many times","brush_frequency"],raw.columns)
col_sugar = find_col(["added sugar","sugar_between"],raw.columns)
col_pain = find_col(["mouth or teeth problems","oral_pain"],raw.columns)
col_dentist = find_col(["visit a dentist","ever_visited"],raw.columns)
col_perception = find_col(["state of your teeth","perception"],raw.columns)
col_intervention = find_col(["Intervention urgency","intervention"],raw.columns)
col_fluorosis = find_col(["Enamel fluorosis","enamel_fluorosis"],raw.columns)
col_erosion = find_col(["erosion severity","dental_erosion"],raw.columns)
col_abrasion = find_col(["Dental  Abrasion","dental_abrasion","Abrasion"],raw.columns)
col_attrition = find_col(["Dental  Attrition","dental_attrition","Attrition"],raw.columns)
col_trauma = find_col(["Dental trauma","dental_trauma"],raw.columns)
col_lesion = find_col(["mucosal lesion present","oral_muc"],raw.columns)
col_prosthetic = find_col(["Prosthetic status","prosthetic_status"],raw.columns)
col_edentulous = find_col(["any natural teeth","edentulous"],raw.columns)
col_toothpaste = find_col(["type of toothpaste","toothpaste_type"],raw.columns)
col_clicking = find_col(["Clicking","clicking_tmj"],raw.columns)
col_tenderness = find_col(["Tenderness","tenderness_tmj"],raw.columns)
col_jaw_mob = find_col(["jaw mobility","jaw_mobility"],raw.columns)
col_deviation = find_col(["Deviation","deviation_jaw"],raw.columns)
col_crowding = find_col(["Crowding","crowding"],raw.columns)
col_spacing = find_col(["Spacing","incisal_spacing"],raw.columns)
col_overjet_max = find_col(["maxillary overjet","maxillary_overjet"],raw.columns)
col_molar = find_col(["molar relation","molar_relation"],raw.columns)
col_money = find_col(["how much did you spend","money_spent"],raw.columns)
col_where = find_col(["Where did you seek","where_did"],raw.columns)
col_ind_status = find_col(["Individual Status","individual_status"],raw.columns)

# Asset columns for household
asset_cols_labels = ["Pressure Cooker","Color TV","Refrigerator","Table","Washing Machine",
    "Sewing Machine","AC Cooler","Mattress","Motorcycle Scooter","Smartphone",
    "Four wheeler","Home ownership","Tractor","Livestock ownership","Land ownership"]
asset_cols = [find_col([a],raw.columns) for a in asset_cols_labels]
asset_cols = [c for c in asset_cols if c is not None]

# ── PREPARE PARTICIPANT DATA ──
df = pt.copy() if len(pt)>0 else raw.copy()
df = df.dropna(subset=[col_id]) if col_id else df

# ── CLUSTER CODE HANDLING ──
# Step 1: If cluster column exists, propagate from household rows
if col_cluster and col_id and len(hh)>0:
    hh_cluster = hh[[col_id, col_cluster]].dropna(subset=[col_cluster])
    hh_nonempty = hh_cluster[hh_cluster[col_cluster].astype(str).str.strip().replace("nan","") != ""]
    if len(hh_nonempty)>0:
        cluster_map = hh_nonempty.set_index(col_id)[col_cluster].to_dict()
        mapped = df[col_id].map(cluster_map)
        if col_cluster in df.columns:
            existing = df[col_cluster].astype(str).str.strip().replace("nan","")
            df[col_cluster] = df[col_cluster].where(existing != "", mapped)
        else:
            df[col_cluster] = mapped

# Step 2: Ensure col_cluster always exists
if not col_cluster or col_cluster not in df.columns:
    col_cluster = "_cluster_code"
    df[col_cluster] = "Non-Identified"

# Step 3: Fill ALL empty/NaN/nan with "Non-Identified" and clean float values
df[col_cluster] = df[col_cluster].astype(str).str.strip()
df[col_cluster] = df[col_cluster].replace({"nan": "Non-Identified", "": "Non-Identified", "None": "Non-Identified"})
df.loc[df[col_cluster].isna(), col_cluster] = "Non-Identified"
# Clean float-like values: "3.0" -> "3", "12.0" -> "12"
def clean_cluster_val(v):
    if v == "Non-Identified":
        return v
    try:
        f = float(v)
        if f == int(f):
            return str(int(f))
    except (ValueError, TypeError):
        pass
    return v
df[col_cluster] = df[col_cluster].apply(clean_cluster_val)
df["_date"] = pd.to_datetime(df[col_date],errors="coerce") if col_date else pd.NaT
has_date = df["_date"].notna().sum()>0

if len(hh)>0:
    hh["_date"] = pd.to_datetime(hh[col_date],errors="coerce") if col_date and col_date in hh.columns else pd.NaT
    if col_cluster and col_cluster in hh.columns:
        hh[col_cluster] = hh[col_cluster].astype(str).str.strip().apply(clean_cluster_val)


# Parse age as numeric
if col_age:
    df["_age_num"] = pd.to_numeric(df[col_age],errors="coerce")

# ── SIDEBAR FILTERS ──
with st.sidebar:
    st.markdown("### Filters")
    
    # Track base participant IDs to dynamically sync households later
    pt_base_ids = set(df[col_id].dropna().unique())
    
    if has_date:
        mn,mx = df["_date"].min().date(),df["_date"].max().date()
        dr = st.date_input("Date Range",value=(mn,mx),min_value=mn,max_value=mx)
        if isinstance(dr,(list,tuple)) and len(dr)==2:
            df = df[(df["_date"].dt.date>=dr[0])&(df["_date"].dt.date<=dr[1])]
    if col_ag:
        ages = sorted(df[col_ag].dropna().unique())
        sa = st.multiselect("Age Group",ages,default=ages)
        if sa: df = df[df[col_ag].isin(sa)]
    if col_gender:
        gens = sorted(df[col_gender].dropna().unique())
        sg = st.multiselect("Gender",gens,default=gens)
        if sg: df = df[df[col_gender].isin(sg)]
    if col_cluster:
        cls = sorted(df[col_cluster].dropna().unique(), key=lambda x: str(x))
        sc = st.multiselect("Cluster",cls,default=cls)
        if sc: 
            df = df[df[col_cluster].isin(sc)]
            if len(hh)>0 and col_cluster in hh.columns:
                hh = hh[hh[col_cluster].isin(sc)]
    if col_exam:
        exs = sorted(df[col_exam].dropna().unique())
        se = st.multiselect("Examiner",exs,default=exs)
        if se: df = df[df[col_exam].isin(se)]
            
    # Sync households with participant filters: drop a household ONLY if it originally had participants but all of them were filtered out.
    if len(hh)>0:
        pt_after_ids = set(df[col_id].dropna().unique())
        dropped_ids = pt_base_ids - pt_after_ids
        if dropped_ids:
            hh = hh[~hh[col_id].isin(dropped_ids)]

    st.markdown("---")
    st.markdown(f'<div style="font-size:.72rem;color:#64748b;">📊 {len(df)} participants · {len(hh)} households</div>',unsafe_allow_html=True)

# ── HEADER ──
st.markdown('<div style="font-family:Playfair Display,serif;font-size:1.9rem;color:#0f172a;">🦷 OralHealth Analytics Pro</div>',unsafe_allow_html=True)
st.markdown(f'<div style="color:#64748b;font-size:.85rem;margin-bottom:20px;">Central Delhi Oral Health Survey · {datetime.now().strftime("%d %b %Y, %I:%M %p")}</div>',unsafe_allow_html=True)

# KPI ROW
k1,k2,k3,k4,k5 = st.columns(5)
with k1: kpi("Participants",f"{len(df):,}")
with k2: kpi("Households",f"{len(hh):,}","g")
with k3:
    if col_gender: kpi("Male %",f"{(df[col_gender]=='Male').mean()*100:.0f}%","p")
    else: kpi("Columns",f"{raw.shape[1]}","p")
with k4:
    if col_gender: kpi("Female %",f"{(df[col_gender]=='Female').mean()*100:.0f}%","o")
    else: kpi("Rows",f"{len(raw):,}","o")
with k5:
    if col_consent: kpi("Consent %",f"{(df[col_consent]=='Yes').mean()*100:.0f}%","c")
    elif has_date and df['_date'].notna().sum()>0: kpi("Survey Days",f"{(df['_date'].max()-df['_date'].min()).days+1}","r")
    else: kpi("Age Groups",f"{df[col_ag].nunique() if col_ag else '-'}","r")

st.markdown("")

# ── TOOTH HELPERS ──
# Deciduous teeth (for age 4-6)
decid_teeth = [55,54,53,52,51,61,62,63,64,65,75,74,73,72,71,81,82,83,84,85]
# Permanent teeth (for 12+)
perm_teeth = [18,17,16,15,14,13,12,11,21,22,23,24,25,26,27,28,38,37,36,35,34,33,32,31,41,42,43,44,45,46,47,48]

def get_tooth_status_col(tooth_num):
    return find_col([f"Tooth {tooth_num} - status"], raw.columns)

def get_tooth_bleed_col(tooth_num):
    return find_col([f"Tooth {tooth_num} - bleeding"], raw.columns)

def get_tooth_pocket_col(tooth_num):
    return find_col([f"Tooth {tooth_num} - Pocket"], raw.columns)

caries_labels_decid = ["Caries","Filled with caries","Filled no caries","Missing due to caries"]
caries_labels_perm = ["Coronal caries","Root caries","Both coronal and root caries","Filled with caries","Filled no caries","Missing due to caries"]
decayed_decid = ["Caries"]
filled_decid = ["Filled with caries","Filled no caries"]
missing_decid = ["Missing due to caries"]
decayed_perm = ["Coronal caries","Root caries","Both coronal and root caries"]
filled_perm = ["Filled with caries","Filled no caries"]
missing_perm = ["Missing due to caries"]

def calc_dmft(row, teeth_list, d_labels, f_labels, m_labels):
    d=f=m=0
    for t in teeth_list:
        col = get_tooth_status_col(t)
        if col and col in row.index:
            v = str(row[col]).strip()
            if v in d_labels: d+=1
            elif v in f_labels: f+=1
            elif v in m_labels: m+=1
    return pd.Series({"D":d,"M":m,"F":f,"DMFT":d+m+f})

# ── TABS ──
tabs = st.tabs(["📊 Overview","🏠 Household","🪥 Oral Hygiene","🏥 Dental Services",
    "🦷 Caries/DMFT","🩸 Periodontal","🔬 Conditions","🦴 TMJ & Ortho",
    "💊 Lesions & Prosthetics","⚕️ Treatment Needs","👨\u200d⚕️ Examiner Analysis","🗺️ Cluster Analysis","📋 Data Explorer","⏱️ Work Hours"])

# ═══ TAB 0: OVERVIEW ═══
with tabs[0]:
    sec("Demographics Overview")
    c1,c2,c3 = st.columns(3)
    if col_gender:
        with c1: st.plotly_chart(pie(df[col_gender].dropna(),"Gender Distribution"),use_container_width=True)
    if col_ag:
        with c2: st.plotly_chart(pie(df[col_ag].dropna(),"Age Group Distribution"),use_container_width=True)
    if col_exam:
        with c3: st.plotly_chart(bar(df[col_exam].dropna(),"Participants per Examiner","h","#8b5cf6"),use_container_width=True)
    if col_ag and col_gender:
        sec("Gender × Age Group")
        st.plotly_chart(grp_bar(df.dropna(subset=[col_ag,col_gender]),col_ag,col_gender,"Gender × Age Group Cross-Tabulation"),use_container_width=True)
    if col_cluster:
        sec("Cluster Distribution")
        st.plotly_chart(bar(df[col_cluster].dropna(),"Participants per Cluster",clr="#06b6d4"),use_container_width=True)
    if has_date:
        sec("Enrolment Timeline")
        daily=df.groupby(df["_date"].dt.date).size().reset_index();daily.columns=["Date","Count"]
        fig=px.area(daily,x="Date",y="Count",title="Daily Participant Enrolment",color_discrete_sequence=["#3b82f6"])
        fig.update_traces(line_width=2,fill="tozeroy",fillcolor="rgba(59,130,246,.1)")
        fig.update_layout(**LY,height=300,xaxis=dict(showgrid=False),yaxis=dict(gridcolor="#f1f5f9"))
        st.plotly_chart(fig,use_container_width=True)

# ═══ TAB 1: HOUSEHOLD ═══
with tabs[1]:
    sec("Household Characteristics")
    if len(hh)==0:
        st.warning("No household-level records detected.")
    else:
        # ── NEW: HOUSEHOLD STATUS ANALYSIS ──
        if col_hh_status and col_hh_status in hh.columns:
            sec("📋 Household Participation Status")
            hh_status_vals = hh[col_hh_status].astype(str).str.strip()
            hh_status_vals = hh_status_vals[~hh_status_vals.isin(["nan","","None"])]
            total_hh = len(hh_status_vals)
            willing = (hh_status_vals.str.contains("Willing|willing|participate",case=False,na=False)).sum()
            not_avail = (hh_status_vals.str.contains("Not available|not available",case=False,na=False)).sum()
            refused = (hh_status_vals.str.contains("Refused|refused",case=False,na=False)).sum()
            other_status = total_hh - willing - not_avail - refused

            # KPIs
            s1,s2,s3,s4 = st.columns(4)
            with s1: kpi("Total Households",f"{total_hh}","")
            with s2: kpi("Willing",f"{willing}","g",f"{willing/max(total_hh,1)*100:.0f}%")
            with s3: kpi("Not Available",f"{not_avail}","o",f"{not_avail/max(total_hh,1)*100:.0f}%")
            with s4: kpi("Refused",f"{refused}","r",f"{refused/max(total_hh,1)*100:.0f}%")

            # Status distribution charts
            hs1, hs2 = st.columns(2)
            with hs1:
                st.plotly_chart(pie(hh_status_vals,"Household Participation Status",340),use_container_width=True)
            with hs2:
                # Status by cluster
                if col_cluster and col_cluster in hh.columns:
                    hh_with_status = hh.copy()
                    hh_with_status["_hh_status"] = hh[col_hh_status].astype(str).str.strip()
                    hh_filtered = hh_with_status[~hh_with_status["_hh_status"].isin(["nan","","None"])]
                    if len(hh_filtered)>0:
                        st.plotly_chart(grp_bar(hh_filtered.dropna(subset=[col_cluster,"_hh_status"]),col_cluster,"_hh_status","Household Status × Cluster",340),use_container_width=True)

            # Response rate metric
            if total_hh > 0:
                response_rate = willing / total_hh * 100
                if response_rate >= 80:
                    st.success(f"✅ Response rate: {response_rate:.1f}% — Excellent (≥80% WHO threshold)")
                elif response_rate >= 60:
                    st.warning(f"⚠️ Response rate: {response_rate:.1f}% — Moderate (below 80% WHO threshold)")
                else:
                    st.error(f"🚨 Response rate: {response_rate:.1f}% — Low (below 60%, may affect representativeness)")

            # Filter remaining analysis to only willing households
            st.markdown("---")
            st.caption("ℹ️ Charts below show data from **all households**. Use the status filter to see willing-only:")
            status_filter = st.radio("Filter household data:", ["All Households","Willing Only","Non-Respondents Only"], horizontal=True, key="hh_status_filter")
            if status_filter == "Willing Only":
                hh_display = hh[hh[col_hh_status].astype(str).str.contains("Willing|willing|participate",case=False,na=False)]
            elif status_filter == "Non-Respondents Only":
                hh_display = hh[~hh[col_hh_status].astype(str).str.contains("Willing|willing|participate",case=False,na=False)]
            else:
                hh_display = hh
            st.caption(f"Showing: **{len(hh_display)}** households")
        else:
            hh_display = hh

        # ── ORIGINAL HOUSEHOLD CHARTS (now using hh_display) ──
        sec("Socioeconomic Indicators")
        h1,h2 = st.columns(2)
        hh_src = hh_display
        if col_water:
            with h1: st.plotly_chart(pie(hh_src[col_water].dropna(),"Drinking Water Source",340),use_container_width=True)
        if col_fuel:
            with h2: st.plotly_chart(pie(hh_src[col_fuel].dropna(),"Cooking Fuel",340),use_container_width=True)
        h3,h4 = st.columns(2)
        if col_roof:
            with h3: st.plotly_chart(pie(hh_src[col_roof].dropna(),"Roof Material",300),use_container_width=True)
        if col_toilet:
            with h4: st.plotly_chart(pie(hh_src[col_toilet].dropna(),"Toilet Facility",300),use_container_width=True)
        if asset_cols:
            sec("Asset Ownership")
            asset_data = []
            for ac in asset_cols:
                if ac in hh_src.columns:
                    yes_pct = (hh_src[ac].astype(str).str.strip()=="Yes").mean()*100
                    asset_data.append({"Asset":ac,"Ownership %":round(yes_pct,1)})
            adf = pd.DataFrame(asset_data).sort_values("Ownership %",ascending=True)
            fig=px.bar(adf,x="Ownership %",y="Asset",orientation="h",title="Household Asset Ownership (%)",
                color="Ownership %",color_continuous_scale="Viridis")
            fig.update_layout(**LY,height=max(len(adf)*30+100,350),showlegend=False,xaxis=dict(showgrid=True,gridcolor="#f1f5f9"),yaxis=dict(showgrid=False))
            st.plotly_chart(fig,use_container_width=True)
            # Asset score
            sec("Wealth Index (Asset Score)")
            hh_src_copy = hh_src.copy()
            valid_asset_cols = [c for c in asset_cols if c in hh_src_copy.columns]
            hh_src_copy["_asset_score"] = hh_src_copy[valid_asset_cols].apply(lambda r: (r.astype(str).str.strip()=="Yes").sum(), axis=1)
            fig2=px.histogram(hh_src_copy,x="_asset_score",nbins=15,title="Distribution of Asset Score (count of Yes)",color_discrete_sequence=["#10b981"])
            fig2.update_layout(**LY,height=300,xaxis=dict(showgrid=False,title="Asset Score"),yaxis=dict(gridcolor="#f1f5f9",title="Households"))
            st.plotly_chart(fig2,use_container_width=True)

# ═══ TAB 2: ORAL HYGIENE ═══
with tabs[2]:
    sec("Oral Hygiene Behaviours")
    o1,o2 = st.columns(2)
    if col_cleaning:
        with o1: st.plotly_chart(pie(df[col_cleaning].dropna(),"Teeth Cleaning Method"),use_container_width=True)
    if col_brush_freq:
        with o2: st.plotly_chart(pie(df[col_brush_freq].dropna(),"Brushing Frequency"),use_container_width=True)
    o3,o4 = st.columns(2)
    if col_toothpaste:
        with o3: st.plotly_chart(pie(df[col_toothpaste].dropna(),"Toothpaste Type"),use_container_width=True)
    if col_sugar:
        with o4: st.plotly_chart(pie(df[col_sugar].dropna(),"Sugar Consumption Frequency"),use_container_width=True)
    # Cleaning material (checkbox cols)
    clean_mat_cols = [c for c in raw.columns if "material did you use to clean" in c.lower() and c in df.columns]
    if clean_mat_cols:
        sec("Cleaning Material Usage")
        mat_data = []
        for cm in clean_mat_cols:
            lbl = cm.split("choice=")[-1].rstrip(")") if "choice=" in cm else cm
            pct = (df[cm].astype(str).str.strip()=="Checked").mean()*100
            mat_data.append({"Material":lbl,"Usage %":round(pct,1)})
        mdf = pd.DataFrame(mat_data).sort_values("Usage %",ascending=True)
        fig=px.bar(mdf,x="Usage %",y="Material",orientation="h",title="Cleaning Material Usage (%)",color_discrete_sequence=["#8b5cf6"])
        fig.update_layout(**LY,height=250,xaxis=dict(showgrid=True,gridcolor="#f1f5f9"),yaxis=dict(showgrid=False))
        st.plotly_chart(fig,use_container_width=True)
    # Tobacco
    sec("Tobacco & Alcohol Use")
    t1,t2 = st.columns(2)
    if col_tobacco:
        with t1: st.plotly_chart(pie(df[col_tobacco].dropna(),"Current Tobacco Use"),use_container_width=True)
        if col_ag:
            with t2:
                tob_ag = df.dropna(subset=[col_tobacco,col_ag])
                tob_ct = pd.crosstab(tob_ag[col_ag],tob_ag[col_tobacco],normalize="index")*100
                if "Yes" in tob_ct.columns:
                    fig=px.bar(tob_ct.reset_index(),x=col_ag,y="Yes",title="Tobacco Use % by Age Group",color_discrete_sequence=["#ef4444"])
                    fig.update_layout(**LY,height=320,xaxis=dict(showgrid=False),yaxis=dict(gridcolor="#f1f5f9",title="% Using Tobacco"))
                    st.plotly_chart(fig,use_container_width=True)
    if col_alcohol:
        sec("Alcohol Consumption")
        a1,a2 = st.columns(2)
        with a1: st.plotly_chart(pie(df[col_alcohol].dropna(),"Current Alcohol Use"),use_container_width=True)
        if col_ag:
            with a2:
                alc_ag = df.dropna(subset=[col_alcohol,col_ag])
                alc_ct = pd.crosstab(alc_ag[col_ag],alc_ag[col_alcohol],normalize="index")*100
                if "Yes" in alc_ct.columns:
                    fig=px.bar(alc_ct.reset_index(),x=col_ag,y="Yes",title="Alcohol Use % by Age Group",color_discrete_sequence=["#f59e0b"])
                    fig.update_layout(**LY,height=320,xaxis=dict(showgrid=False),yaxis=dict(gridcolor="#f1f5f9",title="% Using Alcohol"))
                    st.plotly_chart(fig,use_container_width=True)
    # Cross: hygiene by gender
    if col_cleaning and col_gender:
        sec("Cleaning Method by Gender")
        st.plotly_chart(grp_bar(df.dropna(subset=[col_cleaning,col_gender]),col_cleaning,col_gender,"Cleaning Method × Gender"),use_container_width=True)

# ═══ TAB 3: DENTAL SERVICES ═══
with tabs[3]:
    sec("Dental Pain & Service Utilisation")
    d1,d2,d3 = st.columns(3)
    if col_pain:
        with d1: st.plotly_chart(pie(df[col_pain].dropna(),"Oral Pain (Last 6 Months)"),use_container_width=True)
    if col_dentist:
        with d2: st.plotly_chart(pie(df[col_dentist].dropna(),"Ever Visited Dentist"),use_container_width=True)
    if col_perception:
        with d3: st.plotly_chart(pie(df[col_perception].dropna(),"Self-Perception of Oral Health"),use_container_width=True)
    # Visit reasons
    visit_reason_cols = [c for c in raw.columns if "main reason for your last dental visit" in c.lower() and c in df.columns]
    if visit_reason_cols:
        sec("Reasons for Last Dental Visit")
        vr_data = []
        for vc in visit_reason_cols:
            lbl = vc.split("choice=")[-1].rstrip(")") if "choice=" in vc else vc
            pct = (df[vc].astype(str).str.strip()=="Checked").mean()*100
            vr_data.append({"Reason":lbl,"Prevalence %":round(pct,1)})
        vdf = pd.DataFrame(vr_data).sort_values("Prevalence %",ascending=True)
        fig=px.bar(vdf,x="Prevalence %",y="Reason",orientation="h",title="Reasons for Dental Visit",color_discrete_sequence=["#10b981"])
        fig.update_layout(**LY,height=max(len(vdf)*28+80,300),xaxis=dict(showgrid=True,gridcolor="#f1f5f9"),yaxis=dict(showgrid=False))
        st.plotly_chart(fig,use_container_width=True)
    # Not visiting reasons
    no_visit_cols = [c for c in raw.columns if "main reason for not visiting" in c.lower() and c in df.columns]
    if no_visit_cols:
        sec("Barriers to Dental Care")
        nv_data = []
        for nc in no_visit_cols:
            lbl = nc.split("choice=")[-1].rstrip(")") if "choice=" in nc else nc
            pct = (df[nc].astype(str).str.strip()=="Checked").mean()*100
            nv_data.append({"Barrier":lbl,"Prevalence %":round(pct,1)})
        ndf = pd.DataFrame(nv_data).sort_values("Prevalence %",ascending=True)
        fig=px.bar(ndf,x="Prevalence %",y="Barrier",orientation="h",title="Barriers to Visiting Dentist",color_discrete_sequence=["#ef4444"])
        fig.update_layout(**LY,height=max(len(ndf)*28+80,300),xaxis=dict(showgrid=True,gridcolor="#f1f5f9"),yaxis=dict(showgrid=False))
        st.plotly_chart(fig,use_container_width=True)
    # Where treatment
    if col_where:
        sec("Treatment Facility Type")
        st.plotly_chart(pie(df[col_where].dropna(),"Where Treatment Was Sought"),use_container_width=True)
    # Money spent
    if col_money:
        sec("Dental Expenditure")
        df["_money"] = pd.to_numeric(df[col_money],errors="coerce")
        money_valid = df["_money"].dropna()
        if len(money_valid)>0:
            m1,m2 = st.columns(2)
            with m1:
                fig=px.histogram(money_valid,nbins=20,title="Distribution of Dental Expenditure (₹)",color_discrete_sequence=["#3b82f6"])
                fig.update_layout(**LY,height=300,xaxis=dict(showgrid=False,title="Amount (₹)"),yaxis=dict(gridcolor="#f1f5f9",title="Count"))
                st.plotly_chart(fig,use_container_width=True)
            with m2:
                fig=px.box(df.dropna(subset=["_money"]),y="_money",title="Expenditure Box Plot",color_discrete_sequence=["#10b981"])
                fig.update_layout(**LY,height=300,yaxis=dict(gridcolor="#f1f5f9",title="Amount (₹)"))
                st.plotly_chart(fig,use_container_width=True)
            st.markdown(f"**Mean:** ₹{money_valid.mean():.0f} | **Median:** ₹{money_valid.median():.0f} | **Max:** ₹{money_valid.max():.0f}")

# ═══ TAB 4: CARIES / DMFT ═══
with tabs[4]:
    sec("Caries & DMFT Analysis")
    st.info("Computing DMFT/dmft indices from tooth-level data...")
    # Calculate DMFT for permanent teeth (age 12+)
    perm_status_cols = [get_tooth_status_col(t) for t in perm_teeth]
    perm_status_cols = [c for c in perm_status_cols if c and c in df.columns]
    decid_status_cols = [get_tooth_status_col(t) for t in decid_teeth]
    decid_status_cols = [c for c in decid_status_cols if c and c in df.columns]

    if perm_status_cols:
        dmft_df = df.apply(lambda r: calc_dmft(r,perm_teeth,decayed_perm,filled_perm,missing_perm),axis=1)
        df["_D"]=dmft_df["D"];df["_M"]=dmft_df["M"];df["_F"]=dmft_df["F"];df["_DMFT"]=dmft_df["DMFT"]
        d1,d2,d3,d4 = st.columns(4)
        with d1: kpi("Mean DMFT",f"{df['_DMFT'].mean():.2f}","","Decayed+Missing+Filled")
        with d2: kpi("Mean D",f"{df['_D'].mean():.2f}","r","Decayed")
        with d3: kpi("Mean M",f"{df['_M'].mean():.2f}","o","Missing")
        with d4: kpi("Mean F",f"{df['_F'].mean():.2f}","g","Filled")
        # DMFT by age group
        if col_ag:
            sec("DMFT by Age Group")
            dmft_ag = df.groupby(col_ag)[["_D","_M","_F","_DMFT"]].mean().round(2).reset_index()
            fig=go.Figure()
            for i,comp in enumerate(["_D","_M","_F"]):
                fig.add_trace(go.Bar(name=comp.replace("_",""),x=dmft_ag[col_ag].astype(str),y=dmft_ag[comp],marker_color=C[i],marker_line_width=0))
            fig.update_layout(**LY,barmode="stack",height=360,title="Mean DMFT Components by Age Group",
                xaxis=dict(showgrid=False,title="Age Group"),yaxis=dict(gridcolor="#f1f5f9",title="Mean Count"),
                legend=dict(orientation="h",yanchor="bottom",y=1.02))
            st.plotly_chart(fig,use_container_width=True)
        # DMFT by gender
        if col_gender:
            sec("DMFT by Gender")
            dmft_gen = df.groupby(col_gender)[["_D","_M","_F","_DMFT"]].mean().round(2).reset_index()
            st.dataframe(dmft_gen.rename(columns={"_D":"Decayed","_M":"Missing","_F":"Filled","_DMFT":"Total DMFT"}),use_container_width=True,hide_index=True)
        # DMFT distribution
        sec("DMFT Score Distribution")
        _dmft_max = df["_DMFT"].max()
        _dmft_bins = max(int(_dmft_max)+1, 10) if pd.notna(_dmft_max) else 10
        fig=px.histogram(df,x="_DMFT",nbins=_dmft_bins,title="DMFT Score Distribution",color_discrete_sequence=["#8b5cf6"])
        fig.update_layout(**LY,height=300,xaxis=dict(showgrid=False,title="DMFT Score"),yaxis=dict(gridcolor="#f1f5f9",title="Count"))
        st.plotly_chart(fig,use_container_width=True)
        # Caries prevalence
        sec("Caries Prevalence (% with D>0)")
        caries_pct = (df["_D"]>0).mean()*100
        st.markdown(f"**Overall caries prevalence: {caries_pct:.1f}%**")
        if col_ag:
            cprev = df.groupby(col_ag).apply(lambda x:(x["_D"]>0).mean()*100).reset_index()
            cprev.columns = [col_ag,"Caries Prevalence %"]
            fig=px.bar(cprev,x=col_ag,y="Caries Prevalence %",title="Caries Prevalence by Age Group",color_discrete_sequence=["#ef4444"])
            fig.update_layout(**LY,height=300,xaxis=dict(showgrid=False),yaxis=dict(gridcolor="#f1f5f9"))
            st.plotly_chart(fig,use_container_width=True)
        # Tooth-level caries heatmap
        sec("Tooth-Level Caries Prevalence")
        tooth_caries = {}
        for t in perm_teeth:
            col = get_tooth_status_col(t)
            if col and col in df.columns:
                vals = df[col].astype(str).str.strip()
                n_total = vals[vals!=""].shape[0]
                if n_total>0:
                    n_caries = vals.isin(decayed_perm).sum()
                    tooth_caries[f"T{t}"] = round(n_caries/n_total*100,1)
        if tooth_caries:
            tc_df = pd.DataFrame([tooth_caries])
            fig=px.imshow(tc_df,text_auto=True,aspect="auto",color_continuous_scale="YlOrRd",title="Caries % by Tooth (Permanent)")
            fig.update_layout(**LY,height=150)
            st.plotly_chart(fig,use_container_width=True)
    else:
        st.warning("No permanent tooth status columns found.")

# ═══ TAB 5: PERIODONTAL ═══
with tabs[5]:
    sec("Periodontal Health Analysis")
    # Bleeding prevalence
    bleed_cols = [get_tooth_bleed_col(t) for t in perm_teeth]
    bleed_cols = [c for c in bleed_cols if c and c in df.columns]
    if bleed_cols:
        sec("Gingival Bleeding Prevalence")
        bleed_data = {}
        for t in perm_teeth:
            col = get_tooth_bleed_col(t)
            if col and col in df.columns:
                vals = df[col].astype(str).str.strip()
                n_total = vals[~vals.isin(["","nan","Not recorded"])].shape[0]
                if n_total>0:
                    n_bleed = (vals=="Bleeding").sum()
                    bleed_data[f"T{t}"] = round(n_bleed/n_total*100,1)
        if bleed_data:
            bd = pd.DataFrame([bleed_data])
            fig=px.imshow(bd,text_auto=True,aspect="auto",color_continuous_scale="YlOrRd",title="Bleeding % by Tooth (Permanent)")
            fig.update_layout(**LY,height=150)
            st.plotly_chart(fig,use_container_width=True)
        # Overall bleeding prevalence
        any_bleed = df[bleed_cols].apply(lambda r: (r.astype(str).str.strip()=="Bleeding").any(),axis=1)
        st.markdown(f"**Any bleeding prevalence: {any_bleed.mean()*100:.1f}%** of participants")
    # Pocket depth
    pocket_cols = [get_tooth_pocket_col(t) for t in perm_teeth]
    pocket_cols = [c for c in pocket_cols if c and c in df.columns]
    if pocket_cols:
        sec("Periodontal Pocket Depth")
        pocket_all = df[pocket_cols].melt(value_name="Pocket")
        pocket_all = pocket_all[pocket_all["Pocket"].astype(str).str.strip().isin(["No pocket","Pocket of 4-5 mm","Pocket 6 mm or more"])]
        if len(pocket_all)>0:
            st.plotly_chart(pie(pocket_all["Pocket"],"Pocket Depth Distribution"),use_container_width=True)
        any_pocket = df[pocket_cols].apply(lambda r: r.astype(str).str.strip().isin(["Pocket of 4-5 mm","Pocket 6 mm or more"]).any(),axis=1)
        st.markdown(f"**Any pocketing (≥4mm) prevalence: {any_pocket.mean()*100:.1f}%**")
    # LOA
    loa_cols = [c for c in raw.columns if c.startswith("Tooth") and "/" in c and c in df.columns]
    if not loa_cols:
        loa_cols = [c for c in raw.columns if "loa" in c.lower() or ("Tooth" in c and ("17/16" in c or "11" in c or "26/27" in c or "36/37" in c or "31" in c or "47/46" in c))]
        loa_cols = [c for c in loa_cols if c in df.columns]
    if loa_cols:
        sec("Loss of Attachment (CPI)")
        loa_all = df[loa_cols].melt(value_name="LOA")
        loa_all = loa_all[loa_all["LOA"].astype(str).str.strip()!=""]
        loa_all = loa_all[~loa_all["LOA"].astype(str).str.strip().isin(["nan",""])]
        if len(loa_all)>0:
            st.plotly_chart(bar(loa_all["LOA"],"Loss of Attachment Distribution","h","#ef4444"),use_container_width=True)

# ═══ TAB 6: DENTAL CONDITIONS ═══
with tabs[6]:
    sec("Dental Conditions")
    c1,c2 = st.columns(2)
    if col_fluorosis:
        with c1: st.plotly_chart(pie(df[col_fluorosis].dropna(),"Enamel Fluorosis Severity"),use_container_width=True)
    if col_erosion:
        with c2: st.plotly_chart(pie(df[col_erosion].dropna(),"Dental Erosion Severity"),use_container_width=True)
    c3,c4 = st.columns(2)
    if col_abrasion:
        with c3: st.plotly_chart(pie(df[col_abrasion].dropna(),"Dental Abrasion"),use_container_width=True)
    if col_attrition:
        with c4: st.plotly_chart(pie(df[col_attrition].dropna(),"Dental Attrition"),use_container_width=True)
    if col_trauma:
        sec("Dental Trauma")
        st.plotly_chart(pie(df[col_trauma].dropna(),"Dental Trauma Type"),use_container_width=True)
    # Fluorosis by age group
    if col_fluorosis and col_ag:
        sec("Fluorosis by Age Group")
        st.plotly_chart(grp_bar(df.dropna(subset=[col_fluorosis,col_ag]),col_ag,col_fluorosis,"Fluorosis Severity × Age Group"),use_container_width=True)
    # Edentulous
    if col_edentulous:
        sec("Edentulous Status (65-74)")
        st.plotly_chart(pie(df[col_edentulous].dropna(),"Edentulous Status"),use_container_width=True)
    # DMH for 4-6
    dmh_col = find_col(["Deciduous Molar Hypomineralization","DMH"],raw.columns)
    if dmh_col and dmh_col in df.columns:
        sec("Deciduous Molar Hypomineralization (4-6 yrs)")
        st.plotly_chart(pie(df[dmh_col].dropna(),"DMH Status"),use_container_width=True)

# ═══ TAB 7: TMJ & ORTHO ═══
with tabs[7]:
    sec("Temporomandibular Joint (TMJ) Assessment")
    tmj_cols = {"Clicking":col_clicking,"Tenderness":col_tenderness,"Reduced Jaw Mobility":col_jaw_mob,"Deviation of Jaw":col_deviation}
    tmj_valid = {k:v for k,v in tmj_cols.items() if v and v in df.columns}
    if tmj_valid:
        tmj_data = []
        for name,col in tmj_valid.items():
            yes_pct = (df[col].astype(str).str.strip()=="Yes").mean()*100
            tmj_data.append({"Finding":name,"Prevalence %":round(yes_pct,1)})
        tdf = pd.DataFrame(tmj_data).sort_values("Prevalence %",ascending=True)
        fig=px.bar(tdf,x="Prevalence %",y="Finding",orientation="h",title="TMJ Findings Prevalence",color_discrete_sequence=["#ef4444"])
        fig.update_layout(**LY,height=250,xaxis=dict(showgrid=True,gridcolor="#f1f5f9"),yaxis=dict(showgrid=False))
        st.plotly_chart(fig,use_container_width=True)
    sec("Dentofacial Anomalies")
    d1,d2 = st.columns(2)
    if col_crowding:
        with d1: st.plotly_chart(pie(df[col_crowding].dropna(),"Crowding Distribution"),use_container_width=True)
    if col_spacing:
        with d2: st.plotly_chart(pie(df[col_spacing].dropna(),"Spacing Distribution"),use_container_width=True)
    if col_molar:
        sec("Molar Relation")
        st.plotly_chart(pie(df[col_molar].dropna(),"Antero-posterior Molar Relation"),use_container_width=True)
    if col_overjet_max:
        sec("Overjet Distribution")
        df["_overjet"] = pd.to_numeric(df[col_overjet_max],errors="coerce")
        oj = df["_overjet"].dropna()
        if len(oj)>0:
            fig=px.histogram(oj,nbins=15,title="Maxillary Overjet Distribution (mm)",color_discrete_sequence=["#06b6d4"])
            fig.update_layout(**LY,height=280,xaxis=dict(showgrid=False,title="mm"),yaxis=dict(gridcolor="#f1f5f9"))
            st.plotly_chart(fig,use_container_width=True)

# ═══ TAB 8: LESIONS & PROSTHETICS ═══
with tabs[8]:
    sec("Oral Mucosal Lesions")
    if col_lesion:
        st.plotly_chart(pie(df[col_lesion].dropna(),"Oral Mucosal Lesion Present?"),use_container_width=True)
    # Lesion types (updated: includes OSMF)
    lesion_types = {"Oral Cancer":"Malignant tumor","Leukoplakia":"Leukoplakia","Lichen Planus":"Lichen planus",
        "Ulceration":"Ulceration","ANUG":"ANUG","Candidiasis":"Candidiasis","Abscess":"Abscess",
        "Oral Submucous Fibrosis (OSMF)":"osmf"}
    lesion_prevalence_data = []
    for lname,lkey in lesion_types.items():
        lcols = [c for c in raw.columns if lkey.lower() in c.lower() and "choice=" in c.lower() and c in df.columns]
        if lcols:
            any_present = df[lcols].apply(lambda r: (r.astype(str).str.strip()=="Checked").any(),axis=1)
            pct = any_present.mean()*100
            if pct>0:
                st.markdown(f"- **{lname}**: {pct:.1f}% prevalence")
                lesion_prevalence_data.append({"Lesion":lname,"Prevalence %":round(pct,1)})

    # Lesion prevalence bar chart (summary)
    if lesion_prevalence_data:
        sec("Lesion Prevalence Summary")
        lpdf = pd.DataFrame(lesion_prevalence_data).sort_values("Prevalence %",ascending=True)
        fig_lp = px.bar(lpdf,x="Prevalence %",y="Lesion",orientation="h",title="Oral Lesion Prevalence (%)",
            color="Prevalence %",color_continuous_scale="Reds")
        fig_lp.update_layout(**LY,height=max(len(lpdf)*40+100,300),showlegend=False,
            xaxis=dict(showgrid=True,gridcolor="#f1f5f9"),yaxis=dict(showgrid=False))
        st.plotly_chart(fig_lp,use_container_width=True)

    # ── NEW: OSMF DETAILED ANALYSIS ──
    osmf_cols = [c for c in raw.columns if "osmf" in c.lower() and "choice=" in c.lower() and c in df.columns]
    if osmf_cols:
        sec("🔬 Oral Submucous Fibrosis (OSMF) — Site Analysis")
        osmf_site_data = []
        for oc in osmf_cols:
            site_label = oc.split("choice=")[-1].rstrip(")") if "choice=" in oc else oc
            site_pct = (df[oc].astype(str).str.strip()=="Checked").mean()*100
            n_affected = (df[oc].astype(str).str.strip()=="Checked").sum()
            osmf_site_data.append({"Site":site_label,"Affected %":round(site_pct,1),"Count":int(n_affected)})
        osmf_df = pd.DataFrame(osmf_site_data)
        any_osmf = df[osmf_cols].apply(lambda r: (r.astype(str).str.strip()=="Checked").any(),axis=1)
        osmf_total = any_osmf.sum()
        osmf_pct = any_osmf.mean()*100

        # KPIs
        os1,os2,os3 = st.columns(3)
        with os1: kpi("OSMF Prevalence",f"{osmf_pct:.1f}%","r",f"{osmf_total} cases")
        with os2:
            # OSMF + tobacco correlation
            if col_tobacco:
                osmf_tob = df[any_osmf & (df[col_tobacco]=="Yes")].shape[0]
                osmf_tob_pct = osmf_tob/max(osmf_total,1)*100
                kpi("OSMF + Tobacco",f"{osmf_tob_pct:.0f}%","o",f"{osmf_tob}/{osmf_total} cases")
        with os3:
            if col_gender:
                osmf_male = df[any_osmf & (df[col_gender]=="Male")].shape[0]
                osmf_female = df[any_osmf & (df[col_gender]=="Female")].shape[0]
                kpi("M:F Ratio",f"{osmf_male}:{osmf_female}","p")

        # Site affected chart
        if osmf_df["Affected %"].sum() > 0:
            osmf_sorted = osmf_df[osmf_df["Affected %"]>0].sort_values("Affected %",ascending=True)
            fig_osmf = px.bar(osmf_sorted,x="Affected %",y="Site",orientation="h",
                title="OSMF Affected Sites (%)",color="Affected %",color_continuous_scale="OrRd",
                text="Count")
            fig_osmf.update_layout(**LY,height=max(len(osmf_sorted)*45+100,300),showlegend=False,
                xaxis=dict(showgrid=True,gridcolor="#f1f5f9"),yaxis=dict(showgrid=False))
            fig_osmf.update_traces(textposition="outside")
            st.plotly_chart(fig_osmf,use_container_width=True)

        # OSMF by age group
        if col_ag:
            osmf_by_age = df.groupby(col_ag).apply(lambda x: x[osmf_cols].apply(lambda r: (r.astype(str).str.strip()=="Checked").any(),axis=1).mean()*100).reset_index()
            osmf_by_age.columns = [col_ag,"OSMF %"]
            fig_osmf_age = px.bar(osmf_by_age,x=col_ag,y="OSMF %",title="OSMF Prevalence by Age Group",
                color_discrete_sequence=["#dc2626"])
            fig_osmf_age.update_layout(**LY,height=300,xaxis=dict(showgrid=False),yaxis=dict(gridcolor="#f1f5f9"))
            st.plotly_chart(fig_osmf_age,use_container_width=True)

        # Detailed site table
        st.dataframe(osmf_df.sort_values("Count",ascending=False),use_container_width=True,hide_index=True)
    sec("Prosthetic Status")
    if col_prosthetic:
        st.plotly_chart(pie(df[col_prosthetic].dropna(),"Has Prosthesis?"),use_container_width=True)
    up_col = find_col(["Upper Prosthetic","upper_prosthetic"],raw.columns)
    lp_col = find_col(["Lower Prosthetic","lower_prosthetic"],raw.columns)
    p1,p2 = st.columns(2)
    if up_col and up_col in df.columns:
        with p1: st.plotly_chart(pie(df[up_col].dropna(),"Upper Prosthetic Status"),use_container_width=True)
    if lp_col and lp_col in df.columns:
        with p2: st.plotly_chart(pie(df[lp_col].dropna(),"Lower Prosthetic Status"),use_container_width=True)

# ═══ TAB 9: TREATMENT NEEDS ═══
with tabs[9]:
    sec("Intervention Urgency")
    if col_intervention:
        st.plotly_chart(pie(df[col_intervention].dropna(),"Intervention Urgency Distribution",380),use_container_width=True)
        if col_ag:
            sec("Urgency by Age Group")
            st.plotly_chart(grp_bar(df.dropna(subset=[col_intervention,col_ag]),col_ag,col_intervention,"Intervention Urgency × Age Group",400),use_container_width=True)
        if col_gender:
            sec("Urgency by Gender")
            st.plotly_chart(grp_bar(df.dropna(subset=[col_intervention,col_gender]),col_gender,col_intervention,"Intervention Urgency × Gender",360),use_container_width=True)
    # Cross-analysis summary
    sec("Clinical Summary Table")
    summary_items = []
    if "_DMFT" in df.columns: summary_items.append({"Indicator":"Mean DMFT","Value":f"{df['_DMFT'].mean():.2f}"})
    if "_D" in df.columns: summary_items.append({"Indicator":"Caries Prevalence (D>0)","Value":f"{(df['_D']>0).mean()*100:.1f}%"})
    if col_fluorosis:
        flr = df[col_fluorosis].dropna()
        non_normal = flr[~flr.astype(str).str.strip().isin(["Normal",""])].shape[0]
        summary_items.append({"Indicator":"Fluorosis (any)","Value":f"{non_normal/max(len(flr),1)*100:.1f}%"})
    if col_tobacco:
        summary_items.append({"Indicator":"Tobacco Use","Value":f"{(df[col_tobacco]=='Yes').mean()*100:.1f}%"})
    if col_pain:
        summary_items.append({"Indicator":"Oral Pain","Value":f"{(df[col_pain]=='Yes').mean()*100:.1f}%"})
    if col_dentist:
        summary_items.append({"Indicator":"Visited Dentist","Value":f"{(df[col_dentist]=='Yes').mean()*100:.1f}%"})
    if col_lesion:
        summary_items.append({"Indicator":"Oral Lesion","Value":f"{(df[col_lesion]=='Yes').mean()*100:.1f}%"})
    if summary_items:
        st.dataframe(pd.DataFrame(summary_items),use_container_width=True,hide_index=True)
    if col_ind_status:
        sec("Individual Status")
        st.plotly_chart(pie(df[col_ind_status].dropna(),"Individual Completion Status"),use_container_width=True)

# ═══ TAB 10: EXAMINER ANALYSIS ═══
with tabs[10]:
    sec("Examiner Performance Overview")
    if col_exam:
        all_examiners = sorted(df[col_exam].dropna().unique())

        def _select_all_examiners():
            st.session_state["exam_tab_selector"] = list(all_examiners)

        # ── EXAMINER SELECTOR ──
        st.markdown('<div style="background:linear-gradient(90deg,#eff6ff,#f0fdf4);padding:16px 20px;border-radius:12px;margin-bottom:16px;border:1px solid #e2e8f0;">',unsafe_allow_html=True)
        st.markdown("**🔍 Select Examiners to Analyse**")
        sel_col1, sel_col2 = st.columns([4,1])
        with sel_col1:
            if "exam_tab_selector" not in st.session_state:
                selected_examiners = st.multiselect(
                    "Pick examiners (add/remove to compare)",
                    options=all_examiners,
                    default=all_examiners,
                    key="exam_tab_selector"
                )
            else:
                selected_examiners = st.multiselect(
                    "Pick examiners (add/remove to compare)",
                    options=all_examiners,
                    key="exam_tab_selector"
                )
        with sel_col2:
            st.markdown("<br>",unsafe_allow_html=True)
            st.button("Select All", key="exam_sel_all", on_click=_select_all_examiners, use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)

        if not selected_examiners:
            st.warning("⚠️ Please select at least one examiner to analyse.")
        else:
            # Filter data to selected examiners only
            edf = df[df[col_exam].isin(selected_examiners)]
            examiner_list = sorted(selected_examiners)
            is_single = len(examiner_list) == 1
            mode_label = f"**Analysing: Examiner {examiner_list[0]}**" if is_single else f"**Analysing: {len(examiner_list)} Examiners** ({', '.join([str(e) for e in examiner_list])})"
            st.info(mode_label)

            # ── SUMMARY TABLE ──
            exam_summary_rows = []
            for ex in examiner_list:
                ex_df = edf[edf[col_exam]==ex]
                row_data = {"Examiner": ex, "Participants": len(ex_df)}
                if col_gender:
                    row_data["Male"] = int((ex_df[col_gender]=="Male").sum())
                    row_data["Female"] = int((ex_df[col_gender]=="Female").sum())
                if col_ag:
                    for ag in sorted(df[col_ag].dropna().unique()):
                        row_data[ag] = int((ex_df[col_ag]==ag).sum())
                if has_date:
                    ex_dates = ex_df["_date"].dropna()
                    row_data["Days Active"] = int(ex_dates.dt.date.nunique()) if len(ex_dates)>0 else 0
                    row_data["Avg/Day"] = round(len(ex_df)/max(row_data.get("Days Active",1),1),1)
                if "_DMFT" in df.columns:
                    row_data["Mean DMFT"] = round(ex_df["_DMFT"].mean(),2) if len(ex_df)>0 else 0
                if "_D" in df.columns:
                    row_data["Caries %"] = round((ex_df["_D"]>0).mean()*100,1) if len(ex_df)>0 else 0
                if col_tobacco:
                    row_data["Tobacco %"] = round((ex_df[col_tobacco]=="Yes").mean()*100,1)
                if col_intervention:
                    urgent = ex_df[col_intervention].astype(str).str.contains("Immediate|urgent",case=False,na=False).sum()
                    row_data["Urgent"] = int(urgent)
                exam_summary_rows.append(row_data)
            exam_sum = pd.DataFrame(exam_summary_rows)
            st.dataframe(exam_sum, use_container_width=True, hide_index=True)

            # ── KPIs ──
            if len(exam_sum)>0:
                total_pts = int(exam_sum["Participants"].sum())
                e1,e2,e3,e4 = st.columns(4)
                with e1: kpi("Selected Examiners",f"{len(examiner_list)}","p")
                with e2: kpi("Total Participants",f"{total_pts}","")
                if is_single:
                    ex_row = exam_sum.iloc[0]
                    with e3: kpi("Avg/Day",f"{ex_row.get('Avg/Day','N/A')}","g")
                    with e4: kpi("Mean DMFT",f"{ex_row.get('Mean DMFT','N/A')}","r")
                else:
                    top_ex = exam_sum.sort_values("Participants",ascending=False).iloc[0]
                    with e3: kpi("Most Active",f"{top_ex['Examiner']}","g",f"{int(top_ex['Participants'])} pts")
                    if "Avg/Day" in exam_sum.columns:
                        with e4:
                            best_prod = exam_sum.sort_values("Avg/Day",ascending=False).iloc[0]
                            kpi("Most Productive",f"{best_prod['Examiner']}","",f"{best_prod['Avg/Day']}/day")

            # ── GENDER DISTRIBUTION ──
            if col_gender:
                sec("Gender Distribution per Examiner")
                st.plotly_chart(grp_bar(edf.dropna(subset=[col_exam,col_gender]),col_exam,col_gender,"Examiner × Gender"),use_container_width=True)

            # ── AGE GROUP DISTRIBUTION ──
            if col_ag:
                sec("Age Group Distribution per Examiner")
                st.plotly_chart(grp_bar(edf.dropna(subset=[col_exam,col_ag]),col_exam,col_ag,"Examiner × Age Group"),use_container_width=True)

            # ── DAILY PRODUCTIVITY ──
            if has_date:
                sec("Daily Productivity")
                daily_ex = edf.dropna(subset=["_date",col_exam]).groupby([edf["_date"].dt.date,col_exam]).size().reset_index()
                daily_ex.columns = ["Date","Examiner","Patients"]
                fig_line = px.line(daily_ex,x="Date",y="Patients",color="Examiner",
                    title="Daily Patients per Examiner",color_discrete_sequence=C,markers=True)
                fig_line.update_layout(**LY,height=350,xaxis=dict(showgrid=False),
                    yaxis=dict(gridcolor="#f1f5f9"),legend=dict(orientation="h",yanchor="bottom",y=1.02))
                st.plotly_chart(fig_line,use_container_width=True)

                sec("Productivity Distribution")
                prod = edf.dropna(subset=["_date",col_exam]).groupby([edf["_date"].dt.date,col_exam]).size().reset_index()
                prod.columns = ["Date","Examiner","Count"]
                fig_box = px.box(prod,x="Examiner",y="Count",color="Examiner",
                    title="Distribution of Daily Patient Count per Examiner",color_discrete_sequence=C)
                fig_box.update_layout(**LY,height=350,showlegend=False,
                    xaxis=dict(showgrid=False),yaxis=dict(gridcolor="#f1f5f9",title="Patients/Day"))
                st.plotly_chart(fig_box,use_container_width=True)

            # ── INDIVIDUAL EXAMINER DETAIL CARDS ──
            sec("📋 Individual Examiner Details")
            st.caption("Expand any examiner below for a detailed individual breakdown")
            for ex in examiner_list:
                ex_df = edf[edf[col_exam]==ex]
                label = f"👨‍⚕️ Examiner {ex}  —  {len(ex_df)} participants"
                with st.expander(label, expanded=is_single):
                    ic1, ic2, ic3, ic4 = st.columns(4)
                    with ic1: kpi("Participants",f"{len(ex_df)}","")
                    if col_gender:
                        with ic2: kpi("Male",f"{int((ex_df[col_gender]=='Male').sum())}","")
                        with ic3: kpi("Female",f"{int((ex_df[col_gender]=='Female').sum())}","p")
                    if "_DMFT" in df.columns:
                        with ic4: kpi("Mean DMFT",f"{ex_df['_DMFT'].mean():.2f}","r")

                    # Age group breakdown for this examiner
                    if col_ag:
                        age_cts = ex_df[col_ag].value_counts().reset_index()
                        age_cts.columns = ["Age Group","Count"]
                        st.dataframe(age_cts, use_container_width=True, hide_index=True)

                    # Cluster breakdown for this examiner
                    if col_cluster:
                        cl_cts = ex_df[col_cluster].value_counts().reset_index()
                        cl_cts.columns = ["Cluster","Count"]
                        st.dataframe(cl_cts, use_container_width=True, hide_index=True)

                    # Intervention urgency for this examiner
                    if col_intervention:
                        urg_cts = ex_df[col_intervention].dropna().value_counts().reset_index()
                        urg_cts.columns = ["Urgency","Count"]
                        st.dataframe(urg_cts, use_container_width=True, hide_index=True)

                    # Date range
                    if has_date:
                        ex_dates = ex_df["_date"].dropna()
                        if len(ex_dates)>0:
                            st.caption(f"📅 Active: {ex_dates.min().date()} → {ex_dates.max().date()} | Days: {ex_dates.dt.date.nunique()} | Avg/Day: {round(len(ex_df)/max(ex_dates.dt.date.nunique(),1),1)}")

            # ── DOWNLOAD REPORT ──
            sec("📥 Download Examiner Report")
            report_rows = []
            for ex in examiner_list:
                ex_df = edf[edf[col_exam]==ex]
                rr = {"Examiner": ex, "Total Participants": len(ex_df)}
                if col_gender:
                    rr["Male"] = int((ex_df[col_gender]=="Male").sum())
                    rr["Female"] = int((ex_df[col_gender]=="Female").sum())
                if col_ag:
                    for ag in sorted(df[col_ag].dropna().unique()):
                        rr[f"Age: {ag}"] = int((ex_df[col_ag]==ag).sum())
                if has_date:
                    dates = ex_df["_date"].dropna()
                    rr["First Date"] = str(dates.min().date()) if len(dates)>0 else ""
                    rr["Last Date"] = str(dates.max().date()) if len(dates)>0 else ""
                    rr["Days Active"] = int(dates.dt.date.nunique()) if len(dates)>0 else 0
                    rr["Avg Patients/Day"] = round(len(ex_df)/max(rr["Days Active"],1),1)
                if "_DMFT" in df.columns:
                    rr["Mean DMFT"] = round(ex_df["_DMFT"].mean(),2)
                    rr["Caries Prevalence %"] = round((ex_df["_D"]>0).mean()*100,1) if "_D" in ex_df.columns else ""
                if col_intervention:
                    urgent = ex_df[col_intervention].astype(str).str.contains("Immediate|urgent",case=False,na=False).sum()
                    rr["Urgent Cases"] = int(urgent)
                report_rows.append(rr)
            report_df = pd.DataFrame(report_rows)
            st.dataframe(report_df, use_container_width=True, hide_index=True)
            csv_report = report_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Examiner Report CSV",csv_report,"examiner_report.csv","text/csv",use_container_width=True)
    else:
        st.warning("No Examiner column found in the data.")

# ═══ TAB 11: CLUSTER ANALYSIS ═══
with tabs[11]:
    sec("Cluster-wise Performance Overview")
    if col_cluster:
        cluster_list = sorted(df[col_cluster].dropna().unique(), key=lambda x: str(x))
        # Summary table
        cl_summary_rows = []
        for cl in cluster_list:
            cl_df = df[df[col_cluster]==cl]
            row_data = {"Cluster": cl, "Participants": len(cl_df)}
            if col_gender:
                row_data["Male"] = int((cl_df[col_gender]=="Male").sum())
                row_data["Female"] = int((cl_df[col_gender]=="Female").sum())
            if col_ag:
                for ag in sorted(df[col_ag].dropna().unique()):
                    row_data[ag] = int((cl_df[col_ag]==ag).sum())
            if col_exam:
                row_data["Examiners"] = int(cl_df[col_exam].nunique())
            if "_DMFT" in df.columns:
                row_data["Mean DMFT"] = round(cl_df["_DMFT"].mean(),2) if len(cl_df)>0 else 0
            if "_D" in df.columns:
                row_data["Caries Prev %"] = round((cl_df["_D"]>0).mean()*100,1) if len(cl_df)>0 else 0
            if col_tobacco:
                row_data["Tobacco %"] = round((cl_df[col_tobacco]=="Yes").mean()*100,1)
            if col_pain:
                row_data["Oral Pain %"] = round((cl_df[col_pain]=="Yes").mean()*100,1)
            if col_intervention:
                urgent = cl_df[col_intervention].astype(str).str.contains("Immediate|urgent",case=False,na=False).sum()
                row_data["Urgent Cases"] = int(urgent)
            cl_summary_rows.append(row_data)
        cl_sum = pd.DataFrame(cl_summary_rows)
        st.dataframe(cl_sum, use_container_width=True, hide_index=True)

        # KPIs
        if len(cl_sum)>0:
            k1,k2,k3,k4 = st.columns(4)
            with k1: kpi("Total Clusters",f"{len(cluster_list)}","")
            with k2:
                top_cl = cl_sum.sort_values("Participants",ascending=False).iloc[0]
                kpi("Largest Cluster",f"{top_cl['Cluster']}","p",f"{int(top_cl['Participants'])} participants")
            if "Mean DMFT" in cl_sum.columns:
                with k3:
                    worst = cl_sum.sort_values("Mean DMFT",ascending=False).iloc[0]
                    kpi("Highest DMFT",f"{worst['Cluster']}","r",f"DMFT: {worst['Mean DMFT']}")
            if "Urgent Cases" in cl_sum.columns:
                with k4:
                    kpi("Total Urgent",f"{int(cl_sum['Urgent Cases'].sum())}","r")

        # Participants per cluster
        sec("Participants per Cluster")
        st.plotly_chart(bar(df[col_cluster].dropna(),"Participants per Cluster","h","#06b6d4"),use_container_width=True)

        # Gender distribution per cluster
        if col_gender:
            sec("Gender Distribution per Cluster")
            st.plotly_chart(grp_bar(df.dropna(subset=[col_cluster,col_gender]),col_cluster,col_gender,"Cluster × Gender"),use_container_width=True)

        # Age group distribution per cluster
        if col_ag:
            sec("Age Group Distribution per Cluster")
            st.plotly_chart(grp_bar(df.dropna(subset=[col_cluster,col_ag]),col_cluster,col_ag,"Cluster × Age Group"),use_container_width=True)

        # DMFT by cluster
        if "_DMFT" in df.columns:
            sec("DMFT by Cluster")
            dmft_cl = df.groupby(col_cluster)[["_D","_M","_F","_DMFT"]].mean().round(2).reset_index()
            dmft_cl.columns = ["Cluster","Mean D","Mean M","Mean F","Mean DMFT"]
            fig_dmft = go.Figure()
            for i,comp in enumerate(["Mean D","Mean M","Mean F"]):
                fig_dmft.add_trace(go.Bar(name=comp,x=dmft_cl["Cluster"].astype(str),y=dmft_cl[comp],
                    marker_color=["#ef4444","#64748b","#10b981"][i]))
            fig_dmft.update_layout(**LY,barmode="stack",height=380,title="Mean DMFT Components by Cluster",
                xaxis=dict(showgrid=False,title="Cluster"),yaxis=dict(gridcolor="#f1f5f9",title="Mean Score"),
                legend=dict(orientation="h",yanchor="bottom",y=1.02))
            st.plotly_chart(fig_dmft,use_container_width=True)

        # Intervention urgency by cluster
        if col_intervention:
            sec("Treatment Urgency by Cluster")
            st.plotly_chart(grp_bar(df.dropna(subset=[col_cluster,col_intervention]),col_cluster,col_intervention,"Cluster × Intervention Urgency",400),use_container_width=True)

        # Daily enrolment per cluster (if dates available)
        if has_date:
            sec("Enrolment Timeline per Cluster")
            daily_cl = df.dropna(subset=["_date",col_cluster]).groupby([df["_date"].dt.date,col_cluster]).size().reset_index()
            daily_cl.columns = ["Date","Cluster","Patients"]
            fig_tl = px.line(daily_cl,x="Date",y="Patients",color="Cluster",
                title="Daily Enrolment per Cluster",color_discrete_sequence=C,markers=True)
            fig_tl.update_layout(**LY,height=350,xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="#f1f5f9"),legend=dict(orientation="h",yanchor="bottom",y=1.02))
            st.plotly_chart(fig_tl,use_container_width=True)

        # Examiner × Cluster cross-tabulation
        if col_exam:
            sec("Examiner-wise Patient Count per Cluster")
            ct_ex_cl = pd.crosstab(df[col_cluster], df[col_exam], margins=True, margins_name="Total")
            ct_ex_cl.index.name = "Cluster"
            ct_ex_cl.columns = [f"Examiner {c}" if c != "Total" else c for c in ct_ex_cl.columns]
            ct_ex_cl = ct_ex_cl.reset_index()
            st.dataframe(ct_ex_cl, use_container_width=True, hide_index=True)

            # Grouped bar: Examiner counts in each cluster
            fig_ex_cl = grp_bar(df.dropna(subset=[col_cluster, col_exam]), col_cluster, col_exam, "Patients per Examiner in Each Cluster", 400)
            st.plotly_chart(fig_ex_cl, use_container_width=True)

            # Detailed per-cluster examiner breakdown
            sec("Detailed Cluster × Examiner Breakdown")
            for cl in cluster_list:
                cl_df = df[df[col_cluster]==cl]
                if len(cl_df)==0:
                    continue
                with st.expander(f"📁 Cluster: {cl}  ({len(cl_df)} participants)", expanded=False):
                    rows = []
                    for ex in sorted(cl_df[col_exam].dropna().unique()):
                        ex_sub = cl_df[cl_df[col_exam]==ex]
                        r = {"Examiner": ex, "Patients": len(ex_sub)}
                        if col_gender:
                            r["Male"] = int((ex_sub[col_gender]=="Male").sum())
                            r["Female"] = int((ex_sub[col_gender]=="Female").sum())
                        if col_ag:
                            for ag in sorted(df[col_ag].dropna().unique()):
                                r[ag] = int((ex_sub[col_ag]==ag).sum())
                        if "_DMFT" in df.columns:
                            r["Mean DMFT"] = round(ex_sub["_DMFT"].mean(), 2) if len(ex_sub)>0 else 0
                        rows.append(r)
                    if rows:
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # Downloadable cluster report
        sec("📥 Download Cluster Report")
        st.dataframe(cl_sum, use_container_width=True, hide_index=True)
        csv_cl = cl_sum.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Cluster Report CSV",csv_cl,"cluster_report.csv","text/csv",use_container_width=True)
    else:
        st.warning("No Cluster column found in the data.")

# ═══ TAB 12: DATA EXPLORER ═══
with tabs[12]:
    sec("Raw Data Explorer")
    st.markdown(f"**{len(df)} rows × {len(df.columns)} columns** (filtered)")
    st.dataframe(df.drop(columns=[c for c in df.columns if c.startswith("_")],errors="ignore"),use_container_width=True,height=500)
    csv = df.drop(columns=[c for c in df.columns if c.startswith("_")],errors="ignore").to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Filtered Data",csv,"filtered_data.csv","text/csv",use_container_width=True)
    sec("Column Summary")
    col_info = pd.DataFrame({
        "Column":raw.columns,
        "Non-Null":raw.notna().sum().values,
        "Missing %":(raw.isna().mean()*100).round(1).values,
        "Dtype":raw.dtypes.astype(str).values,
        "Unique":raw.nunique().values
    })
    st.dataframe(col_info,use_container_width=True,hide_index=True,height=400)

# ═══ TAB 13: EXAMINER WORK HOURS & CONSISTENCY ═══
with tabs[13]:
    sec("Examiner Work Hours & Day-wise Consistency")
    if col_exam and has_date:
        wh = df.dropna(subset=[col_exam,"_date"]).copy()
        wh["_day"] = wh["_date"].dt.date

        daily_rows = []
        for (ex,day),grp in wh.groupby([col_exam,"_day"]):
            first_t = grp["_date"].min()
            last_t = grp["_date"].max()
            n_pat = len(grp)
            dur_hr = (last_t-first_t).total_seconds()/3600
            avg_gap_min = (dur_hr*60/(n_pat-1)) if n_pat>1 else np.nan
            daily_rows.append({
                "Examiner":ex,"Date":day,"First Patient":first_t,"Last Patient":last_t,
                "Patients":n_pat,"Work Duration (hrs)":round(dur_hr,2),
                "Avg Time/Patient (min)":round(avg_gap_min,1) if pd.notna(avg_gap_min) else None,
                "First Time":first_t.strftime("%H:%M"),"Last Time":last_t.strftime("%H:%M")
            })
        daily_log = pd.DataFrame(daily_rows)

        if len(daily_log)==0:
            st.warning("No examiner + timestamp data available to compute work hours.")
        else:
            daily_log = daily_log.sort_values(["Examiner","Date"])
            daily_log["_start_dec"] = daily_log["First Patient"].apply(lambda t:t.hour+t.minute/60+t.second/3600)
            daily_log["_end_dec"] = daily_log["Last Patient"].apply(lambda t:t.hour+t.minute/60+t.second/3600)

            st.caption("First/Last Patient time is taken from the earliest and latest **Consent date/time** recorded per examiner per day.")

            # ── KPI ROW ──
            cons = daily_log.groupby("Examiner")["Work Duration (hrs)"].agg(["mean","std","count"]).reset_index()
            cons_multi = cons[cons["count"]>=2].copy()
            k1,k2,k3,k4 = st.columns(4)
            with k1: kpi("Examiner-Days Logged",f"{len(daily_log)}","")
            with k2: kpi("Avg Work Duration",f"{daily_log['Work Duration (hrs)'].mean():.1f} hrs","c")
            if len(cons_multi)>0:
                cons_multi["CV %"] = cons_multi["std"]/cons_multi["mean"].replace(0,np.nan)*100
                most_c = cons_multi.sort_values("CV %").iloc[0]
                least_c = cons_multi.sort_values("CV %",ascending=False).iloc[0]
                with k3: kpi("Most Consistent",f"Examiner {most_c['Examiner']}","g",f"CV: {most_c['CV %']:.1f}%")
                with k4: kpi("Least Consistent",f"Examiner {least_c['Examiner']}","r",f"CV: {least_c['CV %']:.1f}%")
            else:
                with k3: kpi("Examiners Tracked",f"{daily_log['Examiner'].nunique()}","g")
                with k4: kpi("Days Covered",f"{daily_log['Date'].nunique()}","o")

            # ── DAILY WORK SESSION TIMELINE (GANTT-STYLE) ──
            sec("📅 Daily Work Session Timeline")
            tl = daily_log.copy()
            tl["_disp_end"] = tl.apply(lambda r:r["Last Patient"]+pd.Timedelta(minutes=15) if r["First Patient"]==r["Last Patient"] else r["Last Patient"],axis=1)
            tl["Examiner Label"] = "Examiner "+tl["Examiner"].astype(str)
            fig_tl = px.timeline(tl,x_start="First Patient",x_end="_disp_end",y="Examiner Label",color="Examiner Label",
                color_discrete_sequence=C,hover_data=["Patients","Work Duration (hrs)","First Time","Last Time"])
            fig_tl.update_yaxes(title="",categoryorder="category descending")
            fig_tl.update_layout(**LY,height=max(tl["Examiner Label"].nunique()*70+100,300),showlegend=False,
                xaxis=dict(showgrid=True,gridcolor="#f1f5f9",title="Date & Time"))
            st.plotly_chart(fig_tl,use_container_width=True)
            st.caption("Each bar spans one examiner's working window on a given day — from first patient consented to last patient consented.")

            # ── DAY-WISE WORK DURATION, EXAMINER-WISE ──
            sec("📆 Work Duration by Day (Examiner-wise)")
            fig_day = go.Figure()
            for i,ex in enumerate(sorted(daily_log["Examiner"].unique())):
                sub = daily_log[daily_log["Examiner"]==ex].sort_values("Date")
                fig_day.add_trace(go.Bar(name=f"Examiner {ex}",x=sub["Date"].astype(str),y=sub["Work Duration (hrs)"],
                    marker_color=C[i%len(C)],marker_line_width=0))
            fig_day.update_layout(**LY,barmode="group",height=360,title="Daily Work Duration per Examiner",
                xaxis=dict(showgrid=False,title="Date"),yaxis=dict(gridcolor="#f1f5f9",title="Hours"),
                legend=dict(orientation="h",yanchor="bottom",y=1.02))
            st.plotly_chart(fig_day,use_container_width=True)

            # ── DAILY TIMING LOG TABLE ──
            sec("📋 Daily Timing Log")
            display_log = daily_log[["Examiner","Date","First Time","Last Time","Work Duration (hrs)","Patients","Avg Time/Patient (min)"]].sort_values(["Date","Examiner"])
            st.dataframe(display_log,use_container_width=True,hide_index=True)

            # ── START / END TIME CONSISTENCY ──
            sec("⏰ Start & End Time Consistency")
            b1,b2 = st.columns(2)
            with b1:
                fig_start = px.box(daily_log,x="Examiner",y="_start_dec",color="Examiner",points="all",
                    title="Daily Start Time Spread",color_discrete_sequence=C)
                fig_start.update_layout(**LY,height=340,showlegend=False,
                    xaxis=dict(showgrid=False,title="Examiner"),yaxis=dict(gridcolor="#f1f5f9",title="Start Hour (24h)"))
                st.plotly_chart(fig_start,use_container_width=True)
            with b2:
                fig_dur = px.box(daily_log,x="Examiner",y="Work Duration (hrs)",color="Examiner",points="all",
                    title="Daily Work Duration Spread",color_discrete_sequence=C)
                fig_dur.update_layout(**LY,height=340,showlegend=False,
                    xaxis=dict(showgrid=False,title="Examiner"),yaxis=dict(gridcolor="#f1f5f9",title="Hours"))
                st.plotly_chart(fig_dur,use_container_width=True)

            # ── EXAMINER CONSISTENCY SUMMARY ──
            sec("📊 Examiner Consistency Summary")
            summary_rows = []
            for ex,g in daily_log.groupby("Examiner"):
                days_worked = g["Date"].nunique()
                avg_dur = round(g["Work Duration (hrs)"].mean(),2)
                std_dur = round(g["Work Duration (hrs)"].std(),2) if days_worked>1 else None
                cv = round(std_dur/avg_dur*100,1) if (std_dur is not None and avg_dur>0) else None
                summary_rows.append({
                    "Examiner":ex,
                    "Days Worked":days_worked,
                    "Total Patients":int(g["Patients"].sum()),
                    "Avg Patients/Day":round(g["Patients"].mean(),1),
                    "Avg Start Time":f"{int(g['_start_dec'].mean()):02d}:{int((g['_start_dec'].mean()%1)*60):02d}",
                    "Avg End Time":f"{int(g['_end_dec'].mean()):02d}:{int((g['_end_dec'].mean()%1)*60):02d}",
                    "Avg Duration (hrs)":avg_dur,
                    "Std Dev Duration (hrs)":std_dur,
                    "Consistency CV %":cv,
                })
            summary_df = pd.DataFrame(summary_rows).sort_values("Consistency CV %",na_position="last")
            st.dataframe(summary_df,use_container_width=True,hide_index=True)
            st.caption("Lower Consistency CV % = steadier day-to-day work duration for that examiner. Blank CV means only 1 day logged — not enough data to judge consistency.")

            # ── DOWNLOAD REPORTS ──
            sec("📥 Download Reports")
            dl1,dl2 = st.columns(2)
            with dl1:
                csv_log = display_log.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Download Daily Timing Log CSV",csv_log,"examiner_daily_timing_log.csv","text/csv",use_container_width=True)
            with dl2:
                csv_summary = summary_df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Download Consistency Summary CSV",csv_summary,"examiner_consistency_summary.csv","text/csv",use_container_width=True)
    else:
        st.warning("Examiner and/or Date columns not found — cannot compute work-hour consistency.")
