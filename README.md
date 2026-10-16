# Bristol Community Events

Bristol Community Events is a full-stack web application for discovering local events and managing ticket bookings. Built with Python, Flask, and MySQL, it provides customer booking features and an administrative interface for managing event operations.

Developed as a university project at the University of the West of England (UWE Bristol).

## Features

### Event discovery and booking

- Browse and filter events by category, date, and free-entry availability.
- View event details and book tickets.
- Apply advance-booking discounts of 5% to 20%, depending on how far ahead a booking is made.
- Apply a 10% UWE student discount.
- Use simulated payment with card validation.
- View booking history, download receipts, and cancel bookings.
- Join a waiting list when an event is fully booked.

### Administration

- Manage events, venues, users, and bookings.
- View reports, including sales and top-customer summaries.
- Apply a 25% price reduction to events with low ticket sales.

### Implementation

- Responsive interface for desktop, tablet, and mobile.
- Password hashing with Werkzeug.
- Parameterised SQL queries.
- Role-based access control for customer and administrator pages.
- Cookie consent banner.

## Technology

- Python 3.10+
- Flask
- MySQL
- HTML, CSS, and JavaScript

## Project structure

```text
bristol-community-events/
├── README.md
├── .gitignore
├── Database/
│   ├── bce_dump.sql
│   └── ERD.png
└── website/
    ├── app.py
    ├── requirements.txt
    ├── static/
    │   └── style.css
    └── templates/
        ├── admin/
        └── [application page templates]
```

## Run locally

### Requirements

- Python 3.10 or later
- MySQL Server

### Database setup

The repository's `Database/bce_dump.sql` defines the project tables and creates the `bce` database. It is schema-only and contains no user, booking, payment, or event sample records. Add fictional test data locally if you want to demonstrate the application with populated pages.

To set up the database with MySQL Workbench:

1. Open `Database/bce_dump.sql` in MySQL Workbench.
2. Connect to your local MySQL server.
3. Run the complete SQL script to create the `bce` database and its tables.

### Start the application

1. Install the Python dependencies:

   ```bash
   cd website
   pip install -r requirements.txt
   ```

2. Configure the database connection and Flask session key for your local environment. Before publishing, remove hard-coded credentials and secrets from `app.py` and load them from environment variables instead. Never commit real passwords or secret keys.
3. Start the application:

   ```bash
   python app.py
   ```

4. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Admin access

The application includes an administrator panel for authorised accounts. No login credentials are included in this repository.

## Current limitations

- Payments are simulated; no external payment provider is connected.
- Waiting-list status is stored in the database, but email notifications are not sent.
- Multi-day event bookings are stored in the database but are not available through the booking interface.

## Database diagram

![Entity relationship diagram](Database/ERD.png)

## Author

**Mostafa Abdelkarim** · BSc (Hons) Computer Science, UWE Bristol · [LinkedIn](https://www.linkedin.com/in/mostafa-ayman-8045a7399/)
