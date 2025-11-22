# SOFORT-ANLEITUNG: Spotify OAuth Fehler beheben

## Dein aktueller Fehler

```
INVALID_CLIENT: Insecure redirect URI
```

## Die Lösung (3 einfache Schritte)

### Schritt 1: Deine .env Datei anpassen

Öffne die `.env` Datei im `docker/` Verzeichnis und setze:

```env
SPOTIFY_CLIENT_ID=bad2ac519cd042d89cd061b1cbe1b99f
SPOTIFY_CLIENT_SECRET=dein_secret_hier
SPOTIFY_REDIRECT_URI=http://192.168.178.100:8765/api/auth/callback
```

**WICHTIG:** 
- ❌ Nicht: `http://192.168.178.100:8765/auth/spotify/callback`
- ✅ Richtig: `http://192.168.178.100:8765/api/auth/callback`

### Schritt 2: Spotify Developer Dashboard aktualisieren

1. Gehe zu: https://developer.spotify.com/dashboard
2. Melde dich an
3. Klicke auf deine App (mit Client-ID `bad2ac519cd042d89cd061b1cbe1b99f`)
4. Klicke **"Edit Settings"**
5. Scrolle zu **"Redirect URIs"**
6. Gib ein: `http://192.168.178.100:8765/api/auth/callback`
7. Klicke **"Add"**
8. Klicke **"Save"** ganz unten

**TIPP:** Du kannst mehrere URIs hinzufügen:
- `http://localhost:8765/api/auth/callback`
- `http://127.0.0.1:8765/api/auth/callback`  
- `http://192.168.178.100:8765/api/auth/callback`

### Schritt 3: Docker Container neu starten

```bash
cd docker
docker-compose restart
```

**ODER** komplett neu bauen:

```bash
docker-compose down
docker-compose up -d
```

### Schritt 4: Testen

1. Öffne deinen Browser
2. Gehe zu: `http://192.168.178.100:8765/auth`
3. Klicke "Connect Spotify"
4. Du wirst zu Spotify weitergeleitet
5. Autorisiere die App
6. Du kommst zurück zur App - **FERTIG!**

## Was wurde gefixt?

### Problem 1: Falscher Pfad
- **Alt:** `/auth/spotify/callback` ❌
- **Neu:** `/api/auth/callback` ✅

### Problem 2: Veraltete Version
- **Alt:** `/api/v1/auth/callback` ❌
- **Neu:** `/api/auth/callback` ✅

### Problem 3: Redirect URI nicht registriert
- Die URI muss **EXAKT** in Spotify Dashboard eingetragen sein
- Jedes Detail zählt: Protokoll (http), IP, Port, Pfad

## Checkliste

- [ ] `.env` Datei aktualisiert mit korrekter redirect_uri
- [ ] Spotify Dashboard: redirect_uri hinzugefügt
- [ ] Spotify Dashboard: "Save" geklickt
- [ ] Docker Container neu gestartet
- [ ] Browser-Test erfolgreich

## Wenn es immer noch nicht funktioniert

### Debug: Welche redirect_uri wird verwendet?

```bash
# Überprüfe deine .env
cat docker/.env | grep SPOTIFY_REDIRECT_URI

# Sollte zeigen:
# SPOTIFY_REDIRECT_URI=http://192.168.178.100:8765/api/auth/callback
```

### Debug: Ist die redirect_uri in Spotify registriert?

1. Gehe zu Spotify Dashboard
2. Öffne deine App
3. Klicke "Edit Settings"
4. Schaue unter "Redirect URIs"
5. Muss exakt enthalten sein: `http://192.168.178.100:8765/api/auth/callback`

### Warte 30 Sekunden

Spotify braucht manchmal ein paar Sekunden, um Änderungen zu übernehmen.

### Probiere Inkognito-Modus

Alte authorization-Versuche können im Browser-Cache sein.

## Weitere Hilfe

Siehe die ausführliche Dokumentation:
- `docs/REDIRECT_URI_FIX_EXPLAINED.md` (auf Deutsch)
- `docs/SPOTIFY_AUTH_TROUBLESHOOTING.md` (auf Englisch)
