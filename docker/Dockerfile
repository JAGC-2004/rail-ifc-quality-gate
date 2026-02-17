FROM python:3.11-slim

WORKDIR /app
COPY . /app

# Install runtime deps
RUN pip install -U pip \
    && pip install -r requirements.txt \
    && pip install -e .

ENTRYPOINT ["rail-ifc-quality-gate"]
