FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run automatically handles the port, but we'll expose the app's internal port

EXPOSE 8080 

# Note: In your code, ensure the app runs on port 8080 (Cloud Run's default)

CMD ["python", "writer.py"]