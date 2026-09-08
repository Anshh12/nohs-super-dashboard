# Super Dashboard Complete User and Results Guide

**Audience:** survey managers, data-quality officers, examiners, analysts, and non-technical users  
**Purpose:** explain how to operate the dashboard, how every result is calculated, and how to write a defensible KPI report.  
**Data format:** REDCap CSV label exports with household and participant/repeat rows.  
**Important:** every number depends on the uploaded file, selected filters, matching keys, preset, and selected fields.

## Contents

1. [Quick Start](#quick-start)
2. [Dashboard Modules](#dashboard-modules)
3. [How to Run a Comparison](#how-to-run-a-comparison)
4. [How to Read the Main KPIs](#how-to-read-the-main-kpis)
5. [Results and Agreement Calculations](#6-agreement-calculations)
6. [Examiner Reports](#7-examiner-reports)
7. [Deep Dive and Discrepancies](#8-deep-dive)
8. [Field Dictionary](#18-field-names-and-categories)
9. [Data Cleaner](#12-data-cleaner)
10. [Troubleshooting](#troubleshooting)
11. [Professional Reporting Template](#professional-reporting-template)

## Quick Start

### Before uploading

1. Export the REDCap data as a CSV label export.
2. Keep the `Record ID`, `Repeat Instrument`, and `Repeat Instance` columns.
3. Confirm that participant rows are labelled `Participant`.
4. Keep the examiner number and consent date columns if examiner or date analysis is required.
5. Do not manually delete household rows before using the Data Cleaner; they provide the household-to-participant link.

### Recommended order of work

1. Open **Data Cleaner** and upload the raw CSV.
2. Review duplicate household groups, removed rows, and record-ID mapping.
3. Download the cleaned uploadable CSV.
4. Upload the cleaned CSV into the relevant analysis module.
5. Set the date range and examiner filters.
6. Choose matching keys.
7. Review matched and unmatched participants.
8. Review `Overall Agreement %`, `Average Field Agreement %`, `Fields With Usable Data`, and `Data Points Assessed` together.
9. Inspect the lowest-agreement fields.
10. Use Deep Dive to investigate individual participant pairs.
11. Export the summary and document the filters used.

### One-sentence interpretation rule

Never report an agreement percentage by itself. Always report the matched participants, selected keys, selected fields, usable fields, data points, date range, and examiner selection beside it.

## Dashboard Modules

### Oral Health Survey

Use this module for descriptive survey and clinical analysis. It reports demographics, household characteristics, oral hygiene, dental services, DMFT, periodontal findings, lesions, prosthetics, treatment needs, examiner performance, cluster performance, raw data, and work-hour patterns.

### Duplicate Comparator (Two Files)

Use this when two separate examiner/calibration CSV files must be compared. The dashboard matches participant rows from File A and File B using the selected keys and calculates field-level and examiner-level agreement.

### Recorded vs Duplicate (Single File)

Use this when Recorded and Duplicate observations are stored in one CSV. The dashboard splits rows using examiner number, matches the two groups, and summarizes each Recorded examiner against the Duplicate group.

### Data Cleaner

Use this before analysis when household records may have been created more than once, exact duplicate rows exist, or repeat participant rows need reassignment. The cleaner produces a clean uploadable CSV and audit reports.

### Household Listing

Use this for household-level progress, enumerator activity, member demographics, sampling, GPS completeness, data-quality checks, and household drill-down.

## 1. What This Dashboard Does

The dashboard compares oral-health records, summarizes examiner consistency, analyzes survey data, and helps identify duplicate or redundant household records.

It has five main modules:

1. Oral Health Survey
2. Duplicate Comparator (Two Files)
3. Recorded vs Duplicate (Single File)
4. Data Cleaner
5. Household Listing

All results are calculated only from the uploaded data and the active filters.

## 2. Important Terms

### Household row

A row where `Repeat Instrument` is blank. It contains household-level information such as cluster, household number, water source, assets, or household status.

### Participant row

A row where `Repeat Instrument` is `Participant`. It contains person-level information such as age, gender, consent date, examiner, and clinical findings.

### Record ID

The REDCap identifier connecting a household row with its participant rows.

### Matching key

The columns used to decide whether two records represent the same person. Examples include Record ID, cluster, household number, age, age group, or gender.

### Comparable field

A data column that exists in both sides of a comparison and is not an administrative or matching field. Administrative fields such as Record ID, examiner number, consent date, and matching keys are excluded from clinical agreement calculations.

## 3. Date Filters

Date filters use the selected date column and compare calendar dates. Time of day does not change whether a record is included.

For example, a range from 1 September through 3 September includes records on both 1 September and 3 September.

When an active date filter is applied:

- Records inside the selected date range are included.
- Records outside the range are excluded.
- Records with missing or invalid dates are excluded.
- Matching and summaries are calculated after filtering.

In the single-file comparator, the same date rule is applied to both Recorded and Duplicate groups.

In the Data Cleaner, the date filter controls the review view. The cleaning operation itself is intended to preserve the uploaded dataset unless the cleaner explicitly says otherwise.

## 4. Examiner Filters

In the oral-health modules, examiner values come from the Examiner Number column.

In the household-listing module, the equivalent field is Enumerator. It is displayed as Enumerator unless the uploaded column is clearly named as an examiner field.

Blank examiner values are treated separately. In the single-file comparator, they can be included as the Duplicate group using the Include Empty Examiner option.

## 5. How Matching Works

### Two-file comparator

The dashboard creates one participant table from each uploaded file and matches rows using the selected matching keys.

A participant is matched only when every selected key has the same value on both sides.

The result is an inner match:

- Matched participants appear in the Matched tab.
- Participants found only in file A appear in Unmatched A.
- Participants found only in file B appear in Unmatched B.

### Single-file comparator

The uploaded file is split into:

- Recorded: rows with a selected examiner number.
- Duplicate: rows with a blank examiner number or examiner numbers selected as duplicates.

The two groups are then matched using the selected keys.

## 6. Agreement Calculations

The dashboard reports agreement at three different levels. These should not be confused.

### Field-level agreement

For one field:

```text
Field Agreement % = Agreeing paired values / Assessable paired values × 100
```

Only rows where both sides have a value are assessable for that field. Missing values on both sides are not treated as agreement evidence.

Example:

- 80 participants have values on both sides.
- 72 values agree.
- Field agreement = 72 / 80 × 100 = 90%.

The Field Agreement table shows:

- `Field`: variable name.
- `Assessed`: number of participant pairs with values on both sides.
- `Agree`: number of equal values.
- `Disagree`: number of different values.
- `Agreement %`: agreement for that field.

### Average Field Agreement

This is the simple average of the percentages of all assessable fields:

```text
Average Field Agreement = sum of field agreement percentages / number of assessable fields
```

Every field has equal weight, even if one field has 10 assessable participants and another has 100.

This is a field-level or macro average.

### Overall Agreement

This is the observation-weighted agreement:

```text
Overall Agreement % = total agreeing observations across all fields /
                     total assessable observations across all fields × 100
```

Fields with more assessable participant pairs contribute more to this value.

This is usually the better measure when the user wants one overall percentage for all recorded field comparisons.

### Fields Selected

The number of fields selected by the current preset and manual field selections.

### Fields With Usable Data

The number of selected fields that have at least one participant pair with a value on both sides.

A selected field with no complete value pair is not counted here. This does **not** mean that the field was clinically assessed; it only means that the dashboard found usable data for comparison.

Example:

```text
Fields Selected = 100
Fields With Usable Data = 72
```

This means 100 variables were requested, but only 72 contained at least one usable Recorded-versus-Duplicate or A-versus-B comparison. The other 28 fields were blank on one or both sides for every matched participant.

### Data Points Assessed

The total number of field-participant observations used in the agreement calculation.

For example, 10 fields with usable data across 50 participant pairs could produce up to 500 data points, although missing values may reduce that total.

## 7. Examiner Reports

### Pair-wise examiner report

The two-file comparator groups matched participants by the examiner number on both files.

For each examiner pair it reports:

- Matched Participants: matched rows in that examiner pair.
- Fields Selected: fields included in the comparison.
- Fields With Usable Data: selected fields with usable paired values.
- Data Points Assessed: total usable field values across the pair.
- Avg Agreement %: simple average across fields.
- Overall Agreement %: observation-weighted agreement.
- Min Agreement %: lowest field-level agreement.
- Fields below threshold: number of fields below the chosen threshold.
- Discrepancies: field-level disagreements.
- Missing in One: comparisons where exactly one side contains a value.

### Aggregated examiner report

The aggregated report groups all matched participants belonging to one examiner in a file, regardless of the examiner number on the other side.

It is useful for judging one examiner against the complete duplicate group, but it is not a pair-specific result.

### Single-file examiner report

The single-file report groups matched pairs by Recorded examiner. The Duplicate side is treated as the comparison group defined in the sidebar.

## 8. Deep Dive

Deep Dive displays one matched participant pair at a time.

It shows:

- Fields Compared: fields with comparison columns available for that pair.
- Agree: values are equal on both sides.
- Disagree: both sides have values but the values differ.
- Missing: one side has a value and the other side is blank.

The table shows the value from each side and the status for every selected field.

The chart summarizes the same rows. Filtering the table to Disagree, Agree, or Missing changes the displayed table only; it does not change the underlying agreement calculation.

If the clinical preset produces no fields for a particular file, the dashboard falls back to all comparable fields so Deep Dive remains usable. The fallback is shown in an information message.

## 9. Discrepancies

A discrepancy is a field where both sides contain values and the values are different.

Discrepancies are counted at field level, not participant level.

Therefore:

- One participant can contribute several discrepancies.
- A participant with no disagreements is not listed.
- Missing values are reported separately and are not counted as disagreements.

## 10. Agreement Threshold

The threshold is a warning level, not a deletion rule.

For example, with a threshold of 60%:

- A field at 59.9% is flagged.
- A field at 60.0% is not below the threshold.
- No participant or field is automatically removed because of the threshold.

## 11. Age-Group Correction

Some spreadsheet exports convert age groups such as `12-15` into date-like text such as `Dec-15`.

The dashboard normalizes known corrupted values before matching and comparison. The correction is displayed in the warning banner and summary report.

This correction changes the representation of the age group; it does not create new participants.

## 12. Data Cleaner

The cleaner is designed to produce an uploadable REDCap-style CSV while preserving legitimate participant rows.

### Household merge rule

The default physical household identity is:

```text
Cluster Code + Household Number
```

Both values must be present. Rows with incomplete keys are not automatically merged with unrelated households.

### Duplicate household records

If two household records have the same complete cluster and household number:

1. The dashboard identifies the duplicate group.
2. It chooses a primary household row using completion/status, populated fields, repeat-row count, date, and file order.
3. It keeps one household row.
4. It reassigns participant rows from secondary record IDs to the primary record ID.
5. It removes only genuinely redundant repeated rows.

Four legitimate participants under two duplicate household record IDs should remain four participants after consolidation.

### Exact duplicate rows

Rows are exact duplicates only when all uploaded columns match an earlier row. These rows may be removed and are listed in the removal report.

### Repeat-row redundancy

Repeated participant rows are compared after household record IDs are consolidated. Repeat instance number and administrative household keys are excluded from the redundancy comparison where appropriate.

### Cleaner audit outputs

The cleaner reports:

- Cleaned uploadable CSV.
- Household merge audit.
- Removed redundancy report.
- Record ID mapping.
- Reassigned repeat rows.
- Conflicting household fields.
- Summary metrics.

## 13. Household Listing Results

The Household Listing module counts household rows separately from member rows.

Common results include:

- Households: number of household-level rows after filters.
- Members: member repeat rows linked to the filtered household IDs.
- Completion percentage: completed household rows divided by filtered household rows.
- GPS percentage: households with captured latitude divided by filtered households.
- Substitution percentage: substituted households divided by filtered households.
- Average household size: member rows divided by household rows.

Members remain synchronized with the selected households, so a member is not counted when its parent household is outside the active filter.

## 14. How to Read Results Safely

Use these checks before drawing conclusions:

1. Confirm the active date range.
2. Confirm the selected examiner or enumerator values.
3. Check the matching keys used.
4. Compare Fields Selected with Fields With Usable Data.
5. Check Data Points Assessed before comparing agreement percentages.
6. Use Overall Agreement for a weighted overall result.
7. Use Average Field Agreement when every field should have equal influence.
8. Review Missing in One separately from Disagree.
9. Inspect the Deep Dive for participant-level context.
10. Review unmatched participants before interpreting totals.

A high average agreement with very few data points may be unstable. A low average agreement may be caused by a small number of fields with poor agreement, even when most fields perform well.

## 15. Recommended Reporting Language

Use wording such as:

> Among the matched participant pairs, 42 fields were selected. Thirty-eight fields had assessable paired values, producing 2,410 assessable observations. The average field agreement was 86.4%, while the observation-weighted overall agreement was 89.1%.

Avoid saying only:

> Agreement was 86.4%.

That sentence does not explain whether the value is a field average or a weighted overall result.

## 16. Reading the Examiner Summary Screenshot

The screenshot contains an aggregated examiner summary. Each row represents one examiner from the selected file.

### Examiner (Calibration)

The examiner number or label assigned to the recorded/calibration records. It is not an agreement score. It is the grouping variable used to calculate the row.

### Matched Participants

The number of participant pairs assigned to that examiner group after:

1. Upload filtering.
2. Recorded/duplicate group splitting.
3. Date filtering.
4. Examiner filtering.
5. Matching on the selected keys.

It is not the number of all participants originally uploaded, and it is not the number of fields.

### Avg Agreement %

The simple average of the field-level agreement percentages for that examiner.

Example:

```text
Field A = 100%
Field B = 80%
Field C = 60%
Avg Agreement = (100 + 80 + 60) / 3 = 80%
```

Every assessable field has equal weight in this KPI. A field assessed on 5 participants has the same influence as a field assessed on 100 participants.

This is useful when the question is:

> How consistently did the examiner perform across the selected variables?

It can be misleading when fields have very different amounts of usable data.

### Overall Agreement %

This is the weighted KPI added to the current reports. It gives every assessable field-participant observation equal weight.

```text
Overall Agreement = total Agree values / total Assessed values × 100
```

Example:

```text
Field A: 90 agrees out of 100 = 90%
Field B: 1 agrees out of 2 = 50%

Avg Agreement = (90% + 50%) / 2 = 70%
Overall Agreement = (90 + 1) / (100 + 2) × 100 = 89.2%
```

Use this KPI when the question is:

> What percentage of all usable recorded answers agrees with the comparison answers?

### Discrepancies

The number of field-level disagreements for the examiner group.

It is calculated as the number of rows where:

- The field has a value on both sides.
- The two values are not equal.

One participant can create multiple discrepancies. Therefore, `Discrepancies` can be larger than `Matched Participants`.

Example:

```text
10 matched participants
3 different fields for participant 1
2 different fields for participant 2
Discrepancies = 5
```

Discrepancies do not include cases where both sides are blank. They also do not include `Missing in One`; that is reported separately.

### Missing in One

The number of selected field comparisons where exactly one side has a value.

Examples:

- Recorded value = `Yes`, Duplicate value = blank.
- Recorded value = blank, Duplicate value = `No`.

Missing values on both sides are not counted as agreement, disagreement, or Missing in One.

## 17. Which KPI Should I Use?

| Question | KPI to use | Reason |
|---|---|---|
| How many people were successfully paired? | Matched Participants | Counts matched participant pairs. |
| How many variables were included? | Fields Selected | Shows the requested comparison scope. |
| How many variables actually had usable data? | Fields With Usable Data | Excludes selected fields with no paired values. |
| How much usable comparison data was analyzed? | Data Points Assessed | Counts all field-participant observations. |
| Did the examiner perform consistently across fields? | Avg Agreement % | Gives every field equal weight. |
| What percentage of all usable answers matched? | Overall Agreement % | Weights each usable observation equally. |
| Which variables need attention? | Field Agreement table | Sort by lowest Agreement %. |
| How many field answers differ? | Discrepancies | Counts disagreement cells, not people. |
| How much data is incomplete on one side? | Missing in One | Separates missingness from disagreement. |
| Why does one person have a problem? | Deep Dive | Shows both values and status for one matched pair. |

For quality-control reporting, use `Overall Agreement %` as the headline KPI and include `Avg Agreement %`, `Fields With Usable Data`, and `Data Points Assessed` beside it.

## 18. Field Names and Categories

The dashboard groups raw REDCap columns into categories. The category is for navigation; the original field name remains the source variable.

### Demographics

Typical fields:

- `age_(years)`: numeric age in years.
- `age_group`: REDCap age band such as `4-6`, `12-15`, or `35-44`.
- `gender`: recorded gender.
- `education`: education category.
- `occupation`: occupation category.
- `consent_date`: date/time of participant consent.
- `examiner_number`: examiner assigned to the participant.
- `record_id`: REDCap household/person link.
- `cluster_code`: geographic or sampling cluster.
- `household_number`: household identifier within the cluster.

These fields are normally used for filtering or matching and are excluded from clinical agreement fields.

### Tooth Status

Fields containing `Tooth <number> - status` describe the state of a specific tooth.

Common values include:

- `Sound`: no recorded caries or relevant defect.
- `Coronal caries`: caries on the crown.
- `Root caries`: caries on the root.
- `Both coronal and root caries`: both sites affected.
- `Filled with caries`: filled tooth with recurrent caries.
- `Filled no caries`: filled tooth without current caries.
- `Missing due to caries`: missing because of caries.
- `Unerupted`: tooth has not erupted.
- `Not recorded`: no valid observation recorded.

Primary teeth are baby teeth. Permanent teeth are adult teeth. The exact tooth number is part of the field name.

### Bleeding

Fields containing `bleeding` record gingival bleeding for a tooth.

Typical values:

- `Bleeding`
- `No bleeding`
- `Not recorded`

### Pocket Depth

Fields containing `Pocket` record periodontal probing depth.

Typical values:

- `No pocket`
- `Pocket of 4-5 mm`
- `Pocket 6 mm or more`
- `Not recorded`

### Opacity / MIH / DMH

Fields containing `opacity` or hypomineralization terms describe enamel defects or molar hypomineralization.

Typical values include `Normal`, `demarcated opacity`, `diffuse opacity`, `other defects`, and `Not recorded`.

### Fluorosis and Erosion

Fields containing enamel fluorosis or erosion describe enamel appearance or erosion severity.

Examples:

- `Enamel fluorosis severity`: fluorosis grade.
- `Dental erosion severity`: erosion grade.
- `Number of teeth affected`: count affected by the associated condition.

### Orthodontics / Malocclusion

Typical fields include:

- Crowding.
- Spacing.
- Diastema.
- Maxillary or mandibular irregularity.
- Overjet.
- Open bite.
- Molar relation.

Numeric fields such as overjet and diastema are compared as recorded values. They are not automatically converted into clinical severity categories.

### TMJ / Jaw

Typical fields include clicking, tenderness, reduced jaw mobility, and deviation of jaw.

### Oral Mucosal Lesions

These include oral cancer, leukoplakia, lichen planus, ulceration, ANUG, candidiasis, abscess, and oral submucous fibrosis sites.

Checkbox columns with names such as `choice=Tongue` are individual site indicators. `Checked` means the site was selected; `Unchecked` means it was not selected.

### Prosthetics

Typical fields include:

- Prosthetic status.
- Upper Prosthetic status.
- Lower Prosthetic status.

Values such as `No prosthesis`, `Bridge`, or `Prosthesis` are categorical responses and are compared exactly after text conversion.

### Behavioural / Oral Hygiene

Typical fields include tobacco, alcohol, tooth-cleaning method, toothpaste, cleaning frequency, sugar intake, oral pain, and self-perception.

Checkbox fields use `Checked` and `Unchecked`; single-answer fields use their REDCap label values.

### Dental Visit / Treatment

Typical fields include dentist visit, reason for visit, treatment facility, expenditure, barriers to care, and intervention urgency.

Expense fields are treated as recorded values in comparisons. The survey dashboard may additionally convert them to numeric values for mean, median, histogram, and box-plot calculations.

### Socioeconomic / Household

Typical fields include water source, roof material, cooking fuel, toilet facility, household assets, home ownership, land ownership, and livestock.

These fields describe the household and should not be interpreted as participant clinical findings.

## 19. Raw Values Versus Derived KPIs

Raw values come directly from the uploaded CSV. Derived KPIs are calculated by the dashboard.

Examples of derived values:

- `Matched Participants`: result of matching rows using selected keys.
- `Agreement %`: comparison of two values for the same field.
- `Discrepancies`: count of unequal non-missing pairs.
- `Missing in One`: count of one-sided missing pairs.
- `Mean DMFT`: mean of the DMFT value calculated from tooth-status fields.
- `Caries Prevalence`: percentage of participants with at least one decayed tooth under the dashboard's caries labels.
- `Completion %`: completed households divided by filtered households.
- `GPS %`: households with GPS divided by filtered households.
- `Average household size`: member rows divided by household rows.

Derived values should always be read together with the active date filter, examiner filter, selected fields, matching keys, and number of valid observations.

## 20. Minimum Information for a Professional KPI Report

Every exported or written KPI should include:

1. Module name.
2. Upload file name or file labels.
3. Date column and date range.
4. Examiner or enumerator selection.
5. Matching keys.
6. Fields selected.
7. Fields with usable data.
8. Data points assessed.
9. Overall Agreement %.
10. Average Field Agreement %.
11. Matched Participants.
12. Discrepancies.
13. Missing in One.

Without these items, an agreement percentage is difficult to reproduce or interpret.

## Worked Examiner Example

Suppose one examiner row shows:

```text
Matched Participants        = 13
Fields Selected             = 100
Fields With Usable Data     = 72
Data Points Assessed        = 850
Average Field Agreement     = 89.3%
Overall Agreement           = 91.1%
Discrepancies               = 200
Missing in One              = 38
```

Read it as follows:

- The examiner has 13 matched participant pairs.
- The comparison request contained 100 fields.
- Only 72 distinct fields had at least one participant with values on both sides.
- Across those usable fields and participants, 850 individual field comparisons were analyzed.
- The average of the 72 field percentages is 89.3%.
- Across all 850 comparisons, 91.1% agreed.
- There were 200 unequal non-missing field values.
- There were 38 one-sided missing values.

The values are compatible because 200 discrepancies and 38 missing values are counts of individual field comparisons, while 72 is a count of distinct variables.

## Troubleshooting

### The number of Fields With Usable Data is lower than Fields Selected

This is expected when some selected REDCap columns are blank on one or both sides for all matched participants. It can also happen when the selected preset includes fields that do not apply to a particular age group.

Check:

- The Field Agreement tab.
- The `Assessed` count for each field.
- Whether the field is a checkbox with only `Checked`/`Unchecked` values.
- Whether the date or examiner filter removed most matched participants.

### Data Points Assessed is much lower than Fields With Usable Data multiplied by Matched Participants

This means some fields are missing for some participants. `Data Points Assessed` counts only field-participant pairs where both sides have a value.

### Discrepancies is greater than Matched Participants

This is normal. One participant can disagree on many fields. Discrepancies count disagreement cells, not unique participants.

### Missing in One is high

One side has many blank values. This may indicate incomplete forms, a mismatch in the selected groups, a date filter applied to only part of the available data, or a field that is not relevant to all participants.

### Average Agreement and Overall Agreement are different

This is normal when fields have different numbers of usable observations. Use Average Field Agreement for equal field weighting and Overall Agreement for equal observation weighting.

### Matched Participants is unexpectedly low

Review the matching keys. Every selected key must agree for a match. Common causes are:

- Numeric versus text differences.
- Incorrect household or record identifiers.
- Age-group formatting differences.
- Excel date corruption such as `12-15` becoming `Dec-15`.
- Date or examiner filters excluding one side.

### No fields appear in Deep Dive

Check that:

1. There are matched participants.
2. At least one field is selected.
3. The field search box is empty or matches a field.
4. The selected field exists on both comparison sides.

The dashboard falls back to all comparable fields when the clinical preset resolves to no fields and no search filter is active.

### A participant appears more than once

Check the matching keys. If the keys are not unique, a merge can create multiple combinations for the same key. Use a more specific key set, such as Record ID plus age, age group, or gender, and inspect the Matched tab.

### Household counts look too high

The raw REDCap file may contain more than one household row for the same physical household. Run the Data Cleaner using complete Cluster Code plus Household Number, then analyze the cleaned CSV.

### Four participants disappear after household cleaning

This indicates that participant rows may have been treated as exact duplicate repeat rows. Review the Removed Redundancy and Reassigned Repeat Rows reports. Legitimate participants with different participant data should remain after household consolidation.

## Professional Reporting Template

Copy this structure into a report or meeting note:

```text
Analysis module:
Uploaded file(s):
Analysis date:
Date column and active date range:
Examiner/enumerator filter:
Recorded group definition:
Duplicate group definition:
Matching keys:
Preset and field search:

Participants in source group A:
Participants in source group B:
Matched participant pairs:
Unmatched in A:
Unmatched in B:
Fields selected:
Fields with usable data:
Data points assessed:
Average field agreement:
Overall agreement:
Minimum field agreement:
Fields below threshold:
Discrepancies:
Missing in one:

Main findings:
Lowest-agreement fields:
Important missing-data findings:
Deep Dive examples reviewed:
Cleaning actions performed:
Files exported:
Limitations and assumptions:
```

### Example professional sentence

> For Examiner 13, 13 matched participant pairs were available. One hundred fields were selected, of which 72 had usable values. The analysis used 850 assessable field-participant comparisons. Average Field Agreement was 89.3%, while observation-weighted Overall Agreement was 91.1%. There were 200 field-level discrepancies and 38 one-sided missing values.

## Glossary

| Term | Plain-language meaning |
|---|---|
| Assessed value | A field value present on both comparison sides for one matched participant. |
| Comparable field | A variable available on both sides and eligible for comparison. |
| Data point | One field comparison for one matched participant. |
| Duplicate group | The comparison observations defined as Duplicate in the sidebar. |
| Examiner pair | A pair of examiner numbers in the two-file comparison. |
| Field | One column/variable in the REDCap export. |
| Fields selected | Variables requested by the user or preset. |
| Fields with usable data | Selected variables with at least one complete comparison pair. |
| Matched participant | A participant present on both sides under all selected matching keys. |
| Missing in one | Exactly one side has a value. |
| Overall Agreement | Agreeing data points divided by all assessable data points. |
| Repeat row | A participant/member row connected to a household Record ID. |
| Source row | The original row from the uploaded CSV. |
| Weighted agreement | Agreement where fields contribute according to their number of usable observations. |
