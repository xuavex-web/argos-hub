import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

CHANNEL_ID = "UCFjOxBC4RqL1Qq1_bAKmUSw"

RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"

OUTPUT = "argos_rss.xml"

def main():
    data = urllib.request.urlopen(RSS_URL).read()

    root = ET.fromstring(data)

    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "ARGOS - Gran Misterio Podcast"
    ET.SubElement(channel, "link").text = RSS_URL
    ET.SubElement(channel, "description").text = "Actualización automática de vídeos"

    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        title = entry.find("{http://www.w3.org/2005/Atom}title").text
        link = entry.find("{http://www.w3.org/2005/Atom}link").attrib["href"]
        published = entry.find("{http://www.w3.org/2005/Atom}published").text

        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "link").text = link
        ET.SubElement(item, "pubDate").text = published

    tree = ET.ElementTree(rss)
    tree.write(OUTPUT, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    main()
