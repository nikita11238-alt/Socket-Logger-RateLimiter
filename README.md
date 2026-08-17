# Socket-Logger-RateLimiter

A professional, low-level TCP socket server and logging utility written in Python. Designed for security analysis, this tool tracks incoming network connections, applies real-time rate limiting per IP address, and records security events.

## Features

* **Low-Level Socket Programming:** Uses Python's `socket` module to handle raw TCP connections.
* **IP-Based Rate Limiting:** Implements a sliding time window algorithm to detect and block flood/brute-force attempts.
* **Security Audit Logging:** Automatically logs all connection events and detected threats to `output/security_log.txt`.
* **Testing Suite:** Includes `client_simulator.py` to test both normal traffic and automated flood attacks.

## Project Structure

```text
Socket-Logger-RateLimiter/
├── server.py             ← Main TCP socket server & rate limiter
├── client_simulator.py   ← Traffic & flood attack testing tool
└── output/               ← Generated logs directory
    └── security_log.txt  ← Audit trail and security events
