# 🚛 HaulPool (ReHaul / Sun_Flow) · Freight & Logistics Network

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-black.svg)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB-green.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-Proprietary-orange.svg)](#)

HaulPool is a digital freight-pooling and logistics marketplace that bridges the gap between **Transport Operators** (fleet and truck owners) and **Customers** (shippers and cargo owners). It optimizes empty backhauls and shared truck capacity, allowing shippers to find affordable shipping routes while enabling operators to maximize fleet profitability.

---

## 📋 Table of Contents
1. [Features](#-features)
2. [Tech Stack & Architecture](#-tech-stack--architecture)
3. [Prerequisites](#-prerequisites)
4. [Step-by-Step Installation & Setup](#-step-by-step-installation--setup)
5. [Running the Application](#-running-the-application)
6. [Environment Variables Reference](#-environment-variables-reference)
7. [User Roles & Workflows](#-user-roles--workflows)
8. [Project Directory Structure](#-project-directory-structure)
9. [Common Troubleshooting & FAQs](#-common-troubleshooting--faqs)

---

## 🌟 Features

### 🏢 For Transport Operators (Fleet Owners)
- **Interactive Route Planner**: Schedule new freight trips, specify starting and destination hubs, vehicle types, available weight capacity (tons), and asking rates.
- **Operator Dashboard**: Real-time overview of active trips, pending booking requests, completed deliveries, and total revenue.
- **Booking Management**: Accept, reject, or update shipment requests from shippers.
- **Fleet Analytics**: Monitor vehicle occupancy rates, revenue statistics, and performance metrics.

### 📦 For Customers (Shippers)
- **Route Search**: Browse scheduled trips matching origin and destination hubs.
- **Space Booking**: Reserve full truckloads or partial container/pallet capacity.
- **Shipments Tracker**: Live dashboard to inspect past shipments, status updates (`pending`, `confirmed`, `in-transit`, `delivered`), and payment rates.
- **Customer Profile**: Manage contact details, business profile, and shipping addresses.

### 🔐 Security & Architecture
- **Role-Based Authentication**: Distinct sign-in and registration portals for Operators vs. Customers.
- **Password Security**: Strong password hashing using `Flask-Bcrypt` (12 salt rounds).
- **Session Management**: Session management handled via `Flask-Login` and server-side contexts.
- **Document Store**: High-performance NoSQL schema on **MongoDB**.

---

## 🛠 Tech Stack & Architecture

- **Backend**: Python 3.10+, Flask 2.3.3, Werkzeug 2.3.7
- **Authentication**: Flask-Login, Flask-Bcrypt, WTForms, Flask-WTF
- **Database**: MongoDB 5.0+ via PyMongo 4.9+ / Flask-PyMongo
- **Frontend**: Responsive HTML5, Vanilla CSS3 (Glassmorphism & Dark Mode aesthetic), Jinja2 Templates, FontAwesome 6.5, Google Fonts (`Inter`, `Playfair Display`)
- **Environment Management**: `python-dotenv`

---

## 📦 Prerequisites

Before running the application, make sure you have the following installed on your system:

1. **Python 3.10 or higher**:
   - Check version in terminal:
     ```bash
     python --version
     # or python3 --version
     ```
2. **MongoDB Community Server** (Local or MongoDB Atlas):
   - **Local installation**: [Download MongoDB Community Server](https://www.mongodb.com/try/download/community)
   - Ensure the MongoDB service is running on the default port: `mongodb://localhost:27017`
   - *Windows Users*: Ensure the `MongoDB` Windows Service is started in Services (`services.msc`) or run `mongod` in a terminal.
   - *macOS/Linux Users*: `brew services start mongodb-community` or `sudo systemctl start mongod`.

---

## 🚀 Step-by-Step Installation & Setup

### 1. Clone / Navigate to the Project Directory

Open your terminal or PowerShell and change into the project folder:

```powershell
# Windows PowerShell
cd c:\Users\sidda\OneDrive\Documents\Transport_co_limited\haulpool_project
```

```bash
# macOS / Linux
cd /path/to/Transport_co_limited/haulpool_project
```

---

### 2. Set Up a Python Virtual Environment

It is strongly recommended to use a virtual environment to prevent package conflicts.

#### On Windows (PowerShell):
```powershell
# Create virtual environment named .venv
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```

> **Note for Windows PowerShell Execution Policy:** If you see an error saying `script execution is disabled on this system`, run this once:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
> ```
> then retry `.\.venv\Scripts\Activate.ps1`.

#### On Windows (Command Prompt `cmd`):
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

#### On macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Required Dependencies

With your virtual environment active, install all dependencies from `requirements.txt`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Verified Packages in `requirements.txt`:
| Package | Version | Purpose |
| :--- | :--- | :--- |
| `Flask` | `2.3.3` | Web framework |
| `Werkzeug` | `2.3.7` | WSGI utility library |
| `Flask-Login` | `0.6.2` | User session management |
| `Flask-PyMongo`| `2.3.0` | MongoDB integration for Flask |
| `Flask-WTF` | `1.1.1` | Form handling and CSRF protection |
| `Flask-Bcrypt` | `1.0.1` | Password hashing |
| `WTForms` | `3.0.1` | Flexible form validation |
| `python-dotenv`| `1.0.0` | Loads configuration from `.env` |
| `pymongo` | `>=4.9,<5` | Official Python driver for MongoDB |
| `dnspython` | `2.4.2` | DNS toolkit (required for `mongodb+srv://` URIs) |
| `Pillow` | `>=11.3,<13`| Image handling for uploads |

---

### 4. Configure Environment Variables (`.env`)

A `.env` file should be present in the `haulpool_project/` directory. If it is missing, create a `.env` file with the following contents:

```env
# Flask Secret Key for sessions and CSRF
SECRET_KEY=dev-secret-key-change-this-in-production

# MongoDB Connection String
MONGO_URI=mongodb://localhost:27017/haulpool_db

# MongoDB Database Name
MONGO_DBNAME=haulpool_db

# Environment mode
FLASK_ENV=development
```

> **Using MongoDB Atlas (Cloud)?** Replace `MONGO_URI` with your connection string:
> `MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/haulpool_db?retryWrites=true&w=majority`

---

## ⚡ Running the Application

### Method 1: Using Python directly (Recommended)

Make sure MongoDB is running, then run:

```powershell
python app.py
```

*(Or explicitly with the virtual environment interpreter):*
```powershell
.\.venv\Scripts\python.exe app.py
```

### Method 2: Using the Flask CLI

```powershell
flask run --host=0.0.0.0 --port=5000 --debug
```

### Accessing the Web Application

Once started, open your web browser and navigate to:
```
http://localhost:5000
```
or
```
http://127.0.0.1:5000
```

---

## 👥 User Roles & Workflows

### 1. Transport Operator Flow
1. Visit `http://localhost:5000/auth/operator/register` to create a fleet account (provide Company Name, Fleet Size, Base Hub, etc.).
2. Log in at `http://localhost:5000/auth/operator/login`.
3. Open the **Operator Dashboard** (`/operator/dashboard`).
4. Go to the **Route Planner** (`/operator/route-planner`) to publish empty trucks or planned departures.
5. Review incoming customer booking requests and accept/decline capacity requests.

### 2. Customer (Shipper) Flow
1. Register as a customer at `http://localhost:5000/auth/customer/register`.
2. Log in at `http://localhost:5000/auth/customer/login`.
3. Access your **Customer Dashboard** (`/customer/dashboard`).
4. Search open routes by starting location and destination.
5. Request a shipment booking for your freight weight and cargo specifications.
6. Track booking approval status under **My Shipments** (`/customer/shipments`).

---

## 📁 Project Directory Structure

```plaintext
Transport_co_limited/
│
├── .venv/                         # Project virtual environment (dependencies)
│
└── haulpool_project/              # Main application root
    ├── .env                       # Environment variables (Mongo URI, Secret Key)
    ├── app.py                     # App factory, blueprints, MongoDB index setup
    ├── config.py                  # Configuration loader
    ├── requirements.txt           # Python package requirements
    ├── README.md                  # Project documentation
    │
    ├── database/                  # Database artifacts
    │   └── haulpool.db            # (Legacy placeholder - database is MongoDB)
    │
    ├── models/                    # Data models and MongoDB queries
    │   ├── __init__.py            # Mongo reference initializer
    │   ├── user.py                # Operator and Customer model definitions
    │   ├── trip.py                # Route/trip listings & capacity models
    │   └── booking.py             # Shipment reservations and status
    │
    ├── routes/                    # Flask Blueprint controllers
    │   ├── auth.py                # Login, signup, logout, API auth routes
    │   ├── customer.py            # Customer portal and booking actions
    │   └── operator.py            # Operator portal, route planning, analytics
    │
    ├── templates/                 # Jinja2 HTML templates
    │   ├── base.html              # Core layout, dark-mode styling & navigation
    │   ├── auth/                  # Login and register pages
    │   ├── customers/             # Customer dashboard & shipment views
    │   └── operator/              # Operator dashboard, route planner, analytics
    │
    ├── static/                    # Static assets (custom CSS, JS, branding)
    └── uploads/                   # User-uploaded documents and proof files
```

---

## ❓ Common Troubleshooting & FAQs

### Q1: `ModuleNotFoundError: No module named 'flask'`
- **Cause**: The terminal is using global Python or another environment instead of your virtual environment.
- **Solution**: Explicitly invoke Python using your virtual environment executable:
  ```powershell
  # Inside haulpool_project:
  ..\.venv\Scripts\python.exe app.py
  ```
  Or ensure your virtual environment is activated (`.\.venv\Scripts\Activate.ps1`).

---

### Q2: `ServerSelectionTimeoutError: No replica set members match selector` or MongoDB connection fails
- **Cause**: MongoDB is not running locally on port `27017`.
- **Solution**: 
  - On Windows: Press `Win + R`, type `services.msc`, find **MongoDB Server**, right-click and click **Start**.
  - Alternatively, check your `MONGO_URI` in `.env` to verify the host, port, or cloud Atlas credentials.

---

### Q3: What is the empty `database/haulpool.db` file?
- **Answer**: The project uses **MongoDB** (`haulpool_db` database via PyMongo) for all data persistence (collections: `customers`, `operators`, `trips`, `bookings`). The file `database/haulpool.db` is an empty artifact from earlier SQLite development and is not used by the running application.

---

### Q4: How do I change the port?
To run on a different port (e.g. `8080`), edit the bottom of [`app.py`](file:///c:/Users/sidda/OneDrive/Documents/Transport_co_limited/haulpool_project/app.py):
```python
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8080)
```
Or use the CLI: `flask run --port=8080`.

---

## 🤝 Contributing & License
Developed for transport and freight collaboration. Proprietary software.
