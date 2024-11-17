FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY . .

EXPOSE 3000

CMD ["python", "main.py"]
