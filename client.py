#!/usr/bin/env python3
import socket
import sys

HOST = "localhost"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 50000
BUF_SIZE = 8192
AUTH_NAME = "asma"

sock = socket.socket()
sock.settimeout(2)
sock.connect((HOST, PORT))

def send(msg):
    sock.sendall((msg + "\n").encode())

def receive():
    data = b""
    while True:
        try:
            part = sock.recv(BUF_SIZE)
        except socket.timeout:
            break

        data += part

        if len(part) < BUF_SIZE:
            break

    return data.decode().strip()

def get_servers(command):
    send(command)
    header = receive()

    if not header.startswith("DATA"):
        return []

    send("OK")
    data = receive()

    servers = []

    for line in data.splitlines():
        line = line.strip()

        if not line or line == "." or line == "OK":
            continue

        parts = line.split()

        if len(parts) < 9:
            continue

        try:
            servers.append({
                "type": parts[0],
                "id": int(parts[1]),
                "state": parts[2],
                "cores": int(parts[4]),
                "memory": int(parts[5]),
                "disk": int(parts[6]),
                "waiting": int(parts[7]),
                "running": int(parts[8])
            })
        except ValueError:
            continue

    send("OK")
    receive()

    return servers

def dominant_resource_ratio(server, job):
    if server["cores"] <= 0 or server["memory"] <= 0 or server["disk"] <= 0:
        return 1

    return max(
        job["cores"] / server["cores"],
        job["memory"] / server["memory"],
        job["disk"] / server["disk"]
    )

def resource_waste(server, job):
    return (
        server["cores"] - job["cores"],
        server["memory"] - job["memory"],
        server["disk"] - job["disk"]
    )

def choose_server(job):
    cores = job["cores"]
    memory = job["memory"]
    disk = job["disk"]
    runtime = job["runtime"]

    available = get_servers(f"GETS Avail {cores} {memory} {disk}")

    if available:
        def available_score(s):
            queue = s["waiting"] + s["running"]
            core_waste, mem_waste, disk_waste = resource_waste(s, job)
            fit = 1 - dominant_resource_ratio(s, job)
            active_penalty = 0 if s["state"] == "active" else 1

            if runtime <= 300:
                return (
                    active_penalty,
                    queue,
                    fit,
                    core_waste,
                    mem_waste,
                    disk_waste,
                    s["id"]
                )

            if runtime <= 1200:
                return (
                    fit,
                    core_waste,
                    active_penalty,
                    queue,
                    mem_waste,
                    disk_waste,
                    s["id"]
                )

            return (
                active_penalty,
                queue,
                fit,
                core_waste,
                mem_waste,
                disk_waste,
                s["id"]
            )

        available.sort(key=available_score)
        return available[0]

    capable = get_servers(f"GETS Capable {cores} {memory} {disk}")

    if capable:
        def capable_score(s):
            queue = s["waiting"] + s["running"]
            core_waste, mem_waste, disk_waste = resource_waste(s, job)
            fit = 1 - dominant_resource_ratio(s, job)
            active_penalty = 0 if s["state"] in ("active", "booting") else 1

            if runtime <= 300:
                return (
                    queue,
                    active_penalty,
                    fit,
                    core_waste,
                    mem_waste,
                    disk_waste,
                    s["id"]
                )

            if runtime <= 1200:
                return (
                    fit,
                    core_waste,
                    queue,
                    active_penalty,
                    mem_waste,
                    disk_waste,
                    s["id"]
                )

            return (
                queue,
                active_penalty,
                fit,
                core_waste,
                mem_waste,
                disk_waste,
                s["id"]
            )

        capable.sort(key=capable_score)
        return capable[0]

    return None

def main():
    send("HELO")
    receive()

    send(f"AUTH {AUTH_NAME}")
    receive()

    while True:
        send("REDY")
        msg = receive()

        if msg.startswith("JOBN"):
            parts = msg.split()

            job = {
                "id": int(parts[1]),
                "submit_time": int(parts[2]),
                "cores": int(parts[3]),
                "memory": int(parts[4]),
                "disk": int(parts[5]),
                "runtime": int(parts[6])
            }

            server = choose_server(job)

            if server is not None:
                send(f"SCHD {job['id']} {server['type']} {server['id']}")
                receive()

        elif msg.startswith("JCPL"):
            continue

        elif msg.startswith("NONE"):
            break

    send("QUIT")
    receive()
    sock.close()

if __name__ == "__main__":
    main()