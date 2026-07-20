import os
import urllib.request


def send_notification(title, channel, link):
    server = os.getenv("NTFY_SERVER")
    topic = os.getenv("NTFY_TOPIC")

    if not server or not topic:
        print("NTFY no configurado")
        return

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
        urllib.request.urlopen(req)
        print("Notificación enviada")
    except Exception as e:
        print(e)
