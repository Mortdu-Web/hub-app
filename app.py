import json
import logging
import os
import re
from pathlib import Path
from urllib.parse import urlparse

from flask import Blueprint, Flask, g, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

from auth_client import require_auth

URL_PREFIX = os.environ.get("URL_PREFIX", "/hub-app").rstrip("/")
AUTH_PUBLIC_URL = os.environ.get("AUTH_PUBLIC_URL", "http://localhost:25000/auth").rstrip("/")
PUBLIC_URL = os.environ.get("PUBLIC_URL", "http://localhost:25001/hub-app").rstrip("/")
APPS_CONFIG = Path(os.environ.get("APPS_CONFIG") or Path(__file__).with_name("config.json"))

log = logging.getLogger(__name__)
_VAR = re.compile(r"\$\{(\w+)\}")


def _expand(value: str) -> str | None:
    """Remplace ${VAR} par l'environnement (.env). None si une variable est absente ou vide."""
    missing = False

    def sub(match):
        nonlocal missing
        val = os.environ.get(match.group(1), "").strip()
        missing = missing or not val
        return val

    out = _VAR.sub(sub, value)
    return None if missing else out


def load_apps(path: Path = APPS_CONFIG) -> tuple[str, list[dict]]:
    """(titre, applications) depuis config.json. Une appli dont l'URL est manquante ou invalide est ignoree."""
    data = json.loads(path.read_text(encoding="utf-8"))
    apps = []
    for entry in data.get("apps", []):
        name = entry.get("name", "?")
        url = _expand(entry.get("url", ""))
        if not url:
            log.warning("Appli %r ignoree : variable d'URL absente du .env (%s)", name, entry.get("url"))
            continue
        if urlparse(url).scheme not in ("http", "https"):
            log.warning("Appli %r ignoree : l'URL doit commencer par http:// ou https://", name)
            continue
        apps.append(
            {
                "name": name,
                "description": entry.get("description", ""),
                "icon": entry.get("icon", "🔗"),
                "url": url,
                "roles": entry.get("roles") or [],
            }
        )
    return data.get("title", "Mes applications"), apps


TITLE, APPS = load_apps()  # lu au demarrage : redemarrer le conteneur apres modification

bp = Blueprint("hub", __name__)


def visible_apps(user_roles) -> list[dict]:
    """Applis sans restriction, ou dont l'un des roles requis est detenu par l'utilisateur.

    Ne sert qu'a masquer les liens inutiles : chaque appli reste responsable de son propre controle d'acces.
    """
    roles = set(user_roles or [])
    return [a for a in APPS if not a["roles"] or roles & set(a["roles"])]


@bp.get("/")
@require_auth()
def home():
    return render_template(
        "home.html",
        title=TITLE,
        user=g.user,
        apps=visible_apps(g.user.get("roles")),
        logout_url=f"{AUTH_PUBLIC_URL}/logout?next={PUBLIC_URL}/",
    )


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
