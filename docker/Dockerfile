FROM python:3.12-slim-bullseye

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN python -m pip install "poetry" --break-system-packages
RUN python -m venv venv

COPY poetry.lock pyproject.toml ./
RUN . /venv/bin/activate && poetry install --only main --no-root

COPY src ./app
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

