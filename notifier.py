import os
import urllib.request


def send_notification(title, channel, link):
    server = os.getenv("NTFY_SERVER")
    topic = os.getenv("NTFY_TOPIC")

    if not server or not topic:
        print("NTFY no configurado")
        return False

    body = f"""📺 {channel}

{title}

{link}
"""

    req = urllib.request.Request(
        f"{server}/{topic}",
        data=body.encode("utf-8"),
        method="POST"
    )

    req.add_header("Title", "ARGOS")
    req.add_header("Priority", "default")
    req.add_header("Tags", "tv")

    try:
        print(f"Enviando a: {server}/{topic}")

        with urllib.request.urlopen(req) as response:
            print(f"Notificación enviada ({response.status})")
            return True
                                   
    except Exception as e:
        print(f"Error enviando notificación: {type(e).__name__}: {e}")
        return False
