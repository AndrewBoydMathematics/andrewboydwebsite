# Artist Portfolio Website

A modern artist portfolio website built with Django and React.

## Features
- Artwork gallery with filtering and categorization
- Artwork status tracking (For Sale, Sold, Not Available)
- Artwork tagging system (Graphite, Oil, Portrait, Figure)
- Commission request system
- Responsive design

## Setup Instructions

### Backend Setup
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

### Frontend Setup
1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

## Environment Variables
Create a `.env` file in the root directory with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Admin Password Hint

If you ever need a reminder for your admin password, the hint is: **C.E.** 