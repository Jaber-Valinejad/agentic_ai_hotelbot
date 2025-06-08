FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Safer way to run uvicorn
CMD ["python", "-m", "uvicorn", "week7_main:app", "--host", "0.0.0.0", "--port", "8000"]