FROM python:3.9-slim-buster

RUN apt-get update \
    && apt-get install -y --fix-missing build-essential \
    && apt-get install -y --no-install-recommends curl \
    && apt-get install -y --fix-missing default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY . .

# Expose the port on which your FastApi App will run
EXPOSE 8000

# Start the FastApi app
CMD ["python", "entry.py"]
