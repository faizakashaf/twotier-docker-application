# Stage 1: Build Dependencies

FROM python:3.9-slim AS builder

WORKDIR /app

RUN apt-get update -y && apt-get install -y gcc python3-dev libpq-dev

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Production Image
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update -y && apt-get install -y libpq-dev postgresql-client && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY . .

EXPOSE 5000

CMD ["python3", "app.py"]
