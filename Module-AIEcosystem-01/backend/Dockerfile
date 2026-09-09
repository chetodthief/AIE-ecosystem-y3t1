FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install torch CPU first to avoid downloading full CUDA binaries
RUN pip install --no-cache-dir torch --extra-index-url https://download.pytorch.org/whl/cpu

# Copy pyproject.toml and install python requirements for API
RUN pip install --no-cache-dir \
    "typing-extensions>=4.8.0" \
    fastapi \
    "uvicorn[standard]" \
    arq \
    minio \
    datasets \
    mlflow-skinny==2.11.3 \
    boto3 \
    "transformers<4.45.0" \
    pydantic \
    "pydantic[email]" \
    email-validator \
    pydantic-settings \
    bcrypt \
    "passlib[bcrypt]" \
    psycopg2-binary \
    sqlalchemy \
    pyjwt \
    label-studio-sdk

# Copy application source code
COPY . /app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
