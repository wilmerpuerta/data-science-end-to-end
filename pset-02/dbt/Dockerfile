FROM python:3.11.13-slim-bookworm@sha256:cec9aa7aa96eea4fa036e9b82be1e6b325f2e3707f462d885868df51ec0a4b47
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DBT_SEND_ANONYMOUS_USAGE_STATS=false \
    DBT_PROFILES_DIR=/workspace/dbt
WORKDIR /workspace/dbt
COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir --only-binary=:all: --require-hashes -r /tmp/requirements.txt
RUN useradd --create-home --uid 10001 runner
USER runner
ENTRYPOINT ["dbt"]
CMD ["--version"]
