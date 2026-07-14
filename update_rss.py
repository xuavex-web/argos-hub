import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

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


def main():

    videos = []

    for feed_url in get_feed_urls():
        try:
            data = urllib.request.urlopen(feed_url, timeout=10).read()
            root = ET.fromstring(data)

            channel_name = get_channel_name(root)

            for entry in root.findall(f"{ATOM}entry"):
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
            print("Error leyendo:", feed_url, e)


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


    tree = ET.ElementTree(rss)

    tree.write(
        OUTPUT,
        encoding="utf-8",
        xml_declaration=True
    )


if __name__ == "__main__":
    main()
