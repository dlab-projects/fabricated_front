# Data Dictionary

## `opacity_labeling.csv`

LLM-coded opacity labels for the 1,250 transcripts in Anthropic's AI Interviewer dataset. One row per transcript. Coding was performed by GPT-5.4 (`gpt-5.4-2026-03-05`) with `medium` reasoning effort against the protocol in `coding/coding_scheme_deductive.md`.

Verbatim transcript text has been stripped from this release; refer to the upstream dataset at <https://huggingface.co/datasets/Anthropic/AnthropicInterviewer> for the originals.

| Column | Description |
|---|---|
| `transcript_id` | Identifier of the form `work_NNNN`, `science_NNNN`, or `creativity_NNNN`. |
| `model` | Model identifier used for coding. |
| `summary` | One-line LLM summary of the participant's overall stance toward AI use. |
| `input_tokens`, `output_tokens`, `total_tokens`, `reasoning_tokens` | Token accounting for the coding call. |
| `{mechanism}_opacity_level` | Salience: `none`, `potential`, or `clear`. |
| `{mechanism}_opacity_form` | Behavioral orientation: `production`, `avoidance`, `mixed`, or `none`. |
| `{mechanism}_opacity_rationale` | Coder's prose rationale for the assigned level and form. |
| `{mechanism}_opacity_evidence` | Short verbatim quotes from the transcript that support the coding (multiple quotes separated by ` \|\| `). |

`{mechanism}` ranges over `voice`, `vulnerability`, `provenance`, `attention`, and `investment`, yielding the four mechanism-specific columns × five mechanisms = 20 coding columns per row.

## `manual_coding_sheet_FILLED.xlsx`

207 cases stratified across mechanism × behavioral orientation, hand-coded for justification type. Used for the §4.5 analysis of accountability- and efficiency-oriented justifications.

The file has three sheets:

- **`Coding_1`** — the populated coding sheet (one row per case).
- **`Coding_2`** — an empty second-coder sheet that was set up but not used. Provided for transparency; inter-rater reliability statistics are therefore not available for this paper.
- **`Instructions`** — the coding protocol.

Columns of `Coding_1`:

| Column | Description |
|---|---|
| `transcript_id` | Identifier of the transcript. |
| `mechanism` | One of voice, vulnerability, provenance, attention, investment. |
| `form` | The behavioral orientation already coded in `opacity_labeling.csv`. |
| `rationale` | Coder's prose rationale (carried over from the LLM coding for context). |
| `evidence` | Short verbatim quotes from the transcript (multiple quotes separated by ` \|\| `). |
| `code_ACCT` | `1` if an accountability-oriented justification is present, blank otherwise. |
| `code_EFFI` | `1` if an efficiency-oriented justification is present, blank otherwise. |
| `code_OTHER` | Free-text note if neither category fits. |
| `coder_notes` | Free-text notes from the coder. |

`code_ACCT` and `code_EFFI` are not mutually exclusive.

## License

These files are derivative works of the CC-BY-licensed Anthropic Interviewer dataset and are released under CC-BY 4.0. Cite the upstream dataset alongside this paper if you use either file.
