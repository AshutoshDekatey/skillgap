# SkillGap — Personalized Learning V3

SkillGap V3 is a three-user Streamlit learning system with diagnostic-led adaptive practice.

## Accounts and learning paths

| Learner | Demo password | V3 learning path | Questions |
|---|---|---|---:|
| Ashutosh | `Ashutosh` | SQL, Pandas and Python Data Analysis | 100 |
| Aakash | `Aakash` | Terraform, Microservices and SDLC | 100 |
| Neeraj | `Neeraj` | Capital Markets, Payments and Private Equity | 100 |

The passwords are intentionally simple demonstration credentials. Use a real authentication provider before opening the app to untrusted users.

## V3 behavior

- 300 total questions
- 10 measurable skills and 100 questions per learner
- 20-question diagnostic for each learner
- Recommended 10-question practice sessions
- Weak skills from the diagnostic are ranked first
- Every incorrectly answered question remains eligible and is promoted in later sessions
- Once a question is answered correctly, it never appears again for that learner
- Every answer has a concise explanation
- Separate progress, question history and mastery for each account
- Blue-violet animated mastery dashboard
- V3 starts with a new database file, so all three accounts begin fresh

## Question-bank design

Each learning path contains 10 skills. Every skill has five curated concept cards. Each concept produces:

1. A definition-selection question
2. A concept-recognition question

This produces 10 questions per skill and 100 per learner. Options are deterministically shuffled, so they remain stable across deployments.

## Adaptive selection

After the 20-question diagnostic, the engine calculates mastery for each skill using unique questions attempted and resolved. The next session excludes every question ever answered correctly, then ranks the remaining questions by:

1. Low skill mastery
2. Whether the question is an unresolved wrong answer
3. Number of previous attempts
4. Difficulty

Wrong answers receive a strong retry priority. Once the learner answers that question correctly, it is permanently retired.

## Fresh V3 data

V3 writes to:

```text
.data/skillgap_v3.db
```

This is intentionally different from the V1/V2 database filename. Existing histories therefore do not carry into V3.

Do not commit the `.data` directory. The included `.gitignore` already excludes it.

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

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Create V3 on GitHub

1. Keep the existing V1 and V2 releases/tags unchanged.
2. Create a branch named `v3` from `main`.
3. Extract `skillgap-v3.zip`.
4. Replace the application files in the repository root with the extracted V3 files.
5. Do not upload `.data`, `.venv`, `__pycache__`, or `.streamlit/secrets.toml`.
6. Commit the files to the `v3` branch.
7. Create a temporary Streamlit deployment pointed at the `v3` branch and `app.py`.
8. Test the diagnostic and practice flow using all three accounts.
9. Merge `v3` into `main` after verification.
10. Create a GitHub release tagged `v3.0.0`.

## Existing Streamlit deployment

If the app is already connected to the repository's `main` branch, merging V3 into `main` should trigger redeployment. Confirm in **Manage app** that:

- Repository is correct
- Branch is `main`
- Main file path is `app.py`

Reboot the app if it does not pick up the new commit.

## Persistence and concurrency

SQLite with WAL mode and a 15-second connection timeout is adequate for this controlled three-user beta. Hosting-local files should not be treated as durable production storage. For persistent public use, move `users` and `attempts` to PostgreSQL, Supabase, Neon or AWS RDS.

## Files

```text
skillgap-v3/
├── app.py
├── engine.py
├── questions.py
├── storage.py
├── CONTENT_SOURCES.md
├── requirements.txt
├── tests/
│   └── test_engine.py
└── README.md
```
