FROM spark:3.5.6-scala2.12-java17-python3-ubuntu@sha256:fee303e5788e8f3875aac670611f0be12012e866f09147ad59386d5e6239232c
USER root
COPY requirements.txt /tmp/oulad-requirements.txt
RUN python3 -m pip install --no-cache-dir --target /opt/oulad-deps --only-binary=:all: --require-hashes -r /tmp/oulad-requirements.txt
COPY jars.lock.json fetch_jars.py /tmp/oulad-jars/
RUN python3 /tmp/oulad-jars/fetch_jars.py /tmp/oulad-jars/jars.lock.json /opt/spark/oulad-jars
# Sustituir Commons Lang, dependencia provided 3.18.0 del conector.
RUN python3 -c "from pathlib import Path; import shutil; [p.unlink() for p in Path('/opt/spark/jars').glob('commons-lang3-*.jar')]; shutil.copy('/opt/spark/oulad-jars/commons-lang3-3.18.0.jar','/opt/spark/jars/commons-lang3-3.18.0.jar')"
ENV PYTHONPATH=/opt/oulad-deps \
    PYTHONDONTWRITEBYTECODE=1
USER 185
