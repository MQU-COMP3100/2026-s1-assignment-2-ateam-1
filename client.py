import socket
import sys

HOST = "localhost"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 50000
BUF_SIZE = 8192
AUTH_NAME = "ATeam"

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


def calculate_drfScore(server, job):
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


def available_score(server, job):
    runtime = job["runtime"]

    queue = server["waiting"] + server["running"]

    core_waste, mem_waste, disk_waste = resource_waste(server, job)

    fit = 1 - calculate_drfScore(server, job)

    active_penalty = 0 if server["state"] == "active" else 1

    if runtime <= 300:
        return (
            active_penalty,
            queue,
            fit,
            core_waste,
            mem_waste,
            disk_waste,
            server["id"]
        )

    if runtime <= 1200:
        return (
            fit,
            core_waste,
            active_penalty,
            queue,
            mem_waste,
            disk_waste,
            server["id"]
        )

    return (
        active_penalty,
        queue,
        fit,
        core_waste,
        mem_waste,
        disk_waste,
        server["id"]
    )


def capableScore(server, job):
    runtime = job["runtime"]

    queue = server["waiting"] + server["running"]

    core_waste, mem_waste, disk_waste = resource_waste(server, job)

    fit = 1 - calculate_drfScore(server, job)

    active_penalty = 0 if server["state"] in ("active", "booting") else 1

    if runtime <= 300:
        return (
            queue,
            active_penalty,
            fit,
            core_waste,
            mem_waste,
            disk_waste,
            server["id"]
        )

    if runtime <= 1200:
        return (
            fit,
            core_waste,
            queue,
            active_penalty,
            mem_waste,
            disk_waste,
            server["id"]
        )

    return (
        queue,
        active_penalty,
        fit,
        core_waste,
        mem_waste,
        disk_waste,
        server["id"]
    )


def select_server(job):
    cores = job["cores"]
    memory = job["memory"]
    disk = job["disk"]

    available = get_servers(f"GETS Avail {cores} {memory} {disk}")

    if available:
        available.sort(key=lambda s: available_score(s, job))
        return available[0]

    capable = get_servers(f"GETS Capable {cores} {memory} {disk}")

    if capable:
        capable.sort(key=lambda s: capableScore(s, job))
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

            server = select_server(job)

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