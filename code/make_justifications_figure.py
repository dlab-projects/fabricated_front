"""Generate the justifications figure for the paper.

Two-panel grouped-bar chart matching the style of opacity_form.png:
  Panel A (left): ACCT vs EFFI rate by behavioral orientation
  Panel B (right): ACCT vs EFFI rate by mechanism

Output: paper/figures/justifications.png
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy.stats import beta

DATA = "data/manual_coding_sheet_FILLED.xlsx"
OUT_PDF = "paper/figures/justifications.pdf"
OUT_PNG = "paper/figures/justifications.png"

# Match the serif font + bold-weighted styling used by the other paper PDFs
rcParams["font.family"] = "serif"
rcParams["font.serif"] = ["DejaVu Serif", "Computer Modern Roman", "Times New Roman", "Times"]
rcParams["mathtext.fontset"] = "dejavuserif"
rcParams["font.size"] = 13
rcParams["axes.labelsize"] = 15
rcParams["axes.titlesize"] = 14
rcParams["xtick.labelsize"] = 13
rcParams["ytick.labelsize"] = 12
rcParams["legend.fontsize"] = 12
rcParams["legend.title_fontsize"] = 13


def wilson_ci(k, n, alpha=0.05):
    """Wilson (binomial proportion) confidence interval."""
    if n == 0:
        return 0.0, 0.0
    p = k / n
    z = 1.96
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    lo = max(0.0, centre - half)
    hi = min(1.0, centre + half)
    return lo, hi


def rates(df, col_group):
    rows = []
    for g, sub in df.groupby(col_group):
        n = len(sub)
        for code in ("code_ACCT", "code_EFFI"):
            k = int(sub[code].fillna(0).sum())
            lo, hi = wilson_ci(k, n)
            rows.append({
                "group": g,
                "code": "ACCT" if code == "code_ACCT" else "EFFI",
                "rate": k / n if n > 0 else 0,
                "lo": lo,
                "hi": hi,
                "n": n,
            })
    return pd.DataFrame(rows)


def plot_panel(ax, summary, group_order, title):
    codes = ["ACCT", "EFFI"]
    code_labels = {"ACCT": "accountability-oriented", "EFFI": "efficiency-oriented"}
    # match the edited-PDF palette used by the other paper figures
    colors = {"ACCT": "#3070ad", "EFFI": "#c66526"}
    width = 0.36
    x = np.arange(len(group_order))
    for i, code in enumerate(codes):
        sub = summary[summary["code"] == code].set_index("group").reindex(group_order)
        rates_vals = sub["rate"].values
        err_lo = rates_vals - sub["lo"].values
        err_hi = sub["hi"].values - rates_vals
        ax.bar(
            x + (i - 0.5) * width,
            rates_vals,
            width=width,
            label=code_labels[code],
            color=colors[code],
            edgecolor="white",
            linewidth=0.5,
            yerr=[err_lo, err_hi],
            capsize=3,
            error_kw={"elinewidth": 0.8, "ecolor": "black"},
        )
    ax.set_xticks(x)
    ax.set_xticklabels([g.capitalize() for g in group_order])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Fraction of Cases", fontweight="bold")
    ax.set_title(title)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle="--", color="white", linewidth=0.8)
    ax.set_facecolor("#ececec")
    for spine in ax.spines.values():
        spine.set_visible(False)


def main():
    df = pd.read_excel(DATA)
    # Normalize: 1/0/NaN for code columns
    for c in ("code_ACCT", "code_EFFI"):
        df[c] = df[c].fillna(0).astype(int)

    # Panel A: by behavioral orientation
    summary_form = rates(df, "form")
    form_order = ["avoidance", "mixed", "production"]
    # Panel B: by mechanism
    summary_mech = rates(df, "mechanism")
    mech_order = ["voice", "vulnerability", "provenance", "attention", "investment"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 4.5), gridspec_kw={"width_ratios": [3, 5]})
    plot_panel(ax1, summary_form, form_order, "By Behavioral Orientation")
    plot_panel(ax2, summary_mech, mech_order, "By Mechanism")
    ax2.set_ylabel("")  # share y-label

    # Layout first, then attach the legend outside the right edge
    plt.tight_layout(rect=[0, 0, 0.82, 1])
    handles, labels = ax1.get_legend_handles_labels()
    leg = fig.legend(handles, labels, loc="center left",
                     bbox_to_anchor=(0.83, 0.5), frameon=True,
                     title="Justification", borderpad=0.7)
    leg.get_title().set_fontweight("bold")
    leg.get_frame().set_edgecolor("black")
    leg.get_frame().set_linewidth(0.7)
    for path in (OUT_PDF, OUT_PNG):
        plt.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
        print(f"Wrote {path}")

    # Also print the underlying numbers for verification
    print("\nBy orientation:")
    print(summary_form.pivot(index="group", columns="code", values="rate").round(3))
    print("\nBy mechanism:")
    print(summary_mech.pivot(index="group", columns="code", values="rate").round(3))
    print("\nSample sizes:")
    print(df.groupby("form").size())
    print(df.groupby("mechanism").size())


if __name__ == "__main__":
    main()
