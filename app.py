import os

from flask import Flask, g, render_template_string
from auth_client import require_auth

app = Flask(__name__)
AUTH_PUBLIC_URL = os.environ.get("AUTH_PUBLIC_URL", "http://localhost:5000").rstrip("/")
PUBLIC_URL = os.environ.get("PUBLIC_URL", "http://localhost:5001").rstrip("/")

PAGE = """
<!doctype html>
<html lang="fr">
<head><meta charset="utf-8"><title>hub-app</title></head>
<body style="font-family: sans-serif; max-width: 640px; margin: 3rem auto;">
  <h1>{{ title }}</h1>
  <p>Connecté en tant que <strong>{{ user.username }}</strong> ({{ user.email or "pas d'email" }})</p>
  <p>Rôles : {{ user.roles | join(", ") or "aucun" }}</p>
  <p>
    <a href="/">Accueil (connexion requise)</a> ·
    <a href="/admin">Page admin (rôle « admin » requis)</a> ·
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


@app.get("/")
@require_auth()
def home():
    return render("hub-app : bienvenue 🎉")


@app.get("/admin")
@require_auth("admin")
def admin():
    return render("hub-app : zone admin")


@app.get("/health")
def health():
    return {"status": "ok"}
