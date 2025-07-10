FROM python:3.13.5-slim AS builder

ENV POETRY_VERSION=2.1.3
RUN pip install "poetry==$POETRY_VERSION"

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.MD

RUN poetry install --without dev --no-root --no-interaction && rm -rf $POETRY_CACHE_DIR


FROM python:3.13.5-slim AS runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV
COPY progandbot ./progandbot

ENTRYPOINT ["python", "-m", "progandbot"]
