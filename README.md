# Amazon.sa Price Tracker

A full-stack Amazon.sa price tracking application that allows users to track products and automatically receive email notifications when prices change.

The project uses **React** for the frontend, **FastAPI** for the backend, **SerpApi** for Amazon.sa product data, and **n8n** for automated price monitoring and email notifications.

## Live Demo

**Frontend:**  
https://amazon-sa-price-tracker-frontend.onrender.com

**Backend API:**  
https://amazon-sa-price-tracker.onrender.com

**Swagger API Documentation:**  
https://amazon-sa-price-tracker.onrender.com/docs

## Features

- User registration and login
- Multiple tracked products per user
- Add and remove Amazon.sa products
- Retrieve real Amazon.sa product information using SerpApi
- Detect price changes: `increased`, `decreased`, or `unchanged`
- Automatic price checks every 2 hours
- Gmail notifications for price increases and decreases
- REST API with FastAPI and interactive Swagger documentation
- Deployed frontend and backend

## Tech Stack

**Frontend:** React, Vite, JavaScript, CSS, Render Static Site  
**Backend:** Python, FastAPI, SQLAlchemy, SQLite, Uvicorn, SerpApi, Docker, Render Web Service  
**Automation:** n8n Cloud, Gmail, scheduled workflow every 2 hours

## Architecture

```text
User
  |
  v
React Frontend
  |
  v
FastAPI Backend ----> SQLite
  |
  +----> SerpApi ----> Amazon.sa

n8n Cloud
  |
  | Every 2 hours
  v
POST /check-all-prices
  |
  v
Compare Prices
   /      |       \
increased decreased unchanged
   |         |        |
 Gmail     Gmail      End
```

## How It Works

1. A user creates an account and logs in.
2. The user adds an Amazon.sa product to their tracking list.
3. FastAPI retrieves the current product information through SerpApi and stores it in the database.
4. n8n calls `/check-all-prices` every 2 hours.
5. FastAPI compares the latest price with the stored price.
6. n8n sends a Gmail notification when the price increases or decreases. No email is sent when the price is unchanged.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/users/register` | Register a new user |
| POST | `/users/login` | Log in |
| GET | `/product/{asin}` | Retrieve current Amazon.sa product data |
| POST | `/tracked-products` | Add a tracked product |
| GET | `/tracked-products/{user_id}` | Get a user's tracked products |
| DELETE | `/tracked-products/{product_id}` | Remove a tracked product |
| POST | `/check-prices/{user_id}` | Check prices for one user |
| POST | `/check-all-prices` | Check prices for all tracked products |
| GET | `/health` | Check API health |

## n8n Automation

The exported workflow is included at:

```text
n8n/price-tracker-workflow-public.json
```

Workflow:

```text
Schedule Trigger
      |
      v
HTTP Request (POST /check-all-prices)
      |
      v
Split Out (products)
      |
      v
Switch (status)
   /      |       \
increased decreased unchanged
   |         |        |
 Gmail     Gmail      End
```

To use it, import the JSON into n8n, connect your own Gmail OAuth credentials, verify the backend API URL, and publish the workflow. The public workflow file does not contain Gmail credentials or API keys.

## Local Setup

Clone the repository:

```bash
git clone https://github.com/mohaiyaaldossary/amazon-sa-price-tracker.git
cd amazon-sa-price-tracker
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your SerpApi key:

```env
SERPAPI_KEY=your_serpapi_key_here
```

Never commit your real `.env` file.

Start the backend:

```bash
uvicorn app.main:app --reload
```

Local Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Project Structure

```text
amazon-sa-price-tracker/
├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── config.py
│   ├── database.py
│   ├── errors.py
│   └── main.py
├── n8n/
│   └── price-tracker-workflow-public.json
├── tests/
├── .env.example
├── .gitignore
├── .python-version
├── Dockerfile
├── README.md
└── requirements.txt
```

## Deployment

The FastAPI backend runs as a Render Web Service using Docker. The React/Vite frontend runs as a Render Static Site. n8n Cloud runs the price-check workflow every 2 hours independently of the user's computer.

## Security and Production Notes

This is primarily a portfolio project. Before production use, improvements should include JWT or session-based authentication, stronger user authorization, protection for `/check-all-prices`, PostgreSQL or another persistent production database, rate limiting, improved logging, and secure management of production secrets.

## Future Improvements

- Price history and charts
- Product images
- User notification preferences
- PostgreSQL
- JWT authentication
- Dashboard statistics
- Support for additional online stores

## Author

**Mohaiya Aldossary**

Artificial Intelligence student and developer.

## Disclaimer

This project is an independent portfolio project and is not affiliated with or endorsed by Amazon or SerpApi.
