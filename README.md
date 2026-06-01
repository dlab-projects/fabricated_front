# The Fabricated Front

Replication materials for:

> Van Nuenen, T., Sachdeva, P. S., & Chopra, S. (2026). The Fabricated Front: GenAI and the Social Organization of Workplace Legibility.

The paper analyzes 1,250 interview transcripts from Anthropic's AI Interviewer dataset to identify five mechanisms through which generative AI reorganizes workplace performances: voice, vulnerability, provenance, attention, and investment opacity. This repository contains the LLM-coded labels, the hand-coded justification sheet, the analysis scripts that produce the statistical results, and the LaTeX source of the paper.

## Repository layout

```
paper/    LaTeX source, bibliography, and figure PDFs
code/     Analysis scripts that operate on the released data files
coding/   Coding scheme and hand-coding protocol
data/     LLM-coded opacity labels and hand-coded justification sheet
```

## Data

The transcripts themselves are not redistributed here. They are publicly available under CC-BY at:

<https://huggingface.co/datasets/Anthropic/AnthropicInterviewer>

Downloaded splits should be placed at `interview_transcripts/{workforce,creatives,scientists}_transcripts.csv` if you wish to re-run the coding pipeline.

What is included:

- `data/opacity_labeling.csv` — LLM-coded opacity labels (GPT-5.4, medium reasoning effort) for all 1,250 transcripts across five mechanisms, with per-mechanism `level`, `form`, `rationale`, and short evidence quotes. Full transcript text has been stripped; refer to the source dataset for the originals.
- `data/manual_coding_sheet_FILLED.xlsx` — the 207 stratified cases hand-coded for accountability-oriented and efficiency-oriented justifications (used in §4.5 of the paper).

See `data/README.md` for the column-level data dictionary.

## Reproducing the results

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

| Result | Script |
|---|---|
| Chi-squared tests on prevalence and behavioral orientation across groups (§4.1, §4.2) | `python code/analyze_opacity_labeling.py` |
| Level × form analysis (supplementary) | `python code/analyze_opacity_level_form.py` |
| Justification figure and §4.5 statistics | `python code/make_justifications_figure.py` |

The LLM coding pipeline (GPT-5.4 → `opacity_labeling.csv`) and the activity clustering pipeline (GPT-5.4 → MPNet embeddings → k-means → cluster labelling) that produce the figures in §4 are not yet in this repository; they will be added in a subsequent commit.

## Citation

If you use this dataset or code, please cite both the paper and the source corpus:

```bibtex
@article{vannuenen2026fabricated,
  title  = {The Fabricated Front: {GenAI} and the Social Organization of Workplace Legibility},
  author = {Van Nuenen, Tom and Sachdeva, Pratik S. and Chopra, Sahiba},
  year   = {2026}
}

@misc{handa2025interviewer,
  title  = {Introducing {Anthropic} {Interviewer}: What 1,250 professionals told us about working with {AI}},
  author = {Handa, Kunal and Stern, Michael and Huang, Saffron and Hong, Jerry and Durmus, Esin and McCain, Miles and Yun, Grace and Alt, AJ and Millar, Thomas and Tamkin, Alex and Leibrock, Jane and Ritchie, Stuart and Ganguli, Deep},
  year   = {2025},
  url    = {https://huggingface.co/datasets/Anthropic/AnthropicInterviewer}
}
```

## License

Code is released under the MIT License (see `LICENSE`). Derived data (`data/opacity_labeling.csv`, `data/manual_coding_sheet_FILLED.xlsx`) is released under CC-BY 4.0, consistent with the upstream Anthropic Interviewer dataset license.
