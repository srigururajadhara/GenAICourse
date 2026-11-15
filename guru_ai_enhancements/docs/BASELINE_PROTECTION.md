# Baseline Protection and Project Isolation

**Status:** Mandatory project constraint

## 1. Protected project

`GenAICourse/guru_ai` is the existing working baseline. It must not be edited as part of the enhancement requirements or development work.

Prohibited without separate explicit approval:

- Editing or replacing its `app.py`, API or core files.
- Overwriting its `.env`, `requirements.txt`, PDF collection, manifest or FAISS index.
- Running formatters, migrations, cleanup scripts or dependency updates against its directory.
- Using the baseline project's `data/` or `storage/` paths from the enhancement project.

## 2. Separate project

All enhancement source code will be placed in:

`GenAICourse/guru_ai_enhancements/`

The current package creates only documentation and empty folders. No implementation exists yet.

## 3. Shared Python environment

The product owner agreed to reuse:

`GenAICourse/venv312/`

Expected activation from the enhancement folder:

```bash
source ../venv312/bin/activate
```

Do not create a second virtual environment by default. Do not silently upgrade shared dependencies. Any dependency change must first be documented, checked for impact on the user's course notebooks and approved.

## 4. Separate runtime data and secrets

After implementation approval:

- Use `guru_ai_enhancements/.env` for project-specific configuration (never copy the secret file from baseline automatically).
- Use `guru_ai_enhancements/data/pdfs/` for enhancement test/source documents.
- Use `guru_ai_enhancements/storage/` for the enhanced index and manifest.
- Use project-root-relative paths and verify resolved paths at startup.
- Keep test fixtures separate from real farmer data.
- Keep `.env`, uploaded PDFs, index files and logs out of Git by default.

## 5. Baseline protection checks before and after each change

- Confirm current working directory is `guru_ai_enhancements`.
- Confirm `DATA_DIR` and `STORAGE_DIR` resolve under `guru_ai_enhancements`.
- Confirm no import or path points to `../guru_ai` as an application dependency.
- Run `git status` or equivalent to confirm only enhancement project files changed.
- Do not copy changes back to `guru_ai` unless the product owner approves a separate promotion request.

## 6. Promotion policy

The original project remains untouched even after enhancements pass. If later promotion is desired, prepare a separate change proposal describing the files to be copied/merged, test evidence, rollback plan and approval. Promotion is never automatic.
