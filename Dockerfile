# 1. Base Image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# 2. System dependencies (LightGBM requires libgomp1)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 3. Copying Model and Application Code
COPY . .

# 4. Dependencies
RUN pip install --no-cache-dir -r requirements_docker.txt

# 5. Exposing Port
EXPOSE 8000

# 6. Running FastAPI with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
