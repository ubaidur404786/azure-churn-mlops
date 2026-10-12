# Start from a small official Python image
FROM python:3.12-slim

# Work inside the /app folder in the container
WORKDIR /app

# Install the API packages first (this layer is cached between builds)
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Copy the API code and the trained model
COPY src/ src/
COPY model/ model/

# Run as a normal user, not as root
RUN useradd --create-home appuser
USER appuser

# The API listens on port 8000
EXPOSE 8000

# Start the API
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
