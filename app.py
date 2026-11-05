from flask import Flask, jsonify, render_template, request
from network_monitor import scan_network, monitor_hosts, validate_network, validate_private_ip

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
        "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    )
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "project": "NetWatch", "version": "1.0.0"})


@app.post("/api/scan")
def api_scan():
    data = request.get_json(silent=True) or {}
    cidr = data.get("network", "")
    try:
        network = validate_network(cidr)
        hosts = scan_network(network)
        return jsonify({
            "network": str(network),
            "scanned": len(hosts),
            "online": sum(1 for host in hosts if host["status"] == "online"),
            "offline": sum(1 for host in hosts if host["status"] == "offline"),
            "hosts": hosts,
        })
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/monitor")
def api_monitor():
    data = request.get_json(silent=True) or {}
    addresses = data.get("addresses", [])
    if not isinstance(addresses, list) or not 1 <= len(addresses) <= 254:
        return jsonify({"error": "قائمة الأجهزة غير صالحة."}), 400

    try:
        checked = [validate_private_ip(address) for address in addresses]
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    results = monitor_hosts(checked)
    return jsonify({"results": results})


if __name__ == "__main__":
    # Local-only server. Do not expose the development server to the Internet.
    app.run(host="127.0.0.1", port=5000, debug=False)
