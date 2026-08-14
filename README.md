# SkillGap — Personalized Learning V2

SkillGap is a multi-user Streamlit beta that diagnoses topic-level weaknesses and builds a focused practice session for each learner.

## V2 learning paths

| Learner | Password | Learning path |
|---|---|---|
| Ashutosh | `Ashutosh` | Pandas & Data Cleaning |
| Aakash | `Aakash` | Terraform Foundations |
| Neeraj | `Neeraj` | Capital Markets |

These are demonstration credentials. Replace them with proper authentication before allowing untrusted public access.

## What changed from V1

- Separate subject, skill map and question bank for each learner
- 54 readable questions: 18 per learning path
- 12-question diagnostic for every path
- Minimal white, blue and violet interface
- Animated mastery bars
- Clickable five-question recommended session on the dashboard
- Immediate before/after readiness recalculation when practice is completed
- CSV Lab removed
- Track-aware SQLite persistence prevents subjects from affecting one another
- No external API key required

## Project structure

```text
skillgap-v2/
├── app.py
├── engine.py
├── questions.py
├── storage.py
├── requirements.txt
├── tests/
│   └── test_engine.py
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

Run the included tests:

```bash
python -m unittest discover -s tests -v
```

## Replace V1 in an existing GitHub repository

1. Download and extract `skillgap-v2.zip`.
2. In your GitHub repository, delete the old application files: `app.py`, `engine.py`, `questions.py`, `storage.py`, `requirements.txt`, and the old `tests` folder.
3. Upload the extracted V2 files and folders into the repository root.
4. Do **not** upload `.data/progress.db`, `.venv`, `__pycache__`, or `.streamlit/secrets.toml`.
5. Commit directly to your intended branch, or create a V2 branch first if you want V1 preserved.

Recommended preservation workflow:

1. On the repository's **Releases** page, confirm the V1 release/tag exists.
2. Create a branch named `v2` from `main`.
3. Replace the files on the `v2` branch and test the deployment.
4. Merge `v2` into `main` after verification.
5. Create a GitHub release tagged `v2.0.0`.

## Deploy with Streamlit Community Cloud

### Existing app

If the Streamlit app already points to this repository and `app.py`, a push to its configured branch normally triggers a redeploy automatically.

1. Open the app in Streamlit Community Cloud.
2. Open **Manage app** and confirm the repository, branch, and entry point are correct.
3. The entry point must be `app.py`.
4. Reboot the app if the new commit is not picked up automatically.
5. Sign in once as each user and confirm that the displayed path is correct.

### New V2 test deployment

1. Open Streamlit Community Cloud and select **Create app**.
2. Choose the GitHub repository.
3. Choose the `v2` branch.
4. Set the main file path to `app.py`.
5. Deploy and test all three accounts.

## Persistence limitation

The app stores progress in SQLite. On Streamlit Community Cloud, local files can be reset during restart or redeployment. For durable public progress, move the `users` and `attempts` tables to PostgreSQL, Supabase, Neon, or another persistent database.

## How the recommended session works

The engine ranks questions using:

1. Current mastery of the tagged skill
2. Whether the learner has already seen the question
3. Whether the question belongs to the diagnostic
4. Question difficulty

It selects five questions, records each answer, then recalculates the dashboard. A score can rise or be recalibrated downward depending on performance; it is not increased artificially for completion alone.
