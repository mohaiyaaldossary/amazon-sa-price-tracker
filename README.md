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

---

## Features

- User registration and login
- Email/password authentication
- Multiple tracked products per user
- Add Amazon.sa products using product URLs
- Remove tracked products
- Retrieve real Amazon.sa product information using SerpApi
- Store product information and current prices
- Detect price changes:
  - Increased
  - Decreased
  - Unchanged
- Automatic price checks every 2 hours
- Email notification when a price increases
- Email notification when a price decreases
- REST API with FastAPI
- Interactive Swagger documentation
- Deployed frontend and backend

---

## Tech Stack

### Frontend

- React
- Vite
- JavaScript
- CSS
- Render Static Site

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Uvicorn
- SerpApi
- Docker
- Render Web Service

### Automation

- n8n Cloud
- Gmail
- Scheduled workflow every 2 hours

---

## Architecture

```text
                     ┌──────────────────┐
                     │       User       │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │  React Frontend  │
                     │     (Render)     │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ FastAPI Backend  │
                     │     (Render)     │
                     └───────┬──┬───────┘
                             │  │
                    ┌────────┘  └─────────┐
                    ▼                     ▼
             ┌─────────────┐       ┌─────────────┐
             │   SQLite    │       │   SerpApi   │
             │  Database   │       └──────┬──────┘
             └─────────────┘              │
                                          ▼
                                    ┌───────────┐
                                    │ Amazon.sa │
                                    └───────────┘


                     ┌──────────────────┐
                     │    n8n Cloud     │
                     │ Every 2 Hours    │
                     └────────┬─────────┘
                              │
                              ▼
                     POST /check-all-prices
                              │
                              ▼
                      Compare Prices
                       /      |      \
                      /       |       \
               Increased  Decreased  Unchanged
                   │          │           │
                   ▼          ▼           ▼
                 Gmail      Gmail        End
How It Works
A user creates an account and logs in.
The user adds an Amazon.sa product to their tracking list.
The frontend sends the product information to the FastAPI backend.
The backend retrieves current product information through SerpApi.
The product and its current price are stored in the database.
n8n automatically calls the backend every 2 hours.
FastAPI retrieves the latest price and compares it with the stored price.
Each product receives one of three statuses:
increased
decreased
unchanged
n8n processes each product separately.
If the price increased or decreased, Gmail sends an email notification to the product owner.
If the price did not change, no email is sent.
API Endpoints
Method	Endpoint	Description
POST	/users/register	Register a new user
POST	/users/login	Log in
GET	/product/{asin}	Retrieve current Amazon.sa product data
POST	/tracked-products	Add a tracked product
GET	/tracked-products/{user_id}	Get a user's tracked products
DELETE	/tracked-products/{product_id}	Remove a tracked product
POST	/check-prices/{user_id}	Check prices for one user
POST	/check-all-prices	Check prices for all tracked products
GET	/health	Check API health

Full interactive API documentation is available through Swagger at:

https://amazon-sa-price-tracker.onrender.com/docs

n8n Automation

The n8n workflow is included in this repository:

n8n/price-tracker-workflow-public.json
Workflow
Schedule Trigger
      │
      │ Every 2 hours
      ▼
HTTP Request
POST /check-all-prices
      │
      ▼
Split Products
      │
      ▼
Switch
 ┌────┴──────────────┐
 │                   │
 ▼                   ▼
Price Increased   Price Dropped
 │                   │
 ▼                   ▼
Gmail               Gmail

Unchanged → End
Importing the Workflow
Open n8n.
Import price-tracker-workflow-public.json.
Connect your own Gmail credentials.
Verify the backend API URL.
Publish the workflow.

The public workflow file does not contain Gmail credentials or API keys.

Local Setup
1. Clone the Repository
git clone https://github.com/mohaiyaaldossary/amazon-sa-price-tracker.git
cd amazon-sa-price-tracker
2. Create a Virtual Environment
python -m venv .venv

On Windows:

.venv\Scripts\activate

On macOS/Linux:

source .venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
4. Configure Environment Variables

Create a .env file based on .env.example.

SERPAPI_KEY=your_serpapi_key_here

Never commit your real .env file to GitHub.

5. Start the Backend
uvicorn app.main:app --reload

The API will be available at:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs
Project Structure
amazon-sa-price-tracker/
│
├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── config.py
│   ├── database.py
│   ├── errors.py
│   └── main.py
│
├── n8n/
│   └── price-tracker-workflow-public.json
│
├── tests/
│
├── .env.example
├── .gitignore
├── .python-version
├── Dockerfile
├── README.md
└── requirements.txt
Environment Variables
Variable	Description
SERPAPI_KEY	API key used to retrieve Amazon.sa product information through SerpApi

Secrets are stored as environment variables and are not included in the repository.

Deployment

The project is deployed using Render.

Backend

The FastAPI backend runs as a Render Web Service using Docker.

Frontend

The React/Vite frontend runs as a Render Static Site.

Automation

n8n Cloud runs the price-check workflow every 2 hours independently of the user's computer.

Security and Production Notes

This project is primarily designed as a portfolio project.

For a production environment, the following improvements are recommended:

JWT or session-based authentication
Stronger user authorization
Protection for the /check-all-prices automation endpoint
PostgreSQL or another persistent production database
Rate limiting
Improved logging and error handling
Secure management of production secrets
Future Improvements

Potential improvements include:

Price history
Price history charts
Product images
User notification preferences
PostgreSQL database
JWT authentication
Dashboard statistics
Support for additional online stores
Author

Mohaiya Aldossary

Artificial Intelligence student and developer.

Disclaimer

This project is an independent portfolio project and is not affiliated with or endorsed by Amazon or SerpApi.


This version also documents the **n8n workflow**, so someone viewing your GitHub can understand the entire project rather than only the FastAPI backend.
