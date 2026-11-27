# Data pipeline case studies

Batch pipelines from my data-engineering practice: extract, clean and quarantine bad rows, load a warehouse table and prove the numbers with a reconciliation. Each case says exactly which stages I wrote and what was checked.

| Pattern | Business problem | What I built | Tools | Difficulty |
|---|---|---|---|---|
| [Dimension with history (SCD2)](scd2-dimension/) | Cleaning Up the Customer Feed Before It Hits the Warehouse | the source extract in T-SQL, cleaning and quarantine in pandas, an SCD2 dimension load in T-SQL that is safe to re-run and a reconciliation report in Python | T-SQL, pandas, Python | 5.4/10 (Junior task) |

## How each case is organised

- `README.md` — the business problem, the architecture, my engineering decisions, data before and after, and the results.
- `src/` — the code I wrote, numbered by pipeline stage (01 extract … 05 reconcile). A missing number is a stage the platform wrote, such as the quality gate; the case README names it.
- `results/` — the quality and reconciliation reports the pipeline produced.

## Techniques, and the cases that show them

- Cleaning and standardising values — [Dimension with history (SCD2)](scd2-dimension/)
- De-duplication, latest version wins — [Dimension with history (SCD2)](scd2-dimension/)
- Slowly changing dimension (SCD2) — [Dimension with history (SCD2)](scd2-dimension/)
- Load that is safe to run twice — [Dimension with history (SCD2)](scd2-dimension/)
- Reconciliation of counts and totals — [Dimension with history (SCD2)](scd2-dimension/)

Every number in these READMEs comes from the pipeline's own reconciliation output. The scenarios and their synthetic data come from [PipelineFab](https://acbworkspace.netlify.app/#tours), the practice platform I built.
