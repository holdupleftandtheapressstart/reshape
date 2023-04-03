FROM python:3.10-bullseye

WORKDIR /app/

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry && \
    ./poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock ./

COPY app ./app
ENV PYTHONPATH=/app

# Install dependencies
RUN poetry install --no-dev

# Run the app
CMD ["poetry", "run", "uvicorn", "main:app"]
