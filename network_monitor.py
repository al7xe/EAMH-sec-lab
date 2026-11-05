"""Safe IPv4 discovery and reachability checks for private LANs."""
import ipaddress
import platform
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


MAX_HOSTS = 254
PING_TIMEOUT_SECONDS = 2.5


def validate_network(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("أدخل عنوان الشبكة بصيغة CIDR مثل 192.168.1.0/24.")
    try:
        network = ipaddress.ip_network(value.strip(), strict=False)
    except ValueError:
        raise ValueError("صيغة الشبكة غير صحيحة. استخدم IPv4 بصيغة CIDR.") from None

    if network.version != 4:
        raise ValueError("الإصدار المدعوم حاليًا هو IPv4 فقط.")
    if not network.is_private or network.is_loopback or network.is_link_local or network.is_multicast or network.is_reserved:
        raise ValueError("يسمح بالفحص داخل الشبكات الخاصة المحلية فقط.")
    if network.num_addresses > 256:
        raise ValueError("نطاق الفحص كبير. استخدم شبكة /24 أو نطاقًا أصغر.")
    return network


def validate_private_ip(value):
    try:
        address = ipaddress.ip_address(str(value))
    except ValueError:
        raise ValueError("عنوان IP غير صالح.") from None
    if address.version != 4 or not address.is_private or address.is_loopback or address.is_link_local:
        raise ValueError("يسمح بفحص عناوين IPv4 الخاصة فقط.")
    return str(address)


def ping_host(address):
    address = validate_private_ip(address)
    system = platform.system().lower()
    if system == "windows":
        command = ["ping", "-n", "1", "-w", "1000", address]
    elif system == "darwin":
        command = ["ping", "-c", "1", "-W", "1000", address]
    else:
        command = ["ping", "-c", "1", "-W", "1", address]

    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=PING_TIMEOUT_SECONDS,
            check=False,
        )
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        online = completed.returncode == 0
        ping_time = re.search(r"time[=<]\\s*([0-9.]+)\\s*ms", completed.stdout + completed.stderr, re.IGNORECASE)
        if ping_time:
            elapsed_ms = float(ping_time.group(1))
        return {
            "ip": address,
            "status": "online" if online else "offline",
            "latency_ms": elapsed_ms if online else None,
        }
    except (subprocess.TimeoutExpired, OSError):
        return {"ip": address, "status": "offline", "latency_ms": None}


def _read_arp_table():
    try:
        result = subprocess.run(
            ["arp", "-a"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {}

    entries = {}
    pattern = re.compile(r"(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+(?P<mac>(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2})")
    for match in pattern.finditer(result.stdout):
        entries[match.group("ip")] = match.group("mac").replace("-", ":").lower()
    return entries


def scan_network(network):
    addresses = [str(ip) for ip in network.hosts()]
    results = []
    with ThreadPoolExecutor(max_workers=min(48, max(1, len(addresses)))) as pool:
        futures = {pool.submit(ping_host, address): address for address in addresses}
        for future in as_completed(futures):
            results.append(future.result())

    arp_entries = _read_arp_table()
    for host in results:
        host["mac"] = arp_entries.get(host["ip"])
    results.sort(key=lambda item: ipaddress.ip_address(item["ip"]))
    return results


def monitor_hosts(addresses):
    """Check a batch of already validated private addresses concurrently."""
    results = []
    with ThreadPoolExecutor(max_workers=min(48, max(1, len(addresses)))) as pool:
        futures = [pool.submit(ping_host, address) for address in addresses]
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: ipaddress.ip_address(item["ip"]))
    return results
