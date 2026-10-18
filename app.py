import os

from flask import Blueprint, Flask, g, render_template_string
from werkzeug.middleware.proxy_fix import ProxyFix

from auth_client import require_auth

URL_PREFIX = os.environ.get("URL_PREFIX", "/hub-app").rstrip("/")
AUTH_PUBLIC_URL = os.environ.get("AUTH_PUBLIC_URL", "http://localhost:25000/auth").rstrip("/")
PUBLIC_URL = os.environ.get("PUBLIC_URL", "http://localhost:25001/hub-app").rstrip("/")

bp = Blueprint("hub", __name__)

PAGE = """
<!doctype html>
<html lang="fr">
<head><meta charset="utf-8"><title>hub-app</title></head>
<body style="font-family: sans-serif; max-width: 640px; margin: 3rem auto;">
  <h1>{{ title }}</h1>
  <p>Connecté en tant que <strong>{{ user.username }}</strong> ({{ user.email or "pas d'email" }})</p>
  <p>Rôles : {{ user.roles | join(", ") or "aucun" }}</p>
  <p>
    <a href="{{ url_for('hub.home') }}">Accueil (connexion requise)</a> ·
    <a href="{{ url_for('hub.admin') }}">Page admin (rôle « admin » requis)</a> ·
    <a href="{{ url_for('hub.other') }}">Page admin (rôle « other » requis)</a> ·
    <a href="{{ logout_url }}">Se déconnecter</a>
  </p>
</body>
</html>
"""


def render(title):
    return render_template_string(
        PAGE,
        title=title,
        user=g.user,
        logout_url=f"{AUTH_PUBLIC_URL}/logout?next={PUBLIC_URL}/",
    )


@bp.get("/")
@require_auth()
def home():
    return render("hub-app : bienvenue 🎉")

@bp.get("/admin")
@require_auth("admin")
def admin():
    return render("hub-app : zone admin")

@bp.get("/other")
@require_auth("other")
def other():
    return render("hub-app : zone other")

@bp.get("/health")
def health():
    return {"status": "ok"}

@bp.get("/whoami")
@require_auth()
def whoami():
    return g.user   # doit contenir username, email, roles


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.register_blueprint(bp, url_prefix=URL_PREFIX)