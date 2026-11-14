FROM kestra/kestra:v1.0.0@sha256:3eb172635bf54cfa8856ac633d4d76391da2c366a14e2e4ba760b96ec5b1759e
USER root
COPY requirements.txt /tmp/oulad-requirements.txt
RUN python3 -m pip install --no-cache-dir --only-binary=:all: --require-hashes --target /opt/oulad-deps -r /tmp/oulad-requirements.txt
