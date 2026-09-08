import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Recorded vs Duplicate Examiner Comparator",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .main { background-color: #f0f4f8; }
    .block-container { padding-top: 1.5rem; }
    .metric-card {
        background: white; border-radius: 14px; padding: 1.2rem 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06); border-left: 4px solid #3b82f6; text-align: center;
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
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# AGE GROUP CORRUPTION FIX
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
    """Make REDCap raw and label exports use the same internal column names."""
    column_map = {
        'Repeat Instrument': 'repeat_instrument',
        'Repeat Instance': 'repeat_instance',
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

# ─────────────────────────────────────────────
# DATE FILTER HELPERS
# ─────────────────────────────────────────────
def detect_date_columns(df):
    return [c for c in df.columns if 'date' in c.lower()]

def parse_date_column(series):
    return pd.to_datetime(series, errors='coerce')

# ─────────────────────────────────────────────
# FIELD CATEGORY DEFINITIONS
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
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

def extract_participants(df):
    hh_cols = [c for c in ['record_id', 'cluster_code', 'household_number'] if c in df.columns]
    if 'repeat_instrument' in df.columns:
        repeat_values = df['repeat_instrument'].astype(str).str.strip().str.lower()
        hh = df[df['repeat_instrument'].isna()][hh_cols].drop_duplicates('record_id')
        pt = df[repeat_values == 'participant'].copy()
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
    return result

def compare_fields(merged, suffix_a='_Recorded', suffix_b='_Duplicate'):
    exclude = {
        'record_id','repeat_instrument','repeat_instance','_source',
        'examiner_number','cluster_code','household_number',
        'age_(years)','age_group','gender','consent_date','signature','complete?','complete?.1'
    }
    base_cols = [c.replace(suffix_a, '') for c in merged.columns if c.endswith(suffix_a)]
    return [c for c in base_cols if c not in exclude]

def field_agreement_summary(merged, compare_cols, suffix_a='_Recorded', suffix_b='_Duplicate'):
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
                                 suffix_a='_Recorded', suffix_b='_Duplicate', idx=0):
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
            f'{label_a}': va_str,
            f'{label_b}': vb_str,
            'Status': status
        })
    return pd.DataFrame(records)

def make_label(row, keys):
    parts = []
    for k in keys:
        if k in row.index and pd.notna(row[k]):
            parts.append(f"{k.replace('_',' ').title()}: {row[k]}")
    return ' | '.join(parts) if parts else f"Row #{row.name}"

def get_unmatched(pt, other_pt, keys):
    if not all(k in pt.columns and k in other_pt.columns for k in keys):
        return pd.DataFrame()
    pt_keys  = pt[keys].apply(tuple, axis=1)
    mrg_keys = other_pt[keys].apply(tuple, axis=1)
    mask = ~pt_keys.isin(set(mrg_keys))
    extra = [c for c in ['age_group'] if c in pt.columns and c not in keys]
    cols = list(dict.fromkeys(['record_id'] + keys + extra))
    return pt[mask][cols].copy()

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

# ─────────────────────────────────────────────
# NEW: AGGREGATED EXAMINER REPORTS (single-file version)
# ─────────────────────────────────────────────
def build_examiner_aggregated_reports(merged, compare_cols, selected_keys,
                                      label_recorded, label_duplicate,
                                      low_agree_threshold,
                                      suffix_a='_Recorded', suffix_b='_Duplicate'):
    """
    For each recorded examiner (grouped by examiner_number_Recorded),
    compute aggregated metrics against all duplicate records.
    Returns:
        summary_df: DataFrame with one row per recorded examiner
        agreement_dict: dict {examiner: agreement_df}
        discrepancies_dict: dict {examiner: disc_df}
    """
    summary_records = []
    agreement_dict = {}
    discrepancies_dict = {}

    if 'examiner_number_Recorded' not in merged.columns:
        return pd.DataFrame(), {}, {}

    for exam, group in merged.groupby('examiner_number_Recorded', dropna=False):
        group = group.reset_index(drop=True)
        # Field agreement for this examiner vs all duplicate
        ag_df = field_agreement_summary(group, compare_cols,
                                        suffix_a=suffix_a, suffix_b=suffix_b)
        agreement_dict[exam] = ag_df

        # Build discrepancies for this examiner
        disc_list = []
        missing_count = 0
        for i in range(len(group)):
            comp = participant_level_comparison(group, compare_cols,
                                                label_recorded, label_duplicate,
                                                suffix_a=suffix_a, suffix_b=suffix_b,
                                                idx=i)
            if comp.empty:
                continue
            missing_count += int((comp['Status'] == 'Missing in one').sum())
            disc = comp[comp['Status'].astype(str).str.startswith('Disagree')].copy()
            if disc.empty:
                continue
            disc.insert(0, 'Participant #', i + 1)
            disc.insert(1, f'Record ID ({label_recorded})', group.iloc[i].get('record_id_Recorded', ''))
            disc.insert(2, f'Record ID ({label_duplicate})', group.iloc[i].get('record_id_Duplicate', ''))
            parts = [f"{k.replace('_',' ').title()}: {group.iloc[i][k]}"
                     for k in selected_keys if k in group.columns and pd.notna(group.iloc[i][k])]
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

    summary_df = pd.DataFrame(summary_records) if summary_records else pd.DataFrame()
    if not summary_df.empty:
        summary_df = summary_df.sort_values(['Avg Agreement %', 'Discrepancies'],
                                            ascending=[True, False])
    return summary_df, agreement_dict, discrepancies_dict

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/tooth.png", width=56)
    st.title("🦷 Recorded vs Duplicate")
    st.caption("Compare recorded (with examiner #) vs duplicate (without) within one file")
    st.divider()

    st.markdown("### 📂 Upload Single CSV")
    file = st.file_uploader("REDCap label export (CSV)", type=['csv'], key='single_file')

    label_a = st.text_input("Name for Recorded group", value="Recorded (with examiner)")
    label_b = st.text_input("Name for Duplicate group", value="Duplicate (without examiner)")

    st.divider()
    st.markdown("### ⚙️ Matching Parameters")
    use_record_id  = st.checkbox("Record ID", value=True)
    use_cluster    = st.checkbox("Cluster Code", value=False)
    use_household  = st.checkbox("Household Number", value=False)
    use_age        = st.checkbox("Age (Years)", value=False)
    use_age_group  = st.checkbox("Age Group", value=False)
    use_gender     = st.checkbox("Gender", value=False)

    st.divider()
    st.markdown("### 🔍 Duplicate Examiner Selection")
    st.caption("Define which examiner numbers (or missing values) should be considered 'duplicate'.")
    st.caption("(Will appear after file is loaded)")

    st.divider()
    st.markdown("### 🔍 Agreement Threshold")
    low_agree_threshold = st.slider("Flag fields below (%)", 0, 100, 60)

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
st.markdown("## 🦷 Recorded vs Duplicate Examination Comparison")
st.caption("Upload a single REDCap export; rows with an examiner number are 'recorded', rows without are 'duplicate'.")

if not file:
    st.info("👈 Upload a CSV file from the sidebar to begin.")
    c1, c2, c3 = st.columns(3)
    for col, step, desc in [(c1,"1","Upload CSV"),(c2,"2","Auto-split by examiner number"),(c3,"3","View comparison results")]:
        with col:
            st.markdown(f"<div style='border:2px dashed #cbd5e1;border-radius:14px;padding:2rem;text-align:center;background:white'>"
                        f"<h3>📤 Step {step}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
    st.stop()

# ─── LOAD ───
df = normalize_export_columns(pd.read_csv(file))

# ─── EXTRACT PARTICIPANT DATA ───
pt_all = extract_participants(df)

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

# ── NEW: Aggregated examiner reports ──
examiner_summary_df, examiner_agreement_dict, examiner_discrepancy_dict = build_examiner_aggregated_reports(
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
# TABS (added new "Examiner Summary" tab)
# ─────────────────────────────────────────────
tab_summary, tab_examiner, tab_matched, tab_unmatched, tab_field, tab_deepdive, tab_discrep, tab_export = st.tabs([
    "📋 Summary", "👤 Examiner Summary", "👥 Matched", "⚠️ Unmatched",
    "📊 Field Agreement", "🔍 Deep Dive", "🚨 Discrepancies", "📥 Export"
])

# ── SUMMARY TAB (unchanged) ──
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

# ── EXAMINER SUMMARY TAB (NEW) ──
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

        # Show metrics for that examiner
        row = examiner_summary_df[examiner_summary_df[f'Examiner ({label_a})'] == selected_exam]
        if not row.empty:
            r = row.iloc[0]
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Matched Participants", int(r['Matched Participants']))
            with c2: st.metric("Avg Agreement", f"{r['Avg Agreement %']:.1f}%")
            with c3: st.metric("Low Agreement Fields", int(r[f'Fields < {low_agree_threshold}%']))
            with c4: st.metric("Discrepancies", int(r['Discrepancies']))

        # Field agreement table
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

        # Discrepancies table
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