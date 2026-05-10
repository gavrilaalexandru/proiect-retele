
import socket
import threading
import json

HOST = "0.0.0.0"
PORT = 5000

channels = {}
connected_clients = {}
client_sockets = {}

banned_words = ["bomb", "drugs", "violence", "terror"]

lock = threading.Lock()


def send_json(sock, data):
    try:
        sock.sendall((json.dumps(data) + "\n").encode())
    except:
        pass


def broadcast(data, exclude=None):
    with lock:
        for sock in list(connected_clients.keys()):
            if sock != exclude:
                send_json(sock, data)


def cleanup(sock):
    with lock:
        username = connected_clients.get(sock)

        if username:
            for ch in channels.values():
                if sock in ch["subscribers"]:
                    ch["subscribers"].remove(sock)

            connected_clients.pop(sock, None)
            client_sockets.pop(username, None)

        try:
            sock.close()
        except:
            pass


def contains_banned(text):
    text = text.lower()
    return any(w in text for w in banned_words)


def handle_create(sock, user, req):
    name = req.get("name")
    desc = req.get("description")

    if not name or not desc:
        send_json(sock, {"type": "error", "message": "Invalid data"})
        return

    with lock:
        if name in channels:
            send_json(sock, {"type": "error", "message": "Channel exists"})
            return

        channels[name] = {
            "description": desc,
            "owner": user,
            "subscribers": []
        }

    send_json(sock, {"type": "success", "message": "Channel created"})

    broadcast({
        "type": "channel_created",
        "name": name,
        "description": desc
    })


def handle_delete(sock, user, req):
    name = req.get("name")

    with lock:
        if name not in channels:
            send_json(sock, {"type": "error", "message": "Not found"})
            return

        if channels[name]["owner"] != user:
            send_json(sock, {"type": "error", "message": "Not owner"})
            return

        del channels[name]

    send_json(sock, {"type": "success", "message": "Deleted"})

    broadcast({"type": "channel_deleted", "name": name})


def handle_sub(sock, req):
    ch = req.get("channel")

    with lock:
        if ch not in channels:
            send_json(sock, {"type": "error", "message": "No channel"})
            return

        if sock not in channels[ch]["subscribers"]:
            channels[ch]["subscribers"].append(sock)

    send_json(sock, {"type": "success", "message": "Subscribed"})


def handle_unsub(sock, req):
    ch = req.get("channel")

    with lock:
        if ch in channels and sock in channels[ch]["subscribers"]:
            channels[ch]["subscribers"].remove(sock)

    send_json(sock, {"type": "success", "message": "Unsubscribed"})


def handle_news(sock, user, req):
    ch = req.get("channel")
    content = req.get("content")

    if not content:
        return

    with lock:
        if ch not in channels:
            send_json(sock, {"type": "error", "message": "No channel"})
            return

        if channels[ch]["owner"] != user:
            send_json(sock, {"type": "error", "message": "Not owner"})
            return

        if contains_banned(content):
            send_json(sock, {"type": "error", "message": "Blocked content"})
            return

        subs = list(channels[ch]["subscribers"])

    for s in subs:
        send_json(s, {
            "type": "news",
            "channel": ch,
            "content": content
        })

    send_json(sock, {"type": "success", "message": "Sent"})


def send_channels(sock):
    with lock:
        data = [
            {"name": k, "description": v["description"]}
            for k, v in channels.items()
        ]

    send_json(sock, {"type": "channels", "data": data})


def client_thread(sock):
    user = None
    buffer = ""

    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break

            buffer += data.decode()

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue

                req = json.loads(line)
                t = req.get("type")

                if t == "connect":
                    user = req.get("username")

                    with lock:
                        if user in client_sockets:
                            send_json(sock, {"type": "error", "message": "User taken"})
                            continue

                        connected_clients[sock] = user
                        client_sockets[user] = sock

                    send_channels(sock)

                elif t == "list":
                    send_channels(sock)

                elif t == "create":
                    handle_create(sock, user, req)

                elif t == "delete":
                    handle_delete(sock, user, req)

                elif t == "sub":
                    handle_sub(sock, req)

                elif t == "unsub":
                    handle_unsub(sock, req)

                elif t == "news":
                    handle_news(sock, user, req)

    except:
        pass
    finally:
        cleanup(sock)


def main():
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen()

    print("Server running on 5000")

    while True:
        c, _ = s.accept()
        threading.Thread(target=client_thread, args=(c,), daemon=True).start()


if __name__ == "__main__":
    main()
