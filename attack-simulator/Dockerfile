FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY simulator.py .

ENTRYPOINT ["python", "simulator.py"]
# Default arguments can be overridden on `docker compose run`
CMD ["--target", "http://target-app:8000", "--attack", "all", "--attempts", "20", "--delay", "0.5"]
