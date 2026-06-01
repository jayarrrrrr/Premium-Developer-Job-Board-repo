# Premium Developer Job Board

A Django-based premium tech job board with search, location filters, pagination, signup honeypot protection, and JWT-powered premium field masking.

## Setup
1. Activate the virtual environment.
2. Install dependencies: `python -m pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Load sample data: `python seed_data.py`
5. Start the development server: `python manage.py runserver`

## Features
- Job listing API with search and location filters
- Pagination with filter state preserved in the UI
- Premium-only salary and application link masking
- Signup honeypot trap to block bot submissions
- JWT authentication with `is_premium` claim
