# Contributing

```bash
pip install -r requirements-dev.txt
pytest                                                   # must pass
flake8 api tests --select=E9,F63,F7,F82                  # must be clean
```

- Add a test for any behavior change. Tests live in `tests/` and use temporary state, never your real key files.
- Keep secrets out of the repository. State files and `.env` are already git-ignored.
- Start the server from the repository root: `uvicorn api.main:app --reload`.
