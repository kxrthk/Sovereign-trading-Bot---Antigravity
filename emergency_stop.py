import os

def kill_switch():
    with open("STOP.flag", "w") as f:
        f.write("TERMINATE")
    print("[KILL] KILL SIGNAL SENT. BOT TERMINATING.")

if __name__ == "__main__":
    kill_switch()
