# Data pipeline case studies

Batch pipelines from my data-engineering practice: extract, clean and quarantine bad rows, load a warehouse table and prove the numbers with a reconciliation. Each case says exactly which stages I wrote and what was checked.

| Case | Pattern | What I built | Tools | Difficulty |
|---|---|---|---|---|
| [Cleaning Up the Customer Feed Before It Hits the Warehouse](02-scd2-dimension/) | Dimension with history (SCD2) | the source extract in T-SQL, cleaning and quarantine in pandas, an SCD2 dimension load in T-SQL that is safe to re-run and a reconciliation report in Python | T-SQL, pandas, Python | 5.4/10 (Junior task) |

**Techniques, and the cases that show them**

- Cleaning and standardising values — [02](02-scd2-dimension/)
- De-duplication, latest version wins — [02](02-scd2-dimension/)
- Slowly changing dimension (SCD2) — [02](02-scd2-dimension/)
- Load that is safe to run twice — [02](02-scd2-dimension/)
- Reconciliation of counts and totals — [02](02-scd2-dimension/)

The reported figures come from PipelineFab's quality and reconciliation outputs. The scenarios and their synthetic data come from PipelineFab, a practice platform.
