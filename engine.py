import os, requests, xml.etree.ElementTree as ET, textwrap
from PIL import Image, ImageDraw

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def fetch_latest_space_news():
    url = "https://www.nasa.gov/rss/dyn/breaking_news.rss"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=10)
    root = ET.fromstring(r.content)
    
    for item in root.findall(".//item")[:1]:
        title = item.find("title").text
        desc = item.find("description").text or ""
        link = item.find("link").text
        
        img_url = None
        enc = item.find("enclosure")
        if enc is not None and "url" in enc.attrib:
            img_url = enc.attrib["url"]
            
        return title.strip(), desc.strip(), link.strip(), img_url
    return None, None, None, None

def generate_poster(title, img_url, out_path="poster.png"):
    img_canvas = Image.new("RGB", (1200, 675), (10, 15, 28))
    
    if img_url:
        try:
            r = requests.get(img_url, timeout=10)
            with open("temp.jpg", "wb") as f:
                f.write(r.content)
            base = Image.open("temp.jpg").convert("RGB").resize((1200, 675))
            img_canvas.paste(base, (0, 0))
        except Exception:
            pass

    overlay = Image.new("RGBA", (1200, 675), (0, 0, 0, 170))
    img_canvas.paste(overlay, (0, 0), overlay)
    
    draw = ImageDraw.Draw(img_canvas)
    draw.rectangle([60, 50, 360, 110], fill=(220, 38, 38))
    draw.text((80, 70), "SPACE DISPATCH", fill="white")
    
    y = 380
    for line in textwrap.wrap(title, width=40)[:3]:
        draw.text((60, y), line, fill="white")
        y += 60

    img_canvas.save(out_path)
    return out_path

def send_to_telegram(title, desc, link, poster_path):
    caption = f"🚀 *{title}*\n\n{desc[:300]}...\n\n🔗 [మరిన్ని వివరాలు]({link})"
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto" 
    with open(poster_path, "rb") as photo:
        payload = {
            "chat_id": CHAT_ID,
            "caption": caption,
            "parse_mode": "Markdown"
        }
        r = requests.post(url, data=payload, files={"photo": photo})
        print(f"Telegram Status: {r.status_code}")

def main():
    title, desc, link, img_url = fetch_latest_space_news()
    if title:
        poster = generate_poster(title, img_url)
        send_to_telegram(title, desc, link, poster)

if __name__ == "__main__":
    main()
          
