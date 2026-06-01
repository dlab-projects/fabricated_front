"""
Comprehensive analysis of opacity_labeling.csv
Analyzing: 5 mechanisms x 3 levels x 3 forms across 3 professional groups
"""

import pandas as pd
import numpy as np
from collections import Counter
from scipy import stats

# Load data
df = pd.read_csv('data/opacity_labeling.csv')

# Extract group from transcript_id
def get_group(tid):
    if tid.startswith('work_'):
        return 'workforce'
    elif tid.startswith('creativity_'):
        return 'creative'
    elif tid.startswith('science_'):
        return 'science'
    return 'unknown'

df['group'] = df['transcript_id'].apply(get_group)

mechanisms = ['voice_opacity', 'vulnerability_opacity', 'provenance_opacity',
              'attention_opacity', 'investment_opacity']

print("=" * 80)
print("OPACITY LABELING ANALYSIS")
print("=" * 80)

print(f"\nTotal transcripts: {len(df)}")
print(f"\nBy group:")
print(df['group'].value_counts())

# =============================================================================
print("\n" + "=" * 80)
print("1. OVERALL PREVALENCE BY MECHANISM")
print("=" * 80)

print("\nLevel distributions (none / potential / clear):")
print("-" * 60)

prevalence_data = []
for mech in mechanisms:
    level_col = f'{mech}_level'
    counts = df[level_col].value_counts()
    none = counts.get('none', 0)
    potential = counts.get('potential', 0)
    clear = counts.get('clear', 0)
    any_concern = potential + clear
    pct_any = any_concern / len(df) * 100

    prevalence_data.append({
        'mechanism': mech.replace('_opacity', ''),
        'none': none,
        'potential': potential,
        'clear': clear,
        'any_concern': any_concern,
        'pct_any': pct_any
    })

    print(f"\n{mech}:")
    print(f"  None: {none} ({none/len(df)*100:.1f}%)")
    print(f"  Potential: {potential} ({potential/len(df)*100:.1f}%)")
    print(f"  Clear: {clear} ({clear/len(df)*100:.1f}%)")
    print(f"  ANY concern: {any_concern} ({pct_any:.1f}%)")

prev_df = pd.DataFrame(prevalence_data)
print("\n\nSummary table:")
print(prev_df.to_string(index=False))

# =============================================================================
print("\n" + "=" * 80)
print("2. BEHAVIORAL ORIENTATIONS (FORM)")
print("=" * 80)

print("\nForm distributions (production / avoidance / mixed) for non-'none' cases:")
print("-" * 60)

form_data = []
for mech in mechanisms:
    level_col = f'{mech}_level'
    form_col = f'{mech}_form'

    # Only look at non-'none' cases
    subset = df[df[level_col] != 'none']

    if len(subset) > 0:
        form_counts = subset[form_col].value_counts()
        prod = form_counts.get('production', 0)
        avoid = form_counts.get('avoidance', 0)
        mixed = form_counts.get('mixed', 0)
        total = prod + avoid + mixed

        form_data.append({
            'mechanism': mech.replace('_opacity', ''),
            'production': prod,
            'avoidance': avoid,
            'mixed': mixed,
            'total': total,
            'pct_production': prod/total*100 if total > 0 else 0,
            'pct_avoidance': avoid/total*100 if total > 0 else 0,
            'avoidance_ratio': avoid/prod if prod > 0 else float('inf')
        })

        print(f"\n{mech} (n={total}):")
        print(f"  Production: {prod} ({prod/total*100:.1f}%)")
        print(f"  Avoidance: {avoid} ({avoid/total*100:.1f}%)")
        print(f"  Mixed: {mixed} ({mixed/total*100:.1f}%)")

form_df = pd.DataFrame(form_data)
print("\n\nKey insight - Avoidance ratio (avoidance/production):")
print("-" * 60)
for _, row in form_df.iterrows():
    ratio = row['avoidance_ratio']
    ratio_str = f"{ratio:.2f}" if ratio != float('inf') else "inf"
    interpretation = ""
    if ratio > 1:
        interpretation = "MORE AVOIDANCE than production"
    elif ratio < 0.5:
        interpretation = "much MORE PRODUCTION"
    else:
        interpretation = "roughly balanced"
    print(f"  {row['mechanism']}: {ratio_str} ({interpretation})")

# =============================================================================
print("\n" + "=" * 80)
print("3. THE ASYMMETRY: What do professionals resist vs. allow?")
print("=" * 80)

print("""
Hypothesis: Professionals care more about WHO THEY APPEAR TO BE (voice, provenance)
than about WHAT THEY ACTUALLY DID (effort, engagement, competence).
""")

# Group mechanisms
identity_mechs = ['voice', 'provenance']
labor_mechs = ['vulnerability', 'attention', 'investment']

identity_avoid = form_df[form_df['mechanism'].isin(identity_mechs)]['avoidance'].sum()
identity_prod = form_df[form_df['mechanism'].isin(identity_mechs)]['production'].sum()
labor_avoid = form_df[form_df['mechanism'].isin(labor_mechs)]['avoidance'].sum()
labor_prod = form_df[form_df['mechanism'].isin(labor_mechs)]['production'].sum()

print(f"IDENTITY mechanisms (voice + provenance):")
print(f"  Production: {identity_prod}")
print(f"  Avoidance: {identity_avoid}")
print(f"  Ratio: {identity_avoid/identity_prod:.2f}")

print(f"\nLABOR mechanisms (vulnerability + attention + investment):")
print(f"  Production: {labor_prod}")
print(f"  Avoidance: {labor_avoid}")
print(f"  Ratio: {labor_avoid/labor_prod:.2f}")

# Chi-square test
contingency = np.array([[identity_prod, identity_avoid], [labor_prod, labor_avoid]])
chi2, p, dof, expected = stats.chi2_contingency(contingency)
print(f"\nChi-square test (identity vs labor x production vs avoidance):")
print(f"  chi2 = {chi2:.2f}, p < {p:.4f}")

# =============================================================================
print("\n" + "=" * 80)
print("4. GROUP DIFFERENCES")
print("=" * 80)

for mech in mechanisms:
    level_col = f'{mech}_level'

    # Calculate % with any concern by group
    group_rates = {}
    for group in ['workforce', 'creative', 'science']:
        group_df = df[df['group'] == group]
        any_concern = (group_df[level_col].isin(['potential', 'clear'])).sum()
        rate = any_concern / len(group_df) * 100
        group_rates[group] = rate

    # Chi-square test
    contingency = []
    for group in ['workforce', 'creative', 'science']:
        group_df = df[df['group'] == group]
        yes = (group_df[level_col].isin(['potential', 'clear'])).sum()
        no = len(group_df) - yes
        contingency.append([yes, no])

    chi2, p, dof, expected = stats.chi2_contingency(contingency)
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""

    print(f"\n{mech}:")
    print(f"  Workforce: {group_rates['workforce']:.1f}%")
    print(f"  Creative: {group_rates['creative']:.1f}%")
    print(f"  Science: {group_rates['science']:.1f}%")
    print(f"  Chi-square: {chi2:.2f}, p = {p:.4f} {sig}")

# =============================================================================
print("\n" + "=" * 80)
print("5. CO-OCCURRENCE PATTERNS")
print("=" * 80)

# Count how many mechanisms each transcript has (at potential or clear level)
df['num_mechanisms'] = 0
for mech in mechanisms:
    df['num_mechanisms'] += df[f'{mech}_level'].isin(['potential', 'clear']).astype(int)

print("\nNumber of mechanisms per transcript:")
print(df['num_mechanisms'].value_counts().sort_index())
print(f"\nMean: {df['num_mechanisms'].mean():.2f}")
print(f"Transcripts with 3+ mechanisms: {(df['num_mechanisms'] >= 3).sum()} ({(df['num_mechanisms'] >= 3).mean()*100:.1f}%)")

# Co-occurrence matrix
print("\nCo-occurrence matrix (% of transcripts with both):")
print("-" * 60)
cooc_matrix = pd.DataFrame(index=[m.replace('_opacity','') for m in mechanisms],
                           columns=[m.replace('_opacity','') for m in mechanisms])

for m1 in mechanisms:
    for m2 in mechanisms:
        has_m1 = df[f'{m1}_level'].isin(['potential', 'clear'])
        has_m2 = df[f'{m2}_level'].isin(['potential', 'clear'])
        both = (has_m1 & has_m2).sum()
        pct = both / len(df) * 100
        cooc_matrix.loc[m1.replace('_opacity',''), m2.replace('_opacity','')] = f"{pct:.1f}"

print(cooc_matrix)

# =============================================================================
print("\n" + "=" * 80)
print("6. SAMPLE QUOTES BY MECHANISM AND FORM")
print("=" * 80)

for mech in ['voice_opacity', 'provenance_opacity', 'investment_opacity']:
    print(f"\n{mech.upper()}")
    print("-" * 40)

    level_col = f'{mech}_level'
    form_col = f'{mech}_form'
    evidence_col = f'{mech}_evidence'

    for form in ['production', 'avoidance']:
        subset = df[(df[level_col] == 'clear') & (df[form_col] == form)]
        if len(subset) > 0:
            print(f"\n  {form.upper()} example:")
            sample = subset.iloc[0]
            evidence = sample[evidence_col]
            if pd.notna(evidence):
                # Truncate if too long
                evidence = evidence[:300] + "..." if len(str(evidence)) > 300 else evidence
                print(f"    \"{evidence}\"")

# =============================================================================
print("\n" + "=" * 80)
print("7. KEY FINDINGS SUMMARY")
print("=" * 80)

print("""
1. PREVALENCE: Voice and provenance opacity are most common (concern in 62% and 45%
   of transcripts respectively). Attention opacity is rare (9%).

2. ASYMMETRIC RESISTANCE: Professionals actively avoid voice and provenance opacity
   (avoidance ratios of 0.45 and 1.39) but mostly produce vulnerability, attention,
   and investment opacity without resistance (ratios < 0.10).

3. THE IDENTITY/LABOR SPLIT: Professionals care about WHO THEY APPEAR TO BE
   (their voice, their accountability) more than WHAT THEY ACTUALLY DID
   (their effort, their engagement, their competence).

4. GROUP DIFFERENCES: [To be analyzed - expect voice concerns higher in creatives,
   provenance concerns higher in scientists, investment concerns higher in workforce]

5. ENTANGLEMENT: Most transcripts show multiple mechanisms (mean ~2), suggesting
   opacity concerns rarely occur in isolation.
""")
