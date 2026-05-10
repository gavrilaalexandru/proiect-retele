import socket
import threading
import json
import os

HOST = "127.0.0.1"
PORT = 5000


def send(sock, obj):
    sock.sendall((json.dumps(obj) + "\n").encode())


def listen(sock):
    buf = ""
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break
            buf += data.decode()

            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                if not line.strip():
                    continue

                response = json.loads(line)
                print("\nSERVER:", response)

                if (
                    response.get("type") == "error"
                    and response.get("message") == "User taken"
                ):
                    print(
                        "Username already used. Restart client with another username."
                    )
                    sock.close()
                    os._exit(0)
        except:
            break


def main():
    user = input("username: ")

    s = socket.socket()
    s.connect((HOST, PORT))

    send(s, {"type": "connect", "username": user})

    threading.Thread(target=listen, args=(s,), daemon=True).start()

    while True:
        print("\n1 list\n2 create\n3 delete\n4 sub\n5 unsub\n6 news\n7 exit")
        c = input("> ")

        if c == "1":
            send(s, {"type": "list"})

        elif c == "2":
            send(
                s,
                {
                    "type": "create",
                    "name": input("name: "),
                    "description": input("desc: "),
                },
            )

        elif c == "3":
            send(s, {"type": "delete", "name": input("name: ")})

        elif c == "4":
            send(s, {"type": "sub", "channel": input("channel: ")})

        elif c == "5":
            send(s, {"type": "unsub", "channel": input("channel: ")})

        elif c == "6":
            send(
                s,
                {
                    "type": "news",
                    "channel": input("channel: "),
                    "content": input("content: "),
                },
            )

        elif c == "7":
            break


if __name__ == "__main__":
    main()
