# Pandas GapMap — V1

A personalized Streamlit learning beta focused on practical Pandas data cleaning.

## What V1 includes

- A 16-question diagnostic across eight skills
- An explainable mastery score for every skill
- Adaptive practice that prioritizes weak and under-tested topics
- Confidence-aware attempt tracking
- A dashboard with strengths, weaknesses and a readiness index
- A CSV lab that profiles missing values, duplicates, types and cardinality
- Safe cleaning operations and a cleaned-CSV download
- SQLite persistence for multiple named learners
- 32 reviewed questions with explanations

## Demo users

| User | Password | Initial learning path |
|---|---|---|
| Ashutosh | `Ashutosh` | Financial data |
| Aakash | `Aakash` | Data analysis |
| Neeraj | `Neeraj` | Business reporting |

Progress is stored independently for each user. Their diagnostic answers—not the initial path label—drive their personal mastery map and adaptive practice queue.

These are deliberately simple demonstration credentials. Before publishing the app to untrusted users, replace them with a real authentication provider and never store plain-text passwords in source code.

V1 intentionally has no AI API dependency. The recommendation logic is visible in `engine.py`, making it easier to understand and test before adding an AI tutor.

## Project structure

```text
pandas-gapmap-v1/
├── app.py            # Streamlit pages and interface
├── engine.py         # Mastery and adaptive-practice rules
├── questions.py      # Tagged question bank
├── storage.py        # SQLite persistence
├── tests/
│   └── test_engine.py
├── requirements.txt
└── README.md
```

## Run locally

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy from GitHub with Streamlit Community Cloud

1. Create a GitHub repository and upload all project files.
2. Open Streamlit Community Cloud and choose **Create app**.
3. Select the repository, branch and `app.py` entry point.
4. Deploy. V1 requires no API secrets.

SQLite files on community hosting may be reset when the application restarts or redeploys. For a durable public beta, replace SQLite with PostgreSQL or Supabase.

## How personalization works

Every question is tagged by skill and difficulty. Each answer creates an attempt containing correctness, confidence, mode and timestamp. `get_mastery()` calculates a confidence-adjusted score with a neutral prior, and `build_practice_queue()` ranks questions by:

1. Lowest skill mastery
2. Whether the question is unseen
3. Question difficulty

This is intentionally rules-based. Once real usage data exists, later versions can introduce spaced repetition, item calibration and AI-generated coaching.

## Sensible V2 additions

- PostgreSQL and authenticated accounts
- Short code-writing exercises in a sandbox
- AI hints that do not reveal the answer immediately
- A daily learning plan and spaced repetition
- More question variants and real-world datasets
- Goal-specific paths for financial analysis and business reporting
- Admin tools for reviewing questions and user feedback
