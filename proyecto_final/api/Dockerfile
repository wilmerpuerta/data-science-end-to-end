FROM python:3.11-slim@sha256:07d4824036af339fa1b6ef769cc99d9c10a141769538b52b3b597c84f7a7b535 AS api
ENV PYTHONPATH=/app PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
WORKDIR /app
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --only-binary=:all: --require-hashes -r /tmp/requirements.txt && pip check
COPY requirements.txt ./requirements.txt
COPY api/Dockerfile ./api/Dockerfile
COPY api/main.py api/esquemas.py ./api/
COPY src/datos.py src/pipeline.py src/reentrenar.py ./src/
COPY tests/test_contrato.py tests/test_modelo.py tests/test_comportamiento.py ./tests/
COPY tests/fixtures ./tests/fixtures
COPY monitoreo/deriva.py monitoreo/alertas.py ./monitoreo/
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=10s --retries=8 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/salud')"
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM kestra/kestra:v1.0.0@sha256:3eb172635bf54cfa8856ac633d4d76391da2c366a14e2e4ba760b96ec5b1759e AS kestra
USER root
COPY spark/requirements.txt /tmp/operacion-requirements.txt
RUN python3 -m pip install --no-cache-dir --only-binary=:all: --require-hashes --target /opt/oulad-deps -r /tmp/operacion-requirements.txt
ENV PYTHONPATH=/opt/oulad-deps:/workspace PYTHONDONTWRITEBYTECODE=1 PSET4_API_URL=http://api:8000
WORKDIR /workspace
