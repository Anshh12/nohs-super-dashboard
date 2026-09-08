"""
Super Multi‑Module Combined Dashboard
======================================
Integrates:
  1. Oral Health Survey Analytics (14 tabs)
  2. Duplicate Comparator (two files, pair‑wise + aggregated)
  3. Recorded vs Duplicate (single file, examiner summaries)
  4. Data Cleaner (household duplicate merge + redundancy removal)
  5. Household Listing Dashboard (10 tabs)

All modules share the same page config, CSS, and helper functions.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Super Oral Health & Household Dashboard",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# GLOBAL CSS (merged from all modules)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
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
/* comparator styles */
.metric-card {
    background: white; border-radius: 14px; padding: 1.2rem 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,.05); border-left: 4px solid #3b82f6; text-align: center;
}
.metric-card.green  { border-left-color: #10b981; }
.metric-card.orange { border-left-color: #f59e0b; }
.metric-card.red    { border-left-color: #ef4444; }
.metric-card.purple { border-left-color: #8b5cf6; }
.metric-card.teal   { border-left-color: #14b8a6; }
.metric-value { font-size: 2rem; font-weight: 700; color: #0f172a; font-family: 'DM Mono', monospace; }
.metric-label { font-size: 0.82rem; color: #64748b; margin-top: 0.25rem; font-weight: 500; letter-spacing: 0.02em; }
.section-header {
    font-size: 1rem; font-weight: 600; color: #1e293b;
    padding: 0.5rem 0; border-bottom: 2px solid #e2e8f0; margin-bottom: 1rem;
}
.warning-banner {
    background: linear-gradient(135deg, #fef3c7, #fde68a);
    border: 1px solid #f59e0b; border-radius: 10px;
    padding: 0.8rem 1rem; font-size: 0.88rem; color: #78350f; margin-bottom: 1rem;
}
.fix-banner {
    background: linear-gradient(135deg, #d1fae5, #a7f3d0);
    border: 1px solid #10b981; border-radius: 10px;
    padding: 0.8rem 1rem; font-size: 0.88rem; color: #064e3b; margin-bottom: 1rem;
}
.preset-info {
    background: linear-gradient(135deg, #eff6ff, #dbeafe);
    border: 1px solid #3b82f6; border-radius: 10px;
    padding: 0.7rem 1rem; font-size: 0.85rem; color: #1e40af; margin-bottom: 0.8rem;
}
.date-info {
    background: linear-gradient(135deg, #f5f3ff, #ede9fe);
    border: 1px solid #8b5cf6; border-radius: 10px;
    padding: 0.7rem 1rem; font-size: 0.85rem; color: #5b21b6; margin-bottom: 0.8rem;
}
.stDataFrame { border-radius: 10px; overflow: hidden; }
div[data-testid="stExpander"] { border-radius: 12px; border: 1px solid #e2e8f0; }
.alert-r{background:#fef2f2;border-left:4px solid #ef4444;padding:10px 14px;border-radius:6px;color:#7f1d1d;font-size:.85rem;margin:8px 0;}
.alert-o{background:#fffbeb;border-left:4px solid #f59e0b;padding:10px 14px;border-radius:6px;color:#78350f;font-size:.85rem;margin:8px 0;}
.alert-g{background:#f0fdf4;border-left:4px solid #10b981;padding:10px 14px;border-radius:6px;color:#14532d;font-size:.85rem;margin:8px 0;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SHARED HELPERS (age group fix, column detection, plotting, comparator)
# ─────────────────────────────────────────────

AGE_GROUP_CORRUPTION_MAP = {
    'Dec-15': '12-15', '15-Dec': '12-15', '01-Dec': '12-15',
    'Dec-01': '12-15', '12-Dec': '12-15',
    '04-Jun': '4-6',   'Jun-04': '4-6',   'Jun-26': '4-6',
    'Apr-06': '4-6',   '06-Apr': '4-6',   'Apr-6':  '4-6',
    '6-Apr':  '4-6',   '4-Jun':  '4-6',   'Jun-4':  '4-6',
    'Jan-02': '1-2',   '02-Jan': '1-2',
}

def normalize_age_group(series):
    return series.map(
        lambda x: AGE_GROUP_CORRUPTION_MAP.get(str(x).strip(), str(x).strip())
        if pd.notna(x) else x
    )

def detect_corrupted_values(series):
    return [v for v in series.dropna().unique() if str(v).strip() in AGE_GROUP_CORRUPTION_MAP]

def normalize_export_columns(df):
    column_map = {
        'Repeat Instrument': 'repeat_instrument',
        'Repeat Instance': 'repeat_instance',
        'Record ID': 'record_id',
        'cluster code': 'cluster_code',
        'Cluster Code': 'cluster_code',
        'Household Number': 'household_number',
        'Age (years)': 'age_(years)',
        'Age group': 'age_group',
        'Gender': 'gender',
        'Examiner Number': 'examiner_number',
        'Consent date': 'consent_date',
        'redcap_repeat_instrument': 'repeat_instrument',
        'redcap_repeat_instance': 'repeat_instance',
        'examiner_suffix': 'examiner_number',
        'age': 'age_(years)',
        'sex': 'gender',
    }
    return df.rename(columns={c: column_map.get(c, c) for c in df.columns})

def find_col(keywords, cols):
    for c in cols:
        for kw in keywords:
            if kw.lower() in c.lower():
                return c
    return None

# ─── Plotting helpers ───
C = ["#3b82f6","#10b981","#8b5cf6","#f59e0b","#ef4444","#06b6d4","#ec4899","#14b8a6","#f97316","#6366f1"]
LY = dict(paper_bgcolor="white",plot_bgcolor="white",font=dict(family="Inter",size=11,color="#334155"),margin=dict(l=10,r=10,t=40,b=10))

def kpi(l, v, c="", d=""):
    st.markdown(f'<div class="kpi {c}"><div class="kpi-l">{l}</div><div class="kpi-v">{v}</div>{"<div class=kpi-d>"+d+"</div>" if d else ""}</div>', unsafe_allow_html=True)

def sec(t):
    st.markdown(f'<div class="sec">{t}</div>', unsafe_allow_html=True)

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

def alert(msg, kind="r"):
    st.markdown(f'<div class="alert-{kind}">{msg}</div>', unsafe_allow_html=True)

# ─── Comparator helpers ───
def pct_color(val):
    try:
        v = float(val)
        if v >= 80:   return 'background-color: #dcfce7; color: #166534'
        elif v >= 60: return 'background-color: #fef9c3; color: #854d0e'
        else:          return 'background-color: #fee2e2; color: #991b1b'
    except:
        return ''

def color_status(val):
    if 'Agree' in str(val):      return 'background-color: #f0fdf4; color: #166534'
    elif 'Disagree' in str(val): return 'background-color: #fef2f2; color: #991b1b'
    elif 'Missing' in str(val):  return 'background-color: #fefce8; color: #854d0e'
    return ''

def build_participant_df(df, label):
    hh_cols = [c for c in ['record_id', 'cluster_code', 'household_number'] if c in df.columns]
    if 'repeat_instrument' in df.columns:
        repeat_values = df['repeat_instrument'].astype(str).str.strip().str.lower()
        hh = df[df['repeat_instrument'].isna()][hh_cols].drop_duplicates('record_id')
        pt = df[repeat_values == 'participant'].copy()
        if pt.empty:
            pt = df.copy()
    else:
        hh = df[hh_cols].drop_duplicates('record_id') if hh_cols else pd.DataFrame()
        pt = df.copy()
    for c in ['cluster_code', 'household_number']:
        if c in pt.columns:
            pt = pt.drop(columns=[c])
    if not hh.empty and 'record_id' in pt.columns and 'record_id' in hh.columns:
        result = pt.merge(hh, on='record_id', how='left')
    else:
        result = pt
    result['_source'] = label
    if 'age_group' in result.columns:
        result['age_group'] = normalize_age_group(result['age_group'])
    if 'gender' in result.columns:
        result['gender'] = result['gender'].astype(str).str.strip()
    return result

def compare_fields(merged, suffix_a='_A', suffix_b='_B'):
    exclude = {
        'record_id','repeat_instrument','repeat_instance','_source',
        'examiner_number','cluster_code','household_number',
        'age_(years)','age_group','gender','consent_date','signature','complete?','complete?.1'
    }
    base_cols = [c.replace(suffix_a, '') for c in merged.columns if c.endswith(suffix_a)]
    return [c for c in base_cols if c not in exclude]

def field_agreement_summary(merged, compare_cols, suffix_a='_A', suffix_b='_B'):
    records = []
    for col in compare_cols:
        ca, cb = col + suffix_a, col + suffix_b
        if ca not in merged.columns or cb not in merged.columns:
            continue
        va, vb = merged[ca], merged[cb]
        both = va.notna() & vb.notna()
        if both.sum() == 0:
            continue
        agree = (va[both].astype(str) == vb[both].astype(str)).sum()
        total = both.sum()
        records.append({
            'Field': col, 'Assessed': int(total),
            'Agree': int(agree), 'Disagree': int(total - agree),
            'Agreement %': round(100 * agree / total, 1)
        })
    return pd.DataFrame(records).sort_values('Agreement %') if records else pd.DataFrame(
        columns=['Field','Assessed','Agree','Disagree','Agreement %'])

def participant_level_comparison(merged, compare_cols, label_a, label_b,
                                 suffix_a='_A', suffix_b='_B', idx=0):
    row = merged.iloc[idx]
    records = []
    for col in compare_cols:
        ca, cb = col + suffix_a, col + suffix_b
        if ca not in merged.columns or cb not in merged.columns:
            continue
        va = row.get(ca, np.nan)
        vb = row.get(cb, np.nan)
        va_str = str(va) if not (isinstance(va, float) and np.isnan(va)) else ''
        vb_str = str(vb) if not (isinstance(vb, float) and np.isnan(vb)) else ''
        if not va_str and not vb_str:
            continue
        if not va_str or not vb_str:
            status = 'Missing in one'
        elif va_str == vb_str:
            status = 'Agree ✅'
        else:
            status = 'Disagree ❌'
        records.append({
            'Field': col,
            f'Examiner {label_a}': va_str,
            f'Examiner {label_b}': vb_str,
            'Status': status
        })
    return pd.DataFrame(records)

def build_examiner_reports(merged, compare_cols, selected_keys, label_a, label_b,
                           low_agree_threshold):
    examiner_cols = ['examiner_number_A', 'examiner_number_B']
    if not all(c in merged.columns for c in examiner_cols):
        return pd.DataFrame(), {}, {}

    summary_records = []
    agreement_by_pair = {}
    discrepancies_by_pair = {}

    grouped = merged.groupby(examiner_cols, dropna=False, sort=True)
    for (exam_a, exam_b), group in grouped:
        group = group.reset_index(drop=True)
        pair_key = f"{exam_a} vs {exam_b}"
        pair_agreement = field_agreement_summary(group, compare_cols)
        agreement_by_pair[pair_key] = pair_agreement

        pair_discrepancies = []
        missing_count = 0
        for i in range(len(group)):
            comp = participant_level_comparison(group, compare_cols, label_a, label_b, idx=i)
            if comp.empty:
                continue
            missing_count += int((comp['Status'] == 'Missing in one').sum())
            disc = comp[comp['Status'].astype(str).str.startswith('Disagree')].copy()
            if disc.empty:
                continue
            disc.insert(0, 'Participant #', i + 1)
            disc.insert(1, f'Record ID ({label_a})', group.iloc[i].get('record_id_A', ''))
            disc.insert(2, f'Record ID ({label_b})', group.iloc[i].get('record_id_B', ''))
            parts = [f"{k.replace('_',' ').title()}: {group.iloc[i][k]}"
                     for k in selected_keys if k in group.columns and pd.notna(group.iloc[i][k])]
            disc.insert(3, 'Matching Key', ' | '.join(parts))
            disc.insert(4, f'Examiner Number ({label_a})', exam_a)
            disc.insert(5, f'Examiner Number ({label_b})', exam_b)
            pair_discrepancies.append(disc)

        pair_disc_df = pd.concat(pair_discrepancies, ignore_index=True) if pair_discrepancies else pd.DataFrame()
        discrepancies_by_pair[pair_key] = pair_disc_df

        summary_records.append({
            f'Examiner Number ({label_a})': exam_a,
            f'Examiner Number ({label_b})': exam_b,
            'Matched Participants': len(group),
            'Fields Assessed': len(pair_agreement),
            'Avg Agreement %': round(pair_agreement['Agreement %'].mean(), 1) if not pair_agreement.empty else 0,
            'Min Agreement %': round(pair_agreement['Agreement %'].min(), 1) if not pair_agreement.empty else 0,
            f'Fields < {low_agree_threshold}%': (
                int((pair_agreement['Agreement %'] < low_agree_threshold).sum())
                if not pair_agreement.empty else 0
            ),
            'Discrepancies': len(pair_disc_df),
            'Missing in One': missing_count,
        })

    summary_df = pd.DataFrame(summary_records)
    if not summary_df.empty:
        summary_df = summary_df.sort_values(['Avg Agreement %', 'Discrepancies'],
                                            ascending=[True, False])
    return summary_df, agreement_by_pair, discrepancies_by_pair

def build_examiner_aggregated_reports(merged, compare_cols, selected_keys, label_a, label_b,
                                      low_agree_threshold):
    summary_A_records = []
    summary_B_records = []
    agreement_A = {}
    agreement_B = {}
    discrepancies_A = {}
    discrepancies_B = {}

    if 'examiner_number_A' in merged.columns:
        for exam, group in merged.groupby('examiner_number_A', dropna=False):
            group = group.reset_index(drop=True)
            ag_df = field_agreement_summary(group, compare_cols)
            agreement_A[exam] = ag_df
            disc_list = []
            missing_count = 0
            for i in range(len(group)):
                comp = participant_level_comparison(group, compare_cols, label_a, label_b, idx=i)
                if comp.empty:
                    continue
                missing_count += int((comp['Status'] == 'Missing in one').sum())
                disc = comp[comp['Status'].astype(str).str.startswith('Disagree')].copy()
                if disc.empty:
                    continue
                disc.insert(0, 'Participant #', i + 1)
                disc.insert(1, f'Record ID ({label_a})', group.iloc[i].get('record_id_A', ''))
                disc.insert(2, f'Record ID ({label_b})', group.iloc[i].get('record_id_B', ''))
                parts = [f"{k.replace('_',' ').title()}: {group.iloc[i][k]}"
                         for k in selected_keys if k in group.columns and pd.notna(group.iloc[i][k])]
                disc.insert(3, 'Matching Key', ' | '.join(parts))
                disc.insert(4, f'Examiner Number ({label_a})', exam)
                disc.insert(5, f'Examiner Number ({label_b})', 'Aggregated')
                disc_list.append(disc)
            disc_df = pd.concat(disc_list, ignore_index=True) if disc_list else pd.DataFrame()
            discrepancies_A[exam] = disc_df
            summary_A_records.append({
                f'Examiner ({label_a})': exam,
                'Matched Participants': len(group),
                'Fields Assessed': len(ag_df),
                'Avg Agreement %': round(ag_df['Agreement %'].mean(), 1) if not ag_df.empty else 0,
                'Min Agreement %': round(ag_df['Agreement %'].min(), 1) if not ag_df.empty else 0,
                f'Fields < {low_agree_threshold}%': (
                    int((ag_df['Agreement %'] < low_agree_threshold).sum()) if not ag_df.empty else 0
                ),
                'Discrepancies': len(disc_df),
                'Missing in One': missing_count,
            })

    if 'examiner_number_B' in merged.columns:
        for exam, group in merged.groupby('examiner_number_B', dropna=False):
            group = group.reset_index(drop=True)
            ag_df = field_agreement_summary(group, compare_cols)
            agreement_B[exam] = ag_df
            disc_list = []
            missing_count = 0
            for i in range(len(group)):
                comp = participant_level_comparison(group, compare_cols, label_a, label_b, idx=i)
                if comp.empty:
                    continue
                missing_count += int((comp['Status'] == 'Missing in one').sum())
                disc = comp[comp['Status'].astype(str).str.startswith('Disagree')].copy()
                if disc.empty:
                    continue
                disc.insert(0, 'Participant #', i + 1)
                disc.insert(1, f'Record ID ({label_a})', group.iloc[i].get('record_id_A', ''))
                disc.insert(2, f'Record ID ({label_b})', group.iloc[i].get('record_id_B', ''))
                parts = [f"{k.replace('_',' ').title()}: {group.iloc[i][k]}"
                         for k in selected_keys if k in group.columns and pd.notna(group.iloc[i][k])]
                disc.insert(3, 'Matching Key', ' | '.join(parts))
                disc.insert(4, f'Examiner Number ({label_a})', 'Aggregated')
                disc.insert(5, f'Examiner Number ({label_b})', exam)
                disc_list.append(disc)
            disc_df = pd.concat(disc_list, ignore_index=True) if disc_list else pd.DataFrame()
            discrepancies_B[exam] = disc_df
            summary_B_records.append({
                f'Examiner ({label_b})': exam,
                'Matched Participants': len(group),
                'Fields Assessed': len(ag_df),
                'Avg Agreement %': round(ag_df['Agreement %'].mean(), 1) if not ag_df.empty else 0,
                'Min Agreement %': round(ag_df['Agreement %'].min(), 1) if not ag_df.empty else 0,
                f'Fields < {low_agree_threshold}%': (
                    int((ag_df['Agreement %'] < low_agree_threshold).sum()) if not ag_df.empty else 0
                ),
                'Discrepancies': len(disc_df),
                'Missing in One': missing_count,
            })

    summary_A = pd.DataFrame(summary_A_records) if summary_A_records else pd.DataFrame()
    summary_B = pd.DataFrame(summary_B_records) if summary_B_records else pd.DataFrame()
    if not summary_A.empty:
        summary_A = summary_A.sort_values(['Avg Agreement %', 'Discrepancies'], ascending=[True, False])
    if not summary_B.empty:
        summary_B = summary_B.sort_values(['Avg Agreement %', 'Discrepancies'], ascending=[True, False])

    return summary_A, summary_B, agreement_A, agreement_B, discrepancies_A, discrepancies_B

def safe_excel_sheet_name(name, used_names):
    cleaned = ''.join('_' if ch in '[]:*?/\\' else ch for ch in str(name))[:31]
    cleaned = cleaned or 'Sheet'
    candidate = cleaned
    n = 1
    while candidate in used_names:
        suffix = f"_{n}"
        candidate = cleaned[:31 - len(suffix)] + suffix
        n += 1
    used_names.add(candidate)
    return candidate

def get_unmatched(pt, other_pt, keys):
    if not all(k in pt.columns and k in other_pt.columns for k in keys):
        return pd.DataFrame()
    pt_keys  = pt[keys].apply(tuple, axis=1)
    mrg_keys = other_pt[keys].apply(tuple, axis=1)
    mask = ~pt_keys.isin(set(mrg_keys))
    extra = [c for c in ['age_group'] if c in pt.columns and c not in keys]
    return pt[mask][['record_id'] + keys + extra].copy()

def make_label(row, keys):
    parts = []
    for k in keys:
        if k in row.index and pd.notna(row[k]):
            parts.append(f"{k.replace('_',' ').title()}: {row[k]}")
    return ' | '.join(parts) if parts else f"Row #{row.name}"

def classify_fields(all_cols):
    categories = {
        "🦷 Tooth Status (Primary)": [],
        "🦷 Tooth Status (Permanent)": [],
        "🩸 Bleeding": [],
        "📏 Pocket Depth": [],
        "🔬 Opacity / MIH / DMH": [],
        "🌡️ Fluorosis & Erosion": [],
        "🦴 Orthodontics / Malocclusion": [],
        "👄 Oral Mucosal Lesions": [],
        "🔩 Prosthetics": [],
        "🦷 TMJ / Jaw": [],
        "🎭 Dental Trauma & Abrasion": [],
        "🧬 Fluorosis Index (Index Teeth)": [],
        "🧑 Demographics": [],
        "📋 Behavioural / Oral Hygiene": [],
        "💊 Dental Visit / Treatment": [],
        "🏠 Socioeconomic / Household": [],
        "📝 Other Clinical": [],
    }
    primary_teeth = ['55','54','53','52','51','61','62','63','64','65',
                     '75','74','73','72','71','81','82','83','84','85']
    permanent_teeth = ['18','17','16','15','14','13','12','11',
                       '21','22','23','24','25','26','27','28',
                       '38','37','36','35','34','33','32','31',
                       '41','42','43','44','45','46','47','48']
    ses_keywords = ['pressure_cooker','color_tv','refrigerator','table','washing_machine',
                    'sewing_machine','ac_cooler','mattress','motorcycle','smartphone',
                    'four_wheeler','home_ownership','tractor','livestock','land_ownership',
                    'roof_material','cooking_fuel','toilet_facility','drinking_water','household']
    demo_keywords = ['age','gender','education','occupation','consent','signature',
                     'examiner_number','cluster_code','household_number']
    behav_keywords = ['tobacco','alcohol','clean_your_teeth','toothpaste','tooth_powder',
                      'charcoal','sugar','mouth_or_teeth_problems','state_of_your_teeth']
    dental_visit_keywords = ['dentist','dental_visit','seek_treatment','spend_on','not_visiting']
    mucosal_keywords = ['leukoplakia','lichen_planus','ulceration','anug','candidiasis',
                        'abscess','malignant_tumor','oral_cancer','mucosal_lesion']
    ortho_keywords = ['overjet','overbite','molar_rel','crowding','spacing','diastema',
                      'irregularity','open_bite','incisor,_canine','premolar_teeth',
                      'antero-posterior','vertical__anterior']
    tmj_keywords = ['clicking','tenderness','jaw_mobility','deviation_of_jaw']
    trauma_keywords = ['dental_trauma','abrasion','attrition','erosion_severity',
                       'number_of_teeth_affected']
    fluorosis_index = ['tooth_17/16','tooth_11','tooth_26/27','tooth_36/37',
                       'tooth_31','tooth_47/46','enamel_fluorosis']
    other_clin = ['dmh','hypomineralization','teeth_present','natural_teeth',
                  'intervention_urgency','individual_status','prosthetic_status',
                  'upper_prosthetic','lower_prosthetic']

    for col in all_cols:
        c = col.lower()
        placed = False
        for t in primary_teeth:
            if f'tooth_{t}_-_status' in c or f'tooth_-_{t}' in c:
                categories["🦷 Tooth Status (Primary)"].append(col); placed = True; break
            if f'tooth_{t}_-_bleeding' in c:
                categories["🩸 Bleeding"].append(col); placed = True; break
        if placed: continue
        for t in permanent_teeth:
            if f'tooth_{t}_-_status' in c:
                categories["🦷 Tooth Status (Permanent)"].append(col); placed = True; break
            if f'tooth_{t}_-_bleeding' in c:
                categories["🩸 Bleeding"].append(col); placed = True; break
            if f'tooth_{t}_-_pocket' in c:
                categories["📏 Pocket Depth"].append(col); placed = True; break
            if f'tooth_{t}_-_opacity' in c:
                categories["🔬 Opacity / MIH / DMH"].append(col); placed = True; break
        if placed: continue
        if any(k in c for k in [x.lower() for x in fluorosis_index]):
            categories["🧬 Fluorosis Index (Index Teeth)"].append(col)
        elif any(k in c for k in mucosal_keywords):
            categories["👄 Oral Mucosal Lesions"].append(col)
        elif any(k in c for k in ortho_keywords):
            categories["🦴 Orthodontics / Malocclusion"].append(col)
        elif any(k in c for k in tmj_keywords):
            categories["🦷 TMJ / Jaw"].append(col)
        elif any(k in c for k in trauma_keywords):
            categories["🎭 Dental Trauma & Abrasion"].append(col)
        elif any(k in c for k in ['fluorosis','erosion']) and 'enamel' in c:
            categories["🌡️ Fluorosis & Erosion"].append(col)
        elif any(k in c for k in ['prosthetic']):
            categories["🔩 Prosthetics"].append(col)
        elif any(k in c for k in other_clin):
            categories["📝 Other Clinical"].append(col)
        elif any(k in c for k in demo_keywords):
            categories["🧑 Demographics"].append(col)
        elif any(k in c for k in dental_visit_keywords):
            categories["💊 Dental Visit / Treatment"].append(col)
        elif any(k in c for k in behav_keywords):
            categories["📋 Behavioural / Oral Hygiene"].append(col)
        elif any(k in c for k in ses_keywords):
            categories["🏠 Socioeconomic / Household"].append(col)
        else:
            categories["📝 Other Clinical"].append(col)
    return {k: v for k, v in categories.items() if v}

CLINICAL_CATEGORIES = {
    "🦷 Tooth Status (Primary)", "🦷 Tooth Status (Permanent)",
    "🩸 Bleeding", "📏 Pocket Depth", "🔬 Opacity / MIH / DMH",
    "🌡️ Fluorosis & Erosion", "🦴 Orthodontics / Malocclusion",
    "👄 Oral Mucosal Lesions", "🔩 Prosthetics", "🦷 TMJ / Jaw",
    "🎭 Dental Trauma & Abrasion", "🧬 Fluorosis Index (Index Teeth)",
    "📝 Other Clinical"
}

def detect_date_columns(df):
    """Return columns that are likely to contain dates."""
    return [c for c in df.columns if 'date' in str(c).lower()]

def parse_date_column(series):
    """Parse date columns robustly for both exported labels and typed CSV data."""
    parsed = pd.to_datetime(series, errors='coerce')
    parsed_dayfirst = pd.to_datetime(series, errors='coerce', dayfirst=True)
    if parsed_dayfirst.notna().sum() > parsed.notna().sum():
        return parsed_dayfirst
    return parsed

def clean_cluster_val(v):
    """Display numeric cluster IDs without a trailing .0 while preserving labels."""
    if pd.isna(v):
        return "(missing)"
    text = str(v).strip()
    if text in {"", "nan", "<NA>", "None"}:
        return "(missing)"
    if text in {"Non-Identified", "(missing)"}:
        return text
    try:
        number = float(text)
        if number == int(number):
            return str(int(number))
    except (ValueError, TypeError):
        pass
    return text

def extract_participants(df):
    """Extract participant rows and bring household identifiers onto them."""
    hh_cols = [c for c in ['record_id', 'cluster_code', 'household_number'] if c in df.columns]

    if 'repeat_instrument' in df.columns:
        repeat_values = df['repeat_instrument'].astype(str).str.strip().str.lower()
        household_mask = df['repeat_instrument'].isna() | repeat_values.isin(["", "nan", "<na>"])
        hh = df.loc[household_mask, hh_cols].drop_duplicates('record_id') if hh_cols else pd.DataFrame()
        pt = df.loc[repeat_values.eq('participant')].copy()
        if pt.empty:
            pt = df.loc[~household_mask].copy()
        if pt.empty:
            pt = df.copy()
    else:
        hh = df[hh_cols].drop_duplicates('record_id') if hh_cols else pd.DataFrame()
        pt = df.copy()

    for c in ['cluster_code', 'household_number']:
        if c in pt.columns:
            pt = pt.drop(columns=[c])

    if not hh.empty and 'record_id' in pt.columns and 'record_id' in hh.columns:
        result = pt.merge(hh, on='record_id', how='left')
    else:
        result = pt

    if 'age_group' in result.columns:
        result['age_group'] = normalize_age_group(result['age_group'])
    if 'gender' in result.columns:
        result['gender'] = result['gender'].astype(str).str.strip()
    if 'examiner_number' in result.columns:
        result['examiner_number'] = result['examiner_number'].replace(r'^\s*$', np.nan, regex=True)
    return result

# ─── Data cleaner helpers ───
def cleaner_is_blank(value):
    if pd.isna(value):
        return True
    text = str(value).strip()
    return text == "" or text.lower() in {"nan", "none", "<na>", "nat"}

def cleaner_key_value(value):
    if cleaner_is_blank(value):
        return ""
    text = str(value).strip()
    try:
        number = float(text)
        if np.isfinite(number) and number == int(number):
            return str(int(number))
    except (ValueError, TypeError):
        pass
    return text.lower()

def cleaner_nonblank_count(row):
    return int(sum(not cleaner_is_blank(v) for v in row))

def cleaner_display_value(value):
    if cleaner_is_blank(value):
        return ""
    text = str(value).strip()
    try:
        number = float(text)
        if np.isfinite(number) and number == int(number):
            return str(int(number))
    except (ValueError, TypeError):
        pass
    return text

def cleaner_key_display(row, key_cols):
    return " | ".join(f"{col}: {cleaner_display_value(row.get(col, ''))}" for col in key_cols)

def cleaner_format_date(value):
    if pd.isna(value):
        return "not available"
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M")
    return str(value)

def cleaner_detected_columns_df(detected):
    rows = []
    for label, value in detected.items():
        if label == "identity_cols":
            value = ", ".join(value) if value else "Not detected"
        rows.append({"Field": label.replace("_", " ").title(), "Detected Column": value or "Not detected"})
    return pd.DataFrame(rows)

def cleaner_basis_notes(key_cols, detected, renumber_repeats):
    household_basis = ", ".join(key_cols) if key_cols else "no household match columns selected"
    repeat_col = detected.get("repeat_instrument") or "Repeat Instrument not detected"
    instance_col = detected.get("repeat_instance") or "Repeat Instance not detected"
    return pd.DataFrame([
        {"Cleaning Step": "Exact duplicate removal", "Basis Used": "Rows are removed only when every uploaded column matches an earlier row exactly."},
        {"Cleaning Step": "Duplicate household merge", "Basis Used": f"Household rows are combined when they share the selected household match columns: {household_basis}."},
        {"Cleaning Step": "Primary household selection", "Basis Used": "Within each duplicate household group, the kept record is selected by completion/status priority, more filled household fields, more attached repeat rows, latest date, then original upload order."},
        {"Cleaning Step": "Participant/member reassignment", "Basis Used": f"Rows where {repeat_col} is filled are reassigned from secondary record IDs to the selected primary household record ID."},
        {"Cleaning Step": "Redundant participant/member removal", "Basis Used": f"After reassignment, repeated rows are removed when their values match an earlier repeat row, excluding {instance_col} and selected household match columns."},
        {"Cleaning Step": "Repeat instance numbering", "Basis Used": "Repeat Instance is renumbered within each clean record and repeat instrument." if renumber_repeats else "Repeat Instance renumbering is turned off."},
    ])

def cleaner_report_workbook(cleaned_df, cleaner_report):
    output = BytesIO()
    used_names = set()
    metrics_df = pd.DataFrame([{"Metric": k, "Value": v} for k, v in cleaner_report["metrics"].items()])
    sheets = [
        ("Summary", metrics_df),
        ("Cleaning Basis", cleaner_report.get("basis_notes", pd.DataFrame())),
        ("Detected Columns", cleaner_detected_columns_df(cleaner_report["detected"])),
        ("Detailed Actions", cleaner_report.get("detailed_report", pd.DataFrame())),
        ("Record ID Summary", cleaner_report.get("record_id_summary", pd.DataFrame())),
        ("Household Merges", cleaner_report.get("merge_summary", pd.DataFrame())),
        ("Merged HH Source Rows", cleaner_report.get("merged_household_rows", pd.DataFrame())),
        ("Repeat Reassignments", cleaner_report.get("reassigned_repeat_rows", pd.DataFrame())),
        ("Garbage Removed Rows", cleaner_report.get("garbage_rows", pd.DataFrame())),
    ]
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, df in sheets:
            safe_name = safe_excel_sheet_name(sheet_name, used_names)
            frame = df if df is not None and not df.empty else pd.DataFrame({"Note": ["No records for this section"]})
            frame.to_excel(writer, index=False, sheet_name=safe_name)
    output.seek(0)
    return output.getvalue()

def detect_cleaner_columns(df):
    cols = df.columns
    identity_candidates = []
    for keywords in [
        ["Member Name", "participant_name", "member_name", "name"],
        ["Member Age", "Age (years)", "age_(years)", "age"],
        ["Age group", "age_group"],
        ["Member Gender", "Gender", "member_gender", "sex"],
        ["Member Education", "Education", "member_education"],
        ["Member Occupation", "Occupation", "member_occupation"],
    ]:
        col = find_col(keywords, cols)
        if col and col not in identity_candidates:
            identity_candidates.append(col)
    return {
        "repeat_instrument": find_col(["Repeat Instrument", "redcap_repeat_instrument"], cols),
        "repeat_instance": find_col(["Repeat Instance", "redcap_repeat_instance"], cols),
        "record_id": find_col(["Record ID", "record_id", "patient_id"], cols) or (cols[0] if len(cols) else None),
        "cluster": find_col(["Cluster Code", "cluster_code", "cluster"], cols),
        "household_number": find_col(["Household Number", "household_number"], cols),
        "date": find_col(["Listing Date", "listing_date", "Consent date", "consent_date", "date"], cols),
        "status": find_col(["Household Status", "household_status", "completion status", "complete"], cols),
        "identity_cols": identity_candidates,
    }

def cleaner_household_mask(df, repeat_col):
    if not repeat_col or repeat_col not in df.columns:
        return pd.Series([True] * len(df), index=df.index)
    repeat_values = df[repeat_col].map(lambda v: "" if cleaner_is_blank(v) else str(v).strip().lower())
    return repeat_values.isin(["", "nan", "none", "<na>"])

def cleaner_household_key(df, key_cols):
    key_cols = [c for c in key_cols if c in df.columns]
    if not key_cols:
        return pd.Series([""] * len(df), index=df.index)
    key_parts = df[key_cols].apply(lambda col: col.map(cleaner_key_value))
    valid = key_parts.apply(lambda row: all(str(v) != "" for v in row), axis=1)
    key = key_parts.astype(str).agg("||".join, axis=1)
    key.loc[~valid] = ""
    return key

def cleaner_conflict_summary(group, columns, ignore_cols):
    conflict_cols = []
    for col in columns:
        if col in ignore_cols or col not in group.columns:
            continue
        values = [cleaner_key_value(v) for v in group[col] if not cleaner_is_blank(v)]
        if len(set(values)) > 1:
            conflict_cols.append(col)
    return conflict_cols

def cleaner_choose_primary_household(group, id_col, date_col, status_col, repeat_counts):
    score = pd.DataFrame(index=group.index)
    score["_nonblank"] = group.apply(cleaner_nonblank_count, axis=1)
    if id_col and id_col in group.columns and not repeat_counts.empty:
        score["_repeat_rows"] = group[id_col].map(repeat_counts).fillna(0).astype(int)
    else:
        score["_repeat_rows"] = 0
    if status_col and status_col in group.columns:
        status_text = group[status_col].astype(str).str.lower()
        score["_status"] = status_text.str.contains("completed|complete|willing|yes", na=False).astype(int)
    else:
        score["_status"] = 0
    if date_col and date_col in group.columns:
        score["_date"] = parse_date_column(group[date_col])
    else:
        score["_date"] = pd.NaT
    score["_order"] = np.arange(len(score))
    score = score.sort_values(
        ["_status", "_nonblank", "_repeat_rows", "_date", "_order"],
        ascending=[False, False, False, False, True],
        na_position="last",
    )
    return score.index[0]

def cleaner_merge_household_rows(group, primary_idx, output_columns, id_col):
    combined = group.loc[primary_idx, output_columns].copy()
    for col in output_columns:
        if col == id_col or not cleaner_is_blank(combined.get(col)):
            continue
        nonblank = group[col].loc[~group[col].map(cleaner_is_blank)]
        if len(nonblank):
            combined[col] = nonblank.iloc[0]
    return combined

def cleaner_renumber_repeat_instances(repeat_df, id_col, repeat_col, instance_col):
    if repeat_df.empty or not id_col or not repeat_col or not instance_col:
        return repeat_df
    if id_col not in repeat_df.columns or repeat_col not in repeat_df.columns or instance_col not in repeat_df.columns:
        return repeat_df
    result = repeat_df.copy()
    result["_cleaner_repeat_order"] = pd.to_numeric(result[instance_col], errors="coerce")
    sort_cols = [id_col, repeat_col, "_cleaner_repeat_order"]
    if "_cleaner_original_order" in result.columns:
        sort_cols.append("_cleaner_original_order")
    result = result.sort_values(sort_cols, kind="stable", na_position="last")
    result[instance_col] = result.groupby([id_col, repeat_col], dropna=False).cumcount() + 1
    return result.drop(columns=["_cleaner_repeat_order"], errors="ignore")

def clean_household_redundancy(raw, household_key_cols=None, combine_households=True, renumber_repeats=True):
    raw = raw.copy()
    output_columns = list(raw.columns)
    detected = detect_cleaner_columns(raw)
    id_col = detected["record_id"]
    repeat_col = detected["repeat_instrument"]
    instance_col = detected["repeat_instance"]
    date_col = detected["date"]
    status_col = detected["status"]
    key_cols = [c for c in (household_key_cols or []) if c in output_columns]
    warnings_out = []
    action_rows = []
    secondary_household_frames = []
    merged_household_frames = []
    id_map_by_key = {}
    id_basis_by_key = {}
    id_household_key_by_key = {}

    raw["_cleaner_original_row"] = np.arange(len(raw)) + 2
    exact_duplicate_mask = raw[output_columns].duplicated(keep="first")
    exact_duplicate_rows = raw.loc[exact_duplicate_mask, output_columns].copy()
    if not exact_duplicate_rows.empty:
        exact_duplicate_meta = raw.loc[exact_duplicate_mask]
        exact_duplicate_rows.insert(0, "Cleaner Clean Record ID", exact_duplicate_meta[id_col].values if id_col and id_col in exact_duplicate_meta.columns else "")
        exact_duplicate_rows.insert(0, "Cleaner Original Record ID", exact_duplicate_meta[id_col].values if id_col and id_col in exact_duplicate_meta.columns else "")
        exact_duplicate_rows.insert(0, "Cleaner Original Row", exact_duplicate_meta["_cleaner_original_row"].values)
        exact_duplicate_rows.insert(0, "Cleaner Basis", "Every uploaded column matched an earlier row exactly.")
        exact_duplicate_rows.insert(0, "Cleaner Row Type", "Exact duplicate")
        exact_duplicate_rows.insert(0, "Cleaner Action", "Removed exact duplicate uploaded row")
        action_rows.append({
            "Action": "Removed exact duplicate uploaded rows",
            "Record IDs": ", ".join(map(str, exact_duplicate_meta[id_col].dropna().unique())) if id_col and id_col in exact_duplicate_meta.columns else "",
            "Rows Affected": int(len(exact_duplicate_rows)),
            "Basis": "All uploaded columns were identical to an earlier row.",
            "Result": "Rows removed from the clean upload file and listed in Garbage Records.",
        })
    df = raw.loc[~exact_duplicate_mask].copy()
    df["_cleaner_original_order"] = np.arange(len(df))

    if not repeat_col:
        warnings_out.append("No Repeat Instrument column was detected. The cleaner can remove exact duplicate rows and merge household rows, but repeated participant/member rows cannot be reconstructed from a flat file.")
    if combine_households and not key_cols:
        warnings_out.append("No household match columns were selected, so household-level merging was skipped.")
    elif combine_households and len(key_cols) == 1:
        warnings_out.append("Only one household match column is selected. Review the merge list before using the cleaned file for final analysis.")

    household_mask = cleaner_household_mask(df, repeat_col)
    household_rows = df.loc[household_mask].copy()
    repeat_rows = df.loc[~household_mask].copy()
    households_before = int(household_rows[id_col].dropna().nunique()) if id_col and id_col in household_rows.columns else int(len(household_rows))
    repeat_before = int(len(repeat_rows))

    repeat_counts = pd.Series(dtype=int)
    if id_col and id_col in repeat_rows.columns and not repeat_rows.empty:
        repeat_counts = repeat_rows.groupby(id_col, dropna=False).size()

    id_map = {}
    merge_rows = []
    combined_households = []
    drop_household_indexes = set()

    if combine_households and key_cols and id_col and id_col in household_rows.columns and not household_rows.empty:
        household_rows["_cleaner_household_key"] = cleaner_household_key(household_rows, key_cols)
        valid_households = household_rows[household_rows["_cleaner_household_key"] != ""]
        for _, group in valid_households.groupby("_cleaner_household_key", sort=False):
            if len(group) <= 1:
                continue
            primary_idx = cleaner_choose_primary_household(group, id_col, date_col, status_col, repeat_counts)
            primary_id = group.loc[primary_idx, id_col]
            primary_id_key = cleaner_key_value(primary_id)
            original_ids = [v for v in group[id_col].dropna().unique() if not cleaner_is_blank(v)]
            secondary_ids = [v for v in original_ids if cleaner_key_value(v) != primary_id_key]
            for old_id in secondary_ids:
                id_map[old_id] = primary_id
                id_map_by_key[cleaner_key_value(old_id)] = primary_id
            combined = cleaner_merge_household_rows(group, primary_idx, output_columns, id_col)
            combined[id_col] = primary_id
            combined_households.append(combined)
            drop_household_indexes.update(group.index.tolist())
            conflict_cols = cleaner_conflict_summary(group, output_columns, {id_col, repeat_col, instance_col})
            repeat_reassigned = int(repeat_rows[id_col].isin(secondary_ids).sum()) if secondary_ids and id_col in repeat_rows.columns else 0
            primary_row = group.loc[primary_idx]
            primary_status = cleaner_display_value(primary_row.get(status_col, "")) if status_col else "not available"
            primary_nonblank = cleaner_nonblank_count(primary_row[output_columns])
            primary_repeat_rows = int(repeat_counts.get(primary_id, 0)) if not repeat_counts.empty else 0
            primary_date = cleaner_format_date(parse_date_column(pd.Series([primary_row.get(date_col)])).iloc[0]) if date_col else "not available"
            key_display = cleaner_key_display(group.iloc[0], key_cols)
            merge_basis = (
                f"Matched on selected household columns ({', '.join(key_cols)}): {key_display}. "
                f"Primary record {primary_id} selected by status/completion ({primary_status}), "
                f"filled household fields ({primary_nonblank}), attached repeat rows ({primary_repeat_rows}), "
                f"latest date ({primary_date}), then upload order."
            )

            source_rows = group[output_columns].copy()
            source_rows.insert(0, "Cleaner Clean Record ID", primary_id)
            source_rows.insert(0, "Cleaner Original Record ID", group[id_col].values)
            source_rows.insert(0, "Cleaner Original Row", group["_cleaner_original_row"].values if "_cleaner_original_row" in group.columns else "")
            source_rows.insert(0, "Cleaner Basis", merge_basis)
            source_rows.insert(0, "Cleaner Household Key", key_display)
            source_rows.insert(0, "Cleaner Row Type", "Household source row")
            source_rows.insert(0, "Cleaner Action", ["Primary household kept" if idx == primary_idx else "Secondary household merged and removed" for idx in group.index])
            merged_household_frames.append(source_rows)

            secondary_source = group[group.index != primary_idx][output_columns].copy()
            if not secondary_source.empty:
                secondary_meta = group.loc[group.index != primary_idx]
                secondary_source.insert(0, "Cleaner Clean Record ID", primary_id)
                secondary_source.insert(0, "Cleaner Original Record ID", secondary_meta[id_col].values)
                secondary_source.insert(0, "Cleaner Original Row", secondary_meta["_cleaner_original_row"].values if "_cleaner_original_row" in secondary_meta.columns else "")
                secondary_source.insert(0, "Cleaner Basis", merge_basis)
                secondary_source.insert(0, "Cleaner Row Type", "Merged duplicate household")
                secondary_source.insert(0, "Cleaner Action", "Secondary household row merged into primary and removed")
                secondary_household_frames.append(secondary_source)

            merge_rows.append({
                "Household Key Columns": ", ".join(key_cols),
                "Household Key Values": key_display,
                "Basis for Merge": f"Same selected household match columns: {', '.join(key_cols)}.",
                "Primary Selection Basis": merge_basis,
                "Primary Record ID": primary_id,
                "Secondary Record IDs": ", ".join(str(v) for v in secondary_ids),
                "All Merged Record IDs": ", ".join(str(v) for v in original_ids),
                "Household Rows Combined": int(len(group)),
                "Records Combined": int(max(len(original_ids) - 1, 0)),
                "Repeat Rows Reassigned": repeat_reassigned,
                "Conflicting Household Fields Kept From Primary": int(len(conflict_cols)),
                "Conflict Fields": ", ".join(conflict_cols[:50]),
            })
            action_rows.append({
                "Action": "Merged duplicate household records",
                "Record IDs": ", ".join(str(v) for v in original_ids),
                "Rows Affected": int(len(group) + repeat_reassigned),
                "Basis": merge_basis,
                "Result": f"Kept record {primary_id}; merged secondary record IDs {', '.join(str(v) for v in secondary_ids) or 'none'}; reassigned {repeat_reassigned} repeat rows.",
            })
            for old_id in original_ids:
                old_key = cleaner_key_value(old_id)
                id_household_key_by_key[old_key] = key_display
                id_basis_by_key[old_key] = merge_basis

    household_clean = household_rows.drop(index=list(drop_household_indexes), errors="ignore")
    household_clean = household_clean[output_columns].copy()
    if combined_households:
        household_clean = pd.concat(
            [household_clean, pd.DataFrame(combined_households, columns=output_columns)],
            ignore_index=True,
        )

    repeat_clean = repeat_rows.copy()
    if id_col and id_col in repeat_clean.columns:
        repeat_clean["_cleaner_original_record_id"] = repeat_clean[id_col]
        repeat_clean["_cleaner_clean_record_id"] = repeat_clean[id_col]
    if id_map_by_key and id_col in repeat_clean.columns:
        mapped_ids = repeat_clean[id_col].map(lambda v: id_map_by_key.get(cleaner_key_value(v), np.nan))
        reassigned_mask = mapped_ids.notna()
        repeat_clean.loc[reassigned_mask, "_cleaner_clean_record_id"] = mapped_ids[reassigned_mask]
        reassigned_source = repeat_clean.loc[reassigned_mask, output_columns].copy()
        if not reassigned_source.empty:
            reassigned_meta = repeat_clean.loc[reassigned_mask]
            reassigned_source.insert(0, "Cleaner Clean Record ID", reassigned_meta["_cleaner_clean_record_id"].values)
            reassigned_source.insert(0, "Cleaner Original Record ID", reassigned_meta["_cleaner_original_record_id"].values)
            reassigned_source.insert(0, "Cleaner Original Row", reassigned_meta["_cleaner_original_row"].values if "_cleaner_original_row" in reassigned_meta.columns else "")
            reassigned_source.insert(0, "Cleaner Basis", "The repeat row belonged to a secondary household record ID that was merged into a primary household.")
            reassigned_source.insert(0, "Cleaner Row Type", "Participant/member repeat row")
            reassigned_source.insert(0, "Cleaner Action", "Repeat row reassigned to merged household")
            reassigned_repeat_rows = reassigned_source
        repeat_clean.loc[reassigned_mask, id_col] = mapped_ids[reassigned_mask]
    elif id_map and id_col in repeat_clean.columns:
        mapped_ids = repeat_clean[id_col].map(id_map)
        repeat_clean.loc[mapped_ids.notna(), id_col] = mapped_ids[mapped_ids.notna()]

    repeat_duplicate_rows = pd.DataFrame(columns=["Cleaner Action", "Cleaner Row Type", "Cleaner Basis", "Cleaner Original Row", "Cleaner Original Record ID", "Cleaner Clean Record ID"] + output_columns)
    if not repeat_clean.empty:
        dedupe_exclude = {c for c in [instance_col] + key_cols if c}
        dedupe_subset = [c for c in output_columns if c in repeat_clean.columns and c not in dedupe_exclude]
        duplicate_mask = repeat_clean.duplicated(subset=dedupe_subset, keep="first") if dedupe_subset else pd.Series([False] * len(repeat_clean), index=repeat_clean.index)
        repeat_duplicate_rows = repeat_clean.loc[duplicate_mask, output_columns].copy()
        if not repeat_duplicate_rows.empty:
            repeat_duplicate_meta = repeat_clean.loc[duplicate_mask]
            repeat_duplicate_rows.insert(0, "Cleaner Clean Record ID", repeat_duplicate_meta["_cleaner_clean_record_id"].values if "_cleaner_clean_record_id" in repeat_duplicate_meta.columns else "")
            repeat_duplicate_rows.insert(0, "Cleaner Original Record ID", repeat_duplicate_meta["_cleaner_original_record_id"].values if "_cleaner_original_record_id" in repeat_duplicate_meta.columns else "")
            repeat_duplicate_rows.insert(0, "Cleaner Original Row", repeat_duplicate_meta["_cleaner_original_row"].values if "_cleaner_original_row" in repeat_duplicate_meta.columns else "")
            repeat_duplicate_rows.insert(0, "Cleaner Basis", f"After household merge, this repeated row matched an earlier row. Dedupe compared all uploaded columns except: {', '.join(dedupe_exclude) if dedupe_exclude else 'none'}.")
            repeat_duplicate_rows.insert(0, "Cleaner Row Type", "Duplicate repeated row")
            repeat_duplicate_rows.insert(0, "Cleaner Action", "Removed redundant participant/member row")
            action_rows.append({
                "Action": "Removed redundant participant/member repeat rows",
                "Record IDs": ", ".join(map(str, repeat_duplicate_meta["_cleaner_clean_record_id"].dropna().unique())) if "_cleaner_clean_record_id" in repeat_duplicate_meta.columns else "",
                "Rows Affected": int(len(repeat_duplicate_rows)),
                "Basis": f"Repeated rows matched after record ID reassignment, excluding: {', '.join(dedupe_exclude) if dedupe_exclude else 'none'}.",
                "Result": "Rows removed from the clean upload file and listed in Garbage Records.",
            })
        repeat_clean = repeat_clean.loc[~duplicate_mask].copy()

    repeat_clean = cleaner_renumber_repeat_instances(repeat_clean, id_col, repeat_col, instance_col) if renumber_repeats else repeat_clean
    repeat_clean = repeat_clean[output_columns].copy() if not repeat_clean.empty else pd.DataFrame(columns=output_columns)

    cleaned = pd.concat([household_clean, repeat_clean], ignore_index=True)
    if id_col and id_col in cleaned.columns and not cleaned.empty:
        cleaned["_cleaner_record_num"] = pd.to_numeric(cleaned[id_col], errors="coerce")
        cleaned["_cleaner_record_text"] = cleaned[id_col].map(cleaner_key_value)
        cleaned["_cleaner_row_type"] = cleaner_household_mask(cleaned, repeat_col).map(lambda x: 0 if x else 1)
        if instance_col and instance_col in cleaned.columns:
            cleaned["_cleaner_instance_num"] = pd.to_numeric(cleaned[instance_col], errors="coerce")
            sort_cols = ["_cleaner_record_num", "_cleaner_record_text", "_cleaner_row_type", "_cleaner_instance_num"]
        else:
            sort_cols = ["_cleaner_record_num", "_cleaner_record_text", "_cleaner_row_type"]
        cleaned = cleaned.sort_values(sort_cols, kind="stable", na_position="last")
        cleaned = cleaned.drop(columns=[c for c in cleaned.columns if c.startswith("_cleaner_")], errors="ignore")
    cleaned = cleaned[output_columns].reset_index(drop=True)

    household_after_mask = cleaner_household_mask(cleaned, repeat_col)
    households_after = int(cleaned.loc[household_after_mask, id_col].dropna().nunique()) if id_col and id_col in cleaned.columns else int(household_after_mask.sum())
    repeat_after = int((~household_after_mask).sum()) if repeat_col else 0
    merge_summary = pd.DataFrame(merge_rows)
    merged_household_rows = pd.concat(merged_household_frames, ignore_index=True) if merged_household_frames else pd.DataFrame()
    garbage_parts = [exact_duplicate_rows, repeat_duplicate_rows] + secondary_household_frames
    garbage_rows = pd.concat([p for p in garbage_parts if p is not None and not p.empty], ignore_index=True) if any(p is not None and not p.empty for p in garbage_parts) else pd.DataFrame()
    basis_notes = cleaner_basis_notes(key_cols, detected, renumber_repeats)

    record_id_rows = []
    if id_col and id_col in raw.columns and id_col in cleaned.columns:
        raw_hh_mask = cleaner_household_mask(raw, repeat_col)
        clean_hh_mask = cleaner_household_mask(cleaned, repeat_col)
        raw_repeat_mask = ~raw_hh_mask if repeat_col else pd.Series([False] * len(raw), index=raw.index)
        clean_repeat_mask = ~clean_hh_mask if repeat_col else pd.Series([False] * len(cleaned), index=cleaned.index)
        raw_id_keys = raw[id_col].map(cleaner_key_value)
        clean_id_keys = cleaned[id_col].map(cleaner_key_value)
        seen_ids = set()
        for rid in raw[id_col]:
            rid_key = cleaner_key_value(rid)
            if not rid_key or rid_key in seen_ids:
                continue
            seen_ids.add(rid_key)
            clean_id = id_map_by_key.get(rid_key, rid)
            clean_key = cleaner_key_value(clean_id)
            status = "Merged into primary record ID" if rid_key in id_map_by_key else ("Primary kept for merged household" if rid_key in id_basis_by_key else "Unchanged")
            record_id_rows.append({
                "Original Record ID": rid,
                "Clean Record ID": clean_id,
                "Record ID Status": status,
                "Household Key": id_household_key_by_key.get(rid_key, ""),
                "Basis": id_basis_by_key.get(rid_key, "No duplicate household key was detected for this record ID."),
                "Rows Before": int((raw_id_keys == rid_key).sum()),
                "Rows After Under Clean ID": int((clean_id_keys == clean_key).sum()),
                "Household Rows Before": int(((raw_id_keys == rid_key) & raw_hh_mask).sum()),
                "Household Rows After Under Clean ID": int(((clean_id_keys == clean_key) & clean_hh_mask).sum()),
                "Repeat Rows Before": int(((raw_id_keys == rid_key) & raw_repeat_mask).sum()),
                "Repeat Rows After Under Clean ID": int(((clean_id_keys == clean_key) & clean_repeat_mask).sum()),
            })
    record_id_summary = pd.DataFrame(record_id_rows)

    if not action_rows:
        action_rows.append({
            "Action": "No merge/removal action needed",
            "Record IDs": "",
            "Rows Affected": 0,
            "Basis": "The uploaded file did not contain duplicate household groups or redundant rows under the selected settings.",
            "Result": "Cleaned file matches the uploaded file after validation.",
        })
    detailed_report = pd.DataFrame(action_rows)

    metrics = {
        "Rows Before": int(len(raw)),
        "Rows After": int(len(cleaned)),
        "Rows Removed From Upload": int(len(raw) - len(cleaned)),
        "Households Before": households_before,
        "Households After": households_after,
        "Repeated Rows Before": repeat_before,
        "Repeated Rows After": repeat_after,
        "Exact Duplicate Rows Removed": int(len(exact_duplicate_rows)),
        "Duplicate Repeated Rows Removed": int(len(repeat_duplicate_rows)),
        "Merged Secondary Household Rows Removed": int(sum(len(p) for p in secondary_household_frames)),
        "Garbage Rows Available For Download": int(len(garbage_rows)),
        "Household Groups Merged": int(len(merge_summary)),
        "Household Records Combined": int(merge_summary["Records Combined"].sum()) if not merge_summary.empty else 0,
        "Repeat Rows Reassigned": int(len(reassigned_repeat_rows)),
    }
    return cleaned, {
        "metrics": metrics,
        "detected": detected,
        "basis_notes": basis_notes,
        "detailed_report": detailed_report,
        "merge_summary": merge_summary,
        "merged_household_rows": merged_household_rows,
        "reassigned_repeat_rows": reassigned_repeat_rows,
        "record_id_summary": record_id_summary,
        "removed_rows": garbage_rows,
        "garbage_rows": garbage_rows,
        "warnings": warnings_out,
    }
def build_single_file_examiner_aggregated_reports(
    merged, compare_cols, selected_keys, label_recorded, label_duplicate,
    low_agree_threshold, suffix_a='_Recorded', suffix_b='_Duplicate'
):
    """
    For each recorded examiner, compare all matched rows against the duplicate group.
    This is intentionally separate from the two-file aggregation helper above.
    """
    summary_records = []
    agreement_dict = {}
    discrepancies_dict = {}

    examiner_col = f'examiner_number{suffix_a}'
    if examiner_col not in merged.columns:
        return pd.DataFrame(), {}, {}

    for exam, group in merged.groupby(examiner_col, dropna=False):
        group = group.reset_index(drop=True)
        ag_df = field_agreement_summary(group, compare_cols, suffix_a=suffix_a, suffix_b=suffix_b)
        agreement_dict[exam] = ag_df

        disc_list = []
        missing_count = 0
        for i in range(len(group)):
            comp = participant_level_comparison(
                group, compare_cols, label_recorded, label_duplicate,
                suffix_a=suffix_a, suffix_b=suffix_b, idx=i
            )
            if comp.empty:
                continue
            missing_count += int((comp['Status'] == 'Missing in one').sum())
            disc = comp[comp['Status'].astype(str).str.startswith('Disagree')].copy()
            if disc.empty:
                continue
            disc.insert(0, 'Participant #', i + 1)
            disc.insert(1, f'Record ID ({label_recorded})', group.iloc[i].get(f'record_id{suffix_a}', ''))
            disc.insert(2, f'Record ID ({label_duplicate})', group.iloc[i].get(f'record_id{suffix_b}', ''))
            parts = [
                f"{k.replace('_',' ').title()}: {group.iloc[i][k]}"
                for k in selected_keys
                if k in group.columns and pd.notna(group.iloc[i][k])
            ]
            disc.insert(3, 'Matching Key', ' | '.join(parts))
            disc.insert(4, f'Examiner Number ({label_recorded})', exam)
            disc_list.append(disc)

        disc_df = pd.concat(disc_list, ignore_index=True) if disc_list else pd.DataFrame()
        discrepancies_dict[exam] = disc_df
        summary_records.append({
            f'Examiner ({label_recorded})': exam,
            'Matched Participants': len(group),
            'Fields Assessed': len(ag_df),
            'Avg Agreement %': round(ag_df['Agreement %'].mean(), 1) if not ag_df.empty else 0,
            'Min Agreement %': round(ag_df['Agreement %'].min(), 1) if not ag_df.empty else 0,
            f'Fields < {low_agree_threshold}%': (
                int((ag_df['Agreement %'] < low_agree_threshold).sum()) if not ag_df.empty else 0
            ),
            'Discrepancies': len(disc_df),
            'Missing in One': missing_count,
        })

    summary_df = pd.DataFrame(summary_records)
    if not summary_df.empty:
        summary_df = summary_df.sort_values(['Avg Agreement %', 'Discrepancies'], ascending=[True, False])
    return summary_df, agreement_dict, discrepancies_dict

# ─────────────────────────────────────────────
# SIDEBAR – MODE SELECTION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="padding:14px 0 18px;">'
        '<div style="font-family:Playfair Display,serif;font-size:1.3rem;color:white;">🦷 Super Dashboard</div>'
        '<div style="font-size:.7rem;color:#64748b;margin-top:2px;">All Modules in One</div>'
        '</div>',
        unsafe_allow_html=True
    )
    mode = st.radio(
        "Select Module",
        [
            "📊 Oral Health Survey",
            "🔁 Duplicate Comparator (Two Files)",
            "📄 Recorded vs Duplicate (Single File)",
            "🧹 Data Cleaner",
            "🏘️ Household Listing"
        ],
        index=0
    )
    st.divider()

# ─────────────────────────────────────────────
# MODULE 1: ORAL HEALTH SURVEY (14 tabs)
# ─────────────────────────────────────────────
if mode == "📊 Oral Health Survey":
    # ── SURVEY DASHBOARD (full code from v9dashboard combine both.py) ──
    # We'll embed the entire survey code here.
    # Because this is a huge block, we include it directly.
    st.markdown('<div style="font-family:Playfair Display,serif;font-size:1.9rem;color:#0f172a;">🦷 OralHealth Analytics Pro</div>', unsafe_allow_html=True)

    # File uploader for survey
    uploaded = st.sidebar.file_uploader("Upload Survey CSV", type=["csv"], label_visibility="collapsed")
    st.sidebar.markdown("---")

    if not uploaded:
        st.markdown('<div style="font-family:Playfair Display,serif;font-size:2.2rem;color:#0f172a;">🦷 OralHealth Analytics Pro</div>',unsafe_allow_html=True)
        st.markdown('<div style="color:#64748b;margin-bottom:20px;">Upload your survey CSV from the sidebar to begin comprehensive analysis.</div>',unsafe_allow_html=True)
        st.info("📁 Upload `CentralDelhi1_DATA_LABELS_*.csv` to get started with all 11 analysis modules.")
        st.stop()

    # ── LOAD DATA ──
    @st.cache_data
    def load_csv(file_bytes):
        return pd.read_csv(BytesIO(file_bytes), low_memory=False)

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

    if not col_cluster or col_cluster not in df.columns:
        col_cluster = "_cluster_code"
        df[col_cluster] = "Non-Identified"

    df[col_cluster] = df[col_cluster].astype(str).str.strip()
    df[col_cluster] = df[col_cluster].replace({"nan": "Non-Identified", "": "Non-Identified", "None": "Non-Identified"})
    df.loc[df[col_cluster].isna(), col_cluster] = "Non-Identified"
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

    if col_age:
        df["_age_num"] = pd.to_numeric(df[col_age],errors="coerce")

    # ── SIDEBAR FILTERS ──
    with st.sidebar:
        st.markdown("### Filters")
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
    decid_teeth = [55,54,53,52,51,61,62,63,64,65,75,74,73,72,71,81,82,83,84,85]
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
        "💊 Lesions & Prosthetics","⚕️ Treatment Needs","👨‍⚕️ Examiner Analysis","🗺️ Cluster Analysis","📋 Data Explorer","⏱️ Work Hours"])

    # ── TAB 0: Overview ──
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

    # ── TAB 1: Household ──
    with tabs[1]:
        sec("Household Characteristics")
        if len(hh)==0:
            st.warning("No household-level records detected.")
        else:
            if col_hh_status and col_hh_status in hh.columns:
                sec("📋 Household Participation Status")
                hh_status_vals = hh[col_hh_status].astype(str).str.strip()
                hh_status_vals = hh_status_vals[~hh_status_vals.isin(["nan","","None"])]
                total_hh = len(hh_status_vals)
                willing = (hh_status_vals.str.contains("Willing|willing|participate",case=False,na=False)).sum()
                not_avail = (hh_status_vals.str.contains("Not available|not available",case=False,na=False)).sum()
                refused = (hh_status_vals.str.contains("Refused|refused",case=False,na=False)).sum()
                other_status = total_hh - willing - not_avail - refused

                s1,s2,s3,s4 = st.columns(4)
                with s1: kpi("Total Households",f"{total_hh}","")
                with s2: kpi("Willing",f"{willing}","g",f"{willing/max(total_hh,1)*100:.0f}%")
                with s3: kpi("Not Available",f"{not_avail}","o",f"{not_avail/max(total_hh,1)*100:.0f}%")
                with s4: kpi("Refused",f"{refused}","r",f"{refused/max(total_hh,1)*100:.0f}%")

                hs1, hs2 = st.columns(2)
                with hs1:
                    st.plotly_chart(pie(hh_status_vals,"Household Participation Status",340),use_container_width=True)
                with hs2:
                    if col_cluster and col_cluster in hh.columns:
                        hh_with_status = hh.copy()
                        hh_with_status["_hh_status"] = hh[col_hh_status].astype(str).str.strip()
                        hh_filtered = hh_with_status[~hh_with_status["_hh_status"].isin(["nan","","None"])]
                        if len(hh_filtered)>0:
                            st.plotly_chart(grp_bar(hh_filtered.dropna(subset=[col_cluster,"_hh_status"]),col_cluster,"_hh_status","Household Status × Cluster",340),use_container_width=True)

                if total_hh > 0:
                    response_rate = willing / total_hh * 100
                    if response_rate >= 80:
                        st.success(f"✅ Response rate: {response_rate:.1f}% — Excellent (≥80% WHO threshold)")
                    elif response_rate >= 60:
                        st.warning(f"⚠️ Response rate: {response_rate:.1f}% — Moderate (below 80% WHO threshold)")
                    else:
                        st.error(f"🚨 Response rate: {response_rate:.1f}% — Low (below 60%, may affect representativeness)")

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
                sec("Wealth Index (Asset Score)")
                hh_src_copy = hh_src.copy()
                valid_asset_cols = [c for c in asset_cols if c in hh_src_copy.columns]
                hh_src_copy["_asset_score"] = hh_src_copy[valid_asset_cols].apply(lambda r: (r.astype(str).str.strip()=="Yes").sum(), axis=1)
                fig2=px.histogram(hh_src_copy,x="_asset_score",nbins=15,title="Distribution of Asset Score (count of Yes)",color_discrete_sequence=["#10b981"])
                fig2.update_layout(**LY,height=300,xaxis=dict(showgrid=False,title="Asset Score"),yaxis=dict(gridcolor="#f1f5f9",title="Households"))
                st.plotly_chart(fig2,use_container_width=True)

    # ── TAB 2: Oral Hygiene ──
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
        if col_cleaning and col_gender:
            sec("Cleaning Method by Gender")
            st.plotly_chart(grp_bar(df.dropna(subset=[col_cleaning,col_gender]),col_cleaning,col_gender,"Cleaning Method × Gender"),use_container_width=True)

    # ── TAB 3: Dental Services ──
    with tabs[3]:
        sec("Dental Pain & Service Utilisation")
        d1,d2,d3 = st.columns(3)
        if col_pain:
            with d1: st.plotly_chart(pie(df[col_pain].dropna(),"Oral Pain (Last 6 Months)"),use_container_width=True)
        if col_dentist:
            with d2: st.plotly_chart(pie(df[col_dentist].dropna(),"Ever Visited Dentist"),use_container_width=True)
        if col_perception:
            with d3: st.plotly_chart(pie(df[col_perception].dropna(),"Self-Perception of Oral Health"),use_container_width=True)
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
        if col_where:
            sec("Treatment Facility Type")
            st.plotly_chart(pie(df[col_where].dropna(),"Where Treatment Was Sought"),use_container_width=True)
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

    # ── TAB 4: Caries/DMFT ──
    with tabs[4]:
        sec("Caries & DMFT Analysis")
        st.info("Computing DMFT/dmft indices from tooth-level data...")
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
            if col_gender:
                sec("DMFT by Gender")
                dmft_gen = df.groupby(col_gender)[["_D","_M","_F","_DMFT"]].mean().round(2).reset_index()
                st.dataframe(dmft_gen.rename(columns={"_D":"Decayed","_M":"Missing","_F":"Filled","_DMFT":"Total DMFT"}),use_container_width=True,hide_index=True)
            sec("DMFT Score Distribution")
            _dmft_max = df["_DMFT"].max()
            _dmft_bins = max(int(_dmft_max)+1, 10) if pd.notna(_dmft_max) else 10
            fig=px.histogram(df,x="_DMFT",nbins=_dmft_bins,title="DMFT Score Distribution",color_discrete_sequence=["#8b5cf6"])
            fig.update_layout(**LY,height=300,xaxis=dict(showgrid=False,title="DMFT Score"),yaxis=dict(gridcolor="#f1f5f9",title="Count"))
            st.plotly_chart(fig,use_container_width=True)
            sec("Caries Prevalence (% with D>0)")
            caries_pct = (df["_D"]>0).mean()*100
            st.markdown(f"**Overall caries prevalence: {caries_pct:.1f}%**")
            if col_ag:
                cprev = df.groupby(col_ag).apply(lambda x:(x["_D"]>0).mean()*100).reset_index()
                cprev.columns = [col_ag,"Caries Prevalence %"]
                fig=px.bar(cprev,x=col_ag,y="Caries Prevalence %",title="Caries Prevalence by Age Group",color_discrete_sequence=["#ef4444"])
                fig.update_layout(**LY,height=300,xaxis=dict(showgrid=False),yaxis=dict(gridcolor="#f1f5f9"))
                st.plotly_chart(fig,use_container_width=True)
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

    # ── TAB 5: Periodontal ──
    with tabs[5]:
        sec("Periodontal Health Analysis")
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
            any_bleed = df[bleed_cols].apply(lambda r: (r.astype(str).str.strip()=="Bleeding").any(),axis=1)
            st.markdown(f"**Any bleeding prevalence: {any_bleed.mean()*100:.1f}%** of participants")
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

    # ── TAB 6: Conditions ──
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
        if col_fluorosis and col_ag:
            sec("Fluorosis by Age Group")
            st.plotly_chart(grp_bar(df.dropna(subset=[col_fluorosis,col_ag]),col_ag,col_fluorosis,"Fluorosis Severity × Age Group"),use_container_width=True)
        if col_edentulous:
            sec("Edentulous Status (65-74)")
            st.plotly_chart(pie(df[col_edentulous].dropna(),"Edentulous Status"),use_container_width=True)
        dmh_col = find_col(["Deciduous Molar Hypomineralization","DMH"],raw.columns)
        if dmh_col and dmh_col in df.columns:
            sec("Deciduous Molar Hypomineralization (4-6 yrs)")
            st.plotly_chart(pie(df[dmh_col].dropna(),"DMH Status"),use_container_width=True)

    # ── TAB 7: TMJ & Ortho ──
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

    # ── TAB 8: Lesions & Prosthetics ──
    with tabs[8]:
        sec("Oral Mucosal Lesions")
        if col_lesion:
            st.plotly_chart(pie(df[col_lesion].dropna(),"Oral Mucosal Lesion Present?"),use_container_width=True)
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
                    lesion_prevalence_data.append({"Lesion":lname,"Prevalence %":round(pct,1)})
        if lesion_prevalence_data:
            sec("Lesion Prevalence Summary")
            lpdf = pd.DataFrame(lesion_prevalence_data).sort_values("Prevalence %",ascending=True)
            fig_lp = px.bar(lpdf,x="Prevalence %",y="Lesion",orientation="h",title="Oral Lesion Prevalence (%)",
                color="Prevalence %",color_continuous_scale="Reds")
            fig_lp.update_layout(**LY,height=max(len(lpdf)*40+100,300),showlegend=False,
                xaxis=dict(showgrid=True,gridcolor="#f1f5f9"),yaxis=dict(showgrid=False))
            st.plotly_chart(fig_lp,use_container_width=True)

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
            os1,os2,os3 = st.columns(3)
            with os1: kpi("OSMF Prevalence",f"{osmf_pct:.1f}%","r",f"{osmf_total} cases")
            with os2:
                if col_tobacco:
                    osmf_tob = df[any_osmf & (df[col_tobacco]=="Yes")].shape[0]
                    osmf_tob_pct = osmf_tob/max(osmf_total,1)*100
                    kpi("OSMF + Tobacco",f"{osmf_tob_pct:.0f}%","o",f"{osmf_tob}/{osmf_total} cases")
            with os3:
                if col_gender:
                    osmf_male = df[any_osmf & (df[col_gender]=="Male")].shape[0]
                    osmf_female = df[any_osmf & (df[col_gender]=="Female")].shape[0]
                    kpi("M:F Ratio",f"{osmf_male}:{osmf_female}","p")
            if osmf_df["Affected %"].sum() > 0:
                osmf_sorted = osmf_df[osmf_df["Affected %"]>0].sort_values("Affected %",ascending=True)
                fig_osmf = px.bar(osmf_sorted,x="Affected %",y="Site",orientation="h",
                    title="OSMF Affected Sites (%)",color="Affected %",color_continuous_scale="OrRd",
                    text="Count")
                fig_osmf.update_layout(**LY,height=max(len(osmf_sorted)*45+100,300),showlegend=False,
                    xaxis=dict(showgrid=True,gridcolor="#f1f5f9"),yaxis=dict(showgrid=False))
                fig_osmf.update_traces(textposition="outside")
                st.plotly_chart(fig_osmf,use_container_width=True)
            if col_ag:
                osmf_by_age = df.groupby(col_ag).apply(lambda x: x[osmf_cols].apply(lambda r: (r.astype(str).str.strip()=="Checked").any(),axis=1).mean()*100).reset_index()
                osmf_by_age.columns = [col_ag,"OSMF %"]
                fig_osmf_age = px.bar(osmf_by_age,x=col_ag,y="OSMF %",title="OSMF Prevalence by Age Group",
                    color_discrete_sequence=["#dc2626"])
                fig_osmf_age.update_layout(**LY,height=300,xaxis=dict(showgrid=False),yaxis=dict(gridcolor="#f1f5f9"))
                st.plotly_chart(fig_osmf_age,use_container_width=True)
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

    # ── TAB 9: Treatment Needs ──
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

    # ── TAB 10: Examiner Analysis ──
    with tabs[10]:
        sec("Examiner Performance Overview")
        if col_exam:
            all_examiners = sorted(df[col_exam].dropna().unique())

            def _select_all_examiners():
                st.session_state["exam_tab_selector"] = list(all_examiners)

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
                edf = df[df[col_exam].isin(selected_examiners)]
                examiner_list = sorted(selected_examiners)
                is_single = len(examiner_list) == 1
                mode_label = f"**Analysing: Examiner {examiner_list[0]}**" if is_single else f"**Analysing: {len(examiner_list)} Examiners** ({', '.join([str(e) for e in examiner_list])})"
                st.info(mode_label)

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

                if col_gender:
                    sec("Gender Distribution per Examiner")
                    st.plotly_chart(grp_bar(edf.dropna(subset=[col_exam,col_gender]),col_exam,col_gender,"Examiner × Gender"),use_container_width=True)
                if col_ag:
                    sec("Age Group Distribution per Examiner")
                    st.plotly_chart(grp_bar(edf.dropna(subset=[col_exam,col_ag]),col_exam,col_ag,"Examiner × Age Group"),use_container_width=True)
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
                        if col_ag:
                            age_cts = ex_df[col_ag].value_counts().reset_index()
                            age_cts.columns = ["Age Group","Count"]
                            st.dataframe(age_cts, use_container_width=True, hide_index=True)
                        if col_cluster:
                            cl_cts = ex_df[col_cluster].value_counts().reset_index()
                            cl_cts.columns = ["Cluster","Count"]
                            st.dataframe(cl_cts, use_container_width=True, hide_index=True)
                        if col_intervention:
                            urg_cts = ex_df[col_intervention].dropna().value_counts().reset_index()
                            urg_cts.columns = ["Urgency","Count"]
                            st.dataframe(urg_cts, use_container_width=True, hide_index=True)
                        if has_date:
                            ex_dates = ex_df["_date"].dropna()
                            if len(ex_dates)>0:
                                st.caption(f"📅 Active: {ex_dates.min().date()} → {ex_dates.max().date()} | Days: {ex_dates.dt.date.nunique()} | Avg/Day: {round(len(ex_df)/max(ex_dates.dt.date.nunique(),1),1)}")

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

    # ── TAB 11: Cluster Analysis ──
    with tabs[11]:
        sec("Cluster-wise Performance Overview")
        if col_cluster:
            cluster_list = sorted(df[col_cluster].dropna().unique(), key=lambda x: str(x))
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
            sec("Participants per Cluster")
            st.plotly_chart(bar(df[col_cluster].dropna(),"Participants per Cluster","h","#06b6d4"),use_container_width=True)
            if col_gender:
                sec("Gender Distribution per Cluster")
                st.plotly_chart(grp_bar(df.dropna(subset=[col_cluster,col_gender]),col_cluster,col_gender,"Cluster × Gender"),use_container_width=True)
            if col_ag:
                sec("Age Group Distribution per Cluster")
                st.plotly_chart(grp_bar(df.dropna(subset=[col_cluster,col_ag]),col_cluster,col_ag,"Cluster × Age Group"),use_container_width=True)
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
            if col_intervention:
                sec("Treatment Urgency by Cluster")
                st.plotly_chart(grp_bar(df.dropna(subset=[col_cluster,col_intervention]),col_cluster,col_intervention,"Cluster × Intervention Urgency",400),use_container_width=True)
            if has_date:
                sec("Enrolment Timeline per Cluster")
                daily_cl = df.dropna(subset=["_date",col_cluster]).groupby([df["_date"].dt.date,col_cluster]).size().reset_index()
                daily_cl.columns = ["Date","Cluster","Patients"]
                fig_tl = px.line(daily_cl,x="Date",y="Patients",color="Cluster",
                    title="Daily Enrolment per Cluster",color_discrete_sequence=C,markers=True)
                fig_tl.update_layout(**LY,height=350,xaxis=dict(showgrid=False),
                    yaxis=dict(gridcolor="#f1f5f9"),legend=dict(orientation="h",yanchor="bottom",y=1.02))
                st.plotly_chart(fig_tl,use_container_width=True)
            if col_exam:
                sec("Examiner-wise Patient Count per Cluster")
                ct_ex_cl = pd.crosstab(df[col_cluster], df[col_exam], margins=True, margins_name="Total")
                ct_ex_cl.index.name = "Cluster"
                ct_ex_cl.columns = [f"Examiner {c}" if c != "Total" else c for c in ct_ex_cl.columns]
                ct_ex_cl = ct_ex_cl.reset_index()
                st.dataframe(ct_ex_cl, use_container_width=True, hide_index=True)
                fig_ex_cl = grp_bar(df.dropna(subset=[col_cluster, col_exam]), col_cluster, col_exam, "Patients per Examiner in Each Cluster", 400)
                st.plotly_chart(fig_ex_cl, use_container_width=True)
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
            sec("📥 Download Cluster Report")
            st.dataframe(cl_sum, use_container_width=True, hide_index=True)
            csv_cl = cl_sum.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Cluster Report CSV",csv_cl,"cluster_report.csv","text/csv",use_container_width=True)
        else:
            st.warning("No Cluster column found in the data.")

    # ── TAB 12: Data Explorer ──
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

    # ── TAB 13: Work Hours ──
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

                sec("📋 Daily Timing Log")
                display_log = daily_log[["Examiner","Date","First Time","Last Time","Work Duration (hrs)","Patients","Avg Time/Patient (min)"]].sort_values(["Date","Examiner"])
                st.dataframe(display_log,use_container_width=True,hide_index=True)

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
                summary_df_work = pd.DataFrame(summary_rows).sort_values("Consistency CV %",na_position="last")
                st.dataframe(summary_df_work,use_container_width=True,hide_index=True)
                st.caption("Lower Consistency CV % = steadier day-to-day work duration for that examiner. Blank CV means only 1 day logged — not enough data to judge consistency.")

                sec("📥 Download Reports")
                dl1,dl2 = st.columns(2)
                with dl1:
                    csv_log = display_log.to_csv(index=False).encode("utf-8")
                    st.download_button("📥 Download Daily Timing Log CSV",csv_log,"examiner_daily_timing_log.csv","text/csv",use_container_width=True)
                with dl2:
                    csv_summary = summary_df_work.to_csv(index=False).encode("utf-8")
                    st.download_button("📥 Download Consistency Summary CSV",csv_summary,"examiner_consistency_summary.csv","text/csv",use_container_width=True)
        else:
            st.warning("Examiner and/or Date columns not found — cannot compute work-hour consistency.")

# ─────────────────────────────────────────────
# MODULE 2: DUPLICATE COMPARATOR (TWO FILES)
# ─────────────────────────────────────────────
elif mode == "🔁 Duplicate Comparator (Two Files)":
    # ─── TWO-FILE COMPARATOR ───
    with st.sidebar:
        st.markdown("### 📂 Upload Two Examiner Files")
        file_a = st.file_uploader("Examiner A (File 1)", type=['csv'], key='fa')
        file_b = st.file_uploader("Examiner B (File 2)", type=['csv'], key='fb')
        st.markdown("---")
        if file_a and file_b:
            label_a = st.text_input("Name for Examiner A", value=file_a.name.replace('.csv',''))
            label_b = st.text_input("Name for Examiner B", value=file_b.name.replace('.csv',''))
            st.markdown("### ⚙️ Matching Parameters")
            use_cluster   = st.checkbox("Cluster Code",     value=True)
            use_household = st.checkbox("Household Number", value=True)
            use_age       = st.checkbox("Age (Years)",      value=True)
            use_age_group = st.checkbox("Age Group",        value=True)
            use_gender    = st.checkbox("Gender",           value=True)
            st.markdown("### 🔍 Agreement Threshold")
            low_agree_threshold = st.slider("Flag fields below (%)", 0, 100, 60)
        else:
            st.info("Upload both files to see comparator options.")

    if not file_a or not file_b:
        st.info("👈 Upload both examiner files from the sidebar to begin duplicate comparison.")
        c1, c2, c3 = st.columns(3)
        for col, step, desc in [(c1,"1","Upload Examiner A CSV"),(c2,"2","Upload Examiner B CSV"),(c3,"3","View comparison results")]:
            with col:
                st.markdown(f"<div style='border:2px dashed #cbd5e1;border-radius:14px;padding:2rem;text-align:center;background:white'>"
                            f"<h3>📤 Step {step}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
        st.stop()

    # ─── LOAD & PROCESS ───
    with st.spinner("🔄 Processing files and matching participants..."):
        df_a = normalize_export_columns(pd.read_csv(file_a))
        df_b = normalize_export_columns(pd.read_csv(file_b))

        pt_a = build_participant_df(df_a, label_a)
        pt_b = build_participant_df(df_b, label_b)

        corrupted_a = detect_corrupted_values(
            df_a[df_a['repeat_instrument'] == 'Participant']['age_group']
            if 'repeat_instrument' in df_a.columns and 'age_group' in df_a.columns else pd.Series(dtype=str))
        corrupted_b = detect_corrupted_values(
            df_b[df_b['repeat_instrument'] == 'Participant']['age_group']
            if 'repeat_instrument' in df_b.columns and 'age_group' in df_b.columns else pd.Series(dtype=str))

        all_keys = {
            'cluster_code': use_cluster, 'household_number': use_household,
            'age_(years)': use_age,      'age_group': use_age_group, 'gender': use_gender
        }
        selected_keys = [k for k, v in all_keys.items() if v and k in pt_a.columns and k in pt_b.columns]
        if not selected_keys:
            st.error("Please select at least one matching parameter.")
            st.stop()

        merged = pd.merge(pt_a, pt_b, on=selected_keys, suffixes=('_A','_B'))
        unmatched_a = get_unmatched(pt_a, pt_b, selected_keys)
        unmatched_b = get_unmatched(pt_b, pt_a, selected_keys)

        all_compare_cols = compare_fields(merged)
        field_categories = classify_fields(all_compare_cols)

    # ─────────────────────────────────────────────
    # FIELD SELECTION PANEL
    # ─────────────────────────────────────────────
    if corrupted_a or corrupted_b:
        st.markdown(
            f"<div class='warning-banner'>⚠️ <strong>Excel date-corruption detected and auto-fixed.</strong><br>"
            f"{'<b>'+label_a+'</b>: '+', '.join(corrupted_a)+' → corrected' if corrupted_a else ''}"
            f"{'<br>' if corrupted_a and corrupted_b else ''}"
            f"{'<b>'+label_b+'</b>: '+', '.join(corrupted_b)+' → corrected' if corrupted_b else ''}"
            f"</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎯 Field Selection — Choose What to Analyse")

    preset_col1, preset_col2, preset_col3, preset_col4, preset_col5 = st.columns(5)
    with preset_col1:
        btn_clinical = st.button("🏥 Clinical Only", use_container_width=True,
                                 help="Tooth Status, Bleeding, Pocket, Opacity, Mucosal, Ortho, TMJ, Trauma, Prosthetics")
    with preset_col2:
        btn_tooth    = st.button("🦷 Teeth Only",    use_container_width=True,
                                 help="Tooth Status + Bleeding + Pocket Depth only")
    with preset_col3:
        btn_behav    = st.button("📋 Behavioural",   use_container_width=True,
                                 help="Oral Hygiene + Dental Visit + Tobacco/Alcohol")
    with preset_col4:
        btn_all      = st.button("🌐 All Fields",    use_container_width=True,
                                 help="Every comparable field in the dataset")
    with preset_col5:
        btn_low      = st.button("🔴 Low Agreement", use_container_width=True,
                                 help=f"Show only fields below {low_agree_threshold}% (computed from All Fields)")

    if 'field_preset' not in st.session_state:
        st.session_state.field_preset = 'clinical'
    if btn_clinical: st.session_state.field_preset = 'clinical'
    if btn_tooth:    st.session_state.field_preset = 'teeth'
    if btn_behav:    st.session_state.field_preset = 'behavioural'
    if btn_all:      st.session_state.field_preset = 'all'
    if btn_low:      st.session_state.field_preset = 'low'

    with st.expander("🔧 Fine-Grained Category Selection (override presets)", expanded=False):
        st.caption("Select/deselect individual fields within each category. Preset buttons above will reset selections.")
        n_cats = len(field_categories)
        cat_cols = st.columns(3)
        category_selections = {}
        preset = st.session_state.field_preset

        for i, (cat_name, cat_fields) in enumerate(field_categories.items()):
            col_idx = i % 3
            is_clinical = cat_name in CLINICAL_CATEGORIES
            non_clinical_behav = cat_name in {"📋 Behavioural / Oral Hygiene",
                                              "💊 Dental Visit / Treatment"}

            if preset == 'clinical':
                default_fields = cat_fields if is_clinical else []
            elif preset == 'teeth':
                default_fields = cat_fields if cat_name in {"🦷 Tooth Status (Primary)","🦷 Tooth Status (Permanent)",
                                                             "🩸 Bleeding","📏 Pocket Depth"} else []
            elif preset == 'behavioural':
                default_fields = cat_fields if non_clinical_behav else []
            else:  # 'all' or 'low'
                default_fields = cat_fields

            with cat_cols[col_idx]:
                selected = st.multiselect(
                    f"{cat_name} ({len(cat_fields)})",
                    options=cat_fields,
                    default=default_fields,
                    key=f"multiselect_{cat_name}"
                )
                category_selections[cat_name] = selected

    filtered_cols = []
    for cat, sel_fields in category_selections.items():
        filtered_cols.extend(sel_fields)
    filtered_cols = list(set(filtered_cols))
    filtered_cols = [c for c in filtered_cols if c in all_compare_cols]

    field_search = st.text_input("🔎 Search for specific field name (optional)", placeholder="e.g. tooth_16, pocket, leukoplakia")
    if field_search.strip():
        filtered_cols = [c for c in filtered_cols if field_search.strip().lower() in c.lower()]

    preset_labels = {
        'clinical':     '🏥 Clinical Only',
        'teeth':        '🦷 Teeth Only',
        'behavioural':  '📋 Behavioural',
        'all':          '🌐 All Fields',
        'low':          '🔴 Low Agreement',
    }
    st.markdown(
        f"<div class='preset-info'>Active preset: <strong>{preset_labels[preset]}</strong> · "
        f"<strong>{len(filtered_cols)}</strong> fields selected across "
        f"<strong>{len(category_selections)}</strong> categories"
        f"{'  ·  Search filter active: <em>'+field_search+'</em>' if field_search.strip() else ''}"
        f"</div>", unsafe_allow_html=True)

    # ── Compute agreement for currently filtered fields ──
    agreement_df = field_agreement_summary(merged, filtered_cols)

    if preset == 'low' and not agreement_df.empty:
        agreement_df = agreement_df[agreement_df['Agreement %'] < low_agree_threshold]
        filtered_cols = list(agreement_df['Field'])

    # ── Top-level metrics ──
    total_participants_a = len(pt_a)
    total_participants_b = len(pt_b)
    common_count  = len(merged)
    avg_agreement = agreement_df['Agreement %'].mean() if not agreement_df.empty else 0
    low_agree_cnt = len(agreement_df[agreement_df['Agreement %'] < low_agree_threshold]) if not agreement_df.empty else 0

    # Build all discrepancies for filtered fields
    all_discrepancies = []
    if common_count > 0 and filtered_cols:
        for i in range(len(merged)):
            comp = participant_level_comparison(merged, filtered_cols, label_a, label_b, idx=i)
            disc = comp[comp['Status'].astype(str).str.startswith('Disagree')].copy()
            if not disc.empty:
                disc.insert(0, 'Participant #', i + 1)
                disc.insert(1, f'Record ID ({label_a})', merged.iloc[i].get('record_id_A', ''))
                disc.insert(2, f'Record ID ({label_b})', merged.iloc[i].get('record_id_B', ''))
                parts = [f"{k.replace('_',' ').title()}: {merged.iloc[i][k]}"
                         for k in selected_keys if k in merged.columns and pd.notna(merged.iloc[i][k])]
                disc.insert(3, 'Matching Key', ' | '.join(parts))
                all_discrepancies.append(disc)

    all_disc_df = pd.concat(all_discrepancies, ignore_index=True) if all_discrepancies else pd.DataFrame()

    # ── Pair‑wise examiner reports ──
    examiner_summary_df, examiner_agreement_tables, examiner_discrepancy_tables = build_examiner_reports(
        merged, filtered_cols, selected_keys, label_a, label_b, low_agree_threshold
    )

    # ── Aggregated examiner reports ──
    agg_summary_A, agg_summary_B, agg_agreement_A, agg_agreement_B, agg_discrepancies_A, agg_discrepancies_B = (
        build_examiner_aggregated_reports(
            merged, filtered_cols, selected_keys, label_a, label_b, low_agree_threshold
        )
    )

    # ── Build combined examiner discrepancy dataframes (for export) ──
    all_examiner_disc_df = pd.DataFrame()
    examiner_disc_summary_df = pd.DataFrame()
    for pair_key, pair_disc_df in examiner_discrepancy_tables.items():
        if not pair_disc_df.empty:
            tmp_disc = pair_disc_df.copy()
            tmp_disc.insert(0, 'Examiner Pair', pair_key)
            all_examiner_disc_df = pd.concat([all_examiner_disc_df, tmp_disc], ignore_index=True)
    if not all_examiner_disc_df.empty:
        disc_col_a = f'Examiner Number ({label_a})'
        disc_col_b = f'Examiner Number ({label_b})'
        examiner_disc_summary_df = (
            all_examiner_disc_df.groupby([disc_col_a, disc_col_b, 'Examiner Pair', 'Field'], dropna=False)
            .size()
            .reset_index(name='Discrepancy Count')
            .sort_values(['Discrepancy Count', 'Field'], ascending=[False, True])
        )

    # ── Summary dataframe ──
    summary_data = {
        'Metric': [
            f'Participants — {label_a}', f'Participants — {label_b}',
            'Matched Participants', f'Unmatched in {label_a}', f'Unmatched in {label_b}',
            'Active Preset', 'Fields Selected', 'Average Field Agreement (%)',
            f'Fields Below {low_agree_threshold}%', 'Total Discrepancies (field-level)',
            'Matching Keys Used',
            'Age Group Auto-corrected (A)', 'Age Group Auto-corrected (B)',
        ],
        'Value': [
            total_participants_a, total_participants_b, common_count,
            len(unmatched_a), len(unmatched_b),
            preset_labels[preset], len(filtered_cols),
            f"{avg_agreement:.1f}%", low_agree_cnt, len(all_disc_df),
            ', '.join(selected_keys),
            ', '.join(corrupted_a) if corrupted_a else 'None',
            ', '.join(corrupted_b) if corrupted_b else 'None',
        ]
    }
    summary_df = pd.DataFrame(summary_data)

    # ── Metric cards ──
    st.markdown("---")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    for col, color, val, lbl in [
        (c1, "",       total_participants_a, f"Participants — {label_a}"),
        (c2, "green",  total_participants_b, f"Participants — {label_b}"),
        (c3, "purple", common_count,         "Matched Participants"),
        (c4, "orange" if (len(unmatched_a)+len(unmatched_b)) > 0 else "green",
             len(unmatched_a)+len(unmatched_b), "Unmatched (A+B)"),
        (c5, "green" if avg_agreement >= 80 else "orange" if avg_agreement >= 60 else "red",
             f"{avg_agreement:.1f}%", "Avg Field Agreement"),
        (c6, "red", low_agree_cnt, f"Fields < {low_agree_threshold}%"),
    ]:
        with col:
            st.markdown(
                f"<div class='metric-card {color}'>"
                f"<div class='metric-value'>{val}</div>"
                f"<div class='metric-label'>{lbl}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if common_count == 0:
        st.error("⚠️ No common participants found. Try unchecking some matching parameters in the sidebar.")
        if not unmatched_a.empty:
            st.markdown("**Participants in A with no match in B:**")
            st.dataframe(unmatched_a, use_container_width=True)
        if not unmatched_b.empty:
            st.markdown("**Participants in B with no match in A:**")
            st.dataframe(unmatched_b, use_container_width=True)
        st.stop()

    if not filtered_cols:
        st.warning("No fields match the current selection. Please adjust your category choices or search term.")
        st.stop()

    # ─────────────────────────────────────────────
    # TABS (comparator version)
    # ─────────────────────────────────────────────
    tab_examiner, tab_agg_examiner, tab_summary, tab_matched, tab_unmatched, tab_field, tab_deepdive, tab_discrep, tab_export = st.tabs([
        "Examiner Reports (Pair‑wise)",
        "Examiner (Aggregated)",
        "📋 Summary", "👥 Matched", "⚠️ Unmatched", "📊 Field Agreement",
        "🔍 Deep Dive", "🚨 Discrepancies", "📥 Export"
    ])

    # ─── Examiner Reports (Pair‑wise) ───
    with tab_examiner:
        st.markdown("<div class='section-header'>Examiner Number Wise Detailed Reports (Pair‑wise)</div>",
                    unsafe_allow_html=True)
        if examiner_summary_df.empty:
            st.info("Examiner‑number columns were not found in both matched files.")
        else:
            st.markdown("#### Examiner Pair Summary")
            styled_examiner = (examiner_summary_df.style
                .map(pct_color, subset=['Avg Agreement %','Min Agreement %'])
                .format({'Avg Agreement %':'{:.1f}%','Min Agreement %':'{:.1f}%'})
                .set_properties(**{'font-size':'13px'}))
            st.dataframe(styled_examiner, width='stretch', height=320)
            st.download_button("Download Examiner Summary CSV",
                examiner_summary_df.to_csv(index=False).encode(),
                "examiner_number_summary.csv", "text/csv", key="dl_examiner_summary")

            st.markdown("---")
            pair_options = list(examiner_agreement_tables.keys())
            selected_pair = st.selectbox("Choose examiner number pair", pair_options,
                                         key="examiner_pair_select")
            pair_agreement_df = examiner_agreement_tables.get(selected_pair, pd.DataFrame())
            pair_disc_df = examiner_discrepancy_tables.get(selected_pair, pd.DataFrame())

            selected_exam_a, selected_exam_b = selected_pair.split(' vs ', 1)
            pair_rows = examiner_summary_df[
                (examiner_summary_df[f'Examiner Number ({label_a})'].astype(str) == selected_exam_a) &
                (examiner_summary_df[f'Examiner Number ({label_b})'].astype(str) == selected_exam_b)
            ]
            if not pair_rows.empty:
                row = pair_rows.iloc[0]
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("Matched Participants", int(row['Matched Participants']))
                with c2: st.metric("Avg Agreement", f"{row['Avg Agreement %']:.1f}%")
                with c3: st.metric("Low Agreement Fields", int(row[f'Fields < {low_agree_threshold}%']))
                with c4: st.metric("Discrepancies", int(row['Discrepancies']))

            col_left, col_right = st.columns([3, 2])
            with col_left:
                st.markdown("#### Field Agreement for Selected Examiner Pair")
                if pair_agreement_df.empty:
                    st.info("No assessable fields for this examiner pair.")
                else:
                    st.dataframe(
                        pair_agreement_df.style
                            .map(pct_color, subset=['Agreement %'])
                            .format({'Agreement %':'{:.1f}%'} )
                            .set_properties(**{'font-size':'13px'}),
                        width='stretch', height=420
                    )
                    st.download_button("Download Pair Field Agreement CSV",
                        pair_agreement_df.to_csv(index=False).encode(),
                        f"field_agreement_{selected_pair}.csv", "text/csv",
                        key="dl_examiner_pair_agreement")
            with col_right:
                st.markdown("#### Lowest Agreement Fields")
                if not pair_agreement_df.empty:
                    lowest_pair = pair_agreement_df.head(12)
                    fig_pair = px.bar(lowest_pair, x='Agreement %', y='Field', orientation='h',
                                      color='Agreement %', color_continuous_scale='RdYlGn',
                                      range_color=[0,100])
                    fig_pair.update_layout(height=420, margin=dict(t=20,b=0,l=0,r=0),
                                           showlegend=False)
                    st.plotly_chart(fig_pair, width='stretch')

            st.markdown("#### Detailed Discrepancies for Selected Examiner Pair")
            if pair_disc_df.empty:
                st.success("No discrepancies found for this examiner pair in selected fields.")
            else:
                pf1, pf2 = st.columns(2)
                with pf1:
                    field_filter = st.text_input("Filter pair discrepancies by field",
                                                 key="examiner_disc_field_filter")
                with pf2:
                    pair_participant_filter = st.multiselect(
                        "Filter pair discrepancies by participant #",
                        sorted(pair_disc_df['Participant #'].dropna().unique().tolist()),
                        key="examiner_pair_participant_filter"
                    )
                shown_pair_disc = pair_disc_df.copy()
                if field_filter.strip():
                    shown_pair_disc = shown_pair_disc[shown_pair_disc['Field'].str.contains(
                        field_filter.strip(), case=False, na=False)]
                if pair_participant_filter:
                    shown_pair_disc = shown_pair_disc[shown_pair_disc['Participant #'].isin(pair_participant_filter)]
                st.info(f"Showing {len(shown_pair_disc)} of {len(pair_disc_df)} discrepancies")
                st.download_button("Download Pair Discrepancies CSV",
                    shown_pair_disc.to_csv(index=False).encode(),
                    f"discrepancies_{selected_pair}.csv", "text/csv",
                    key="dl_examiner_pair_disc")
                st.dataframe(shown_pair_disc, width='stretch', height=420)

            st.markdown("---")
            st.markdown("#### All Examiner‑Wise Discrepancies Report")
            if all_examiner_disc_df.empty:
                st.success("No examiner‑wise discrepancies found in selected fields.")
            else:
                disc_col_a = f'Examiner Number ({label_a})'
                disc_col_b = f'Examiner Number ({label_b})'
                f1, f2, f3 = st.columns(3)
                with f1:
                    pair_filter = st.multiselect(
                        "Filter examiner pair",
                        sorted(all_examiner_disc_df['Examiner Pair'].dropna().unique().tolist()),
                        key="all_exam_disc_pair_filter"
                    )
                with f2:
                    exam_a_filter = st.multiselect(
                        f"Filter {label_a} examiner number",
                        sorted(all_examiner_disc_df[disc_col_a].dropna().unique().tolist()),
                        key="all_exam_disc_filter_a"
                    )
                with f3:
                    exam_b_filter = st.multiselect(
                        f"Filter {label_b} examiner number",
                        sorted(all_examiner_disc_df[disc_col_b].dropna().unique().tolist()),
                        key="all_exam_disc_filter_b"
                    )
                f4, f5, f6 = st.columns(3)
                with f4:
                    exam_field_filter = st.text_input("Filter discrepancy field",
                                                      key="all_exam_disc_field_filter")
                with f5:
                    exam_participant_filter = st.multiselect(
                        "Filter participant #",
                        sorted(all_examiner_disc_df['Participant #'].dropna().unique().tolist()),
                        key="all_exam_disc_participant_filter"
                    )
                with f6:
                    match_key_filter = st.text_input("Filter matching key text",
                                                     key="all_exam_disc_match_key_filter")

                shown_all_exam_disc = all_examiner_disc_df.copy()
                if pair_filter:
                    shown_all_exam_disc = shown_all_exam_disc[shown_all_exam_disc['Examiner Pair'].isin(pair_filter)]
                if exam_a_filter:
                    shown_all_exam_disc = shown_all_exam_disc[shown_all_exam_disc[disc_col_a].isin(exam_a_filter)]
                if exam_b_filter:
                    shown_all_exam_disc = shown_all_exam_disc[shown_all_exam_disc[disc_col_b].isin(exam_b_filter)]
                if exam_field_filter.strip():
                    shown_all_exam_disc = shown_all_exam_disc[shown_all_exam_disc['Field'].str.contains(
                        exam_field_filter.strip(), case=False, na=False)]
                if exam_participant_filter:
                    shown_all_exam_disc = shown_all_exam_disc[
                        shown_all_exam_disc['Participant #'].isin(exam_participant_filter)]
                if match_key_filter.strip():
                    shown_all_exam_disc = shown_all_exam_disc[shown_all_exam_disc['Matching Key'].str.contains(
                        match_key_filter.strip(), case=False, na=False)]

                shown_examiner_disc_summary_df = pd.DataFrame()
                if not shown_all_exam_disc.empty:
                    shown_examiner_disc_summary_df = (
                        shown_all_exam_disc.groupby([disc_col_a, disc_col_b, 'Examiner Pair', 'Field'], dropna=False)
                        .size()
                        .reset_index(name='Discrepancy Count')
                        .sort_values(['Discrepancy Count', 'Field'], ascending=[False, True])
                    )

                st.info(f"Showing {len(shown_all_exam_disc)} of {len(all_examiner_disc_df)} examiner‑wise discrepancies")
                d1, d2 = st.columns(2)
                with d1:
                    st.download_button("Download Filtered Examiner‑Wise Discrepancies CSV",
                        shown_all_exam_disc.to_csv(index=False).encode(),
                        "filtered_examiner_wise_discrepancies.csv", "text/csv",
                        key="dl_all_examiner_disc")
                with d2:
                    st.download_button("Download Filtered Examiner Discrepancy Summary CSV",
                        shown_examiner_disc_summary_df.to_csv(index=False).encode(),
                        "filtered_examiner_discrepancy_summary.csv", "text/csv",
                        key="dl_examiner_disc_summary")

                st.markdown("##### Discrepancy Counts by Examiner Pair and Field")
                st.dataframe(shown_examiner_disc_summary_df, width='stretch', height=260)
                st.markdown("##### Detailed Examiner‑Wise Discrepancies")
                st.dataframe(shown_all_exam_disc, width='stretch', height=420)

    # ─── Examiner (Aggregated) ───
    with tab_agg_examiner:
        st.markdown("<div class='section-header'>Aggregated Examiner Reports</div>", unsafe_allow_html=True)
        st.caption(
            f"For each examiner in either file, all matches from the other file are combined. "
            f"This gives the overall consistency of an examiner against the aggregated duplicate group."
        )

        colA, colB = st.columns(2)
        with colA:
            st.markdown(f"#### Summary for {label_a} Examiners")
            if agg_summary_A.empty:
                st.info(f"No examiner numbers found in {label_a} file.")
            else:
                styled_aggA = (agg_summary_A.style
                               .map(pct_color, subset=['Avg Agreement %','Min Agreement %'])
                               .format({'Avg Agreement %':'{:.1f}%','Min Agreement %':'{:.1f}%'})
                               .set_properties(**{'font-size':'13px'}))
                st.dataframe(styled_aggA, width='stretch', height=300)
                st.download_button("Download Summary A CSV",
                    agg_summary_A.to_csv(index=False).encode(),
                    f"aggregated_summary_{label_a}.csv", "text/csv",
                    key="dl_agg_summary_A")
        with colB:
            st.markdown(f"#### Summary for {label_b} Examiners")
            if agg_summary_B.empty:
                st.info(f"No examiner numbers found in {label_b} file.")
            else:
                styled_aggB = (agg_summary_B.style
                               .map(pct_color, subset=['Avg Agreement %','Min Agreement %'])
                               .format({'Avg Agreement %':'{:.1f}%','Min Agreement %':'{:.1f}%'})
                               .set_properties(**{'font-size':'13px'}))
                st.dataframe(styled_aggB, width='stretch', height=300)
                st.download_button("Download Summary B CSV",
                    agg_summary_B.to_csv(index=False).encode(),
                    f"aggregated_summary_{label_b}.csv", "text/csv",
                    key="dl_agg_summary_B")

        st.markdown("---")
        st.markdown("### Drill‑down: Select an Examiner to View Field Agreement and Discrepancies")

        drill_choice = st.radio("Examiner from which file?", [label_a, label_b], horizontal=True)
        if drill_choice == label_a:
            if agg_summary_A.empty:
                st.warning(f"No {label_a} examiners found.")
            else:
                exam_options = sorted(agg_summary_A[f'Examiner ({label_a})'].dropna().unique().tolist())
                selected_exam = st.selectbox(f"Select {label_a} examiner", exam_options, key="agg_exam_A")
                ag_df = agg_agreement_A.get(selected_exam, pd.DataFrame())
                disc_df = agg_discrepancies_A.get(selected_exam, pd.DataFrame())

                row = agg_summary_A[agg_summary_A[f'Examiner ({label_a})'] == selected_exam]
                if not row.empty:
                    r = row.iloc[0]
                    c1, c2, c3, c4 = st.columns(4)
                    with c1: st.metric("Matched Participants", int(r['Matched Participants']))
                    with c2: st.metric("Avg Agreement", f"{r['Avg Agreement %']:.1f}%")
                    with c3: st.metric("Low Agreement Fields", int(r[f'Fields < {low_agree_threshold}%']))
                    with c4: st.metric("Discrepancies", int(r['Discrepancies']))

                st.markdown(f"#### Field Agreement for {label_a} examiner {selected_exam} (Aggregated)")
                if ag_df.empty:
                    st.info("No fields assessed for this examiner.")
                else:
                    st.dataframe(ag_df.style.map(pct_color, subset=['Agreement %'])
                                 .format({'Agreement %':'{:.1f}%'})
                                 .set_properties(**{'font-size':'13px'}),
                                 width='stretch', height=350)

                st.markdown(f"#### Discrepancies for {label_a} examiner {selected_exam} (Aggregated)")
                if disc_df.empty:
                    st.success("No discrepancies found for this examiner.")
                else:
                    fcol1, fcol2 = st.columns(2)
                    with fcol1:
                        field_filt = st.text_input("Filter by field", key="agg_disc_field_A")
                    with fcol2:
                        part_filt = st.multiselect("Filter by participant #",
                            sorted(disc_df['Participant #'].dropna().unique().tolist()),
                            key="agg_disc_part_A")
                    shown_disc = disc_df.copy()
                    if field_filt.strip():
                        shown_disc = shown_disc[shown_disc['Field'].str.contains(field_filt.strip(), case=False, na=False)]
                    if part_filt:
                        shown_disc = shown_disc[shown_disc['Participant #'].isin(part_filt)]
                    st.info(f"Showing {len(shown_disc)} discrepancies")
                    st.download_button("Download Discrepancies CSV",
                        shown_disc.to_csv(index=False).encode(),
                        f"aggregated_discrepancies_{label_a}_{selected_exam}.csv", "text/csv",
                        key="dl_agg_disc_A")
                    st.dataframe(shown_disc, width='stretch', height=400)
        else:  # label_b
            if agg_summary_B.empty:
                st.warning(f"No {label_b} examiners found.")
            else:
                exam_options = sorted(agg_summary_B[f'Examiner ({label_b})'].dropna().unique().tolist())
                selected_exam = st.selectbox(f"Select {label_b} examiner", exam_options, key="agg_exam_B")
                ag_df = agg_agreement_B.get(selected_exam, pd.DataFrame())
                disc_df = agg_discrepancies_B.get(selected_exam, pd.DataFrame())

                row = agg_summary_B[agg_summary_B[f'Examiner ({label_b})'] == selected_exam]
                if not row.empty:
                    r = row.iloc[0]
                    c1, c2, c3, c4 = st.columns(4)
                    with c1: st.metric("Matched Participants", int(r['Matched Participants']))
                    with c2: st.metric("Avg Agreement", f"{r['Avg Agreement %']:.1f}%")
                    with c3: st.metric("Low Agreement Fields", int(r[f'Fields < {low_agree_threshold}%']))
                    with c4: st.metric("Discrepancies", int(r['Discrepancies']))

                st.markdown(f"#### Field Agreement for {label_b} examiner {selected_exam} (Aggregated)")
                if ag_df.empty:
                    st.info("No fields assessed for this examiner.")
                else:
                    st.dataframe(ag_df.style.map(pct_color, subset=['Agreement %'])
                                 .format({'Agreement %':'{:.1f}%'})
                                 .set_properties(**{'font-size':'13px'}),
                                 width='stretch', height=350)

                st.markdown(f"#### Discrepancies for {label_b} examiner {selected_exam} (Aggregated)")
                if disc_df.empty:
                    st.success("No discrepancies found for this examiner.")
                else:
                    fcol1, fcol2 = st.columns(2)
                    with fcol1:
                        field_filt = st.text_input("Filter by field", key="agg_disc_field_B")
                    with fcol2:
                        part_filt = st.multiselect("Filter by participant #",
                            sorted(disc_df['Participant #'].dropna().unique().tolist()),
                            key="agg_disc_part_B")
                    shown_disc = disc_df.copy()
                    if field_filt.strip():
                        shown_disc = shown_disc[shown_disc['Field'].str.contains(field_filt.strip(), case=False, na=False)]
                    if part_filt:
                        shown_disc = shown_disc[shown_disc['Participant #'].isin(part_filt)]
                    st.info(f"Showing {len(shown_disc)} discrepancies")
                    st.download_button("Download Discrepancies CSV",
                        shown_disc.to_csv(index=False).encode(),
                        f"aggregated_discrepancies_{label_b}_{selected_exam}.csv", "text/csv",
                        key="dl_agg_disc_B")
                    st.dataframe(shown_disc, width='stretch', height=400)

    # ─── Summary Tab ───
    with tab_summary:
        st.markdown("<div class='section-header'>📋 Executive Summary</div>", unsafe_allow_html=True)

        summary_output = BytesIO()
        with pd.ExcelWriter(summary_output, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Key Metrics', index=False)
            if not examiner_summary_df.empty:
                examiner_summary_df.to_excel(writer, sheet_name='Examiner Summary (Pair)', index=False)
            if not examiner_disc_summary_df.empty:
                examiner_disc_summary_df.head(100).to_excel(
                    writer, sheet_name='Exam Disc Summary', index=False)
            if not agreement_df.empty:
                agreement_df.head(20)[['Field','Agreement %']].to_excel(
                    writer, sheet_name='Lowest Agreement Fields', index=False)
            if not all_disc_df.empty:
                disc_freq = all_disc_df['Field'].value_counts().head(20).reset_index()
                disc_freq.columns = ['Field','Discrepancy Count']
                disc_freq.to_excel(writer, sheet_name='Frequent Discrepancies', index=False)

        st.download_button("📥 Download Summary Report (Excel)", summary_output.getvalue(),
            "summary_report.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_summary")
        st.markdown("---")

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Matched", common_count)
        with col2: st.metric("Avg Agreement", f"{avg_agreement:.1f}%")
        with col3: st.metric("Below Threshold", low_agree_cnt)
        with col4: st.metric("Discrepancies", len(all_disc_df))

        st.markdown("---")
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("#### 🔴 Lowest Agreement Fields (Top 10)")
            if not agreement_df.empty:
                top_low = agreement_df.head(10)[['Field','Agreement %']].copy()
                fig_low = px.bar(top_low, x='Agreement %', y='Field', orientation='h',
                                 color='Agreement %', color_continuous_scale='RdYlGn_r',
                                 range_color=[0,100], text_auto='.1f')
                fig_low.update_layout(height=350, margin=dict(l=0,r=0,t=30,b=0))
                st.plotly_chart(fig_low, width='stretch')
        with col_right:
            st.markdown("#### 🔥 Most Frequent Discrepancies (Top 10)")
            if not all_disc_df.empty:
                disc_freq = all_disc_df['Field'].value_counts().head(10).reset_index()
                disc_freq.columns = ['Field','Discrepancy Count']
                fig_disc = px.bar(disc_freq, x='Discrepancy Count', y='Field', orientation='h',
                                  color='Discrepancy Count', color_continuous_scale='Reds', text_auto=True)
                fig_disc.update_layout(height=350, margin=dict(l=0,r=0,t=30,b=0))
                st.plotly_chart(fig_disc, width='stretch')
            else:
                st.success("🎉 No discrepancies found in selected fields!")

        st.markdown("---")
        st.markdown("#### 📊 Agreement Distribution Across Selected Fields")
        if not agreement_df.empty:
            bins = [0,20,40,60,80,100]
            labels_ = ['0–20%','20–40%','40–60%','60–80%','80–100%']
            agreement_df['Band'] = pd.cut(agreement_df['Agreement %'], bins=bins,
                                          labels=labels_, include_lowest=True)
            band_counts = agreement_df['Band'].value_counts().sort_index().reset_index()
            band_counts.columns = ['Band','Fields']
            fig_band = px.bar(band_counts, x='Band', y='Fields', color='Band',
                              color_discrete_sequence=['#ef4444','#f97316','#eab308','#84cc16','#22c55e'])
            fig_band.update_layout(showlegend=False, height=300, margin=dict(l=0,r=0))
            st.plotly_chart(fig_band, use_container_width=True)

        st.markdown("#### 📂 Agreement by Category")
        cat_summary = []
        for cat_name, sel_fields in category_selections.items():
            if sel_fields:
                cat_adf = field_agreement_summary(merged, sel_fields)
                if not cat_adf.empty:
                    cat_summary.append({
                        'Category': cat_name,
                        'Fields': len(cat_adf),
                        'Avg Agreement %': round(cat_adf['Agreement %'].mean(),1),
                        'Min Agreement %': round(cat_adf['Agreement %'].min(),1),
                        'Fields < Threshold': len(cat_adf[cat_adf['Agreement %'] < low_agree_threshold]),
                    })
        if cat_summary:
            cat_df = pd.DataFrame(cat_summary).sort_values('Avg Agreement %')
            styled_cat = (cat_df.style
                .map(pct_color, subset=['Avg Agreement %','Min Agreement %'])
                .format({'Avg Agreement %':'{:.1f}%','Min Agreement %':'{:.1f}%'})
                .set_properties(**{'font-size':'13px'}))
            st.dataframe(styled_cat, width='stretch')

        st.markdown("#### 📥 Quick Downloads")
        dl1, dl2, dl3 = st.columns(3)
        disp = [c for c in selected_keys + ['record_id_A','record_id_B',
                'examiner_number_A','examiner_number_B'] if c in merged.columns]
        with dl1:
            st.download_button("⬇️ Matched CSV", merged[disp].to_csv(index=False).encode(),
                               "matched_participants.csv","text/csv", key="dl_matched_s")
        with dl2:
            if not agreement_df.empty:
                st.download_button("⬇️ Field Agreement CSV",
                    agreement_df.drop(columns=['Band'],errors='ignore').to_csv(index=False).encode(),
                    "field_agreement.csv","text/csv", key="dl_agree_s")
        with dl3:
            if not all_disc_df.empty:
                st.download_button("⬇️ Discrepancies CSV",
                    all_disc_df.to_csv(index=False).encode(),
                    "discrepancies.csv","text/csv", key="dl_disc_s")

    # ─── Matched Tab ───
    with tab_matched:
        st.markdown("<div class='section-header'>✅ Matched Participants</div>", unsafe_allow_html=True)
        disp = [c for c in selected_keys+['record_id_A','record_id_B',
                'examiner_number_A','examiner_number_B'] if c in merged.columns]
        st.dataframe(merged[disp].reset_index(drop=True), width='stretch', height=400)

        st.markdown("#### 📊 Demographics of Matched Participants")
        col1, col2, col3 = st.columns(3)
        with col1:
            if 'gender' in merged.columns:
                fig = px.pie(merged, names='gender', title='Gender',
                             color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_layout(margin=dict(t=40,b=0,l=0,r=0), height=280)
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            if 'age_group' in merged.columns:
                ac = merged['age_group'].value_counts().reset_index()
                ac.columns = ['Age Group','Count']
                fig = px.bar(ac, x='Age Group', y='Count', title='Age Group',
                             color='Count', color_continuous_scale='Blues')
                fig.update_layout(margin=dict(t=40,b=0,l=0,r=0), height=280, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        with col3:
            if 'cluster_code' in merged.columns:
                cc = merged['cluster_code'].value_counts().reset_index()
                cc.columns = ['Cluster','Count']
                fig = px.bar(cc, x='Cluster', y='Count', title='Cluster',
                             color='Count', color_continuous_scale='Greens')
                fig.update_layout(margin=dict(t=40,b=0,l=0,r=0), height=280, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

    # ─── Unmatched Tab ───
    with tab_unmatched:
        st.markdown("<div class='section-header'>⚠️ Unmatched Participants Diagnostics</div>",
                    unsafe_allow_html=True)
        if corrupted_a or corrupted_b:
            st.markdown("<div class='fix-banner'>✅ <strong>Auto-fix applied:</strong> "
                        "Excel-corrupted age_group values were normalised. "
                        "Unmatched records below are genuinely unmatched.</div>",
                        unsafe_allow_html=True)

        total_unmatched = len(unmatched_a) + len(unmatched_b)
        if total_unmatched == 0:
            st.success("🎉 All participants were matched!")
        else:
            st.info(f"**{total_unmatched} participants** could not be matched with keys: "
                    f"`{'`, `'.join(selected_keys)}`")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"#### 📋 Unmatched in **{label_a}** ({len(unmatched_a)})")
                if not unmatched_a.empty:
                    st.dataframe(unmatched_a.reset_index(drop=True), width='stretch')
                    st.download_button(f"⬇️ Download", unmatched_a.to_csv(index=False).encode(),
                        f"unmatched_{label_a}.csv","text/csv", key="dl_unm_a")
                else:
                    st.success("No unmatched participants.")
            with col_b:
                st.markdown(f"#### 📋 Unmatched in **{label_b}** ({len(unmatched_b)})")
                if not unmatched_b.empty:
                    st.dataframe(unmatched_b.reset_index(drop=True), width='stretch')
                    st.download_button(f"⬇️ Download", unmatched_b.to_csv(index=False).encode(),
                        f"unmatched_{label_b}.csv","text/csv", key="dl_unm_b")
                else:
                    st.success("No unmatched participants.")

            st.markdown("---")
            st.markdown("#### 💡 Common Reasons for Unmatched Records")
            for title, desc in [
                ("🔑 Key mismatch", "A value in one of the matching fields differs between files."),
                ("🗂️ Not a duplicate exam", "Participant examined by only one examiner."),
                ("📅 Excel date corruption (auto-fixed)", "age_group corrupted by Excel (e.g. '12-15' → 'Dec-15'). Auto-corrected."),
                ("🔢 Numeric precision", "Float/integer mismatch in age_(years) (e.g. 5 vs 5.0)."),
            ]:
                with st.expander(title):
                    st.write(desc)

    # ─── Field Agreement Tab ───
    with tab_field:
        if agreement_df.empty:
            st.warning("No comparable fields found for the current selection.")
        else:
            col1, col2 = st.columns([3,2])
            with col1:
                st.markdown("<div class='section-header'>📋 Field-Level Agreement Table</div>",
                            unsafe_allow_html=True)
                disp_adf = agreement_df.drop(columns=['Band'], errors='ignore').copy()
                styled = (disp_adf.style
                          .map(pct_color, subset=['Agreement %'])
                          .format({'Agreement %':'{:.1f}%'})
                          .set_properties(**{'font-size':'13px'}))
                st.dataframe(styled, width='stretch', height=500)
            with col2:
                st.markdown("<div class='section-header'>📊 Distribution</div>",
                            unsafe_allow_html=True)
                if 'Band' not in agreement_df.columns:
                    agreement_df['Band'] = pd.cut(agreement_df['Agreement %'],
                        bins=[0,20,40,60,80,100],
                        labels=['0–20%','20–40%','40–60%','60–80%','80–100%'],
                        include_lowest=True)
                bc = agreement_df['Band'].value_counts().sort_index().reset_index()
                bc.columns = ['Band','Fields']
                fig = px.bar(bc, x='Band', y='Fields', color='Band',
                             color_discrete_sequence=['#ef4444','#f97316','#eab308','#84cc16','#22c55e'],
                             title='Fields by Agreement Band')
                fig.update_layout(margin=dict(t=40,b=0,l=0,r=0), height=250, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("<div class='section-header'>🔴 Lowest 10 Fields</div>",
                            unsafe_allow_html=True)
                b10 = agreement_df.head(10)[['Field','Agreement %']]
                fig2 = px.bar(b10, y='Field', x='Agreement %', orientation='h',
                              color='Agreement %', color_continuous_scale='RdYlGn', range_color=[0,100])
                fig2.update_layout(margin=dict(t=10,b=0,l=0,r=0), height=320, showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown("<div class='section-header'>🗺️ Agreement Heatmap (All Selected Fields)</div>",
                        unsafe_allow_html=True)
            show_n = st.slider("Number of fields to show in heatmap", 10, min(200, len(agreement_df)), 
                               min(40, len(agreement_df)), key="heatmap_n")
            top_n = agreement_df.tail(show_n)
            fig3 = go.Figure(go.Bar(
                x=top_n['Agreement %'], y=top_n['Field'], orientation='h',
                marker=dict(color=top_n['Agreement %'], colorscale='RdYlGn',
                            cmin=0, cmax=100, showscale=True)
            ))
            fig3.update_layout(height=max(400, show_n*18),
                               margin=dict(t=20,l=280),
                               xaxis_title='Agreement %', yaxis_title='')
            st.plotly_chart(fig3, use_container_width=True)

    # ─── Deep Dive Tab ───
    with tab_deepdive:
        st.markdown("<div class='section-header'>🔍 Per-Participant Deep Dive</div>",
                    unsafe_allow_html=True)

        if len(merged) == 0:
            st.warning("No matched participants to explore.")
        else:
            labels_list = [f"#{i+1} — {make_label(merged.iloc[i], selected_keys)}"
                           for i in range(len(merged))]
            selected_label = st.selectbox("Choose participant pair", labels_list)
            idx = labels_list.index(selected_label)
            comp_df = participant_level_comparison(merged, filtered_cols, label_a, label_b, idx=idx)

            if not comp_df.empty:
                n_agree    = comp_df['Status'].astype(str).str.startswith('Agree').sum()
                n_disagree = comp_df['Status'].astype(str).str.startswith('Disagree').sum()
                n_missing  = (comp_df['Status'] == 'Missing in one').sum()

                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("Fields Compared", len(comp_df))
                with c2: st.metric("✅ Agree",    int(n_agree))
                with c3: st.metric("❌ Disagree", int(n_disagree))
                with c4: st.metric("⚠️ Missing",  int(n_missing))

                fig_pie = go.Figure(go.Pie(
                    labels=['Agree','Disagree','Missing in one'],
                    values=[n_agree, n_disagree, n_missing],
                    marker_colors=['#22c55e','#ef4444','#eab308'], hole=0.45
                ))
                fig_pie.update_layout(height=220, margin=dict(t=10,b=10,l=0,r=0),
                                      legend=dict(orientation='h',y=-0.1))
                st.plotly_chart(fig_pie, use_container_width=True)

                show_filter = st.radio("Show", ['All','Disagree only','Agree only','Missing only'],
                                       horizontal=True, key="deepdive_filter")
                if show_filter == 'Disagree only': comp_df = comp_df[comp_df['Status'].astype(str).str.startswith('Disagree')]
                elif show_filter == 'Agree only':  comp_df = comp_df[comp_df['Status'].astype(str).str.startswith('Agree')]
                elif show_filter == 'Missing only':comp_df = comp_df[comp_df['Status']=='Missing in one']

                st.dataframe(comp_df.style.map(color_status, subset=['Status'])
                             .set_properties(**{'font-size':'13px'}),
                             use_container_width=True, height=500)

                st.download_button("⬇️ Download This Participant's Comparison",
                    comp_df.to_csv(index=False).encode(),
                    f"participant_{idx+1}_comparison.csv","text/csv", key="dl_pp")
            else:
                st.info("No comparable fields for this participant pair with current selection.")

    # ─── Discrepancies Tab ───
    with tab_discrep:
        st.markdown("<div class='section-header'>⚠️ Fields Below Agreement Threshold</div>",
                    unsafe_allow_html=True)
        low_df = agreement_df[agreement_df['Agreement %'] < low_agree_threshold].sort_values('Agreement %') \
                 if not agreement_df.empty else pd.DataFrame()
        if low_df.empty:
            st.success(f"✅ All selected fields are above the {low_agree_threshold}% threshold!")
        else:
            st.warning(f"**{len(low_df)} fields** below {low_agree_threshold}% agreement")
            disp_low = low_df.drop(columns=['Band'], errors='ignore').copy()
            st.dataframe(disp_low.style.map(pct_color, subset=['Agreement %'])
                     .format({'Agreement %':'{:.1f}%'})
                     .bar(subset=['Disagree'], color='#fca5a5')
                     .set_properties(**{'font-size':'13px'}),
                     use_container_width=True, height=400)

        st.markdown("<br><div class='section-header'>🗃️ All Discrepancies (Selected Fields)</div>",
                    unsafe_allow_html=True)

        if not all_disc_df.empty:
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                search_field = st.text_input("Filter by field name", key="disc_field_search")
            with col_f2:
                unique_parts = sorted(all_disc_df['Participant #'].unique().tolist())
                participant_filter = st.multiselect("Filter by participant #",
                    options=unique_parts, default=[], key="disc_part_filter")

            filtered_disc = all_disc_df.copy()
            if search_field.strip():
                filtered_disc = filtered_disc[filtered_disc['Field'].str.contains(
                    search_field.strip(), case=False, na=False)]
            if participant_filter:
                filtered_disc = filtered_disc[filtered_disc['Participant #'].isin(participant_filter)]

            st.info(f"Showing **{len(filtered_disc)}** discrepancies")
            st.download_button("⬇️ Download All Discrepancies (CSV)",
                all_disc_df.to_csv(index=False).encode(),
                "all_discrepancies.csv","text/csv", key="dl_disc_all")
            st.dataframe(filtered_disc, use_container_width=True, height=450)

            if not filtered_disc.empty:
                disc_freq = filtered_disc['Field'].value_counts().head(20).reset_index()
                disc_freq.columns = ['Field','Discrepancy Count']
                fig_disc = px.bar(disc_freq, x='Discrepancy Count', y='Field', orientation='h',
                                  color='Discrepancy Count', color_continuous_scale='Reds',
                                  title='Most Frequently Discrepant Fields (Filtered)')
                fig_disc.update_layout(height=max(350, len(disc_freq)*22),
                                       margin=dict(t=40,b=0,l=0,r=0))
                st.plotly_chart(fig_disc, use_container_width=True)
        else:
            st.success("🎉 No discrepancies found across any matched participants in selected fields!")

    # ─── Export Tab ───
    with tab_export:
        st.markdown("<div class='section-header'>📥 Download Reports</div>", unsafe_allow_html=True)
        disp = [c for c in selected_keys+['record_id_A','record_id_B',
                'examiner_number_A','examiner_number_B'] if c in merged.columns]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Matched Participants**")
            st.download_button("⬇️ CSV", merged[disp].to_csv(index=False).encode(),
                "matched_participants.csv","text/csv", key="exp_match")
        with col2:
            st.markdown("**Field Agreement Summary**")
            st.download_button("⬇️ CSV",
                agreement_df.drop(columns=['Band'],errors='ignore').to_csv(index=False).encode(),
                "field_agreement_summary.csv","text/csv", key="exp_agree")
        with col3:
            st.markdown("**All Discrepancies**")
            st.download_button("⬇️ CSV",
                all_disc_df.to_csv(index=False).encode() if not all_disc_df.empty
                else "No discrepancies".encode(),
                "all_discrepancies.csv","text/csv", key="exp_disc")

        if not all_examiner_disc_df.empty:
            st.markdown("**Examiner‑Wise Discrepancy Reports**")
            exd1, exd2 = st.columns(2)
            with exd1:
                st.download_button("Download All Examiner‑Wise Discrepancies CSV",
                    all_examiner_disc_df.to_csv(index=False).encode(),
                    "all_examiner_wise_discrepancies.csv", "text/csv",
                    key="exp_all_examiner_disc")
            with exd2:
                st.download_button("Download Examiner Discrepancy Summary CSV",
                    examiner_disc_summary_df.to_csv(index=False).encode(),
                    "examiner_discrepancy_summary.csv", "text/csv",
                    key="exp_examiner_disc_summary")

        if not unmatched_a.empty or not unmatched_b.empty:
            st.markdown("**Unmatched Participants**")
            cu1, cu2 = st.columns(2)
            with cu1:
                if not unmatched_a.empty:
                    st.download_button(f"⬇️ Unmatched {label_a}",
                        unmatched_a.to_csv(index=False).encode(),
                        f"unmatched_{label_a}.csv","text/csv", key="exp_unm_a")
            with cu2:
                if not unmatched_b.empty:
                    st.download_button(f"⬇️ Unmatched {label_b}",
                        unmatched_b.to_csv(index=False).encode(),
                        f"unmatched_{label_b}.csv","text/csv", key="exp_unm_b")

        st.markdown("<br>")
        st.markdown("**📊 Complete Multi‑Sheet Excel Report**")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            used_sheet_names = set()
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            used_sheet_names.add('Summary')
            merged[disp].to_excel(writer, sheet_name='Matched Participants', index=False)
            used_sheet_names.add('Matched Participants')
            agreement_df.drop(columns=['Band'],errors='ignore').to_excel(
                writer, sheet_name='Field Agreement', index=False)
            used_sheet_names.add('Field Agreement')

            if not examiner_summary_df.empty:
                examiner_summary_df.to_excel(writer, sheet_name='Examiner Summary (Pair)', index=False)
                used_sheet_names.add('Examiner Summary (Pair)')
                if not examiner_disc_summary_df.empty:
                    examiner_disc_summary_df.to_excel(writer, sheet_name='Exam Disc Summary', index=False)
                    used_sheet_names.add('Exam Disc Summary')
                if not all_examiner_disc_df.empty:
                    all_examiner_disc_df.to_excel(writer, sheet_name='Examiner Discrepancies', index=False)
                    used_sheet_names.add('Examiner Discrepancies')
                for pair_key, pair_agreement_df in examiner_agreement_tables.items():
                    if not pair_agreement_df.empty:
                        sheet_name = safe_excel_sheet_name(f"Exam Agree {pair_key}", used_sheet_names)
                        pair_agreement_df.to_excel(writer, sheet_name=sheet_name, index=False)
                for pair_key, pair_disc_df in examiner_discrepancy_tables.items():
                    if not pair_disc_df.empty:
                        sheet_name = safe_excel_sheet_name(f"Exam Disc {pair_key}", used_sheet_names)
                        pair_disc_df.to_excel(writer, sheet_name=sheet_name, index=False)

            if not agg_summary_A.empty:
                sheet_name = safe_excel_sheet_name(f"Aggregated Summary {label_a}", used_sheet_names)
                agg_summary_A.to_excel(writer, sheet_name=sheet_name, index=False)
            if not agg_summary_B.empty:
                sheet_name = safe_excel_sheet_name(f"Aggregated Summary {label_b}", used_sheet_names)
                agg_summary_B.to_excel(writer, sheet_name=sheet_name, index=False)
            for exam, disc_df in agg_discrepancies_A.items():
                if not disc_df.empty:
                    sheet_name = safe_excel_sheet_name(f"Agg Disc A {exam}", used_sheet_names)
                    disc_df.head(100).to_excel(writer, sheet_name=sheet_name, index=False)
            for exam, disc_df in agg_discrepancies_B.items():
                if not disc_df.empty:
                    sheet_name = safe_excel_sheet_name(f"Agg Disc B {exam}", used_sheet_names)
                    disc_df.head(100).to_excel(writer, sheet_name=sheet_name, index=False)

            if not all_disc_df.empty:
                all_disc_df.to_excel(writer, sheet_name='All Discrepancies', index=False)
                used_sheet_names.add('All Discrepancies')
            else:
                pd.DataFrame({'Message':['No discrepancies found']}).to_excel(
                    writer, sheet_name='All Discrepancies', index=False)
                used_sheet_names.add('All Discrepancies')
            low_df2 = agreement_df[agreement_df['Agreement %'] < low_agree_threshold] \
                      if not agreement_df.empty else pd.DataFrame()
            low_df2.drop(columns=['Band'],errors='ignore').to_excel(
                writer, sheet_name=f'Low Agreement (<{low_agree_threshold}%)', index=False)
            used_sheet_names.add(f'Low Agreement (<{low_agree_threshold}%)')
            if not unmatched_a.empty:
                sheet_name = safe_excel_sheet_name(f'Unmatched {label_a[:20]}', used_sheet_names)
                unmatched_a.to_excel(writer, sheet_name=sheet_name, index=False)
            if not unmatched_b.empty:
                sheet_name = safe_excel_sheet_name(f'Unmatched {label_b[:20]}', used_sheet_names)
                unmatched_b.to_excel(writer, sheet_name=sheet_name, index=False)
            for cat_name, sel_fields in category_selections.items():
                if sel_fields:
                    cat_adf = field_agreement_summary(merged, sel_fields)
                    if not cat_adf.empty:
                        safe_name = safe_excel_sheet_name(cat_name.replace('/','_').replace(':','')[:28], used_sheet_names)
                        cat_adf.drop(columns=['Band'],errors='ignore').to_excel(
                            writer, sheet_name=safe_name, index=False)

        st.download_button(
            "📥 Download Full Excel Report (All Sheets + Per‑Category + Aggregated)",
            output.getvalue(), "duplicate_exam_full_report.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="exp_full_excel")

        st.markdown("---")
        st.caption(
            f"Preset: {preset_labels[preset]} · "
            f"{common_count} matched participants · "
            f"{len(filtered_cols)} fields · "
            f"Matching keys: {', '.join(selected_keys)} · "
            f"Age‑group corrections: {len(corrupted_a)+len(corrupted_b)}"
        )

# ─────────────────────────────────────────────
# MODULE 3: RECORDED vs DUPLICATE (SINGLE FILE)
# ─────────────────────────────────────────────
elif mode == "📄 Recorded vs Duplicate (Single File)":
    # ─── SINGLE-FILE RECORDED vs DUPLICATE ───
    # Sidebar widgets for this module are rendered inside the main area.
    with st.sidebar:
        st.markdown("### 📂 Upload Single CSV")
        file = st.file_uploader("REDCap label export (CSV)", type=['csv'], key='single_file')
        st.markdown("---")
        if file:
            label_a = st.text_input("Name for Recorded group", value="Recorded (with examiner)")
            label_b = st.text_input("Name for Duplicate group", value="Duplicate (without examiner)")
            st.markdown("### ⚙️ Matching Parameters")
            use_record_id  = st.checkbox("Record ID", value=True)
            use_cluster    = st.checkbox("Cluster Code", value=False)
            use_household  = st.checkbox("Household Number", value=False)
            use_age        = st.checkbox("Age (Years)", value=False)
            use_age_group  = st.checkbox("Age Group", value=False)
            use_gender     = st.checkbox("Gender", value=False)
            st.markdown("### 🔍 Agreement Threshold")
            low_agree_threshold = st.slider("Flag fields below (%)", 0, 100, 60)
        else:
            st.info("Upload a CSV to begin.")

    if not file:
        st.info("👈 Upload a CSV file from the sidebar to begin.")
        c1, c2, c3 = st.columns(3)
        for col, step, desc in [(c1,"1","Upload CSV"),(c2,"2","Auto-split by examiner number"),(c3,"3","View comparison results")]:
            with col:
                st.markdown(f"<div style='border:2px dashed #cbd5e1;border-radius:14px;padding:2rem;text-align:center;background:white'>"
                            f"<h3>📤 Step {step}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
        st.stop()

    # ─── LOAD ───
    @st.cache_data(show_spinner=False)
    def load_single_duplicate_csv(file_bytes):
        return pd.read_csv(BytesIO(file_bytes), low_memory=False)

    df = normalize_export_columns(load_single_duplicate_csv(file.getvalue()))

    # ─── EXTRACT PARTICIPANT DATA ───
    pt_all = extract_participants(df)  # defined in shared helpers

    # Check examiner_number column exists
    if 'examiner_number' not in pt_all.columns:
        st.error("Column 'examiner_number' not found. Cannot split into recorded and duplicate groups.")
        st.stop()

    # ─── DUPLICATE EXAMINER SELECTION (sidebar) ───
    st.sidebar.markdown("### 🔍 Duplicate Examiner Selection")
    st.sidebar.caption("Define which examiner numbers (or missing values) should be considered 'duplicate'.")

    examiner_values = sorted(pt_all['examiner_number'].dropna().unique().astype(str).tolist())

    include_empty = st.sidebar.checkbox("Include rows with no examiner number", value=True)

    selected_examiners = st.sidebar.multiselect(
        "Select examiner numbers to consider as duplicates",
        options=examiner_values,
        default=[],
        help="Leave empty if you only want to use the 'empty' option."
    )

    # ─── RECORDED EXAMINER SELECTION (sidebar) ───
    st.sidebar.markdown("### 📌 Recorded Examiner Selection")
    st.sidebar.caption("Select which examiner numbers to include in the recorded group. By default, all non-duplicate examiners are included.")

    if 'recorded_examiners' not in st.session_state:
        st.session_state.recorded_examiners = [e for e in examiner_values if e not in selected_examiners]

    if st.sidebar.button("Reset recorded to default"):
        st.session_state.recorded_examiners = [e for e in examiner_values if e not in selected_examiners]

    recorded_examiners = st.sidebar.multiselect(
        "Recorded examiner numbers",
        options=examiner_values,
        default=st.session_state.recorded_examiners,
        key='recorded_examiners',
        help="Select examiner numbers to be considered as recorded. Empty examiner numbers are never included in recorded."
    )

    # ─── COMPUTE MASKS ───
    duplicate_mask = pd.Series(False, index=pt_all.index)
    if include_empty:
        duplicate_mask |= pt_all['examiner_number'].isna()
    if selected_examiners:
        duplicate_mask |= pt_all['examiner_number'].astype(str).isin(selected_examiners)

    recorded_mask = pt_all['examiner_number'].astype(str).isin(recorded_examiners) & ~duplicate_mask

    excluded_mask = ~duplicate_mask & ~recorded_mask
    excluded_count = excluded_mask.sum()

    overlap = set(recorded_examiners) & set(selected_examiners)
    if overlap:
        st.sidebar.warning(f"⚠️ Examiner(s) {', '.join(overlap)} are selected in both groups. They will be treated as duplicates (recorded excludes them).")

    if excluded_count > 0:
        st.sidebar.warning(f"{excluded_count} rows have examiner numbers not selected in recorded and not defined as duplicate — they will be ignored.")

    if duplicate_mask.sum() == 0:
        st.sidebar.error("No rows match the duplicate definition. Please select at least one examiner number or include empty.")
    if recorded_mask.sum() == 0:
        st.sidebar.error("No rows match the recorded definition. Please select at least one examiner number for recorded.")

    # ─── DATE FILTER (sidebar) ───
    st.sidebar.divider()
    st.sidebar.markdown("### 📅 Date Filter")
    date_candidates = detect_date_columns(pt_all)
    date_col = None
    date_mode = 'All dates'
    date_range_choice = None
    specific_dates_choice = []

    if not date_candidates:
        st.sidebar.caption("No date-like column found in this file — nothing to filter on.")
    else:
        date_col = st.sidebar.selectbox(
            "Date column",
            options=["(none)"] + date_candidates,
            index=(["(none)"] + date_candidates).index('consent_date') if 'consent_date' in date_candidates else 0,
            help="Column used to filter records by date. Detected automatically from any column containing 'date' in its name."
        )
        if date_col != "(none)":
            parsed_all = parse_date_column(pt_all[date_col])
            valid_dates = parsed_all.dropna()
            if valid_dates.empty:
                st.sidebar.warning(f"Couldn't parse any valid dates from '{date_col}'.")
                date_col = None
            else:
                min_d, max_d = valid_dates.dt.date.min(), valid_dates.dt.date.max()
                date_mode = st.sidebar.radio("Filter mode", ["All dates", "Date range", "Specific date(s)"], index=0)
                if date_mode == "Date range":
                    date_range_choice = st.sidebar.date_input(
                        "Select date range", value=(min_d, max_d), min_value=min_d, max_value=max_d
                    )
                elif date_mode == "Specific date(s)":
                    available_dates = sorted(valid_dates.dt.date.unique())
                    specific_dates_choice = st.sidebar.multiselect(
                        "Select date(s)", options=available_dates, default=[]
                    )
        else:
            date_col = None

    # ─── APPLY FILTERS ───
    with st.spinner("🔄 Processing file and splitting groups..."):
        pt_recorded = pt_all[recorded_mask].copy()
        pt_duplicate = pt_all[duplicate_mask].copy()

        date_filter_active = False
        pre_filter_recorded_count = len(pt_recorded)
        if date_col and date_col in pt_recorded.columns:
            parsed = parse_date_column(pt_recorded[date_col])
            if date_mode == "Date range" and date_range_choice:
                if isinstance(date_range_choice, (tuple, list)) and len(date_range_choice) == 2:
                    start_d, end_d = date_range_choice
                    keep_mask = parsed.dt.date.between(start_d, end_d)
                    pt_recorded = pt_recorded[keep_mask.fillna(False)]
                    date_filter_active = True
            elif date_mode == "Specific date(s)" and specific_dates_choice:
                keep_mask = parsed.dt.date.isin(specific_dates_choice)
                pt_recorded = pt_recorded[keep_mask.fillna(False)]
                date_filter_active = True

        corrupted_recorded = detect_corrupted_values(
            pt_recorded['age_group'] if 'age_group' in pt_recorded.columns else pd.Series(dtype=str))
        corrupted_duplicate = detect_corrupted_values(
            pt_duplicate['age_group'] if 'age_group' in pt_duplicate.columns else pd.Series(dtype=str))

        all_keys = {
            'record_id': use_record_id,
            'cluster_code': use_cluster,
            'household_number': use_household,
            'age_(years)': use_age,
            'age_group': use_age_group,
            'gender': use_gender
        }
        selected_keys = [k for k, v in all_keys.items() if v and k in pt_recorded.columns and k in pt_duplicate.columns]

        if not selected_keys:
            st.error("Please select at least one matching parameter that exists in both groups.")
            st.stop()

        merged = pd.merge(pt_recorded, pt_duplicate, on=selected_keys, suffixes=('_Recorded', '_Duplicate'))
        unmatched_recorded = get_unmatched(pt_recorded, pt_duplicate, selected_keys)
        unmatched_duplicate = get_unmatched(pt_duplicate, pt_recorded, selected_keys)

        all_compare_cols = compare_fields(merged, suffix_a='_Recorded', suffix_b='_Duplicate')
        field_categories = classify_fields(all_compare_cols)

    # ─────────────────────────────────────────────
    # DATE FILTER STATUS BANNER
    # ─────────────────────────────────────────────
    if date_filter_active:
        if date_mode == "Date range" and date_range_choice and len(date_range_choice) == 2:
            range_txt = f"{date_range_choice[0].strftime('%d %b %Y')} → {date_range_choice[1].strftime('%d %b %Y')}"
        elif date_mode == "Specific date(s)":
            range_txt = ', '.join(d.strftime('%d %b %Y') for d in sorted(specific_dates_choice))
        else:
            range_txt = "—"
        st.markdown(
            f"<div class='date-info'>📅 <strong>Date filter active</strong> on <code>{date_col}</code>: {range_txt} · "
            f"Showing <strong>{len(pt_recorded)}</strong> of <strong>{pre_filter_recorded_count}</strong> "
            f"recorded participants.</div>", unsafe_allow_html=True)
        if len(pt_recorded) == 0:
            st.warning("No recorded participants fall within the selected date filter. "
                       "Adjust the date range/selection in the sidebar.")
            st.stop()

    # ─────────────────────────────────────────────
    # FIELD SELECTION PANEL
    # ─────────────────────────────────────────────
    if corrupted_recorded or corrupted_duplicate:
        st.markdown(
            f"<div class='warning-banner'>⚠️ <strong>Excel date-corruption detected and auto-fixed.</strong><br>"
            f"{'<b>'+label_a+'</b>: '+', '.join(corrupted_recorded)+' → corrected' if corrupted_recorded else ''}"
            f"{'<br>' if corrupted_recorded and corrupted_duplicate else ''}"
            f"{'<b>'+label_b+'</b>: '+', '.join(corrupted_duplicate)+' → corrected' if corrupted_duplicate else ''}"
            f"</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎯 Field Selection — Choose What to Analyse")

    preset_col1, preset_col2, preset_col3, preset_col4, preset_col5 = st.columns(5)
    with preset_col1:
        btn_clinical = st.button("🏥 Clinical Only", use_container_width=True)
    with preset_col2:
        btn_tooth    = st.button("🦷 Teeth Only",    use_container_width=True)
    with preset_col3:
        btn_behav    = st.button("📋 Behavioural",   use_container_width=True)
    with preset_col4:
        btn_all      = st.button("🌐 All Fields",    use_container_width=True)
    with preset_col5:
        btn_low      = st.button("🔴 Low Agreement", use_container_width=True)

    if 'field_preset' not in st.session_state:
        st.session_state.field_preset = 'clinical'
    if btn_clinical: st.session_state.field_preset = 'clinical'
    if btn_tooth:    st.session_state.field_preset = 'teeth'
    if btn_behav:    st.session_state.field_preset = 'behavioural'
    if btn_all:      st.session_state.field_preset = 'all'
    if btn_low:      st.session_state.field_preset = 'low'

    with st.expander("🔧 Fine-Grained Category Selection (override presets)", expanded=False):
        st.caption("Select/deselect individual fields within each category. Preset buttons above will reset selections.")
        n_cats = len(field_categories)
        cat_cols = st.columns(3)
        category_selections = {}
        preset = st.session_state.field_preset

        for i, (cat_name, cat_fields) in enumerate(field_categories.items()):
            col_idx = i % 3
            is_clinical = cat_name in CLINICAL_CATEGORIES
            non_clinical_behav = cat_name in {"📋 Behavioural / Oral Hygiene",
                                              "💊 Dental Visit / Treatment"}

            if preset == 'clinical':
                default_fields = cat_fields if is_clinical else []
            elif preset == 'teeth':
                default_fields = cat_fields if cat_name in {"🦷 Tooth Status (Primary)","🦷 Tooth Status (Permanent)",
                                                             "🩸 Bleeding","📏 Pocket Depth"} else []
            elif preset == 'behavioural':
                default_fields = cat_fields if non_clinical_behav else []
            else:
                default_fields = cat_fields

            with cat_cols[col_idx]:
                selected = st.multiselect(
                    f"{cat_name} ({len(cat_fields)})",
                    options=cat_fields,
                    default=default_fields,
                    key=f"multiselect_{cat_name}"
                )
                category_selections[cat_name] = selected

    filtered_cols = []
    for cat, sel_fields in category_selections.items():
        filtered_cols.extend(sel_fields)
    filtered_cols = list(set(filtered_cols))
    filtered_cols = [c for c in filtered_cols if c in all_compare_cols]

    field_search = st.text_input("🔎 Search for specific field name (optional)", placeholder="e.g. tooth_16, pocket, leukoplakia")
    if field_search.strip():
        filtered_cols = [c for c in filtered_cols if field_search.strip().lower() in c.lower()]

    preset_labels = {
        'clinical':     '🏥 Clinical Only',
        'teeth':        '🦷 Teeth Only',
        'behavioural':  '📋 Behavioural',
        'all':          '🌐 All Fields',
        'low':          '🔴 Low Agreement',
    }
    st.markdown(
        f"<div class='preset-info'>Active preset: <strong>{preset_labels[preset]}</strong> · "
        f"<strong>{len(filtered_cols)}</strong> fields selected across "
        f"<strong>{len(category_selections)}</strong> categories"
        f"{'  ·  Search filter active: <em>'+field_search+'</em>' if field_search.strip() else ''}"
        f"</div>", unsafe_allow_html=True)

    # ── Compute agreement ──
    agreement_df = field_agreement_summary(merged, filtered_cols, suffix_a='_Recorded', suffix_b='_Duplicate')
    if preset == 'low' and not agreement_df.empty:
        agreement_df = agreement_df[agreement_df['Agreement %'] < low_agree_threshold]
        filtered_cols = list(agreement_df['Field'])

    # ── Top-level metrics ──
    total_recorded = len(pt_recorded)
    total_duplicate = len(pt_duplicate)
    common_count  = len(merged)
    avg_agreement = agreement_df['Agreement %'].mean() if not agreement_df.empty else 0
    low_agree_cnt = len(agreement_df[agreement_df['Agreement %'] < low_agree_threshold]) if not agreement_df.empty else 0

    # Build all discrepancies
    all_discrepancies = []
    if common_count > 0 and filtered_cols:
        for i in range(len(merged)):
            comp = participant_level_comparison(merged, filtered_cols, label_a, label_b,
                                                suffix_a='_Recorded', suffix_b='_Duplicate', idx=i)
            disc = comp[comp['Status'].astype(str).str.startswith('Disagree')].copy()
            if not disc.empty:
                disc.insert(0, 'Participant #', i + 1)
                disc.insert(1, f'Record ID ({label_a})', merged.iloc[i].get('record_id_Recorded', ''))
                disc.insert(2, f'Record ID ({label_b})', merged.iloc[i].get('record_id_Duplicate', ''))
                parts = [f"{k.replace('_',' ').title()}: {merged.iloc[i][k]}"
                         for k in selected_keys if k in merged.columns and pd.notna(merged.iloc[i][k])]
                disc.insert(3, 'Matching Key', ' | '.join(parts))
                all_discrepancies.append(disc)

    all_disc_df = pd.concat(all_discrepancies, ignore_index=True) if all_discrepancies else pd.DataFrame()

    # ── Aggregated examiner reports ──
    examiner_summary_df, examiner_agreement_dict, examiner_discrepancy_dict = build_single_file_examiner_aggregated_reports(
        merged, filtered_cols, selected_keys, label_a, label_b,
        low_agree_threshold,
        suffix_a='_Recorded', suffix_b='_Duplicate'
    )

    # ── Summary dataframe ──
    summary_data = {
        'Metric': [
            f'Participants — {label_a}', f'Participants — {label_b}',
            'Matched Participants (have both recorded & duplicate)',
            f'Unmatched in {label_a}', f'Unmatched in {label_b}',
            'Active Preset', 'Fields Selected', 'Average Field Agreement (%)',
            f'Fields Below {low_agree_threshold}%', 'Total Discrepancies (field-level)',
            'Matching Keys Used', 'Date Filter Column', 'Date Filter Mode',
            'Age Group Auto-corrected (Recorded)', 'Age Group Auto-corrected (Duplicate)',
            'Duplicate Examiner Numbers (selected)', 'Include Empty Examiner?',
            'Recorded Examiner Numbers (selected)', 'Excluded Rows (ignored)'
        ],
        'Value': [
            total_recorded, total_duplicate, common_count,
            len(unmatched_recorded), len(unmatched_duplicate),
            preset_labels[preset], len(filtered_cols),
            f"{avg_agreement:.1f}%", low_agree_cnt, len(all_disc_df),
            ', '.join(selected_keys),
            date_col if date_col else 'None',
            date_mode if date_filter_active else 'All dates',
            ', '.join(corrupted_recorded) if corrupted_recorded else 'None',
            ', '.join(corrupted_duplicate) if corrupted_duplicate else 'None',
            ', '.join(selected_examiners) if selected_examiners else 'None',
            'Yes' if include_empty else 'No',
            ', '.join(recorded_examiners) if recorded_examiners else 'None',
            excluded_count
        ]
    }
    summary_df = pd.DataFrame(summary_data)

    # ── Metric cards ──
    st.markdown("---")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    for col, color, val, lbl in [
        (c1, "",       total_recorded, f"Participants — {label_a}"),
        (c2, "green",  total_duplicate, f"Participants — {label_b}"),
        (c3, "purple", common_count,   "Matched (have both)"),
        (c4, "orange" if (len(unmatched_recorded)+len(unmatched_duplicate)) > 0 else "green",
             len(unmatched_recorded)+len(unmatched_duplicate), "Unmatched (A+B)"),
        (c5, "green" if avg_agreement >= 80 else "orange" if avg_agreement >= 60 else "red",
             f"{avg_agreement:.1f}%", "Avg Field Agreement"),
        (c6, "red", low_agree_cnt, f"Fields < {low_agree_threshold}%"),
    ]:
        with col:
            st.markdown(
                f"<div class='metric-card {color}'>"
                f"<div class='metric-value'>{val}</div>"
                f"<div class='metric-label'>{lbl}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if common_count == 0:
        st.error("⚠️ No common participants found. Try adjusting matching parameters or the date filter.")
        if not unmatched_recorded.empty:
            st.markdown("**Participants in Recorded with no match in Duplicate:**")
            st.dataframe(unmatched_recorded, use_container_width=True)
        if not unmatched_duplicate.empty:
            st.markdown("**Participants in Duplicate with no match in Recorded:**")
            st.dataframe(unmatched_duplicate, use_container_width=True)
        st.stop()

    if not filtered_cols:
        st.warning("No fields match the current selection. Please adjust your category choices or search term.")
        st.stop()

    # ─────────────────────────────────────────────
    # TABS (single-file version)
    # ─────────────────────────────────────────────
    tab_summary, tab_examiner, tab_matched, tab_unmatched, tab_field, tab_deepdive, tab_discrep, tab_export = st.tabs([
        "📋 Summary", "👤 Examiner Summary", "👥 Matched", "⚠️ Unmatched",
        "📊 Field Agreement", "🔍 Deep Dive", "🚨 Discrepancies", "📥 Export"
    ])

    # ── SUMMARY TAB ──
    with tab_summary:
        st.markdown("<div class='section-header'>📋 Executive Summary</div>", unsafe_allow_html=True)

        summary_output = BytesIO()
        with pd.ExcelWriter(summary_output, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Key Metrics', index=False)
            if not agreement_df.empty:
                agreement_df.head(20)[['Field','Agreement %']].to_excel(
                    writer, sheet_name='Lowest Agreement Fields', index=False)
            if not all_disc_df.empty:
                disc_freq = all_disc_df['Field'].value_counts().head(20).reset_index()
                disc_freq.columns = ['Field','Discrepancy Count']
                disc_freq.to_excel(writer, sheet_name='Frequent Discrepancies', index=False)

        st.download_button("📥 Download Summary Report (Excel)", summary_output.getvalue(),
            "recorded_duplicate_summary.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_summary")
        st.markdown("---")

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Matched", common_count)
        with col2: st.metric("Avg Agreement", f"{avg_agreement:.1f}%")
        with col3: st.metric("Below Threshold", low_agree_cnt)
        with col4: st.metric("Discrepancies", len(all_disc_df))

        st.markdown("---")
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("#### 🔴 Lowest Agreement Fields (Top 10)")
            if not agreement_df.empty:
                top_low = agreement_df.head(10)[['Field','Agreement %']].copy()
                fig_low = px.bar(top_low, x='Agreement %', y='Field', orientation='h',
                                 color='Agreement %', color_continuous_scale='RdYlGn_r',
                                 range_color=[0,100], text_auto='.1f')
                fig_low.update_layout(height=350, margin=dict(l=0,r=0,t=30,b=0))
                st.plotly_chart(fig_low, width='stretch')
        with col_right:
            st.markdown("#### 🔥 Most Frequent Discrepancies (Top 10)")
            if not all_disc_df.empty:
                disc_freq = all_disc_df['Field'].value_counts().head(10).reset_index()
                disc_freq.columns = ['Field','Discrepancy Count']
                fig_disc = px.bar(disc_freq, x='Discrepancy Count', y='Field', orientation='h',
                                  color='Discrepancy Count', color_continuous_scale='Reds', text_auto=True)
                fig_disc.update_layout(height=350, margin=dict(l=0,r=0,t=30,b=0))
                st.plotly_chart(fig_disc, width='stretch')
            else:
                st.success("🎉 No discrepancies found in selected fields!")

        st.markdown("---")
        st.markdown("#### 📊 Agreement Distribution Across Selected Fields")
        if not agreement_df.empty:
            bins = [0,20,40,60,80,100]
            labels_ = ['0–20%','20–40%','40–60%','60–80%','80–100%']
            agreement_df['Band'] = pd.cut(agreement_df['Agreement %'], bins=bins,
                                          labels=labels_, include_lowest=True)
            band_counts = agreement_df['Band'].value_counts().sort_index().reset_index()
            band_counts.columns = ['Band','Fields']
            fig_band = px.bar(band_counts, x='Band', y='Fields', color='Band',
                              color_discrete_sequence=['#ef4444','#f97316','#eab308','#84cc16','#22c55e'])
            fig_band.update_layout(showlegend=False, height=300, margin=dict(l=0,r=0))
            st.plotly_chart(fig_band, use_container_width=True)

        if date_col and date_col in pt_recorded.columns:
            st.markdown("---")
            st.markdown("#### 📅 Recorded Participants Over Time")
            dts = parse_date_column(pt_recorded[date_col]).dt.date
            dcounts = dts.value_counts().sort_index().reset_index()
            dcounts.columns = ['Date', 'Count']
            fig_dt = px.bar(dcounts, x='Date', y='Count', title=f'Recorded exams by {date_col}',
                            color='Count', color_continuous_scale='Purples')
            fig_dt.update_layout(margin=dict(t=40,b=0,l=0,r=0), height=280, showlegend=False)
            st.plotly_chart(fig_dt, use_container_width=True)

    # ── EXAMINER SUMMARY TAB ──
    with tab_examiner:
        st.markdown("<div class='section-header'>Recorded Examiner Summary (vs Aggregated Duplicate)</div>", unsafe_allow_html=True)
        st.caption(
            f"For each recorded examiner, all matched duplicate records are combined. "
            f"This shows the overall consistency of each examiner against the aggregated duplicate group."
        )

        if examiner_summary_df.empty:
            st.info("No examiner numbers found in the recorded group.")
        else:
            st.markdown("#### Summary per Recorded Examiner")
            styled_examiner = (examiner_summary_df.style
                .map(pct_color, subset=['Avg Agreement %','Min Agreement %'])
                .format({'Avg Agreement %':'{:.1f}%','Min Agreement %':'{:.1f}%'})
                .set_properties(**{'font-size':'13px'}))
            st.dataframe(styled_examiner, width='stretch', height=320)
            st.download_button("Download Examiner Summary CSV",
                examiner_summary_df.to_csv(index=False).encode(),
                "recorded_examiner_summary.csv", "text/csv", key="dl_examiner_summary")

            st.markdown("---")
            st.markdown("### Drill‑down: Select an Examiner to View Field Agreement and Discrepancies")

            exam_options = sorted(examiner_summary_df[f'Examiner ({label_a})'].dropna().unique().tolist())
            selected_exam = st.selectbox(f"Select {label_a} examiner", exam_options, key="examiner_select")

            row = examiner_summary_df[examiner_summary_df[f'Examiner ({label_a})'] == selected_exam]
            if not row.empty:
                r = row.iloc[0]
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("Matched Participants", int(r['Matched Participants']))
                with c2: st.metric("Avg Agreement", f"{r['Avg Agreement %']:.1f}%")
                with c3: st.metric("Low Agreement Fields", int(r[f'Fields < {low_agree_threshold}%']))
                with c4: st.metric("Discrepancies", int(r['Discrepancies']))

            ag_df = examiner_agreement_dict.get(selected_exam, pd.DataFrame())
            st.markdown(f"#### Field Agreement for {label_a} examiner {selected_exam} (Aggregated)")
            if ag_df.empty:
                st.info("No fields assessed for this examiner.")
            else:
                st.dataframe(ag_df.style.map(pct_color, subset=['Agreement %'])
                             .format({'Agreement %':'{:.1f}%'})
                             .set_properties(**{'font-size':'13px'}),
                             width='stretch', height=350)
                st.download_button("Download Field Agreement CSV",
                    ag_df.to_csv(index=False).encode(),
                    f"field_agreement_examiner_{selected_exam}.csv", "text/csv",
                    key="dl_examiner_agreement")

            disc_df = examiner_discrepancy_dict.get(selected_exam, pd.DataFrame())
            st.markdown(f"#### Discrepancies for {label_a} examiner {selected_exam} (Aggregated)")
            if disc_df.empty:
                st.success("No discrepancies found for this examiner.")
            else:
                fcol1, fcol2 = st.columns(2)
                with fcol1:
                    field_filt = st.text_input("Filter by field", key="exam_disc_field")
                with fcol2:
                    part_filt = st.multiselect("Filter by participant #",
                        sorted(disc_df['Participant #'].dropna().unique().tolist()),
                        key="exam_disc_part")
                shown_disc = disc_df.copy()
                if field_filt.strip():
                    shown_disc = shown_disc[shown_disc['Field'].str.contains(field_filt.strip(), case=False, na=False)]
                if part_filt:
                    shown_disc = shown_disc[shown_disc['Participant #'].isin(part_filt)]
                st.info(f"Showing {len(shown_disc)} discrepancies")
                st.download_button("Download Discrepancies CSV",
                    shown_disc.to_csv(index=False).encode(),
                    f"discrepancies_examiner_{selected_exam}.csv", "text/csv",
                    key="dl_examiner_disc")
                st.dataframe(shown_disc, width='stretch', height=400)

    # ── MATCHED TAB (unchanged) ──
    with tab_matched:
        st.markdown("<div class='section-header'>✅ Matched Participants</div>", unsafe_allow_html=True)
        disp = [c for c in selected_keys+['record_id_Recorded','record_id_Duplicate'] if c in merged.columns]
        st.dataframe(merged[disp].reset_index(drop=True), width='stretch', height=400)

        st.markdown("#### 📊 Demographics of Matched Participants")
        col1, col2, col3 = st.columns(3)
        with col1:
            if 'gender' in merged.columns:
                fig = px.pie(merged, names='gender', title='Gender',
                             color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_layout(margin=dict(t=40,b=0,l=0,r=0), height=280)
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            if 'age_group' in merged.columns:
                ac = merged['age_group'].value_counts().reset_index()
                ac.columns = ['Age Group','Count']
                fig = px.bar(ac, x='Age Group', y='Count', title='Age Group',
                             color='Count', color_continuous_scale='Blues')
                fig.update_layout(margin=dict(t=40,b=0,l=0,r=0), height=280, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        with col3:
            if 'cluster_code' in merged.columns:
                cc = merged['cluster_code'].value_counts().reset_index()
                cc.columns = ['Cluster','Count']
                fig = px.bar(cc, x='Cluster', y='Count', title='Cluster',
                             color='Count', color_continuous_scale='Greens')
                fig.update_layout(margin=dict(t=40,b=0,l=0,r=0), height=280, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

    # ── UNMATCHED TAB (unchanged) ──
    with tab_unmatched:
        st.markdown("<div class='section-header'>⚠️ Unmatched Participants Diagnostics</div>", unsafe_allow_html=True)
        if corrupted_recorded or corrupted_duplicate:
            st.markdown("<div class='fix-banner'>✅ <strong>Auto-fix applied:</strong> "
                        "Excel-corrupted age_group values were normalised. "
                        "Unmatched records below are genuinely unmatched.</div>",
                        unsafe_allow_html=True)

        total_unmatched = len(unmatched_recorded) + len(unmatched_duplicate)
        if total_unmatched == 0:
            st.success("🎉 All participants were matched!")
        else:
            st.info(f"**{total_unmatched} participants** could not be matched with keys: "
                    f"`{'`, `'.join(selected_keys)}`")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"#### 📋 Unmatched in **{label_a}** ({len(unmatched_recorded)})")
                if not unmatched_recorded.empty:
                    st.dataframe(unmatched_recorded.reset_index(drop=True), width='stretch')
                    st.download_button(f"⬇️ Download", unmatched_recorded.to_csv(index=False).encode(),
                        f"unmatched_{label_a}.csv","text/csv", key="dl_unm_a")
                else:
                    st.success("No unmatched participants.")
            with col_b:
                st.markdown(f"#### 📋 Unmatched in **{label_b}** ({len(unmatched_duplicate)})")
                if not unmatched_duplicate.empty:
                    st.dataframe(unmatched_duplicate.reset_index(drop=True), width='stretch')
                    st.download_button(f"⬇️ Download", unmatched_duplicate.to_csv(index=False).encode(),
                        f"unmatched_{label_b}.csv","text/csv", key="dl_unm_b")
                else:
                    st.success("No unmatched participants.")

            st.markdown("---")
            st.markdown("#### 💡 Common Reasons for Unmatched Records")
            for title, desc in [
                ("🔑 Key mismatch", "A value in one of the matching fields differs between groups."),
                ("🗂️ Not a duplicate exam", "Participant exists only in one group (e.g., only recorded or only duplicate)."),
                ("📅 Excluded by date filter", "The record's date falls outside the selected date range/date(s) in the sidebar."),
                ("📅 Excel date corruption (auto-fixed)", "age_group corrupted by Excel (e.g. '12-15' → 'Dec-15'). Auto-corrected."),
                ("🔢 Numeric precision", "Float/integer mismatch in age_(years) (e.g. 5 vs 5.0)."),
            ]:
                with st.expander(title):
                    st.write(desc)

    # ── FIELD AGREEMENT TAB (unchanged) ──
    with tab_field:
        if agreement_df.empty:
            st.warning("No comparable fields found for the current selection.")
        else:
            col1, col2 = st.columns([3,2])
            with col1:
                st.markdown("<div class='section-header'>📋 Field-Level Agreement Table</div>", unsafe_allow_html=True)
                disp_adf = agreement_df.drop(columns=['Band'], errors='ignore').copy()
                styled = (disp_adf.style
                          .map(pct_color, subset=['Agreement %'])
                          .format({'Agreement %':'{:.1f}%'})
                          .set_properties(**{'font-size':'13px'}))
                st.dataframe(styled, width='stretch', height=500)
            with col2:
                st.markdown("<div class='section-header'>📊 Distribution</div>", unsafe_allow_html=True)
                if 'Band' not in agreement_df.columns:
                    agreement_df['Band'] = pd.cut(agreement_df['Agreement %'],
                        bins=[0,20,40,60,80,100],
                        labels=['0–20%','20–40%','40–60%','60–80%','80–100%'],
                        include_lowest=True)
                bc = agreement_df['Band'].value_counts().sort_index().reset_index()
                bc.columns = ['Band','Fields']
                fig = px.bar(bc, x='Band', y='Fields', color='Band',
                             color_discrete_sequence=['#ef4444','#f97316','#eab308','#84cc16','#22c55e'],
                             title='Fields by Agreement Band')
                fig.update_layout(margin=dict(t=40,b=0,l=0,r=0), height=250, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("<div class='section-header'>🔴 Lowest 10 Fields</div>", unsafe_allow_html=True)
                b10 = agreement_df.head(10)[['Field','Agreement %']]
                fig2 = px.bar(b10, y='Field', x='Agreement %', orientation='h',
                              color='Agreement %', color_continuous_scale='RdYlGn', range_color=[0,100])
                fig2.update_layout(margin=dict(t=10,b=0,l=0,r=0), height=320, showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown("<div class='section-header'>🗺️ Agreement Heatmap (All Selected Fields)</div>", unsafe_allow_html=True)
            show_n = st.slider("Number of fields to show in heatmap", 10, min(200, len(agreement_df)), 
                               min(40, len(agreement_df)), key="heatmap_n")
            top_n = agreement_df.tail(show_n)
            fig3 = go.Figure(go.Bar(
                x=top_n['Agreement %'], y=top_n['Field'], orientation='h',
                marker=dict(color=top_n['Agreement %'], colorscale='RdYlGn',
                            cmin=0, cmax=100, showscale=True)
            ))
            fig3.update_layout(height=max(400, show_n*18),
                               margin=dict(t=20,l=280),
                               xaxis_title='Agreement %', yaxis_title='')
            st.plotly_chart(fig3, use_container_width=True)

    # ── DEEP DIVE TAB (unchanged) ──
    with tab_deepdive:
        st.markdown("<div class='section-header'>🔍 Per-Participant Deep Dive</div>", unsafe_allow_html=True)
        if len(merged) == 0:
            st.warning("No matched participants to explore.")
        else:
            labels_list = [f"#{i+1} — {make_label(merged.iloc[i], selected_keys)}"
                           for i in range(len(merged))]
            selected_label = st.selectbox("Choose participant pair", labels_list)
            idx = labels_list.index(selected_label)
            comp_df = participant_level_comparison(merged, filtered_cols, label_a, label_b,
                                                   suffix_a='_Recorded', suffix_b='_Duplicate', idx=idx)

            if not comp_df.empty:
                n_agree    = comp_df['Status'].astype(str).str.startswith('Agree').sum()
                n_disagree = comp_df['Status'].astype(str).str.startswith('Disagree').sum()
                n_missing  = (comp_df['Status'] == 'Missing in one').sum()

                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("Fields Compared", len(comp_df))
                with c2: st.metric("✅ Agree",    int(n_agree))
                with c3: st.metric("❌ Disagree", int(n_disagree))
                with c4: st.metric("⚠️ Missing",  int(n_missing))

                fig_pie = go.Figure(go.Pie(
                    labels=['Agree','Disagree','Missing in one'],
                    values=[n_agree, n_disagree, n_missing],
                    marker_colors=['#22c55e','#ef4444','#eab308'], hole=0.45
                ))
                fig_pie.update_layout(height=220, margin=dict(t=10,b=10,l=0,r=0),
                                      legend=dict(orientation='h',y=-0.1))
                st.plotly_chart(fig_pie, use_container_width=True)

                show_filter = st.radio("Show", ['All','Disagree only','Agree only','Missing only'],
                                       horizontal=True, key="deepdive_filter")
                if show_filter == 'Disagree only': comp_df = comp_df[comp_df['Status'].astype(str).str.startswith('Disagree')]
                elif show_filter == 'Agree only':  comp_df = comp_df[comp_df['Status'].astype(str).str.startswith('Agree')]
                elif show_filter == 'Missing only':comp_df = comp_df[comp_df['Status']=='Missing in one']

                st.dataframe(comp_df.style.map(color_status, subset=['Status'])
                             .set_properties(**{'font-size':'13px'}),
                             use_container_width=True, height=500)

                st.download_button("⬇️ Download This Participant's Comparison",
                    comp_df.to_csv(index=False).encode(),
                    f"participant_{idx+1}_comparison.csv","text/csv", key="dl_pp")
            else:
                st.info("No comparable fields for this participant pair with current selection.")

    # ── DISCREPANCIES TAB (unchanged) ──
    with tab_discrep:
        st.markdown("<div class='section-header'>⚠️ Fields Below Agreement Threshold</div>", unsafe_allow_html=True)
        low_df = agreement_df[agreement_df['Agreement %'] < low_agree_threshold].sort_values('Agreement %') \
                 if not agreement_df.empty else pd.DataFrame()
        if low_df.empty:
            st.success(f"✅ All selected fields are above the {low_agree_threshold}% threshold!")
        else:
            st.warning(f"**{len(low_df)} fields** below {low_agree_threshold}% agreement")
            disp_low = low_df.drop(columns=['Band'], errors='ignore').copy()
            st.dataframe(disp_low.style.map(pct_color, subset=['Agreement %'])
                     .format({'Agreement %':'{:.1f}%'})
                     .bar(subset=['Disagree'], color='#fca5a5')
                     .set_properties(**{'font-size':'13px'}),
                     use_container_width=True, height=400)

        st.markdown("<br><div class='section-header'>🗃️ All Discrepancies (Selected Fields)</div>", unsafe_allow_html=True)

        if not all_disc_df.empty:
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                search_field = st.text_input("Filter by field name", key="disc_field_search")
            with col_f2:
                unique_parts = sorted(all_disc_df['Participant #'].unique().tolist())
                participant_filter = st.multiselect("Filter by participant #",
                    options=unique_parts, default=[], key="disc_part_filter")

            filtered_disc = all_disc_df.copy()
            if search_field.strip():
                filtered_disc = filtered_disc[filtered_disc['Field'].str.contains(
                    search_field.strip(), case=False, na=False)]
            if participant_filter:
                filtered_disc = filtered_disc[filtered_disc['Participant #'].isin(participant_filter)]

            st.info(f"Showing **{len(filtered_disc)}** discrepancies")
            st.download_button("⬇️ Download All Discrepancies (CSV)",
                all_disc_df.to_csv(index=False).encode(),
                "all_discrepancies.csv","text/csv", key="dl_disc_all")
            st.dataframe(filtered_disc, use_container_width=True, height=450)

            if not filtered_disc.empty:
                disc_freq = filtered_disc['Field'].value_counts().head(20).reset_index()
                disc_freq.columns = ['Field','Discrepancy Count']
                fig_disc = px.bar(disc_freq, x='Discrepancy Count', y='Field', orientation='h',
                                  color='Discrepancy Count', color_continuous_scale='Reds',
                                  title='Most Frequently Discrepant Fields (Filtered)')
                fig_disc.update_layout(height=max(350, len(disc_freq)*22),
                                       margin=dict(t=40,b=0,l=0,r=0))
                st.plotly_chart(fig_disc, use_container_width=True)
        else:
            st.success("🎉 No discrepancies found across any matched participants in selected fields!")

    # ── EXPORT TAB (updated to include examiner sheets) ──
    with tab_export:
        st.markdown("<div class='section-header'>📥 Download Reports</div>", unsafe_allow_html=True)
        disp = [c for c in selected_keys+['record_id_Recorded','record_id_Duplicate'] if c in merged.columns]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Matched Participants**")
            st.download_button("⬇️ CSV", merged[disp].to_csv(index=False).encode(),
                "matched_participants.csv","text/csv", key="exp_match")
        with col2:
            st.markdown("**Field Agreement Summary**")
            st.download_button("⬇️ CSV",
                agreement_df.drop(columns=['Band'],errors='ignore').to_csv(index=False).encode(),
                "field_agreement_summary.csv","text/csv", key="exp_agree")
        with col3:
            st.markdown("**All Discrepancies**")
            st.download_button("⬇️ CSV",
                all_disc_df.to_csv(index=False).encode() if not all_disc_df.empty
                else "No discrepancies".encode(),
                "all_discrepancies.csv","text/csv", key="exp_disc")

        if not unmatched_recorded.empty or not unmatched_duplicate.empty:
            st.markdown("**Unmatched Participants**")
            cu1, cu2 = st.columns(2)
            with cu1:
                if not unmatched_recorded.empty:
                    st.download_button(f"⬇️ Unmatched {label_a}",
                        unmatched_recorded.to_csv(index=False).encode(),
                        f"unmatched_{label_a}.csv","text/csv", key="exp_unm_a")
            with cu2:
                if not unmatched_duplicate.empty:
                    st.download_button(f"⬇️ Unmatched {label_b}",
                        unmatched_duplicate.to_csv(index=False).encode(),
                        f"unmatched_{label_b}.csv","text/csv", key="exp_unm_b")

        st.markdown("<br>")
        st.markdown("**📊 Complete Multi-Sheet Excel Report**")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            used_sheet_names = set()
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            used_sheet_names.add('Summary')
            merged[disp].to_excel(writer, sheet_name='Matched Participants', index=False)
            used_sheet_names.add('Matched Participants')
            agreement_df.drop(columns=['Band'],errors='ignore').to_excel(
                writer, sheet_name='Field Agreement', index=False)
            used_sheet_names.add('Field Agreement')

            # Examiner summary and detailed sheets
            if not examiner_summary_df.empty:
                examiner_summary_df.to_excel(writer, sheet_name='Examiner Summary', index=False)
                used_sheet_names.add('Examiner Summary')
                for exam, ag_df in examiner_agreement_dict.items():
                    if not ag_df.empty:
                        sheet_name = safe_excel_sheet_name(f"Exam Agree {exam}", used_sheet_names)
                        ag_df.to_excel(writer, sheet_name=sheet_name, index=False)
                for exam, disc_df in examiner_discrepancy_dict.items():
                    if not disc_df.empty:
                        sheet_name = safe_excel_sheet_name(f"Exam Disc {exam}", used_sheet_names)
                        disc_df.head(100).to_excel(writer, sheet_name=sheet_name, index=False)

            if not all_disc_df.empty:
                all_disc_df.to_excel(writer, sheet_name='All Discrepancies', index=False)
                used_sheet_names.add('All Discrepancies')
            else:
                pd.DataFrame({'Message':['No discrepancies found']}).to_excel(
                    writer, sheet_name='All Discrepancies', index=False)
                used_sheet_names.add('All Discrepancies')
            low_df2 = agreement_df[agreement_df['Agreement %'] < low_agree_threshold] \
                      if not agreement_df.empty else pd.DataFrame()
            low_df2.drop(columns=['Band'],errors='ignore').to_excel(
                writer, sheet_name=f'Low Agreement (<{low_agree_threshold}%)', index=False)
            used_sheet_names.add(f'Low Agreement (<{low_agree_threshold}%)')
            if not unmatched_recorded.empty:
                sheet_name = safe_excel_sheet_name(f'Unmatched {label_a[:20]}', used_sheet_names)
                unmatched_recorded.to_excel(writer, sheet_name=sheet_name, index=False)
            if not unmatched_duplicate.empty:
                sheet_name = safe_excel_sheet_name(f'Unmatched {label_b[:20]}', used_sheet_names)
                unmatched_duplicate.to_excel(writer, sheet_name=sheet_name, index=False)
            for cat_name, sel_fields in category_selections.items():
                if sel_fields:
                    cat_adf = field_agreement_summary(merged, sel_fields, suffix_a='_Recorded', suffix_b='_Duplicate')
                    if not cat_adf.empty:
                        safe_name = safe_excel_sheet_name(cat_name.replace('/','_').replace(':','')[:28], used_sheet_names)
                        cat_adf.drop(columns=['Band'],errors='ignore').to_excel(
                            writer, sheet_name=safe_name, index=False)

        st.download_button(
            "📥 Download Full Excel Report (All Sheets + Per-Category + Examiner Details)",
            output.getvalue(), "recorded_duplicate_full_report.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="exp_full_excel")

        st.markdown("---")
        st.caption(
            f"Preset: {preset_labels[preset]} · "
            f"{common_count} matched participants · "
            f"{len(filtered_cols)} fields · "
            f"Matching keys: {', '.join(selected_keys)} · "
            f"Date filter: {date_col if date_filter_active else 'None'} · "
            f"Age-group corrections: {len(corrupted_recorded)+len(corrupted_duplicate)}"
        )

# ─────────────────────────────────────────────
# MODULE 4: DATA CLEANER
# ─────────────────────────────────────────────
elif mode == "🧹 Data Cleaner":
    with st.sidebar:
        uploaded = st.file_uploader("Upload CSV to clean", type=["csv"], label_visibility="collapsed", key="data_cleaner_file")
        st.markdown("---")

    st.markdown('<div style="font-family:Playfair Display,serif;font-size:2.1rem;color:#0f172a;">🧹 Data Cleaner</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#64748b;margin-bottom:20px;">Upload a REDCap CSV to merge duplicate households, remove redundant rows, and download a clean analysis-ready file.</div>', unsafe_allow_html=True)

    if not uploaded:
        st.info("📁 Upload your survey or household listing CSV from the sidebar. The cleaner will combine duplicate households using Cluster Code + Household Number when those columns are available.")
        st.stop()

    @st.cache_data
    def load_cleaner_csv(file_bytes):
        return pd.read_csv(BytesIO(file_bytes), low_memory=False)

    try:
        raw_cleaner = load_cleaner_csv(uploaded.getvalue())
    except Exception as exc:
        st.error(f"Could not read the uploaded CSV: {exc}")
        st.stop()

    detected_cleaner = detect_cleaner_columns(raw_cleaner)
    default_key_cols = [c for c in [detected_cleaner.get("cluster"), detected_cleaner.get("household_number")] if c]

    with st.sidebar:
        st.markdown("### Cleaner Settings")
        combine_households = st.checkbox("Combine duplicate households", value=True)
        key_cols = st.multiselect(
            "Household match columns",
            options=list(raw_cleaner.columns),
            default=default_key_cols,
            help="Use Cluster Code + Household Number for the safest household-wise merge.",
        )
        renumber_repeats = st.checkbox("Renumber repeat instances after merge", value=True)
        st.markdown("---")
        st.markdown(f'<div style="font-size:.72rem;color:#64748b;">📊 {len(raw_cleaner)} uploaded rows</div>', unsafe_allow_html=True)

    cleaned_df, cleaner_report = clean_household_redundancy(
        raw_cleaner,
        household_key_cols=key_cols,
        combine_households=combine_households,
        renumber_repeats=renumber_repeats,
    )

    for msg in cleaner_report["warnings"]:
        alert(msg, "o")

    metrics = cleaner_report["metrics"]
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1: kpi("Rows", f"{metrics['Rows Before']:,} -> {metrics['Rows After']:,}", "g")
    with k2: kpi("Households", f"{metrics['Households Before']:,} -> {metrics['Households After']:,}", "p")
    with k3: kpi("Repeat Rows", f"{metrics['Repeated Rows Before']:,} -> {metrics['Repeated Rows After']:,}", "c")
    with k4: kpi("HH Groups Merged", f"{metrics['Household Groups Merged']:,}", "o")
    with k5: kpi("Rows Removed", f"{metrics['Rows Before'] - metrics['Rows After']:,}", "r")

    tab_summary, tab_merges, tab_removed, tab_preview, tab_download = st.tabs([
        "📋 Summary", "🏠 Household Merges", "♻️ Removed Rows", "👀 Preview", "📥 Download"
    ])

    with tab_summary:
        sec("Cleaning Summary")
        summary_df = pd.DataFrame([{"Metric": k, "Value": v} for k, v in metrics.items()])
        st.dataframe(summary_df, hide_index=True, use_container_width=True)

        sec("Detected Columns")
        detected_rows = []
        for label, value in cleaner_report["detected"].items():
            if label == "identity_cols":
                value = ", ".join(value) if value else "Not detected"
            detected_rows.append({"Field": label.replace("_", " ").title(), "Detected Column": value or "Not detected"})
        st.dataframe(pd.DataFrame(detected_rows), hide_index=True, use_container_width=True)
        st.caption("Primary household row is chosen by completion/status, filled fields, number of repeat rows, and latest date. Missing household fields are filled from duplicate records when possible.")

    with tab_merges:
        sec("Households Combined")
        merge_df = cleaner_report["merge_summary"]
        if merge_df.empty:
            alert("✅ No duplicate household groups were detected with the selected match columns.", "g")
        else:
            st.dataframe(merge_df, hide_index=True, use_container_width=True, height=420)
            st.download_button(
                "⬇️ Download household merge report",
                data=merge_df.to_csv(index=False).encode("utf-8-sig"),
                file_name="household_merge_report.csv",
                mime="text/csv",
                use_container_width=True,
            )

    with tab_removed:
        sec("Redundant Rows Removed")
        removed_rows = cleaner_report["removed_rows"]
        if removed_rows.empty:
            alert("✅ No exact duplicate rows or duplicate repeated participant/member rows were removed.", "g")
        else:
            st.caption(f"Showing {min(len(removed_rows), 1000):,} of {len(removed_rows):,} removed rows.")
            st.dataframe(removed_rows.head(1000), use_container_width=True, height=420)
            st.download_button(
                "⬇️ Download removed rows report",
                data=removed_rows.to_csv(index=False).encode("utf-8-sig"),
                file_name="removed_redundant_rows.csv",
                mime="text/csv",
                use_container_width=True,
            )

    with tab_preview:
        sec("Cleaned File Preview")
        st.caption(f"Showing {min(len(cleaned_df), 1000):,} of {len(cleaned_df):,} cleaned rows.")
        st.dataframe(cleaned_df.head(1000), use_container_width=True, height=520)

    with tab_download:
        sec("Clean Uploadable File")
        st.success("Cleaner finished. Download this CSV and upload it into the analysis module.")
        st.download_button(
            "⬇️ Download cleaned uploadable CSV",
            data=cleaned_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="cleaned_uploadable_for_analysis.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.download_button(
            "⬇️ Download cleaning summary CSV",
            data=summary_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="cleaning_summary.csv",
            mime="text/csv",
            use_container_width=True,
        )
# ─────────────────────────────────────────────
# MODULE 5: HOUSEHOLD LISTING
# ─────────────────────────────────────────────
elif mode == "🏘️ Household Listing":

    # ─── HOUSEHOLD LISTING DASHBOARD ───
    with st.sidebar:
        uploaded = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed", key="household_listing_file")
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
        st.stop()

    @st.cache_data
    def load_hh(file_bytes):
        return pd.read_csv(BytesIO(file_bytes), low_memory=False)

    raw = load_hh(uploaded.getvalue())

    ri_col = "Repeat Instrument"
    if ri_col not in raw.columns:
        st.error("❌ CSV must contain a 'Repeat Instrument' column. Re-export from REDCap with labels.")
        st.stop()

    hh_all = raw[raw[ri_col].isna() | (raw[ri_col].astype(str).str.strip() == "")].copy()
    mbr_all = raw[raw[ri_col].astype(str).str.strip() == "Household Member"].copy()

    # Auto-detect columns
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
        st.markdown(f'<div style="font-size:.72rem;color:#64748b;">📊 {len(hh)} households · {len(mbr)} members</div>', unsafe_allow_html=True)

    # ── HEADER ──
    st.markdown(
        '<div style="font-family:Playfair Display,serif;font-size:1.9rem;color:#0f172a;">🏘️ HouseholdListing Analytics Pro</div>',
        unsafe_allow_html=True,
    )
    date_window = ""
    if hh["_date"].notna().any():
        date_window = f"{hh['_date'].min().strftime('%d %b %Y')} – {hh['_date'].max().strftime('%d %b %Y')} ({(hh['_date'].max() - hh['_date'].min()).days + 1} days) · "
    st.markdown(f'<div style="color:#64748b;font-size:.85rem;margin-bottom:20px;">North Delhi Household Listing · {date_window}{datetime.now().strftime("%d %b %Y, %I:%M %p")}</div>', unsafe_allow_html=True)

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

    # ── TABS (10 tabs) ──
    tabs_hh = st.tabs(["📊 Overview", "🗺️ Cluster", "👥 Enumerator", "📈 Progress",
                       "⏱️ Work Hours", "👨‍👩‍👧 Demographics", "🎯 Sampling",
                       "📍 GPS & Tablet", "🔍 Data Quality", "🔎 Drill-down"])

    # ── TAB 0: Overview ──
    with tabs_hh[0]:
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

    # ── TAB 1: Cluster ──
    with tabs_hh[1]:
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

    # ── TAB 2: Enumerator ──
    with tabs_hh[2]:
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

    # ── TAB 3: Progress ──
    with tabs_hh[3]:
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

    # ── TAB 4: Work Hours ──
    with tabs_hh[4]:
        sec("⏱️ Enumerator Work Hours & Day-wise Consistency")
        if not col_enum or hh[col_enum].dropna().empty:
            st.warning("No enumerator column found — cannot compute work hours.")
        elif hh["_date"].notna().sum() == 0:
            st.warning("No valid listing dates with timestamps — cannot compute work hours.")
        else:
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
                    k1, k2, k3 = st.columns(3)
                    with k1: kpi("Enumerator-Days", f"{len(daily_log)}", "")
                    with k2: kpi("Enumerators", f"{daily_log['Enumerator'].nunique()}", "g")
                    with k3: kpi("Total Households", f"{daily_log['Households'].sum()}", "p")

                if has_time:
                    sec("📅 Daily Work Session Timeline")
                    tl = daily_log.copy()
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

                sec("📋 Daily Timing Log")
                display_cols = ["Enumerator", "Date", "First Time", "Last Time",
                                "Work Duration (hrs)", "Households", "Avg Time/HH (min)"]
                if not has_time:
                    display_cols = ["Enumerator", "Date", "Households"]
                display_log = daily_log[display_cols].sort_values(["Date", "Enumerator"])
                st.dataframe(display_log, use_container_width=True, hide_index=True)

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
                    sec("📥 Download Daily Counts")
                    csv_log = display_log.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "📥 Download Daily Household Counts CSV",
                        csv_log, "enumerator_daily_counts.csv", "text/csv",
                        use_container_width=True
                    )

    # ── TAB 5: Demographics ──
    with tabs_hh[5]:
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

    # ── TAB 6: Sampling ──
    with tabs_hh[6]:
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

    # ── TAB 7: GPS & Tablet Location ──
    with tabs_hh[7]:
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

    # ── TAB 8: Data Quality ──
    with tabs_hh[8]:
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

    # ── TAB 9: Drill-down ──
    with tabs_hh[9]:
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

# ─── FOOTER ───
st.markdown("---")
st.markdown(
    f'<div style="color:#94a3b8;font-size:.75rem;text-align:center;padding:10px 0;">'
    f'Super Dashboard · All Modules Integrated · '
    f'Generated {datetime.now().strftime("%d %b %Y %H:%M")}'
    f'</div>',
    unsafe_allow_html=True,
)
