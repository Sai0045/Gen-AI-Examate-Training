# TeekaTimer: Baby Vaccine Due-Date Helper

**Product:** TeekaTimer. Enter your baby's date of birth and see which government vaccines are due, with answers from official MoHFW immunization handbooks.

**User:** A young mother in a village near Kopargaon whose 6-week-old son missed the 6-week anganwadi session and who is worried whether it is too late.

**Problem:** Parents often don't know which vaccine is due when, or whether a missed dose can still be given.

**Data source:** MoHFW National Immunization Schedule and the Immunization Handbook for Medical Officers (mohfw.gov.in, nhm.gov.in).
## Data source
MoHFW National Immunization Schedule (Unit 2) and the Immunization Handbook for Medical Officers, from mohfw.gov.in and nhm.gov.in.

## How to run

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    python -m app.fetch
    python -m app.ingest
    python -m app.cli
    python -m analysis.explore
    python -m uvicorn app.main:app

Then open http://127.0.0.1:8000/docs

## Endpoints
- GET /health
- GET /records?limit=
- GET /records/{id}
- GET /search?q=
- POST /questions
