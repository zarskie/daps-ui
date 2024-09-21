# # syntax=docker/dockerfile:1

# FROM python:3.10-slim

# WORKDIR /code

# RUN apt-get update && apt-get upgrade -y && apt-get install -y

# # COPY (TODO poetry stuff)

# COPY . .

# CMD ["flask", "--app", "daps_webui", "run", "--debug"]

# syntax=docker/dockerfile:1

FROM python:3.10-slim

WORKDIR /code

# Install system dependencies and Poetry
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy the Poetry lock and pyproject files first to cache dependencies
COPY pyproject.toml poetry.lock ./

# Install dependencies using Poetry
RUN poetry install --no-root

# Copy the rest of the application code
COPY . .

# Run the Flask app
CMD ["poetry", "run", "flask", "--app", "daps_webui", "run", "--host=0.0.0.0", "--debug"]
# CMD ["poetry", "run", "gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "daps_webui:app"]
