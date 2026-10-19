# hub-app — page d'accueil globale vers mes applications

Page protégée par le service auth, qui affiche une carte par application (lien vers son URL).

```bash
cp .env.example .env     # renseigner PORT, AUTH_*, PUBLIC_URL et les URLs des applications
docker compose up -d --build
```
- `/` : grille des applications (connexion requise)
- `/health` : sonde de santé (publique)
- `/whoami` : utilisateur connecté en JSON

## Ajouter une application
1. Dans `config.json` (versionné, sans URL réelle) :
   ```json
   {
     "name": "Mon app",
     "description": "Ce qu'elle fait",
     "icon": "📚",
     "url": "${MON_APP_URL}",
     "roles": ["admin"]
   }
   ```
   `roles` est facultatif : sans lui, l'application est visible par tout utilisateur connecté.
2. Dans `.env` (jamais commité) : `MON_APP_URL=https://mon-domaine.fr/mon-app/`
3. `docker compose up -d --build` (le fichier est lu au démarrage).

## Pourquoi les URLs sont dans le `.env`
`config.json` ne contient que des informations non sensibles (nom, description, icône, rôles). Les URLs ne sont pas
secrètes, mais elles révèlent le nom de domaine et la topologie (surtout une URL interne ou un port), et elles
diffèrent entre local et production : elles restent donc dans `.env`, ignoré par git. Une variable absente ou vide
masque simplement l'application (avec un avertissement dans les logs) ; seules les URLs `http://` / `https://` sont acceptées.

`roles` ne fait que **masquer** le lien : chaque application doit faire son propre contrôle d'accès (`require_auth`).
`APPS_CONFIG=/chemin/autre.json` permet d'utiliser un autre fichier de configuration.

## Test en local
Dans le `.env` du repo **auth** : `PUBLIC_URL=http://localhost:5000`, `SESSION_COOKIE_DOMAIN=` (vide),
`SESSION_COOKIE_SECURE=false`, `ALLOWED_REDIRECT_DOMAINS=localhost`.
Dans Keycloak (client auth-service) : ajouter `http://localhost:5000/callback` aux redirect URIs
et `http://localhost:5001/*` aux post logout redirect URIs.
(Les cookies ne sont pas isolés par port : la session de localhost:5000 est bien envoyée à localhost:5001.)
