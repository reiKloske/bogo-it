
# Bogo-It!

A high-performance server-side array sorting & visualizer written in JavaScript, Python, and Rust. This project uses the  **BogoSort** algorithm to shuffle an array until it is sorted. 

*99% of Bogo Sorters quit right before they win big.*

## Stack

**Frontend:**
- **JavaScript (Vanilla):** Real-time rendering using Chart.js.
- **WebSockets:** Seamless, low-latency updates synced to your monitor's refresh rate (60Hz, 144Hz, 240Hz+).
- **Web Audio API:** Procedural sonification of shuffles.

**Backend:**
- **Python:** Flask server with Flask-SocketIO.
- **Rust Core:** High-performance sorting engine integrated via PyO3 for maximum shuffle throughput.
- **Gevent:** High-concurrency WebSocket engine.
- **SQLite:** Persistent state management to survive server restarts.

**Infrastructure:**
- **Docker & Docker Compose:** Containerized deployment with resource management.
- **GitHub Actions:** CI/CD pipeline with automated testing and Rust toolchain integration.

## Performance
By offloading the sorting logic to a compiled Rust extension, this version can perform **hundreds of thousands of shuffles per second** while remaining lightweight enough to run alongside other services on a 24/7 server.

## Live Version
[https://bogo.kloske.xyz/](https://bogo.kloske.xyz/)

![](https://github.com/reiKloske/bogo-it/raw/main/GIF.gif)
