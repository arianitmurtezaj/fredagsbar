# Fredagsbarens event-system

Flask API og Streamlit-frontend, som kommunikerer med httpx.
Systemet viser events og ledige pladser og lader brugeren oprette events,
tilmelde sig og afmelde sig.

## Start med Docker

Start Docker Desktop. Kør fra repositoryets rod, hvor docker-compose.yml ligger:

```bash
docker compose up --build
```

- Frontend: http://localhost:8501
- API til Postman: http://localhost:5002/events

Stop med Ctrl+C og derefter `docker compose down`.
Stop eventuelle lokale servere først, så portene er ledige.

Compose starter to services: `api` og `frontend`. Begge bruger samme Dockerfile.
Frontenden starter, når API'ets healthcheck er godkendt.
`.dockerignore` holder bl.a. den lokale `.venv` ude af image'et.
`uv sync --locked` installerer de versioner, der står i `uv.lock`.

## Start lokalt uden Docker

Kræver uv og Python 3.12 eller nyere. Stop Docker-services først.

```bash
uv sync --locked
```

Terminal 1 i projektmappen:

```bash
uv run api.py
```

Terminal 2 i projektmappen:

```bash
uv run streamlit run app.py --server.port 8502
```

API'et ligger på http://localhost:5002, og den lokale frontend på
http://localhost:8502. Uden portargumentet bruger Streamlit port 8501.

## API

| Metode | Endpoint | Succes | Fejl |
|---|---|---|---|
| GET | `/events` | 200 + liste | - |
| GET | `/events/<event_id>` | 200 + event | 404 |
| POST | `/events` | 201 + nyt event | 400 |
| POST | `/events/<event_id>/signups` | 201 + opdateret event | 400, 404, 409 |
| DELETE | `/events/<event_id>/signups/<name>` | 204 | 404 |
| DELETE | `/events/<event_id>` | 204 | 404 |

Opret event med JSON som:

```json
{"title": "Musikquiz", "date": "2026-12-04", "capacity": 5}
```

Tilmeld med JSON som `{"name": "Emil"}`. Ved POST vælges Body > raw > JSON
i Postman. Afmelding og sletning kræver ingen body.
Fejl returneres som `{"error": "Forklaring"}`. Et 204-svar har ingen body.
Alle seks endpoints er dokumenteret i `swagger.json`, som kan åbnes i
[Swagger Editor](https://editor.swagger.io/).

## Opbygning

`api.py` ejer eventlisten og kontrollerer kapacitet og dobbelt tilmelding.
`app.py` bruger httpx til at hente og ændre data. Ledige pladser beregnes
som kapacitet minus antal deltagere. Navnet gemmes i Streamlits session_state.
Efter tilmelding og afmelding bruges st.rerun til at opdatere visningen.
Fejl fra API'et, forbindelsesfejl og timeout vises med st.error.

Lokalt bruger frontenden `http://127.0.0.1:5002`. I Docker sætter Compose
miljøvariablen `API_URL` til `http://api:5002`, hvor `api` er servicens navn.
Serverne lytter på `0.0.0.0`, så de kan nås uden for containeren.

Data ligger i hukommelsen og nulstilles til de to eksempelevents, når API'et
genstarter. API'et kører uden debug og behandler requests ét ad gangen.
