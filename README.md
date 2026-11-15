# YardFlow — Rail Yard Slot Planner

**Sector:** Freight logistics / rail operations (synthetic portfolio demonstration)

A full-stack scheduling demo that lets dispatchers reserve and release track occupancy intervals, with conflict detection, a responsive browser interface, FastAPI validation, and SQLite persistence. No external services, API keys, or real railway data are required.

## Architecture

Browser (HTML/CSS/vanilla JS) → FastAPI JSON endpoints → SQLite database. The API validates track labels, train names, and minute ranges; it rejects overlapping bookings on the same track with HTTP 409. Adjacent intervals and concurrent bookings on different tracks are permitted.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Visit http://localhost:8000. API documentation: http://localhost:8000/docs. Data persists in `yard.db` (ignored by Git).

## Tests

```bash
python -m pytest -q
```

Tests cover create/list/delete, overlap rejection, adjacent intervals, independent tracks, invalid requests, missing records, and page rendering. CI runs the same command on pushes and pull requests; CI status is **unverified until published**.

## Docker / deployment

```bash
docker compose up --build
```

Open http://localhost:8000. The named Docker volume preserves the SQLite database across container restarts. For a public deployment, add authentication, TLS reverse proxy, backups, rate limiting, and a transactional booking mechanism before admitting concurrent users.

## Sample booking

```bash
curl -X POST http://localhost:8000/api/slots -H 'Content-Type: application/json' -d '{"track":"A1","start_min":480,"end_min":540,"train":"FREIGHT 101"}'
```

## Engineering decision journal

- **SQLite over PostgreSQL:** zero-cost local setup and inspectable persistence; not appropriate for heavy concurrent scheduling.
- **Minutes since midnight:** deterministic interval comparisons; intentionally excludes overnight slots and time zones.
- **Server-side validation:** frontend inputs improve usability but the API enforces constraints.
- **No optimizer:** reservations are manually entered; this is not a train-dispatch recommendation engine.
- **Race condition:** conflict check and insert are not serialized across concurrent requests. A production design would use database-enforced exclusion constraints or transactional locks.

## Limitations

Synthetic data only; no integration with rail signals, dispatch systems, safety-critical operations, authentication, authorization, time-zone handling, or audit trail. Not suitable for real train operations. No live demo or screenshot has been published.

## License

MIT — see LICENSE.
