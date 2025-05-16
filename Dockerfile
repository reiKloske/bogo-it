FROM python:3.13-slim

WORKDIR /app

RUN groupadd -r appgroup && useradd -r -g appgroup -s /sbin/nologin appuser

COPY . /app
RUN chown -R appuser:appgroup /app && \
    pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV FLASK_APP=main.py

USER appuser

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "wsgi:app"]
