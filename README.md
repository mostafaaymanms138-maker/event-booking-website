# Bristol Community Events

Bristol Community Events is a full-stack web application for discovering local events and managing ticket bookings. Built with Python, Flask, and MySQL, the project includes customer booking workflows and an administrative interface for managing event operations.

Developed as a university project at the University of the West of England (UWE) and shared as part of my software development portfolio.

## Key features

### Event discovery and booking

- Browse events and filter by category, date, and free-entry availability.
- View event details and book tickets.
- Apply advance-booking discounts and a UWE student discount.
- View booking history, download booking receipts, and cancel bookings.
- Join a waiting list when an event is fully booked.

### Administration

- Manage events, venues, users, and bookings.
- Review reports, including sales and top-customer summaries.
- Apply a price reduction to events with low ticket sales.

### Implementation

- Responsive interface for desktop, tablet, and mobile.
- Password hashing with Werkzeug.
- Parameterised SQL queries and role-based access controls.
- Cookie consent banner.

## Technology

- Python 3.10+
- Flask
- MySQL
- HTML, CSS, and JavaScript

## Project structure

```text
bristol-community-events/
├── app.py
├── requirements.txt
├── bce_dump.sql
├── templates/
│   ├── admin/
│   └── [application page templates]
├── static/
│   └── style.css
└── README.md
```

## Run locally

### Requirements

- Python 3.10 or later
- MySQL Server
- Packages listed in `requirements.txt`

### Setup

1. Clone or download the repository and open a terminal in the project folder.
2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start MySQL and import the database dump:

   ```bash
   mysql -u <your-mysql-user> -p < bce_dump.sql
   ```

   The dump creates the `bce` database and its tables. Enter your local MySQL password when prompted.

4. Configure the database connection in `app.py` for your local environment. Do not commit database passwords, secret keys, or other credentials to the repository.
5. Start the application:

   ```bash
   python app.py
   ```

6. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in a browser.

## Admin access

The application includes an administrative panel for authorised accounts. Admin credentials are not published in this repository. Configure a local test account for development or assessment.

## Current limitations

- Payments are simulated; no external payment provider is connected.
- Waiting-list status is stored in the database, but notifications are not sent by email.
- Multi-day event bookings are stored in the database but are not available through the booking interface.

## Screenshots

Add screenshots of the event listing, booking flow, and admin panel here when available. Store image files in a `screenshots/` folder and reference them like this:

```markdown
![Event listing](screenshots/events.png)
```

## Academic and portfolio use

This project was developed for university coursework and is presented here to demonstrate my work. Please use it for learning and inspiration, and follow your institution’s academic integrity guidance.
