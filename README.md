# JePPIX Portal

## Overview
JePPIX Portal is a digital platform that connects customers with service providers in the photonic integrated circuit industry. The platform facilitates order management, service delivery, and performance tracking through a sophisticated web interface.

### Key Features
- **User Management**
  - Role-based access control (Customers and Account Managers)
  - Secure authentication and authorization
  - Customer account registration by Account Managers

- **Service Provider Management**
  - Multiple service providers per Account Manager
  - Service provider to Account Manager relationship tracking
  - Product/service catalog management

- **Order Processing**
  - Customer order creation and management
  - Product selection from authorized service providers
  - Order visibility control based on Account Manager relationships

- **Job Execution**
  - Job tracking and management
  - Multiple orders per job support
  - Job status monitoring and updates

- **Statistical Analysis**
  - Quarterly performance reports
  - Job completion analytics
  - Order and revenue statistics
  - User activity metrics
  - PDF report generation

## Technical Stack
- **Backend**: Django (Python)
- **Database**: SQLite (default), supports PostgreSQL
- **Authentication**: Django built-in auth system
- **File Storage**: Django FileField for PDF reports

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the Repository**
   ```powershell
   git clone <https://github.com/tgfawad/jeppix_portal.git>
   cd jeppix_portal
   ```

2. **Create and Activate Virtual Environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Initialize Database**
   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Superuser**
   ```powershell
   python manage.py createsuperuser
   ```

6. **Run Development Server**
   ```powershell
   python manage.py runserver
   ```

The application will be available at `http://localhost:8000`

## Usage

### Admin Interface
1. Access the admin interface at `http://localhost:8000/admin`
2. Log in with superuser credentials
3. Manage users, service providers, products, and view statistics

### Account Manager Tasks
1. Register new customer accounts
2. Manage service provider relationships
3. Monitor customer orders
4. Generate and view statistical reports

### Customer Functions
1. Create new orders
2. Select products from authorized service providers
3. Track order status
4. View order history

## Project Structure
```
jeppix_portal/
├── accounts/            # User management app
├── orders/             # Order processing app
├── execution/          # Job execution app
├── stat_analysis/      # Statistical analysis app
└── jeppix_portal/     # Project configuration
```

## Testing
Run the test suite:
```powershell
python manage.py test
```

For specific app tests:
```powershell
python manage.py test accounts
python manage.py test orders
python manage.py test execution
python manage.py test stat_analysis
```

## Security Notes
- Orders are confidential and visible only to the assigned account manager
- Customer data is protected through role-based access control
- Service provider access is restricted based on account manager relationships

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request