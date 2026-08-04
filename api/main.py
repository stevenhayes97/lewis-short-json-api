"""FastAPI application entrypoint.

No routes yet — this module only constructs the app. Run later with:

    uvicorn api.main:app --reload

from the repository root (so both `api` and `tools` import cleanly).
"""

from fastapi import FastAPI

app = FastAPI(
    title="Lewis & Short Translation API",
    description=(
        "Look up a Latin or English word in Lewis & Short and return matching entries."
    ),
    version="0.1.0",
)
