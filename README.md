# FF-Agent → Listmonk Konverter

Web-App zum Konvertieren von FF-Agent CSV-Exporten in das Listmonk-Importformat.

## Features

- Filtert automatisch **inaktive Mitglieder** (nur `ACTIVE = JA` wird exportiert)
- Überspringt Einträge ohne gültige E-Mail-Adresse
- Exportiert die folgenden Attribute:

| Attribut | Beschreibung |
|---|---|
| `firstname` | Vorname |
| `birthdate` | Geburtsdatum (wird weggelassen wenn maskiert) |
| `einheitsfuehrer` | `true` wenn Einheitsführer |
| `gruppenfuehrer` | `true` wenn Gruppenführer |

## Lokale Entwicklung

```bash
pip install -r requirements.txt
python app.py
```

Die App ist dann unter `http://localhost:5000` erreichbar.

## Tests

```bash
python -m unittest test_converter -v
```

## Deployment

Das Projekt enthält eine `nixpacks.toml` und kann direkt auf Plattformen wie [Railway](https://railway.app) deployed werden.