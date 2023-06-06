import socket
import traceback


def ping_status(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except Exception as e:
        traceback.format_exc()
        return False
