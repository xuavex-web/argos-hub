import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

from state import load_state, save_state
from notifier import send_notification

INPUT = "podcast_feeds.txt"
OUTPUT = "argos_podcasts.xml"


def get_feed_urls():
    with open(INPUT, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def get_date(item):
    try:
        return parsedate_to_datetime(item["published"])
    except Exception:
        try:
            return datetime.fromisoformat(
                item["published"].replace("Z", "+00:00")
            )
        except Exception:
            return datetime.min


def main():

    state = load_state()

    if "podcasts" not in state:
        state["podcasts"] = {}

    videos = []

    for feed_url in get_feed_urls():

        try:
            data = urllib.request.urlopen(
                feed_url,
                timeout=10
            ).read()

            root = ET.fromstring(data)

            channel = root.find("channel")

            if channel is None:
                continue

            channel_name = channel.findtext(
                "title",
                "Podcast desconocido"
            )

            items = channel.findall("item")

            print(
                channel_name,
                "episodios encontrados:",
                len(items)
            )

            guardado = state["podcasts"].get(channel_name)

            # Primera ejecución
            if guardado is None:

                historial = []

                for item in items[:20]:
                    link = item.findtext("link", "")

                    if not link:
                        link = item.findtext("guid", "")

                    historial.append(link)
                      
                
                state["podcasts"][channel_name] = historial
                guardado = historial

            # Migración del formato antiguo
            elif isinstance(guardado, str):

                historial = []

                for item in items[:20]:
                    link = item.findtext("link", "")

                    if not link:
                        link = item.findtext("guid", "")

                    historial.append(link)
                
                     
                   
                state["podcasts"][channel_name] = historial
                guardado = historial

            # Buscar episodios nuevos
            for item in items[:10]:

                title = item.findtext(
                    "title",
                    "Sin título"
                )

                link = item.findtext("link", "")

                if not link:
                    link = item.findtext("guid", "")
                    
                
                if link not in guardado:

                    print(
                        f"Nuevo episodio: {channel_name}"
                    )

                    if send_notification(
                        title,
                        channel_name,
                        link
                    ):

                        print("Notificación enviada")
                        guardado.insert(0, link)

                    else:
                        print("Error enviando notificación")
                        
                       
            state["podcasts"][channel_name] = guardado[:20]

            for item in items:

                videos.append({
                    "title": item.findtext(
                        "title",
                        "Sin título"
                    ),
                    "link": item.findtext(
                        "link",
                        ""
                    ),
                    "published": item.findtext(
                        "pubDate",
                        ""
                    ),
                    "channel": channel_name
                })

        except Exception as e:
            print(
                "Error leyendo:",
                feed_url,
                e
            )
    videos.sort(
        key=get_date,
        reverse=True
    )

    rss = ET.Element(
        "rss",
        {"version": "2.0"}
    )

    channel = ET.SubElement(
        rss,
        "channel"
    )

    ET.SubElement(
        channel,
        "title"
    ).text = "ARGOS - Podcasts"

    ET.SubElement(
        channel,
        "description"
    ).text = "Agregador automático de podcasts"

    for video in videos[:50]:

        item = ET.SubElement(
            channel,
            "item"
        )

        ET.SubElement(
            item,
            "title"
        ).text = video["title"]

        ET.SubElement(
            item,
            "author"
        ).text = video["channel"]

        ET.SubElement(
            item,
            "link"
        ).text = video["link"]

        ET.SubElement(
            item,
            "pubDate"
        ).text = video["published"]

    save_state(state)

    tree = ET.ElementTree(rss)

    tree.write(
        OUTPUT,
        encoding="utf-8",
        xml_declaration=True
    )


if __name__ == "__main__":
    main()
