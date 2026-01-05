# How to Run the Maternal and Child Health Monitoring System

## Prerequisites

- Python 3.8 or higher installed on your system
- pip (Python package installer)

## Installation Steps

### 1. Install Dependencies

Open a terminal/command prompt in the project directory and run:

```powershell
pip install -r requirements.txt
```

This will install all required packages including Flask, SQLAlchemy, and other dependencies.

### 2. Environment Setup (Optional)

Create a `.env` file in the project root directory if you want to customize settings:

```env
FLASK_ENV=development
PORT=5000
HOST=127.0.0.1
SECRET_KEY=your-secret-key-here
```

If no `.env` file is provided, the application will use default settings.

## Running the Application

### Method 1: Using run.py (Recommended)

Simply execute:

```powershell
python run.py
```

This will:
- ✅ Initialize the database automatically
- ✅ Start the Flask development server
- ✅ Open your default browser to http://127.0.0.1:5000
- ✅ Display helpful startup information

### Method 2: Using Flask CLI

```powershell
flask run
```

Or with custom host and port:

```powershell
flask run --host=0.0.0.0 --port=8000
```

## Accessing the Application

Once the server is running, open your browser and navigate to:

```
http://127.0.0.1:5000
```

The browser should open automatically when using `python run.py`.

## Available User Roles

The system supports multiple user types:

1. **Admin** - Full system access
2. **Doctor** - Medical professional access
3. **Patient** - Regular user access

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## Database Management

### Clear Database

To reset the database to a clean state:

```powershell
python clear_database.py
```

### Database Location

The SQLite database is stored at:
```
instance/pregnancy_care.db
```

## Common Issues

### Port Already in Use

If port 5000 is already in use, you can:

1. Change the port in `.env` file:
   ```
   PORT=8000
   ```

2. Or specify when running:
   ```powershell
   $env:PORT=8000; python run.py
   ```

### Missing Dependencies

If you encounter import errors, reinstall dependencies:

```powershell
pip install -r requirements.txt --upgrade
```

### Database Errors

If you encounter database issues, try clearing and reinitializing:

```powershell
python clear_database.py
python run.py
```

## Development Mode

The application runs in debug mode by default, which provides:
- Auto-reload on code changes (when using Flask CLI)
- Detailed error messages
- Interactive debugger

For production deployment, set:
```env
FLASK_ENV=production
```

## Project Structure

```
Maternal/
├── run.py                 # Main entry point
├── requirements.txt       # Python dependencies
├── clear_database.py     # Database reset utility
├── app/                  # Application package
│   ├── __init__.py       # App factory
│   ├── config.py         # Configuration
│   ├── models/           # Database models
│   ├── routes/           # URL routes
│   ├── services/         # Business logic
│   ├── static/           # CSS, JS, images
│   └── templates/        # HTML templates
└── instance/             # Instance-specific files
    └── pregnancy_care.db # SQLite database
```

## Support

For issues or questions, please refer to the application documentation or contact the development team.
