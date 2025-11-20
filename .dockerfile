# 1. Start from the official Python image
FROM python:3.12-slim

# 2. Set working directory
WORKDIR /app

# 3. System dependencies for science libs & build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential gcc && \
    rm -rf /var/lib/apt/lists/*

# 4. Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copy app code
COPY ./src ./src
COPY ./models ./models

# 6. Expose port for FastAPI
EXPOSE 8000

# 7. Run FastAPI app (change main:app to your entrypoint if different)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
