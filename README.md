# Haulpool - Transport Management System

Haulpool is a comprehensive web application designed to streamline the entire transport process, from initial vehicle booking to final payment settlement. The platform serves as a bridge between transport operators and clients, facilitating efficient vehicle allocation, routing, and financial tracking.

## 🚀 Features

### For Transport Operators
- **Dashboard**: Real-time overview of operations, vehicle status, and pending payments.
- **Vehicle Management**: Add, update, and track vehicle details (Type, Registration No, Capacity, Driver).
- **Trip Management**: Assign vehicles to specific routes, manage vehicle availability, and view trip history.
- **Client Tracking**: Monitor client bookings and status.
- **Financials**: Track earnings, pending dues, and settlements.
- **Route Optimization**: Find the most efficient routes for trips.

### For Clients
- **Booking**: Request vehicles for specific dates and locations.
- **Tracking**: Monitor the status of their assigned vehicles.
- **Notifications**: Real-time updates on vehicle assignments and trip progress.

### Core System Features
- **Authentication**: Secure login/registration for both Operators and Clients.
- **Database**: PostgreSQL integration for robust data management.
- **Maps**: Integrated Google Maps for route planning and visualization.
- **Payments**: Support for online payment gateways and manual settlement tracking.

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: PostgreSQL
- **Authentication**: Flask-Bcrypt
- **APIs**: Flask-RESTful
- **Utilities**: Requests (HTTP), Haversine (Distance Calculation)

### Frontend
- **JavaScript**: Vanilla JS for dynamic interactions
- **Mapping**: Leaflet (OpenStreetMap)
- **Charts**: Chart.js (Data Visualization)
- **UI Libraries**:
    - Tabulator (Data Tables)
    -rater.js (Star Ratings)
    - jsPDF & FileSaver (PDF Generation)

### Infrastructure
- **Web Server**: Gunicorn
- **Proxy**: Nginx
- **Process Manager**: Supervisor

## 📂 Project Structure

```
haulpool_project/
├── app.py                      # Main Flask application entry point
├── routes.py                   # API route definitions
├── models.py                   # Database models (SQLAlchemy)
├── config.py                   # Application configuration
├── static/
│   ├── css/                    # Stylesheets
│   ├── js/                     # JavaScript logic (main.js, operator.js, client.js)
│   └── assets/                 # Images and static files
├── templates/
│   ├── auth/                   # Authentication pages (login, register)
│   ├── operator/               # Operator-specific templates (dashboard, trips)
│   └── client/                 # Client-specific templates (booking, dashboard)
├── .env                        # Environment variables (DB credentials, keys)
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation
```

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL Database

### 1. Clone the repository
```bash
git clone <repository-url>
cd haulpool_project
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
.\venv\Scripts\Activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
Ensure your PostgreSQL server is running and create a database.

Run the application:
```bash
python app.py
```
The app will start on `http://[IP_ADDRESS]`.

## 🎯 Deployment

To deploy the application to a Linux server, you can use the following stack:

- **Web Server**: Nginx (Reverse Proxy)
- **Application Server**: Gunicorn
- **Process Manager**: Supervisor

### Quick Deployment Steps

1. **Install System Dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3-venv python3-pip python3-dev nginx supervisor libpq-dev
   ```

2. **Setup Python Environment**:
   ```bash
   python3 -m venv /opt/haulpool/venv
   source /opt/haulpool/venv/bin/activate
   pip install -r /opt/haulpool/haulpool_project/requirements.txt
   ```

3. **Configure Gunicorn**:
   Create a Gunicorn service file:
   ```bash
   sudo nano /etc/systemd/system/haulpool.service
   ```
   Add the following content:
   ```ini
   [Unit]
   Description=Haulpool Gunicorn Service
   After=network.target

   [Service]
   User=ubuntu
   Group=www-data
   WorkingDirectory=/opt/haulpool/haulpool_project
   Environment="PATH=/opt/haulpool/venv/bin"
   ExecStart=/opt/haulpool/venv/bin/gunicorn --workers 3 --bind unix:/opt/haulpool/haulpool.sock app:app

   [Install]
   WantedBy=multi-user.target
   ```

4. **Configure Nginx**:
   Create a Nginx site configuration:
   ```bash
   sudo nano /etc/nginx/sites-available/haulpool
   ```
   Add the following:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           include proxy_params;
           proxy_pass http://unix:/opt/haulpool/haulpool.sock;
       }
   }
   ```
   Enable the site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/haulpool /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

5. **Start Services**:
   ```bash
   sudo systemctl start haulpool
   sudo systemctl enable haulpool
   ```

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
