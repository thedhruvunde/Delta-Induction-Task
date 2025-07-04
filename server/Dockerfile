FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip3 install --no-cache-dir psycopg2-binary colorama

CMD ["python", "scripts/server.py"]

COPY setup.sh /setup.sh
RUN chmod +x /setup.sh && /setup.sh
