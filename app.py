from flask import Flask, render_template

app = Flask(__name__)


@app.after_request
def add_security_headers(response):
    """Apply a small baseline of browser security headers."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self'; "
        "img-src 'self' data:; object-src 'none'; frame-ancestors 'none'; "
        "base-uri 'self'; form-action 'self'"
    )
    return response


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/health")
def health():
    return {"status": "ok", "project": "EAMH Security Lab"}


if __name__ == "__main__":
    # Local development only. Use a production WSGI server for deployment.
    app.run(host="127.0.0.1", port=5000, debug=False)
