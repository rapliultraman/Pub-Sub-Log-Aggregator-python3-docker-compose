FROM python:3.11-slim

WORKDIR /app

COPY publisher.py .

RUN pip install --no-cache-dir requests

CMD ["python", "publisher.py"]