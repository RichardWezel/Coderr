# 👨🏻‍💻👩🏼‍💻 Coderr Backend API

![Django](https://img.shields.io/badge/Django-5.x-green) <br>
![DRF](https://img.shields.io/badge/DRF-3.x-blue)<br>
![Auth](https://img.shields.io/badge/Auth-Token-orange)<br>
![DB](https://img.shields.io/badge/DB-SQLite-lightgrey)

Ein Django REST Backend für eine Marketplace‑ähnliche App mit Rollen (Customer/Business), Angeboten, Bestellungen, Profilen und Bewertungen.

---

## 🚀 Features

- Registrierung und Login mit Token‑Authentifizierung
- Benutzerprofile lesen/aktualisieren, Business/Customer‑Listen, Datei‑Upload
- Angebote mit Preisstaffeln, Suche/Filter/Sortierung, Owner‑Schutz
- Bestellungen zwischen Kunde und Business inkl. Status‑Updates
- Bewertungen inkl. Reviewer/Owner‑Schutz und 1‑Review‑Regel pro Business
- Basis‑Statistiken (Reviews, durchschnittliche Bewertung, Anzahl Angebote/Business‑Profile)

---

## 📦 Setup

- Voraussetzungen: Python 3.10+, pip, virtualenv (optional)
- Installation:

```
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Optionen:
- Admin anlegen: `python manage.py createsuperuser`
- Medienauslieferung im Dev: aktiviert über `MEDIA_URL`/`MEDIA_ROOT`

---

## 🔐 Authentifizierung

- Registrierung: `POST /api/registration/`
  - Felder: `username`, `email`, `password`, `repeated_password`, optional `type` (Default CUSTOMER)
- Login: `POST /api/login/`
  - Felder: `email` oder `username` (je nach Implementierung utils), `password`
- Header für geschützte Endpoints:

```
Authorization: Token <token>
```

---

## 🏁 Endpoints (Auszug)

Profile (`profile_app`)
- `GET/PUT/PATCH /api/profile/<pk>/` – eigenes Profil lesen/aktualisieren (IsAuthenticated + Owner)
- `GET /api/profile/business/` – Liste Business‑Profile (IsAuthenticated)
- `GET /api/profile/customer/` – Liste Customer‑Profile (IsAuthenticated)
- `POST /api/upload/` – Datei‑Upload (aktuell ohne spezielle Permission)

Offers (`offers_app`)
- `GET /api/offers/` – Liste mit Filter/Suche/Sortierung (AllowAny)
- `POST /api/offers/` – Angebot erstellen (Business‑Rolle erforderlich)
- `GET /api/offers/<pk>/` – Angebot lesen
- `PATCH/PUT /api/offers/<pk>/` – nur Owner darf ändern
- `DELETE /api/offers/<pk>/` – nur Ersteller darf löschen
- `GET /api/offerdetails/<pk>/` – OfferDetail lesen (IsAuthenticated)

Orders (`orders_app`)
- `GET /api/orders/` – Bestellungen des eingeloggten Users (als Customer oder Business)
- `POST /api/orders/` – Bestellung erstellen (nur Customer; nicht eigenes Angebot)
- `GET /api/orders/<id>/` – Bestellung lesen (Beteiligte)
- `PUT/PATCH /api/orders/<id>/` – Status ändern (nur Business‑User der Bestellung)
- `DELETE /api/orders/<id>/` – Löschen (zusätzliche Staff/Admin‑Prüfung)
- `GET /api/order-count/<business_user_id>/` – Anzahl Bestellungen für Business
- `GET /api/completed-order-count/<business_user_id>/` – Anzahl abgeschlossene Bestellungen

Reviews (`reviews_app`)
- `GET/POST /api/reviews/` – Liste/Erstellen (1 Review pro Business‑User; nur Customer dürfen erstellen)
- `GET/PATCH/DELETE /api/reviews/<id>/` – Lesen/Aktualisieren/Löschen (IsAuthenticatedOrReadOnly; nur Reviewer darf ändern)

Shared (`shared_app`)
- `GET /api/base-info/` – Statistiken: `review_count`, `average_rating` (eine Nachkommastelle, niemals null), `business_profile_count`, `offer_count`

---

## 🔑 Rollen & Berechtigungen

- User‑Typen: `CUSTOMER`, `BUSINESS` (siehe `auth_app.CustomUser`)
- TokenAuth aktiviert (siehe `REST_FRAMEWORK` in `core/settings.py`)
- Wichtige Checks:
  - Profile: Objekt‑Permission nur Owner
  - Offers: Erstellen nur Business; Update/Delete nur Owner/Creator
  - Orders: Erstellen nur Customer; Status‑Update nur Business der Bestellung; Delete ggf. Staff/Admin
  - Reviews: Nur Customer erstellen; pro Business nur ein Review pro Reviewer; Update/Delete nur Reviewer

---

## 🗂️ Projektstruktur

```
Backend/
├── auth_app/        # Registrierung, Login, User‑Serializers
├── profile_app/     # Profile + Datei‑Upload
├── offers_app/      # Angebote + OfferDetails, Filter, Pagination
├── orders_app/      # Bestellungen + Berechtigungen
├── reviews_app/     # Reviews + Regeln
├── shared_app/      # Base‑Info/Statistiken
├── core/            # Settings, URLs, WSGI/ASGI, Exceptions
└── manage.py
```

---

## ⚠️ Hinweise für Clients

- `average_rating` wird immer als Zahl mit genau einer Nachkommastelle ausgegeben (z. B. `0.0`).
- Datei‑Uploads werden unter `MEDIA_ROOT` gespeichert; Zugriff via `MEDIA_URL` im Dev aktiviert.

---

## 🧑‍🎓 Tech Stack

- Django, Django REST Framework, django‑filters, TokenAuth, corsheaders
- Datenbank: SQLite (Dev)

---

## 📃 Lizenz

Interne/Projektbezogene Nutzung. Keine Lizenzdatei hinterlegt.
