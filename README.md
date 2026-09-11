# Amazon.sa Price Tracker API

FastAPI backend for a multi-user Amazon.sa price tracker. Users can register/login, add and remove tracked products, and check current prices. Product data is retrieved through SerpApi, while n8n can call the global price-check endpoint on a schedule and send email notifications when prices increase or decrease.

## Features

- Email/password registration and login
- Multiple tracked products per user
- Add and remove tracked products
- Real Amazon.sa product names and prices through SerpApi
- SQLite storage for local development
- Price comparison: `increased`, `decreased`, or `unchanged`
- `/check-all-prices` endpoint for n8n automation
- Swagger documentation at `/docs`
- Health endpoint at `/health`

## Architecture

```text
React frontend
      |
      v
FastAPI backend ----> SQLite
      |
      +----> SerpApi ----> Amazon.sa product data
      |
      <---- n8n (scheduled every 2 hours)
                  |
                  +----> Gmail notification when price changes
```

## Local setup

1. Create and activate a Python 3.11 virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and set your SerpApi key:

```env
SERPAPI_KEY=your_real_key_here
```

4. Start the API:

```bash
uvicorn app.main:app --reload
```

5. Open Swagger:

```text
http://127.0.0.1:8000/docs
```

## Main endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/users/register` | Register a user |
| POST | `/users/login` | Log in |
| GET | `/product/{asin}` | Get current product data |
| POST | `/tracked-products` | Add a tracked product |
| GET | `/tracked-products/{user_id}` | List a user's products |
| DELETE | `/tracked-products/{product_id}` | Remove a product |
| POST | `/check-prices/{user_id}` | Check one user's products |
| POST | `/check-all-prices` | Check all products for automation |
| GET | `/health` | Health check |

## n8n workflow

```text
Schedule Trigger
      -> HTTP Request (POST /check-all-prices)
      -> Split Out (products)
      -> Switch (status)
           -> increased: send email
           -> decreased: send email
           -> unchanged: end
```

## Environment variables

See `.env.example`. Never commit `.env`; it contains your SerpApi API key.

## Notes before production

This repository uses SQLite for local development. For an always-on hosted deployment, use persistent storage or migrate to PostgreSQL. The current login flow returns user information but does not yet use JWT/session authentication, so authentication should be strengthened before treating the service as production-ready. The automation endpoint should also be protected before exposing it publicly.
