import socket
import sys
import threading
import argparse
from datetime import datetime

# COLORS (ANSI) #
RESET = "\033[0m"
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"

# CLIENT STATE #
state = {
    "nick": None,
    "channel": None,
    "connected": False
}

# UTILS #
def timestamp():
    return datetime.now().strftime("%H:%M:%S")

def log(msg, color=RESET):
    print(f"{color}[{timestamp()}] {msg}{RESET}")

# RECEIVE LOOP #
def receive_messages(sock):
    while True:
        try:
            data = sock.recv(4096).decode("utf-8", errors="ignore")
            if not data:
                break

            for line in data.split("\r\n"):
                if not line:
                    continue

                # PING -> PONG
                if line.startswith("PING"):
                    response = line.replace("PING", "PONG")
                    sock.sendall((response + "\r\n").encode())
                    log("PING received → PONG sent", YELLOW)
                    continue

                parts = line.split()

                # PRIVMSG
                if "PRIVMSG" in parts:
                    prefix = parts[0]
                    sender = prefix.split("!")[0][1:]
                    msg = line.split(" :", 1)[1]
                    log(f"<{sender}> {msg}", GREEN)

                # JOIN
                elif "JOIN" in parts:
                    user = parts[0].split("!")[0][1:]
                    channel = parts[-1]
                    log(f"{JOIN_ICON(user)} joined {channel}", BLUE)

        except Exception:
            break

# SEND LOOP #
def send_messages(sock):
    while True:
        try:
            msg = input()

            if msg.startswith("/join"):
                _, channel = msg.split(maxsplit=1)
                state["channel"] = channel
                sock.sendall(f"JOIN {channel}\r\n".encode())
                log(f"Joined {channel}", BLUE)

            elif msg.startswith("/quit"):
                sock.sendall(b"QUIT :Bye\r\n")
                log("Disconnected", RED)
                sock.close()
                sys.exit(0)

            else:
                if state["channel"]:
                    sock.sendall(
                        f"PRIVMSG {state['channel']} :{msg}\r\n".encode()
                    )
                else:
                    log("You are not in a channel. Use /join #channel", RED)

        except Exception:
            break

# MAIN #
def main():
    parser = argparse.ArgumentParser(description="Minimal IRC Client (Raw Sockets)")
    parser.add_argument("--server", default="irc.libera.chat")
    parser.add_argument("--port", type=int, default=6667)
    parser.add_argument("--nick", required=True)
    parser.add_argument("--channel", default=None)

    args = parser.parse_args()

    state["nick"] = args.nick
    state["channel"] = args.channel

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((args.server, args.port))
    state["connected"] = True

    log(f"Connected to {args.server}:{args.port}", BLUE)

    # Handshake
    sock.sendall(f"NICK {args.nick}\r\n".encode())
    sock.sendall(f"USER {args.nick} 0 * :{args.nick}\r\n".encode())

    if args.channel:
        sock.sendall(f"JOIN {args.channel}\r\n".encode())
        log(f"Auto-joined {args.channel}", BLUE)

    # Threads
    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()
    send_messages(sock)

# HELPERS #
def JOIN_ICON(user):
    return f"{YELLOW}{user}{RESET}"

if __name__ == "__main__":
    main()