# LangChain 1.x setup using the existing `venv312`

## Decision

Guru is configured for the existing shared Python 3.12 environment at `~/GenAICourse/venv312`. No new environment is required.

## Install / align dependencies

Run from VS Code Terminal:

```bash
cd ~/GenAICourse
source venv312/bin/activate
python -m pip freeze > ~/GenAICourse/venv312-before-guru-upgrade.txt
cd guru_ai
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip check
```

The current requirements align the LangChain package family on 1.x: `langchain`, `langchain-core`, `langchain-openai`, and `langchain-text-splitters`. LangChain 1.0 substantially changed its package namespace. Legacy chains, retrievers, indexes and hub helpers moved to `langchain-classic`; older notebooks may therefore require import updates, for example:

```python
# Older import
from langchain.chains import LLMChain

# LangChain v1 compatibility package
from langchain_classic.chains import LLMChain
```

Do not downgrade `langchain-core` to 0.3.x after this alignment, because installed LangGraph and LangChain-HuggingFace packages require Core 1.x.

## Current Guru integration note

The application imports `PyPDFLoader` and `FAISS` from `langchain-community`. LangChain's maintainers archived that package in June 2026. Version 0.4.2 is retained in this baseline only because those two integrations are currently used. Migrating away from that archived dependency should be handled as a separate change request with impact analysis and regression tests.

## Verify

```bash
python --version
python -m pip show langchain langchain-core langchain-community langchain-openai langchain-text-splitters
python -m pip check
python -m compileall -q api core app.py
```

Expected Python version: 3.12.x. `pip check` should report `No broken requirements found.` If it reports a conflict, share the complete output before attempting manual downgrades.

## Start Guru

Terminal 1:

```bash
cd ~/GenAICourse
source venv312/bin/activate
cd guru_ai
uvicorn api.main:app --reload --port 8000
```

Terminal 2:

```bash
cd ~/GenAICourse
source venv312/bin/activate
cd guru_ai
streamlit run app.py
```
