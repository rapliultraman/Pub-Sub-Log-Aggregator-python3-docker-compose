FROM python:3.11-slim

RUN adduser --disabled-password --gecos '' appuser

WORKDIR /app
RUN mkdir -p /app/src /app/data /app/tests && chown -R appuser:appuser /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY tests ./tests

USER appuser

ENV PYTHONPATH=/app
ENV DB_PATH=/app/data/dedub.db

EXPOSE 8080

# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
# CMD ["pytest", "-v", "-s", "tests/test_app.py"]

CMD ["sh", "-c", "if [ \"$MODE\" = 'TEST' ]; then pytest -v -s; else uvicorn src.main:app --host 0.0.0.0 --port 8080; fi"]