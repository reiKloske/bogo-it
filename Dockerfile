FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:${PATH}"

RUN groupadd -r appgroup && useradd -r -g appgroup -s /sbin/nologin appuser

COPY . /app
RUN chown -R appuser:appgroup /app && \
    pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

RUN cd bogo_rust && cargo build --release && cp target/release/libbogo_rust.so ../bogo_rust.so

EXPOSE 5000

ENV FLASK_APP=main.py

USER appuser

CMD ["gunicorn", "--worker-class", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-w", "1", "-b", "0.0.0.0:5000", "wsgi:app"]
