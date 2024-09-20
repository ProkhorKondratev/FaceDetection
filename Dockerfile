FROM python:3.12-slim

WORKDIR /app/

RUN apt-get update && apt-get install -y curl

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock* /app/
RUN poetry install --no-root

ENV PYTHONPATH=/app

COPY . /app

RUN ls -la /app

EXPOSE 8000
CMD ["fastapi", "run"]
