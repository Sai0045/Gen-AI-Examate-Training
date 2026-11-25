# syntax=docker/dockerfile:1

FROM python:3.14-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements-api.txt .

RUN --mount=type=bind,source=wheelhouse,target=/wheelhouse \
    pip install --no-cache-dir --no-index --find-links=/wheelhouse -r requirements-api.txt

COPY app/ ./app/
COPY data/ ./data/
COPY prompts/ ./prompts/

# Build the RAG index while creating the Docker image.
RUN python -m app.vectorstore

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
