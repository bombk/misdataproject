# MIS Data Project

A Django web application with SB Admin template for storing and visualizing monthly banking data, including customer data and transaction data with normalized database design.

## Features

- **Dashboard**: Interactive dashboard with charts and statistics
- **Data Upload**: Monthly data upload functionality for CSV files
- **Master Parameters**: Management of master data parameters
- **Data Tables**: View and browse uploaded data
- **Normalized Database**: Properly normalized database schema
- **SB Admin Template**: Professional admin interface

## Project Structure

```
misdataproject/
├── dashboard/
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── urls.py            # URL patterns
│   ├── admin.py           # Admin configuration
│   ├── static/            # Static files (CSS, JS, Images)
│   │   ├── css/
│   │   ├── js/
│   │   ├── images/
│   │   └── vendor/
│   └── templates/         # HTML templates
│       └── dashboard/
├── misdataproject/
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py
├── manage.py
└── db.sqlite3
```

## Database Schema

### Master Tables
- **Branch**: Branch codes and names
- **CustomerCategory**: Customer categorization types
- **ServiceType**: Service types (Mobile Banking, Internet Banking, etc.)
- **TransactionType**: Transaction types
- **InstrumentType**: Instrument types
- **GeographicalLocation**: Geographical locations
- **ChannelUsed**: Channels used for transactions

### Data Tables
- **CustomerData**: Monthly customer data records
- **TransactionData**: Monthly transaction data records
- **DataUploadLog**: Upload history and status

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install django
   ```

2. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

4. **Start Development Server**:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

## Usage

### Data Upload

1. Navigate to **Data Upload** page
2. Select data type (Customer Data or Transaction Data)
3. Choose month/year
4. Upload CSV file with proper format

#### Customer Data CSV Format:
- Branch code
- Branch name
- Categorization of customers
- Mobile Banking
- Status
- Number of customers

#### Transaction Data CSV Format:
- Range of transactions
- Form of instrument
- Type of transaction
- Geographical location
- Channel used
- Number of transactions
- Amount

### Navigation

- **Dashboard**: Main overview with charts and statistics
- **Master Parameters**: View all master data parameters
- **Data Upload**: Upload monthly data files
- **Data Tables**: Browse uploaded data
  - Customer Data
  - Transaction Data

### Admin Panel

Access the Django admin panel at `/admin/` to manage:
- All database models
- User accounts
- Data records

## Features

### Dashboard Charts
- Customer status distribution (pie chart)
- Transaction types breakdown (pie chart)
- Monthly customer trends (line chart)
- Monthly transaction amount trends (line chart)

### Data Management
- Automatic creation of master parameters during upload
- Data validation and error handling
- Upload history tracking
- Pagination for large datasets

### Security
- CSRF protection
- User authentication
- Input validation
- SQL injection prevention

## Technical Details

- **Framework**: Django 5.2.5
- **Database**: SQLite (development)
- **Frontend**: SB Admin 2 Bootstrap template
- **Charts**: Chart.js
- **File Upload**: CSV processing with validation

## Login Credentials

- **Username**: admin
- **Password**: admin123

## API Endpoints

- `/api/dashboard-data/`: JSON API for dashboard charts data

## Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Support

For issues or questions, please check the Django admin panel or contact the development team.

