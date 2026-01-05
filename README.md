# Maternal and Child Health Monitoring System

A comprehensive web-based healthcare management system for monitoring maternal and child health, built with Flask and SQLAlchemy.

## Features

- **User Management**: Multi-role support (Admin, Doctor, Patient)
- **Pregnancy Tracking**: Monitor pregnancy progress, weight tracking, and appointments
- **Baby Care**: Growth tracking, vaccination schedules, and nutrition plans
- **Appointments**: Schedule and manage medical consultations
- **Health Reports**: Generate and view medical reports
- **Exercise & Meditation**: Access to health and wellness resources
- **Chatbot Assistant**: AI-powered health assistance
- **Government Schemes**: Information on healthcare schemes
- **FAQ System**: Common health questions and answers

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy with SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Charts**: Chart.js for data visualization
- **Email**: Email notification service

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/maternal-health-system.git
cd maternal-health-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python run.py
```

4. Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## Detailed Documentation

For detailed setup and usage instructions, see [HOW_TO_RUN.md](HOW_TO_RUN.md)

## Project Structure

```
Maternal/
├── run.py                 # Main entry point
├── requirements.txt       # Python dependencies
├── clear_database.py     # Database reset utility
├── app/                  # Application package
│   ├── models/           # Database models
│   ├── routes/           # URL routes
│   ├── services/         # Business logic
│   ├── static/           # CSS, JS, images
│   ├── templates/        # HTML templates
│   └── utils/            # Helper functions
└── instance/             # Instance-specific files
```

## User Roles

- **Admin**: Full system access, manage users and content
- **Doctor**: Access to patient records, appointments, and report generation
- **Patient**: Personal health tracking, appointments, and resources

## Database Management

Reset the database:
```bash
python clear_database.py
```

## Configuration

Create a `.env` file for custom settings:
```env
FLASK_ENV=development
PORT=5000
HOST=127.0.0.1
SECRET_KEY=your-secret-key-here
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

For issues or questions, please open an issue on GitHub.
