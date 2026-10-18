# hub-app — page de test protégée par le service auth

```bash
cp .env.example .env
docker compose up -d --build
```
- http://localhost:5001/       -> connexion requise (n'importe quel utilisateur)
- http://localhost:5001/admin  -> rôle `admin` requis (sinon 403)

## Test en local
Dans le `.env` du repo **auth** : `PUBLIC_URL=http://localhost:5000`, `SESSION_COOKIE_DOMAIN=` (vide),
`SESSION_COOKIE_SECURE=false`, `ALLOWED_REDIRECT_DOMAINS=localhost`.
Dans Keycloak (client auth-service) : ajouter `http://localhost:5000/callback` aux redirect URIs
et `http://localhost:5001/*` aux post logout redirect URIs.
(Les cookies ne sont pas isolés par port : la session de localhost:5000 est bien envoyée à localhost:5001.)
