#!/usr/bin/env python3
"""
Analyze the relationship between opacity LEVEL (potential vs clear)
and FORM (production/avoidance/mixed).

Research questions:
1. Does "clear" vs "potential" predict different behavioral forms?
2. Are "clear" cases more likely to show avoidance (conscious management)?
3. Are "potential" cases more likely to show production (unexamined practice)?
"""

import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, fisher_exact
from scipy.stats.contingency import association
import warnings
warnings.filterwarnings('ignore')

# Load data
print("Loading data...")
df = pd.read_csv('data/opacity_labeling.csv')
print(f"Total rows: {len(df)}\n")

# Define the 5 mechanisms
mechanisms = [
    'voice_opacity',
    'vulnerability_opacity',
    'provenance_opacity',
    'attention_opacity',
    'investment_opacity'
]

print("="*80)
print("ANALYSIS: OPACITY LEVEL × FORM RELATIONSHIP")
print("="*80)
print()

# Storage for aggregated data
all_clear_forms = []
all_potential_forms = []

# Analyze each mechanism
for mechanism in mechanisms:
    print(f"\n{'='*80}")
    print(f"MECHANISM: {mechanism.upper()}")
    print(f"{'='*80}\n")

    level_col = f"{mechanism}_level"
    form_col = f"{mechanism}_form"

    # Filter out null/empty values
    subset = df[[level_col, form_col]].dropna()
    subset = subset[(subset[level_col] != '') & (subset[form_col] != '')]

    print(f"Valid cases: {len(subset)}")

    if len(subset) == 0:
        print("No valid data for this mechanism\n")
        continue

    # Create crosstab
    crosstab = pd.crosstab(
        subset[level_col],
        subset[form_col],
        margins=True
    )

    print(f"\nCrosstab: {level_col} × {form_col}")
    print(crosstab)
    print()

    # Get the data without margins for statistics
    crosstab_no_margin = pd.crosstab(subset[level_col], subset[form_col])

    # Collect data for aggregation
    clear_cases = subset[subset[level_col] == 'clear']
    potential_cases = subset[subset[level_col] == 'potential']

    all_clear_forms.extend(clear_cases[form_col].tolist())
    all_potential_forms.extend(potential_cases[form_col].tolist())

    # Calculate percentages by level
    if len(crosstab_no_margin) > 0:
        print("Percentage distribution by level:")
        pct_by_level = crosstab_no_margin.div(crosstab_no_margin.sum(axis=1), axis=0) * 100
        print(pct_by_level.round(1))
        print()

    # Statistical test
    if crosstab_no_margin.shape[0] > 1 and crosstab_no_margin.shape[1] > 1:
        # Decide between chi-square and Fisher's exact
        expected_freq = chi2_contingency(crosstab_no_margin)[3]
        min_expected = expected_freq.min()

        if min_expected < 5 or len(subset) < 20:
            # Use Fisher's exact test for small samples
            # For 2x2 tables only
            if crosstab_no_margin.shape == (2, 2):
                oddsratio, p_value = fisher_exact(crosstab_no_margin)
                print(f"Fisher's Exact Test:")
                print(f"  Odds Ratio: {oddsratio:.3f}")
                print(f"  p-value: {p_value:.4f}")
            else:
                # For larger tables, use chi-square with warning
                chi2, p_value, dof, expected = chi2_contingency(crosstab_no_margin)
                print(f"Chi-Square Test (Note: small expected frequencies):")
                print(f"  χ² = {chi2:.3f}, df = {dof}, p = {p_value:.4f}")
                print(f"  Minimum expected frequency: {min_expected:.2f}")
        else:
            # Use chi-square test
            chi2, p_value, dof, expected = chi2_contingency(crosstab_no_margin)
            print(f"Chi-Square Test:")
            print(f"  χ² = {chi2:.3f}, df = {dof}, p = {p_value:.4f}")

            # Cramér's V for effect size
            n = crosstab_no_margin.sum().sum()
            min_dim = min(crosstab_no_margin.shape[0] - 1, crosstab_no_margin.shape[1] - 1)
            cramers_v = np.sqrt(chi2 / (n * min_dim))
            print(f"  Cramér's V: {cramers_v:.3f}")

        # Interpretation
        print(f"\nInterpretation:")
        if p_value < 0.001:
            sig_level = "highly significant (p < .001)"
        elif p_value < 0.01:
            sig_level = "very significant (p < .01)"
        elif p_value < 0.05:
            sig_level = "significant (p < .05)"
        else:
            sig_level = "not significant (p >= .05)"

        print(f"  The association is {sig_level}")

        # Theoretical interpretation
        if 'clear' in crosstab_no_margin.index and 'potential' in crosstab_no_margin.index:
            if 'avoidance' in crosstab_no_margin.columns:
                clear_avoid_pct = (crosstab_no_margin.loc['clear', 'avoidance'] /
                                  crosstab_no_margin.loc['clear'].sum() * 100)
                potential_avoid_pct = (crosstab_no_margin.loc['potential', 'avoidance'] /
                                      crosstab_no_margin.loc['potential'].sum() * 100)
                print(f"  Clear → Avoidance: {clear_avoid_pct:.1f}%")
                print(f"  Potential → Avoidance: {potential_avoid_pct:.1f}%")

                if clear_avoid_pct > potential_avoid_pct:
                    print(f"  → SUPPORTS hypothesis: Clear opacity shows more avoidance")
                else:
                    print(f"  → CONTRADICTS hypothesis: Clear opacity shows LESS avoidance")

            if 'production' in crosstab_no_margin.columns:
                clear_prod_pct = (crosstab_no_margin.loc['clear', 'production'] /
                                 crosstab_no_margin.loc['clear'].sum() * 100)
                potential_prod_pct = (crosstab_no_margin.loc['potential', 'production'] /
                                     crosstab_no_margin.loc['potential'].sum() * 100)
                print(f"  Clear → Production: {clear_prod_pct:.1f}%")
                print(f"  Potential → Production: {potential_prod_pct:.1f}%")

                if potential_prod_pct > clear_prod_pct:
                    print(f"  → SUPPORTS hypothesis: Potential opacity shows more production")
                else:
                    print(f"  → CONTRADICTS hypothesis: Potential opacity shows LESS production")
    else:
        print("Insufficient variation for statistical testing")

    print()

# AGGREGATED ANALYSIS ACROSS ALL MECHANISMS
print("\n" + "="*80)
print("AGGREGATED ANALYSIS: ALL MECHANISMS COMBINED")
print("="*80)
print()

# Create dataframe for aggregated analysis
agg_data = pd.DataFrame({
    'level': ['clear'] * len(all_clear_forms) + ['potential'] * len(all_potential_forms),
    'form': all_clear_forms + all_potential_forms
})

print(f"Total aggregated cases: {len(agg_data)}")
print(f"  Clear cases: {len(all_clear_forms)}")
print(f"  Potential cases: {len(all_potential_forms)}")
print()

# Aggregated crosstab
agg_crosstab = pd.crosstab(
    agg_data['level'],
    agg_data['form'],
    margins=True
)

print("Aggregated Crosstab: Level × Form")
print(agg_crosstab)
print()

# Percentages
agg_crosstab_no_margin = pd.crosstab(agg_data['level'], agg_data['form'])
print("Percentage distribution by level:")
agg_pct = agg_crosstab_no_margin.div(agg_crosstab_no_margin.sum(axis=1), axis=0) * 100
print(agg_pct.round(1))
print()

# Statistical test for aggregated data
if agg_crosstab_no_margin.shape[0] > 1 and agg_crosstab_no_margin.shape[1] > 1:
    chi2, p_value, dof, expected = chi2_contingency(agg_crosstab_no_margin)
    print(f"Chi-Square Test:")
    print(f"  χ² = {chi2:.3f}, df = {dof}, p = {p_value:.4f}")

    # Cramér's V
    n = agg_crosstab_no_margin.sum().sum()
    min_dim = min(agg_crosstab_no_margin.shape[0] - 1, agg_crosstab_no_margin.shape[1] - 1)
    cramers_v = np.sqrt(chi2 / (n * min_dim))
    print(f"  Cramér's V: {cramers_v:.3f}")

    # Effect size interpretation
    if cramers_v < 0.1:
        effect = "negligible"
    elif cramers_v < 0.3:
        effect = "small"
    elif cramers_v < 0.5:
        effect = "medium"
    else:
        effect = "large"
    print(f"  Effect size: {effect}")
    print()

    # Interpretation
    print(f"Interpretation:")
    if p_value < 0.001:
        sig_level = "highly significant (p < .001)"
    elif p_value < 0.01:
        sig_level = "very significant (p < .01)"
    elif p_value < 0.05:
        sig_level = "significant (p < .05)"
    else:
        sig_level = "not significant (p >= .05)"

    print(f"  The association is {sig_level}")
    print()

# THEORETICAL SUMMARY
print("="*80)
print("THEORETICAL INTERPRETATION")
print("="*80)
print()

print("Hypothesis:")
print("  H1: Clear/explicit opacity → more AVOIDANCE (conscious management)")
print("  H2: Potential/implicit opacity → more PRODUCTION (unexamined practice)")
print()

if 'avoidance' in agg_crosstab_no_margin.columns and 'production' in agg_crosstab_no_margin.columns:
    clear_avoid = agg_crosstab_no_margin.loc['clear', 'avoidance']
    clear_prod = agg_crosstab_no_margin.loc['clear', 'production']
    clear_total = agg_crosstab_no_margin.loc['clear'].sum()

    potential_avoid = agg_crosstab_no_margin.loc['potential', 'avoidance']
    potential_prod = agg_crosstab_no_margin.loc['potential', 'production']
    potential_total = agg_crosstab_no_margin.loc['potential'].sum()

    print("Results:")
    print(f"\nCLEAR opacity cases (n={clear_total}):")
    print(f"  Avoidance: {clear_avoid} ({clear_avoid/clear_total*100:.1f}%)")
    print(f"  Production: {clear_prod} ({clear_prod/clear_total*100:.1f}%)")
    if 'mixed' in agg_crosstab_no_margin.columns:
        clear_mixed = agg_crosstab_no_margin.loc['clear', 'mixed']
        print(f"  Mixed: {clear_mixed} ({clear_mixed/clear_total*100:.1f}%)")

    print(f"\nPOTENTIAL opacity cases (n={potential_total}):")
    print(f"  Avoidance: {potential_avoid} ({potential_avoid/potential_total*100:.1f}%)")
    print(f"  Production: {potential_prod} ({potential_prod/potential_total*100:.1f}%)")
    if 'mixed' in agg_crosstab_no_margin.columns:
        potential_mixed = agg_crosstab_no_margin.loc['potential', 'mixed']
        print(f"  Mixed: {potential_mixed} ({potential_mixed/potential_total*100:.1f}%)")

    print(f"\nComparative Analysis:")
    avoid_diff = (clear_avoid/clear_total - potential_avoid/potential_total) * 100
    prod_diff = (potential_prod/potential_total - clear_prod/clear_total) * 100

    print(f"  Clear cases show {avoid_diff:+.1f}pp more avoidance than potential cases")
    print(f"  Potential cases show {prod_diff:+.1f}pp more production than clear cases")

    print(f"\nHypothesis Testing:")
    if avoid_diff > 0:
        print(f"  ✓ H1 SUPPORTED: Clear opacity → more avoidance ({avoid_diff:.1f}pp difference)")
    else:
        print(f"  ✗ H1 NOT SUPPORTED: Clear opacity → less avoidance ({avoid_diff:.1f}pp difference)")

    if prod_diff > 0:
        print(f"  ✓ H2 SUPPORTED: Potential opacity → more production ({prod_diff:.1f}pp difference)")
    else:
        print(f"  ✗ H2 NOT SUPPORTED: Potential opacity → less production ({prod_diff:.1f}pp difference)")

    print()
    print("Conclusion:")
    if p_value < 0.05:
        if avoid_diff > 0 and prod_diff > 0:
            print("  There is a statistically significant association between opacity level")
            print("  and behavioral form that SUPPORTS the theoretical framework:")
            print("  - Clear/explicit opacity concerns lead to conscious avoidance")
            print("  - Potential/implicit concerns lead to unexamined production")
        elif avoid_diff > 0 or prod_diff > 0:
            print("  There is a statistically significant association, with PARTIAL support")
            print("  for the theoretical framework (one hypothesis supported).")
        else:
            print("  There is a statistically significant association, but it CONTRADICTS")
            print("  the theoretical predictions about conscious vs unexamined opacity.")
    else:
        print("  The association is not statistically significant. The data do not")
        print("  provide strong evidence for or against the theoretical framework.")

print()
print("="*80)
print("ANALYSIS COMPLETE")
print("="*80)
