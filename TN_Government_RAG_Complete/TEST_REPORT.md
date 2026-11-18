# Build-time test report

This report records static checks performed while assembling the archive.

- Python source compilation: performed by the build process.
- Unit tests: performed by the build process.
- Live TN Government website crawl: not performed as part of archive assembly.
- Neo4j Aura connectivity / writes: not performed.
- OpenAI answer generation: not performed.
- Full scheme coverage: not verified.

After extracting the archive and configuring `.env`, run:

```bash
python -m compileall -q .
pytest -q
```

Then run discovery, crawling, ingestion and Streamlit as described in README.md.
