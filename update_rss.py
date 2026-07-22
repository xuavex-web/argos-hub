import urllib.request
import xml.etree.ElementTree as ET

from state import load_state, save_state
from notifier import send_notification

INPUT = "feeds.txt"
OUTPUT = "argos_rss.xml"

ATOM = "{http://www.w3.org/2005/Atom}"


def get_feed_urls():
    with open(INPUT, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def get_channel_name(root):
    title = root.find(f"{ATOM}title")
    if title is not None:
        return title.text
    return "Canal desconocido"
    
def get_video_id(link):
    if "/shorts/" in link:
        return link.rstrip("/").split("/")[-1]

    from urllib.parse import urlparse, parse_qs

    query = parse_qs(urlparse(link).query)

    if "v" in query:
        return query["v"][0]

    return link

def main():

    state = load_state()

    if "youtube" not in state:
        state["youtube"] = {}

    videos = []

    for feed_url in get_feed_urls():
        try:
            data = urllib.request.urlopen(feed_url, timeout=10).read()
            root = ET.fromstring(data)

            channel_name = get_channel_name(root)

            entries = root.findall(f"{ATOM}entry")
            print(channel_name, "videos encontrados:", len(entries))

            if not entries:
                continue

            # ---------- Notificaciones ----------
            guardado = state["youtube"].get(channel_name)
            print(f"{channel_name!r} -> {'ENCONTRADO' if guardado is not None else 'NO ENCONTRADO'}")

            # Canal nuevo
            if guardado is None:
                historial = []
                print(f"Canal nuevo: {channel_name!r}")

                for entry in entries[:20]:
                    link = entry.find(f"{ATOM}link").attrib["href"]
                    historial.append(get_video_id(link))

                state["youtube"][channel_name] = historial
                guardado = historial
            
            # Migración automática del formato antiguo
            elif isinstance(guardado, str):
                print(f"Migrando historial: {channel_name}")
                
                guardado = []

                for entry in entries[:20]:
                    link = entry.find(f"{ATOM}link").attrib["href"]
                    guardado.append(get_video_id(link))

                state["youtube"][channel_name] = guardado
                 
            
            
            # Recorremos los 10 vídeos más recientes
            for entry in entries[:10]:

                title = entry.find(f"{ATOM}title").text
                link = entry.find(f"{ATOM}link").attrib["href"]
                video_id = get_video_id(link)

                if video_id not in guardado:
                    
                    print(f"Nuevo vídeo: {channel_name}")

                    if send_notification(
                        title,
                        channel_name,
                        link
                    ):
                   
                        print("Notificación enviada")  

                        # Lo marcamos inmediatamente como visto
                        guardado.insert(0, video_id)

                    else:
                        print("Error enviando notificación")
                        
            # Guardamos el historial actualizado (máximo 20 vídeos)
            state["youtube"][channel_name] = guardado[:20]
           
            # ---------- RSS (todos los vídeos) ----------
            for entry in entries:

                title = entry.find(f"{ATOM}title").text
                link = entry.find(f"{ATOM}link").attrib["href"]
                published = entry.find(f"{ATOM}published").text

                videos.append({
                    "title": title,
                    "link": link,
                    "published": published,
                    "channel": channel_name
                })
                                                   
        except Exception as e:
            print(f"Error leyendo {feed_url}: {e}")
            continue

    videos.sort(
        key=lambda x: x["published"],
        reverse=True
    )


    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(
        channel,
        "title"
    ).text = "ARGOS - YouTube"

    ET.SubElement(
        channel,
        "description"
    ).text = "Agregador automático de canales YouTube"


    for video in videos[:50]:

        item = ET.SubElement(channel, "item")

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
