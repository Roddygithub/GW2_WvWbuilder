FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.5.1

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml ./

# Project initialization
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy project
COPY . .

# Install the project in the container
RUN poetry install --no-interaction --no-ansi

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
