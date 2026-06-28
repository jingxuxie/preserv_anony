# Benchmark Quality Audit

Generated schema and integrity audit for the controlled benchmarks and handwritten stress slice.

## Schema Contract

- Each row has `id`, `domain`, `source`, `text`, `private_spans`, `task_critical_facts`, and `qa`.
- Each private span has `text`, `type`, `identifier_type`, and `replacement`; `identifier_type` is `DIRECT` or `QUASI`.
- Each task-critical fact has `type`, `fact`, and boolean `generalization_allowed`.
- Each QA item has `q`, `a`, and `answer_aliases`, with the canonical answer included in aliases.

## Inventory

| Split | Rows | Domains | Sources | Avg spans | Avg facts | Avg QA | Generalizable facts |
|---|---:|---|---|---:|---:|---:|---:|
| Main benchmark | 100 | clinical=50, legal=50 | TAB ECHR dev=6, TAB ECHR test=6, TAB ECHR train=38, synthetic clinical template=50 | 7.50 | 4.09 | 2.09 | 50 |
| Promoted n120 benchmark | 120 | clinical=60, legal=60 | TAB ECHR dev=7, TAB ECHR test=8, TAB ECHR train=45, synthetic clinical template=60 | 7.56 | 4.11 | 2.11 | 60 |
| Stress slice | 12 | clinical=6, legal=6 | handwritten stress slice=12 | 6.42 | 4.17 | 2.50 | 6 |

## Span and Fact Coverage

- Main identifier counts: DIRECT=459, QUASI=291.
- Promoted n120 identifier counts: DIRECT=549, QUASI=358.
- Stress identifier counts: DIRECT=45, QUASI=32.
- Main span types: DIRECT:CODE=54, DIRECT:DATE=50, DIRECT:EMAIL=50, DIRECT:ID=50, DIRECT:ORG=50, DIRECT:PERSON=155, DIRECT:PHONE=50, QUASI:AGE=50, QUASI:DATETIME=76, QUASI:DEM=29, QUASI:LOC=7, QUASI:LOCATION=50, QUASI:MISC=3, QUASI:OCCUPATION=50, QUASI:ORG=11, QUASI:PERSON=15.
- Main fact types: clinical:age=50, clinical:diagnosis=50, clinical:finding=50, clinical:symptom=50, clinical:test=50, clinical:treatment=50, legal:claim=40, legal:legal_basis=50, legal:outcome=19.
- Main QA-pair count distribution: 1=5, 2=81, 3=14.
- Stress tags are summarized in `results/robustness_report.md`.

## Integrity Checks

Status: PASS.

- IDs are unique within each split.
- Required row, span, fact, and QA keys are present.
- Every row has at least one direct identifier, one task-critical fact, and one QA pair.
- Private span texts are found in the source text.
- Task facts or their aliases are found in the source text.
- QA answers or their aliases are found in the source text.

## Paper Caveats

- Clinical rows are synthetic templates and should be described as controlled utility examples, not real clinical notes.
- Legal facts and QA are heuristic TAB-derived annotations with manual spot checks, not expert legal annotation.
- The stress slice is diagnostic and intentionally over-represents hard privacy-utility overlaps.
