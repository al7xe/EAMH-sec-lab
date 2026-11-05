# NetWatch — Local Network Discovery & Monitoring

**EAMH Team | Computer Networks Project**  
**Tagline:** See Your Network. Understand Your Devices.

NetWatch is a local web application for discovering IPv4 devices on a private LAN and checking their reachability and response time. It is built with Python, Flask, and browser-native JavaScript. The interface is Arabic and RTL, and the application does not require a cloud service or external API.

## Features

- Discover hosts in a private IPv4 subnet (CIDR input).
- Concurrent ICMP reachability checks using the operating system ping utility.
- Display IP address, best-effort MAC address from the local ARP cache, online/offline status, and response time.
- Refresh the status of discovered devices every 15 seconds or manually.
- Summary cards for scanned, online, offline, and average response time.
- Local-only Flask server and baseline browser security headers.

## Safety boundaries

- Only private IPv4 address ranges are accepted.
- The scan is limited to 256 addresses (at most a /24-sized range).
- The application binds to 127.0.0.1 and is intended for a trusted local machine.
- Use it only on networks you own or are explicitly authorized to administer.
- A host that does not answer ICMP may still be online; firewalls often block ping.
- MAC addresses are read from the operating system ARP cache and may be unavailable until the host has communicated on the local segment.
- This educational project is not a replacement for enterprise network monitoring.

## Requirements

- Python 3.10+
- Windows, Linux, or macOS
- The system `ping` and `arp` commands available in PATH

## Run on Windows

```powershell
git clone https://github.com/al7xe/EAMH-sec-lab.git
cd EAMH-sec-lab
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

If PowerShell blocks activation, run `.venv\Scripts\activate.bat` from Command Prompt instead.

## Run on Linux

```bash
git clone https://github.com/al7xe/EAMH-sec-lab.git
cd EAMH-sec-lab
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## How to use

1. Find your LAN subnet (for example, `192.168.1.0/24`) from your router or computer network settings.
2. Enter the CIDR range in the scan field.
3. Start discovery and wait for the ping sweep to finish.
4. Review the device table. The status is refreshed automatically every 15 seconds; use the manual refresh button whenever needed.

## Project structure

```text
EAMH-sec-lab/
├── app.py
├── network_monitor.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── tests/
    └── test_network.py
```

## Tests

Run the validation tests:

```bash
python -m unittest discover -s tests -v
```

## Team

- Elias
- Ahmed
- Mohammed
- Hussam

## Academic note

This is a first functional MVP for a computer-networks course project. Future work may add device naming, historical availability charts, SNMP-based metrics for authorized managed devices, and exportable reports.
