# 🔍 Semantic Notes Search

**A semantic search engine for Markdown notes, built from scratch** — no
frameworks, no external services, no hosted models. Pure Python standard
library and explainable math.

> Project from the [AI Engineering from Scratch](https://github.com/rohitg00/ai-engineering-from-scratch)
> course.

[Español](README.md) | **English**

## What does it do?

Point it at a folder of `.md` notes and ask a question in natural language;
it tells you **which note answers it best, and why**:

```bash
python cli.py samples/notes "producto punto direccion" --aliases samples/aliases.json
```

```json
{
  "query": "producto punto direccion",
  "documents": 3,
  "matches": [
    {"id": "similitud-coseno.md", "score": 0.5123, "matched": ["producto", "punto", "direccion"], "preview": "..."}
  ]
}
```

Every result is **explainable**: you see the exact matching tokens and the
score. No black box.

## The engine in 4 pieces

| Function | What it does | Underlying concept |
|---|---|---|
| `normalize()` | text → clean tokens | Unicode NFC, case folding, `\w+` regex, controlled synonym expansion |
| `build_index()` | tokens → TF-IDF index | smoothed IDF `log((1+N)/(1+df)) + 1`, vectors normalized to unit length |
| `search()` | query → top-k ranking | **cosine similarity** (= dot product of unit vectors), stable tie-break by id |
| `evaluate()` | ranking → metric | recall@k over labeled cases |

```
notes .md ──normalize──► tokens ──build_index──► TF-IDF vectors
                                                      │
query ──normalize──► vector ──────search (cosine)────► top-k with explanation
                                                      │
labeled cases ────────────────────evaluate (recall@k)─┘
```

## Design decisions (the interesting part)

- **NFC before the regex.** The combining acute accent `\u0301` is not `\w`:
  tokenize before normalizing and `"café"` written in NFD loses its accent
  forever. Order matters.
- **Aliases expand in a single pass, no cycles.** `{a: b, b: a}` cannot loop
  because each token is substituted exactly once.
- **df counts documents, not occurrences.** Repeating "orchard" ten times in
  one note does not make it appear in ten documents.
- **Unit-length vectors.** Cosine reduces to a dot product, and a long note
  cannot win merely by repeating all of its words.
- **The query uses the index's IDF, never its own.** Refitting weights per
  query would change the coordinate system and invalidate cosine comparisons.
- **Empty list over noise.** Score ≤ 0 is never returned: "found nothing" is
  more honest than padding with zero-score hits.
- **Deterministic ranking.** Score ties break by alphabetical `id` → tests
  and demos are reproducible.

## Running the project

```bash
# Requirements: Python 3.10+ (stdlib only)
python demo.py                      # full walkthrough with sample notes
python -m unittest discover tests   # included test suite
python cli.py <folder> "<query>" --k 3 --aliases samples/aliases.json
```

Note: the sample notes ship in Spanish (they come from my own study notes);
the engine itself is language-agnostic for any whitespace-tokenizable text.

## What it is NOT (technical honesty)

- **It is not an embedding model.** It is a lexical TF-IDF baseline with
  explicit synonyms: `replicas` will not find `replica` (no stemming),
  `numeros` will not find `números` (no accent folding), and "deployment"
  will not find "release" unless you declare it in the aliases file.
- **Perfect recall on the fixture proves nothing about new notes.** Before
  jumping to embeddings, the right move is measuring this baseline against
  30-50 real labeled queries.

## Credits

Project structure, stages and original tests from
[rohitg00/ai-engineering-from-scratch](https://github.com/rohitg00/ai-engineering-from-scratch)
(MIT License, © 2026 Rohit Ghumare). The `main.py` implementation, sample
notes and this README are my own work as the learner.
