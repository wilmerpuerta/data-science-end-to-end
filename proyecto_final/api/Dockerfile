FROM python:3.11-slim@sha256:07d4824036af339fa1b6ef769cc99d9c10a141769538b52b3b597c84f7a7b535
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
WORKDIR /app
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --only-binary=:all: --require-hashes -r /tmp/requirements.txt && pip check
COPY api/main.py api/esquemas.py ./api/
COPY src/datos.py src/pipeline.py src/reentrenar.py ./src/
COPY tests/test_contrato.py tests/test_modelo.py tests/test_comportamiento.py ./tests/
COPY tests/fixtures ./tests/fixtures
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=10s --retries=8 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/salud')"
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
