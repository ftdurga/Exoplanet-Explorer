FROM python:3.12-slim

WORKDIR /app

# Copy the requirements first: Docker caches this layer, so rebuilds are fast
# unless the dependencies change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# 0.0.0.0 is required inside a container. The default (127.0.0.1) is only
# reachable from inside the container itself.
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]