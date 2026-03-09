FROM python:3.12-slim

WORKDIR /app

# Install build deps needed by some packages (bcrypt, lxml)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Persistent directories are mounted as volumes; create them so the
# image works standalone too (e.g. docker run without compose).
RUN mkdir -p data uploads

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
