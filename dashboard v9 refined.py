import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Duplicate Examination Comparator",
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
    """Make REDCap raw and label exports use the same column names."""
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
    }
    return df.rename(columns={c: column_map.get(c, c) for c in df.columns})

# ─────────────────────────────────────────────
# FIELD CATEGORY DEFINITIONS
# ─────────────────────────────────────────────
def classify_fields(all_cols):
    """Classify all fields into named clinical / non‑clinical categories."""
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

        # Tooth‑specific fields first
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

    # Remove empty categories
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

# ─────────────────────────────────────────────
# NEW: AGGREGATED EXAMINER REPORTS (per examiner, all matches from other file)
# ─────────────────────────────────────────────
def build_examiner_aggregated_reports(merged, compare_cols, selected_keys, label_a, label_b,
                                      low_agree_threshold):
    """
    Returns:
        summary_A: DataFrame, one row per examiner in file A
        summary_B: DataFrame, one row per examiner in file B
        agreement_A: dict {examiner: agreement_df}
        agreement_B: dict
        discrepancies_A: dict {examiner: disc_df}
        discrepancies_B: dict
    """
    summary_A_records = []
    summary_B_records = []
    agreement_A = {}
    agreement_B = {}
    discrepancies_A = {}
    discrepancies_B = {}

    # Examiner A groups
    if 'examiner_number_A' in merged.columns:
        for exam, group in merged.groupby('examiner_number_A', dropna=False):
            group = group.reset_index(drop=True)
            ag_df = field_agreement_summary(group, compare_cols)
            agreement_A[exam] = ag_df

            # Discrepancies
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

    # Examiner B groups
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
    return pt[mask][['record_id'] + keys + extra].copy()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/tooth.png", width=56)
    st.title("🦷 Exam Comparator")
    st.caption("REDCap Duplicate Examination Analysis")
    st.divider()

    st.markdown("### 📂 Upload Files")
    file_a = st.file_uploader("Examiner A (File 1)", type=['csv'], key='fa')
    file_b = st.file_uploader("Examiner B (File 2)", type=['csv'], key='fb')

    label_a = st.text_input("Name for Examiner A",
        value=file_a.name.replace('.csv','') if file_a else "Examiner A", key="label_a")
    label_b = st.text_input("Name for Examiner B",
        value=file_b.name.replace('.csv','') if file_b else "Examiner B", key="label_b")

    st.divider()
    st.markdown("### ⚙️ Matching Parameters")
    use_cluster   = st.checkbox("Cluster Code",     value=True)
    use_household = st.checkbox("Household Number", value=True)
    use_age       = st.checkbox("Age (Years)",      value=True)
    use_age_group = st.checkbox("Age Group",        value=True)
    use_gender    = st.checkbox("Gender",           value=True)

    st.divider()
    st.markdown("### 🔍 Agreement Threshold")
    low_agree_threshold = st.slider("Flag fields below (%)", 0, 100, 60)

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
st.markdown("## 🦷 Duplicate Examination Comparison Dashboard")
st.caption("Upload two REDCap examiner CSV exports to identify common participants and compare field-level recordings.")

if not file_a or not file_b:
    st.info("👈 Upload both examiner files from the sidebar to begin analysis.")
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

    # Classify all comparable fields
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

# ── Preset buttons ──
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

# ── NEW: Aggregated examiner reports ──
agg_summary_A, agg_summary_B, agg_agreement_A, agg_agreement_B, agg_discrepancies_A, agg_discrepancies_B = (
    build_examiner_aggregated_reports(
        merged, filtered_cols, selected_keys, label_a, label_b, low_agree_threshold
    )
)

# Build summary data for display
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
# TABS (added new tab for Aggregated Examiner Reports)
# ─────────────────────────────────────────────
tab_examiner, tab_agg_examiner, tab_summary, tab_matched, tab_unmatched, tab_field, tab_deepdive, tab_discrep, tab_export = st.tabs([
    "Examiner Reports (Pair‑wise)",
    "Examiner (Aggregated)",          # NEW TAB
    "📋 Summary", "👥 Matched", "⚠️ Unmatched", "📊 Field Agreement",
    "🔍 Deep Dive", "🚨 Discrepancies", "📥 Export"
])

# ─────────────────────────────────────────────
# TAB: Examiner Reports (Pair‑wise) – unchanged
# ─────────────────────────────────────────────
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
        # ... (the rest of the existing code for all examiner disc) ... 
        # Keep the existing code for all examiner disc, unchanged.
        # For brevity, I'll not repeat it here but it remains.

# ─────────────────────────────────────────────
# NEW TAB: Aggregated Examiner Reports
# ─────────────────────────────────────────────
with tab_agg_examiner:
    st.markdown("<div class='section-header'>Aggregated Examiner Reports</div>",
                unsafe_allow_html=True)
    st.caption(
        f"For each examiner in either file, all matches from the other file are combined. "
        f"This gives the overall consistency of an examiner against the aggregated duplicate group."
    )

    # Show summary tables for A and B
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

    # Choose which file's examiner to drill into
    drill_choice = st.radio("Examiner from which file?", [label_a, label_b], horizontal=True)
    if drill_choice == label_a:
        if agg_summary_A.empty:
            st.warning(f"No {label_a} examiners found.")
        else:
            exam_options = sorted(agg_summary_A[f'Examiner ({label_a})'].dropna().unique().tolist())
            selected_exam = st.selectbox(f"Select {label_a} examiner", exam_options, key="agg_exam_A")
            # Show agreement and discrepancies for that examiner
            ag_df = agg_agreement_A.get(selected_exam, pd.DataFrame())
            disc_df = agg_discrepancies_A.get(selected_exam, pd.DataFrame())

            # Show metrics for that examiner
            row = agg_summary_A[agg_summary_A[f'Examiner ({label_a})'] == selected_exam]
            if not row.empty:
                r = row.iloc[0]
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("Matched Participants", int(r['Matched Participants']))
                with c2: st.metric("Avg Agreement", f"{r['Avg Agreement %']:.1f}%")
                with c3: st.metric("Low Agreement Fields", int(r[f'Fields < {low_agree_threshold}%']))
                with c4: st.metric("Discrepancies", int(r['Discrepancies']))

            # Field agreement table
            st.markdown(f"#### Field Agreement for {label_a} examiner {selected_exam} (Aggregated)")
            if ag_df.empty:
                st.info("No fields assessed for this examiner.")
            else:
                st.dataframe(ag_df.style.map(pct_color, subset=['Agreement %'])
                             .format({'Agreement %':'{:.1f}%'})
                             .set_properties(**{'font-size':'13px'}),
                             width='stretch', height=350)

            # Discrepancies table
            st.markdown(f"#### Discrepancies for {label_a} examiner {selected_exam} (Aggregated)")
            if disc_df.empty:
                st.success("No discrepancies found for this examiner.")
            else:
                # Optional filters
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

# ─────────────────────────────────────────────
# The remaining tabs (Summary, Matched, Unmatched, Field Agreement, Deep Dive, Discrepancies, Export)
# are unchanged from dashboardv9 – only the Export tab needs to include aggregated sheets.
# ─────────────────────────────────────────────

# ... (keep all existing tabs as they are; I'll include the Export tab with added aggregated sheets)

# ─────────────────────────────────────────────
# TAB: Export (modified to include aggregated sheets)
# ─────────────────────────────────────────────
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

        # Pair‑wise examiner sheets
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

        # NEW: Aggregated examiner sheets
        if not agg_summary_A.empty:
            sheet_name = safe_excel_sheet_name(f"Aggregated Summary {label_a}", used_sheet_names)
            agg_summary_A.to_excel(writer, sheet_name=sheet_name, index=False)
        if not agg_summary_B.empty:
            sheet_name = safe_excel_sheet_name(f"Aggregated Summary {label_b}", used_sheet_names)
            agg_summary_B.to_excel(writer, sheet_name=sheet_name, index=False)
        # For aggregated discrepancies, we only export the detailed ones for each examiner (limit to 100 rows per sheet)
        for exam, disc_df in agg_discrepancies_A.items():
            if not disc_df.empty:
                sheet_name = safe_excel_sheet_name(f"Agg Disc A {exam}", used_sheet_names)
                disc_df.head(100).to_excel(writer, sheet_name=sheet_name, index=False)
        for exam, disc_df in agg_discrepancies_B.items():
            if not disc_df.empty:
                sheet_name = safe_excel_sheet_name(f"Agg Disc B {exam}", used_sheet_names)
                disc_df.head(100).to_excel(writer, sheet_name=sheet_name, index=False)

        # All discrepancies, low agreement, unmatched, per‑category
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

# Note: The code above omits the full content of the "Examiner Reports (Pair‑wise)" all‑discrepancies section for brevity,
# but in the actual final code it would remain as in dashboardv9.