# Single Stage Docker
FROM python:3.10-slim

# Set environment variables for Poetry

ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

ENV POETRY_HOME="/opt/poetry"

# Set environment variables for the application
ENV PYTHONPATH=/app

# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install Poetry
RUN pip install poetry

# Set working directory for the project
WORKDIR /app

# Copy pyproject.toml and poetry.lock to leverage Docker caching
COPY pyproject.toml poetry.lock ./

# Copy the rest of the application code
COPY . .

# Install project dependencies
# Use --no-root to avoid installing the project itself as a package during the build stage
RUN poetry install --no-root --no-interaction --no-ansi


# Expose the port FastAPI will run on
EXPOSE 8000

# Define the command to run your application
CMD ["poetry", "run", "python", "./src/main.py"]