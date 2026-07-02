# Google Maps Scraper

Full-stack alat za prikupljanje i pregled leadova sa Google Maps-a. Backend je napisan u Flask-u i Playwright-u, a frontend je Next.js aplikacija sa tabelom za pregled i upravljanje podacima.

## Šta projekat radi

- pretražuje Google Maps po zadatom upitu
- izvučene objekte upisuje u TinyDB bazu
- čuva osnovne podatke o lead-u: naziv, ocenu, kategoriju, sajt, telefon i radno vreme
- omogućava pregled, dodavanje, izmenu i brisanje leadova kroz REST API
- prikazuje podatke u frontend tabeli sa filtriranjem i paginacijom

## Struktura projekta

- `backend/` - Flask API, scraper i baza podataka
- `frontend/` - Next.js UI za prikaz leadova
- `screenshots/` - slike interfejsa i primeri prikaza

## Screenshot

![Pregled leadova](screenshots/leads%20list.png)

## Tehnologije

- Backend: Flask, Flask-CORS, TinyDB, Playwright
- Frontend: Next.js 14, React 18, TypeScript, Tailwind CSS, TanStack Table

## Docker

Najlakši način da pokreneš ceo projekat je preko Docker Compose-a:

```bash
docker compose up --build
```

Nakon toga:

- frontend je na `http://localhost:3000`
- backend je na `http://localhost:5000`

Compose pokreće oba servisa, a frontend dobija backend adresu preko `NEXT_PUBLIC_BACKEND_URL=http://backend:5000`, tako da radi i unutar kontejnera.

Ako želiš da zadržiš podatke između restartova, `backend/db.json` je mapiran kao volume.

## Prerequisites

- Python 3.11+ ili noviji
- Node.js 18+ ili noviji
- Chromium za Playwright

## Pokretanje backend-a

```bash
cd backend
pip install -r requirements.txt
python -m playwright install chromium
python app.py
```

Backend podrazumevano radi na `http://127.0.0.1:5000`.

## Pokretanje frontend-a

```bash
cd frontend
npm install
npm run dev
```

Frontend podrazumevano radi na `http://localhost:3000`.

## API rute

- `GET /leads` - vraća sve leadove
- `GET /lead/<id>` ili `GET /leads/<id>` - vraća jedan lead
- `POST /leads` - dodaje lead
- `PUT /lead/<id>` ili `PUT /leads/<id>` - menja lead
- `DELETE /lead/<id>` ili `DELETE /leads/<id>` - briše lead
- `GET /scrape` ili `POST /scrape` - pokreće scraping za zadati upit

## Napomene

- Frontend očekuje backend na adresi `http://127.0.0.1:5000`.
- Ako želiš da scraping radi bez vidljivog browsera, ostavi `HEADLESS_SCRAPE=true`.
- Podaci se čuvaju lokalno u fajlu `backend/db.json`.
