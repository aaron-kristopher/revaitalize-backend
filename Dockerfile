FROM python:3.9-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Install uv directly via pip to bypass the ghcr.io network timeout
RUN pip install --no-cache-dir uv

WORKDIR /app

COPY requirements.txt .

# Use uv to install dependencies into the system python environment
RUN uv pip install --system --no-cache -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
