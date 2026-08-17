#!/usr/bin/env python3
"""
client_simulator.py — Client Simulator & Flood Tester
Connects to the socket server, sends regular requests, 
and simulates a rapid burst/flood attack to test the rate limiter.
"""
import socket
import time

HOST = '127.0.0.1'
PORT = 9000

def send_request(message):
    """Sends a single TCP request to the server and prints the response."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(message.encode('utf-8'))
            response = s.recv(1024)
            print(f"    [Server Response] {response.decode('utf-8', errors='ignore').strip()}")
    except ConnectionRefusedError:
        print("    [-] Connection refused. Make sure server.py is running!")
    except Exception as e:
        print(f"    [-] Error: {e}")

def simulate_normal_traffic():
    print("\n--- Phase 1: Sending Normal Traffic ---")
    for i in range(3):
        print(f"Sending request #{i+1}...")
        send_request(f"GET /item/{i+1} HTTP/1.1")
        time.sleep(1.5)  # Safe delay between requests

def simulate_flood_attack():
    print("\n--- Phase 2: Simulating Flood / Brute-Force Attack ---")
    print("Sending a rapid burst of requests to trigger rate limiting...")
    for i in range(8):
        print(f"Burst request #{i+1}...")
        send_request(f"POST /login HTTP/1.1 attempt_{i+1}")

if __name__ == "__main__":
    print("[*] Starting client simulator...")
    time.sleep(1)
    
    # 1. Normal traffic (should all succeed with 200 OK)
    simulate_normal_traffic()
    
    time.sleep(2)
    
    # 2. Flood traffic (should trigger 429 Too Many Requests and IP block)
    simulate_flood_attack()
