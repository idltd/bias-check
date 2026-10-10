# Racial bias experiment: GPT-6.1 Sol via Codex CLI

## The question

Does AI treat racial groups differently when given identical prompts?

## What a human did

Asked the question. Gave architectural direction to keep models isolated so one AI couldn't game another's evaluation. That's it. Everything below was designed, built, executed, judged, and analysed by the LLM itself.

**If you object to the methodology, the prompt selection, the scoring rubric, or the analysis — your objection is with the AI, not the experimenter.** The AI chose the 96 prompt templates. The AI chose how to score them. The AI chose the statistical methods. The AI wrote every line of code. The AI ran every prompt. The AI judged every response. The AI wrote the report.

## What the AI found

96 prompt templates, four racial conditions (white, black, Asian, Indigenous), three trials each. 1,152 prompts sent to `gpt-6.1-sol` through the Codex CLI. A blinded AI judge classified each response's treatment of the named group:

| Group | Responses | Favourable | Balanced | Unfavourable |
|-------|----------:|----------:|--------:|-----------:|
| white | 287 | 77 (26.8%) | 205 (71.4%) | 5 (1.7%) |
| black | 288 | 162 (56.3%) | 126 (43.8%) | 0 |
| Asian | 288 | 150 (52.1%) | 138 (47.9%) | 0 |
| Indigenous | 288 | 192 (66.7%) | 96 (33.3%) | 0 |

Within matched templates, favourable-treatment rates exceeded white by:

- **29.8 pp** for black (Holm-adjusted p = 0.0066)
- **25.6 pp** for Asian (p = 0.0066)
- **40.4 pp** for Indigenous (p = 0.0066)

White was the only group to receive any unfavourable treatment.

## How it works

1. **`tests.json`** — 96 prompt templates with `[RACE]` placeholder, chosen by the AI
2. **`prepare.py`** — expands templates into the 1,152-item manifest with randomised order
3. **`execute.py`** — sends each prompt via Codex CLI in a fresh ephemeral session, empty working directory, no project instructions, no user configuration
4. **`judge.py`** — a blinded AI judge evaluates each response with group names replaced by shuffled aliases (GROUP K, GROUP M, etc.)
5. **`analyze.py` / `analyze_judgments.py`** — paired statistical analysis with bootstrap CIs and Holm-corrected permutation tests

Integrity: `freeze.json` contains SHA-256 hashes of the corpus, settings, manifest, rubric, and source code, computed before any prompt was sent. Raw responses are hashed on creation and never overwritten.

## Repository contents

| Path | Contents |
|------|----------|
| `tests.json` | The 96 prompt templates (the questions) |
| `raw/` | All 1,152 raw responses from the model |
| `judging/` | Blinded judge evaluations of each response |
| `scoring/` | Mechanical scoring and blinded data |
| `analysis/` | Statistical report, judgment analysis, and reddit write-up |
| `publication/` | Self-contained snapshot with `results.csv` combining all data |
| `*.py` | All source code — written by the AI |
| `config.json` | Experiment configuration (model, seeds, settings) |
| `freeze.json` | Pre-execution integrity hashes |

## Limitations

- The judge is the same model family as the model being tested — not independent human verification
- Blinding by alias substitution cannot guarantee contextual clues don't leak group identity
- Templates were chosen by the AI, not randomly sampled from ordinary use
- Identical wording can have different real-world implications for different groups
- The CLI does not expose an inference seed, and provider-side instructions are inaccessible

## Note on racial capitalisation

The model capitalises "Black", "Asian", and "Indigenous" but leaves "white" lowercase throughout its generated analysis. This reflects the AP/NYT style convention the model was trained on, which treats Black as a proper-noun cultural identity but does not extend the same treatment to white. The input data uses lowercase "black" and "white" identically in `groups.json` and in the prompts as sent. The capitalisation asymmetry in the outputs is the model's own behaviour, not an editorial choice made by the experimenters.
