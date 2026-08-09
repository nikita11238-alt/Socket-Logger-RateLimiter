#!/usr/bin/env python3
"""
server.py — TCP Socket Logger & Basic Rate Limiter
Listens for incoming TCP connections, tracks request frequencies per IP,
detects potential floods, and logs security events to disk.
"""
import os
import time
import socket
from datetime import datetime
from collections import defaultdict

# Configuration
HOST = '127.0.0.1'
PORT = 9000
MAX_REQUESTS = 5       # Max requests allowed within the time window
TIME_WINDOW = 10       # Time window in seconds
BLOCK_DURATION = 20    # Temporary block duration in seconds

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LOG_FILE = os.path.join(OUTPUT_DIR, "security_log.txt")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# State tracking dictionaries
client_history = defaultdict(list)  # IP -> list of request timestamps
blocked_ips = {}                    # IP -> unblock timestamp

def log_event(message):
    """Logs message with a timestamp to console and security_log.txt."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"
    print(log_line.strip())
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line)

def is_rate_limited(ip):
    """Checks if an IP has exceeded the request rate limit."""
    now = time.time()
    
    # Check if IP is currently blocked
    if ip in blocked_ips:
        if now < blocked_ips[ip]:
            return True
        else:
            del blocked_ips[ip]  # Unblock after duration expires

    # Clean up timestamps outside the time window
    client_history[ip] = [t for t in client_history[ip] if now - t < TIME_WINDOW]
    
    # Check frequency
    if len(client_history[ip]) >= MAX_REQUESTS:
        blocked_ips[ip] = now + BLOCK_DURATION
        log_event(f"[ALERT] Rate limit exceeded for {ip}! Temporarily blocked for {BLOCK_DURATION}s.")
        return True

    # Record current request time
    client_history[ip].append(now)
    return False

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    
    log_event(f"[*] Socket server listening on {HOST}:{PORT}")
    
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            client_ip = client_address[0]
            
            log_event(f"[+] Connection accepted from {client_ip}:{client_address[1]}")
            
            # Apply Rate Limiting check
            if is_rate_limited(client_ip):
                client_socket.sendall(b"HTTP/1.1 429 Too Many Requests\r\n\r\nRate limit exceeded. Try again later.\n")
                client_socket.close()
                continue

            try:
                data = client_socket.recv(1024)
                if data:
                    decoded_data = data.decode('utf-8', errors='ignore').strip()
                    log_event(f"    Data received from {client_ip}: {decoded_data[:100]}")
                
                client_socket.sendall(b"HTTP/1.1 200 OK\r\n\r\nRequest processed successfully.\n")
            except Exception as e:
                log_event(f"[-] Error handling client {client_ip}: {e}")
            finally:
                client_socket.close()
                
    except KeyboardInterrupt:
        log_event("[*] Server shutting down gracefully.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    run_server()
