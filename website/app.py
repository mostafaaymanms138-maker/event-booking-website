# Bristol Community Events (BCE) - Flask application
#
# Main Flask application for Bristol Community Events (BCE)
# This file handles all the routes, business logic, and database operations
# for the booking platform.

from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
import mysql.connector                                      # to connect to MySQL
from werkzeug.security import generate_password_hash, check_password_hash  # for safe password storage
from datetime import datetime, date                        # used in discount and cancellation calculations
from functools import wraps                                # needed to make decorators work properly
import os
import secrets                                             # for generating random booking references

app = Flask(__name__)
# Secret key is needed for Flask sessions to work securely
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)


# Database connection
# Store the connection details in a dict so I only have to change
# them in one place if the password/host ever changes

DB = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'bce'),
}
def get_db():
    # Opens a fresh connection each request - simple and works fine for this scale
    return mysql.connector.connect(**DB)


# Auth decorators
# I learned about decorators from the Flask docs - they are a clean
# way to protect routes without repeating the same if-check everywhere

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    # Slightly stricter than login_required - also checks the is_admin flag
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            abort(403)
        return f(*args, **kwargs)
    return decorated


# Business logic functions
# These implement the pricing and cancellation rules from the brief

def calc_advance_discount(event_date):
    # Returns the advance booking discount % based on how far away the event is
    # Uses the thresholds from Table 2 in the assignment brief
    if isinstance(event_date, str):
        event_date = datetime.strptime(str(event_date), '%Y-%m-%d').date()
    days = (event_date - date.today()).days
    if 50 <= days <= 60:   return 20
    elif 35 <= days < 50:  return 15
    elif 25 <= days < 35:  return 10
    elif 15 <= days < 25:  return 5
    return 0  # no discount if less than 15 days away or already passed

def calc_cancellation_charge(event_date, total_price):
    # Works out how much to charge if a user cancels their booking
    # More than 40 days away = free cancellation
    # 25-39 days = 40% charge
    # Less than 25 days = full price charged (no refund)
    if isinstance(event_date, str):
        event_date = datetime.strptime(str(event_date), '%Y-%m-%d').date()
    days = (event_date - date.today()).days
    if days > 40:
        return 0.0
    elif 25 <= days <= 39:
        return round(float(total_price) * 0.40, 2)
    else:
        return round(float(total_price), 2)

def calc_total(base_price, quantity, advance_pct, is_student):
    # Calculates the final price after applying both discounts
    # Advance discount is applied first, then student discount on top
    subtotal = float(base_price) * int(quantity)
    after_advance = subtotal * (1 - advance_pct / 100)
    return round(after_advance * (0.90 if is_student else 1.0), 2)

def gen_reference():
    # Generates a unique booking reference like BCE-2026-47832
    return f"BCE-{date.today().year}-{secrets.randbelow(90000) + 10000}"


# Custom Jinja2 filter for time formatting
# MySQL returns TIME columns as Python timedelta objects, not time objects
# so .strftime() doesn't work directly - this filter handles both cases

@app.template_global()
def event_photo(event_id, category_name, width=600, height=400):
    # Curated Unsplash photos — one specific image per event, category fallback for new ones
    event_photos = {
        1: 'photo-1511192336575-5a79af67a629',  # Jazz Night
        2: 'photo-1561214115-f2f134cc4912',     # Art Exhibition
        3: 'photo-1459865264687-595d652de67e',  # Football Match
        4: 'photo-1455390582262-044cdead277a',  # Creative Writing Workshop
        5: 'photo-1503095396549-807759245b35',  # Hamlet at Bristol Old Vic
        6: 'photo-1507608158173-1dcec673a2e5',  # Bristol Balloon Fiesta
        7: 'photo-1511632765486-a01980e01a18',  # Community Prayers
        8: 'photo-1516035069371-29a1b244cc32',  # Photography Show
        9: 'photo-1498050108023-c5249f4df085',  # Web Design Workshop
    }
    category_fallbacks = {
        'Music':      'photo-1493225457124-a3eb161ffa5f',
        'Exhibition': 'photo-1574182245530-967d9b3831af',
        'Sports':     'photo-1579952363873-27f3bade9f55',
        'Workshop':   'photo-1524178232363-1fb2b075b655',
        'Theatre':    'photo-1460723237483-7a6dc9d0b212',
        'Community':  'photo-1529156069898-49953e39b3ac',
    }
    pid = event_photos.get(event_id) or category_fallbacks.get(category_name, 'photo-1486325212027-8081e485255e')
    return f"https://images.unsplash.com/{pid}?w={width}&h={height}&fit=crop&q=80&auto=format"


@app.template_filter('timeformat')
def timeformat(t):
    if t is None:
        return ''
    if hasattr(t, 'strftime'):
        return t.strftime('%H:%M')
    # timedelta from MySQL - convert total seconds to HH:MM
    total = int(t.total_seconds())
    return f"{total // 3600:02d}:{(total % 3600) // 60:02d}"


def floatify(row, *keys):
    # MySQL DECIMAL columns come back as Python Decimal objects which
    # cause TypeErrors when used in arithmetic with floats in templates.
    # This converts the specified keys to float before passing to Jinja2.
    for k in keys:
        if k in row and row[k] is not None:
            row[k] = float(row[k])
    return row


# Context processor - runs before every template render
# This injects the logged-in user info into every template automatically
# so I don't have to pass it manually to every render_template() call

@app.context_processor
def inject_user():
    return {
        'current_user': session.get('user_name'),
        'is_admin':     session.get('is_admin', False),
        'is_logged_in': 'user_id' in session
    }


# Public routes (no login required)

@app.route('/')
def index():
    # Homepage - fetch the 3 soonest upcoming events to show as featured
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT e.id, e.name, e.date, e.time, e.price, e.tickets_remaining,
               v.name AS venue_name, c.name AS category_name
        FROM events e
        JOIN venues v ON e.venue_id = v.id
        JOIN categories c ON e.category_id = c.id
        WHERE e.is_active = 1 ORDER BY e.date ASC LIMIT 3
    """)
    featured = [floatify(e, 'price') for e in cur.fetchall()]
    cur.close(); db.close()
    return render_template('index.html', featured=featured)


@app.route('/events')
def events():
    # Events listing page with optional filters from the query string
    db = get_db(); cur = db.cursor(dictionary=True)
    category  = request.args.get('category', '')
    date_from = request.args.get('date_from', '')
    date_to   = request.args.get('date_to', '')
    free_only = request.args.get('free', '')

    # Build query dynamically depending on which filters are active
    sql = """
        SELECT e.id, e.name, e.date, e.time, e.price, e.tickets_remaining,
               v.name AS venue_name, c.name AS category_name
        FROM events e
        JOIN venues v ON e.venue_id = v.id
        JOIN categories c ON e.category_id = c.id
        WHERE e.is_active = 1
    """
    params = []
    if category:  sql += " AND c.name = %s";  params.append(category)
    if date_from: sql += " AND e.date >= %s"; params.append(date_from)
    if date_to:   sql += " AND e.date <= %s"; params.append(date_to)
    if free_only: sql += " AND e.price = 0"
    sql += " ORDER BY e.date ASC"

    cur.execute(sql, params)
    events_list = [floatify(e, 'price') for e in cur.fetchall()]

    # Also fetch categories for the filter dropdown
    cur.execute("SELECT DISTINCT name FROM categories ORDER BY name")
    categories = [r['name'] for r in cur.fetchall()]
    cur.close(); db.close()
    return render_template('events.html', events=events_list,
                           categories=categories, selected=category,
                           date_from=date_from, date_to=date_to, free_only=free_only)


@app.route('/event/<int:eid>')
def event_detail(eid):
    # Single event detail page - also works out advance discount to show on the page
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT e.*, v.name AS venue_name, v.address AS venue_address,
               v.capacity, c.name AS category_name
        FROM events e
        JOIN venues v ON e.venue_id = v.id
        JOIN categories c ON e.category_id = c.id
        WHERE e.id = %s AND e.is_active = 1
    """, (eid,))
    event = cur.fetchone()
    if not event:
        cur.close(); db.close(); abort(404)

    floatify(event, 'price')
    advance_pct = calc_advance_discount(event['date'])

    # Check if the logged-in user is already on the waiting list for this event
    on_waitlist = False
    if 'user_id' in session:
        cur.execute("SELECT id FROM waiting_list WHERE user_id=%s AND event_id=%s",
                    (session['user_id'], eid))
        on_waitlist = bool(cur.fetchone())

    cur.close(); db.close()
    return render_template('event_detail.html', event=event,
                           advance_pct=advance_pct, on_waitlist=on_waitlist)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # In a real system this would send an email - for now just show a success message
        flash('Message sent. We will respond within 2–3 business days.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')


# Authentication routes

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name       = request.form.get('full_name', '').strip()
        email      = request.form.get('email', '').strip().lower()  # always store emails lowercase to avoid duplicates
        pwd        = request.form.get('password', '')
        conf       = request.form.get('confirm_password', '')
        is_student = 1 if request.form.get('is_student') else 0

        # Basic validation before touching the database
        if not name or not email or not pwd:
            flash('All required fields must be filled.', 'danger')
            return render_template('register.html')
        if pwd != conf:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        if len(pwd) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return render_template('register.html')

        db = get_db(); cur = db.cursor(dictionary=True)

        # Check email isn't already registered
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            flash('An account with that email already exists.', 'danger')
            cur.close(); db.close()
            return render_template('register.html')

        # Store a hashed password - never store plain text passwords
        cur.execute(
            "INSERT INTO users (full_name, email, password_hash, is_student) VALUES (%s,%s,%s,%s)",
            (name, email, generate_password_hash(pwd), is_student)
        )
        db.commit(); cur.close(); db.close()
        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        pwd   = request.form.get('password', '')
        db = get_db(); cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close(); db.close()
        print(f"[LOGIN] Attempting login for email: {email}, user found: {user is not None}")

        # check_password_hash compares the submitted password against the stored hash
        if user and check_password_hash(user['password_hash'], pwd):
            print(f"[LOGIN] Login successful for user_id: {user['id']}, is_admin: {user['is_admin']}")
            session['user_id']    = user['id']
            session['user_name']  = user['full_name']
            session['is_student'] = bool(user['is_student'])
            session['is_admin']   = bool(user['is_admin'])
            flash(f"Welcome back, {user['full_name']}!", 'success')
            # Admins go straight to the dashboard, regular users go to homepage
            return redirect(url_for('admin_dashboard') if user['is_admin'] else url_for('index'))

        flash('Invalid email or password.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()  # wipe everything from the session so nothing leaks to the next user
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# Booking routes

@app.route('/booking/<int:eid>', methods=['GET', 'POST'])
@login_required
def booking(eid):
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT e.*, v.name AS venue_name, c.name AS category_name
        FROM events e JOIN venues v ON e.venue_id=v.id
        JOIN categories c ON e.category_id=c.id
        WHERE e.id=%s AND e.is_active=1
    """, (eid,))
    event = cur.fetchone()
    if not event:
        cur.close(); db.close(); abort(404)

    # Redirect away if the event is already sold out
    if event['tickets_remaining'] == 0:
        flash('This event is sold out.', 'warning')
        cur.close(); db.close()
        return redirect(url_for('event_detail', eid=eid))

    if request.method == 'POST':
        qty        = int(request.form.get('quantity', 1))
        is_student = 1 if request.form.get('is_student') else 0  # comes from a checkbox on the form

        # Make sure they haven't requested more tickets than available
        if qty < 1 or qty > event['tickets_remaining']:
            flash(f"Only {event['tickets_remaining']} tickets available.", 'danger')
            cur.close(); db.close()
            return redirect(url_for('booking', eid=eid))

        # Calculate final price - store everything in session so the payment page can use it
        adv_pct    = calc_advance_discount(event['date'])
        base_price = float(event['price'])
        total      = calc_total(base_price, qty, adv_pct, bool(is_student))
        ref        = gen_reference()

        # Save pending booking data in session - it only becomes a real booking after payment
        session['pending_booking'] = {
            'event_id':   eid,
            'quantity':   qty,
            'is_student': is_student,
            'advance_pct': adv_pct,
            'base_price': base_price,
            'total':      total,
            'ref':        ref,
            'event_name': event['name'],
            'venue_name': event['venue_name'],
            'event_date': str(event['date']),
            'event_time': str(event['time']) if event['time'] else '',
        }

        cur.close(); db.close()
        return redirect(url_for('payment'))

    # GET request - show the booking form
    advance_pct = calc_advance_discount(event['date'])
    event['price'] = float(event['price'])
    cur.close(); db.close()
    return render_template('booking.html', event=event, advance_pct=advance_pct,
                           is_student=session.get('is_student', False))


@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    # Pull the pending booking out of session - if it's gone, send them back
    pb = session.get('pending_booking')
    if not pb:
        flash('No pending booking found. Please start again.', 'warning')
        return redirect(url_for('events'))

    if request.method == 'POST':
        # In a real system we'd call a payment gateway here (Stripe, PayPal, etc.)
        # For this academic project we simulate a successful payment
        card_number = request.form.get('card_number', '').replace(' ', '')
        expiry      = request.form.get('expiry', '')
        cvv         = request.form.get('cvv', '')

        # Basic card validation
        if len(card_number) != 16 or not card_number.isdigit():
            flash('Invalid card number. Please enter a 16-digit card number.', 'danger')
            return render_template('payment.html', pb=pb)
        if not expiry or len(expiry) != 5 or expiry[2] != '/':
            flash('Invalid expiry date. Use MM/YY format.', 'danger')
            return render_template('payment.html', pb=pb)
        if len(cvv) not in (3, 4) or not cvv.isdigit():
            flash('Invalid CVV. Please enter a 3 or 4 digit security code.', 'danger')
            return render_template('payment.html', pb=pb)

        # Payment approved — now insert the booking into the database
        db = get_db(); cur = db.cursor(dictionary=True)

        # Double-check tickets are still available - someone else could have booked
        # in the time between the user filling in the booking form and submitting payment
        cur.execute("SELECT tickets_remaining FROM events WHERE id=%s AND is_active=1",
                    (pb['event_id'],))
        ev_row = cur.fetchone()
        if not ev_row or ev_row['tickets_remaining'] < pb['quantity']:
            session.pop('pending_booking', None)
            flash('Sorry, tickets are no longer available for this event.', 'danger')
            cur.close(); db.close()
            return redirect(url_for('event_detail', eid=pb['event_id']))

        cur.execute("""
            INSERT INTO bookings
            (user_id, event_id, quantity, is_student, advance_discount_pct,
             student_discount_pct, base_price, total_price, status, reference)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'confirmed',%s)
        """, (session['user_id'], pb['event_id'], pb['quantity'], pb['is_student'],
              pb['advance_pct'], 10 if pb['is_student'] else 0,
              pb['base_price'], pb['total'], pb['ref']))

        # Reduce the available ticket count
        cur.execute("UPDATE events SET tickets_remaining=tickets_remaining-%s WHERE id=%s",
                    (pb['quantity'], pb['event_id']))
        db.commit()

        # Get the new booking ID - fall back to querying by reference if lastrowid is 0
        bid = cur.lastrowid
        if not bid:
            cur.execute("SELECT id FROM bookings WHERE reference=%s", (pb['ref'],))
            row = cur.fetchone()
            bid = row['id'] if row else 0

        cur.close(); db.close()

        # Clear the pending booking from session now that it's confirmed
        session.pop('pending_booking', None)
        return redirect(url_for('receipt', bid=bid))

    return render_template('payment.html', pb=pb)


@app.route('/receipt/<int:bid>')
@login_required
def receipt(bid):
    # Show the booking confirmation - only the user who made the booking can see it
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT b.*, e.name AS event_name, e.date AS event_date,
               e.time AS event_time, v.name AS venue_name,
               u.full_name AS user_name, u.email AS user_email
        FROM bookings b
        JOIN events e ON b.event_id=e.id
        JOIN venues v ON e.venue_id=v.id
        JOIN users u ON b.user_id=u.id
        WHERE b.id=%s AND b.user_id=%s
    """, (bid, session['user_id']))
    bk = cur.fetchone()
    cur.close(); db.close()
    if not bk:
        abort(404)
    floatify(bk, 'base_price', 'total_price', 'cancellation_charge',
             'advance_discount_pct', 'student_discount_pct')
    return render_template('receipt.html', bk=bk)


@app.route('/waitlist/<int:eid>', methods=['POST'])
@login_required
def join_waitlist(eid):
    # Add the user to the waiting list if they aren't already on it
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT id FROM waiting_list WHERE user_id=%s AND event_id=%s",
                (session['user_id'], eid))
    if not cur.fetchone():
        cur.execute("INSERT INTO waiting_list (user_id, event_id) VALUES (%s,%s)",
                    (session['user_id'], eid))
        db.commit()
        flash('You have been added to the waiting list.', 'success')
    else:
        flash('You are already on the waiting list.', 'info')
    cur.close(); db.close()
    return redirect(url_for('event_detail', eid=eid))


# User account routes

@app.route('/my-bookings')
@login_required
def my_bookings():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT b.*, e.name AS event_name, e.date AS event_date,
               v.name AS venue_name
        FROM bookings b
        JOIN events e ON b.event_id=e.id
        JOIN venues v ON e.venue_id=v.id
        WHERE b.user_id=%s ORDER BY b.booking_date DESC
    """, (session['user_id'],))
    bookings = [floatify(b, 'total_price', 'cancellation_charge') for b in cur.fetchall()]
    cur.execute("""
        SELECT w.joined_at, w.notified, e.name AS event_name, e.date AS event_date, v.name AS venue_name
        FROM waiting_list w
        JOIN events e ON w.event_id=e.id
        JOIN venues v ON e.venue_id=v.id
        WHERE w.user_id=%s ORDER BY w.joined_at DESC
    """, (session['user_id'],))
    my_waitlist = cur.fetchall()
    cur.close(); db.close()
    return render_template('my_bookings.html', bookings=bookings, today=date.today(), my_waitlist=my_waitlist)


@app.route('/cancel/<int:bid>', methods=['POST'])
@login_required
def cancel_booking(bid):
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT b.*, e.date AS event_date
        FROM bookings b JOIN events e ON b.event_id=e.id
        WHERE b.id=%s AND b.user_id=%s AND b.status='confirmed'
    """, (bid, session['user_id']))
    bk = cur.fetchone()
    if not bk:
        cur.close(); db.close(); abort(404)

    # Work out the cancellation charge based on how far away the event is
    charge = calc_cancellation_charge(bk['event_date'], bk['total_price'])
    cur.execute("UPDATE bookings SET status='cancelled', cancellation_charge=%s WHERE id=%s",
                (charge, bid))

    # Put the tickets back in the pool
    cur.execute("UPDATE events SET tickets_remaining=tickets_remaining+%s WHERE id=%s",
                (bk['quantity'], bk['event_id']))

    # If someone is on the waiting list, notify the first person in line
    cur.execute("""
        SELECT user_id FROM waiting_list
        WHERE event_id=%s AND notified=0 ORDER BY joined_at ASC LIMIT 1
    """, (bk['event_id'],))
    nxt = cur.fetchone()
    if nxt:
        cur.execute("UPDATE waiting_list SET notified=1 WHERE user_id=%s AND event_id=%s",
                    (nxt['user_id'], bk['event_id']))

    db.commit(); cur.close(); db.close()

    if charge > 0:
        flash(f'Booking cancelled. Cancellation charge: £{charge:.2f}', 'warning')
    else:
        flash('Booking cancelled with no charge.', 'success')
    return redirect(url_for('my_bookings'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    # This page handles two different forms - profile update and password change
    # I use a hidden 'action' field to tell them apart rather than having two separate routes
    db = get_db(); cur = db.cursor(dictionary=True)
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            name  = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip().lower()
            if not name or not email:
                flash('Name and email are required.', 'danger')
            else:
                cur.execute("UPDATE users SET full_name=%s, email=%s WHERE id=%s",
                            (name, email, session['user_id']))
                db.commit()
                # Update the session so the navbar shows the new name immediately
                session['user_name'] = name
                flash('Profile updated successfully.', 'success')

        elif action == 'change_password':
            cur_pwd = request.form.get('current_password', '')
            new_pwd = request.form.get('new_password', '')
            conf    = request.form.get('confirm_password', '')
            cur.execute("SELECT password_hash FROM users WHERE id=%s", (session['user_id'],))
            row = cur.fetchone()
            if not check_password_hash(row['password_hash'], cur_pwd):
                flash('Current password is incorrect.', 'danger')
            elif new_pwd != conf:
                flash('New passwords do not match.', 'danger')
            elif len(new_pwd) < 8:
                flash('Password must be at least 8 characters.', 'danger')
            else:
                cur.execute("UPDATE users SET password_hash=%s WHERE id=%s",
                            (generate_password_hash(new_pwd), session['user_id']))
                db.commit()
                flash('Password changed successfully.', 'success')

    cur.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user_data = cur.fetchone()
    cur.close(); db.close()
    return render_template('account.html', user_data=user_data)


# Admin routes
# All admin routes are protected by @admin_required which returns 403
# if the logged-in user doesn't have is_admin=1 in the database

@app.route('/admin')
@admin_required
def admin_dashboard():
    # Gather summary stats for the dashboard cards
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS n FROM events WHERE is_active=1")
    total_events = cur.fetchone()['n']
    cur.execute("SELECT COUNT(*) AS n FROM users WHERE is_admin=0")
    total_users = cur.fetchone()['n']
    cur.execute("SELECT COUNT(*) AS n FROM bookings WHERE status='confirmed'")
    total_bookings = cur.fetchone()['n']
    cur.execute("SELECT COALESCE(SUM(total_price),0) AS r FROM bookings WHERE status='confirmed'")
    revenue = float(cur.fetchone()['r'] or 0)

    # Fetch the 8 most recent bookings for the dashboard table
    cur.execute("""
        SELECT b.reference, b.total_price, b.booking_date, b.status,
               e.name AS event_name, u.full_name AS user_name
        FROM bookings b JOIN events e ON b.event_id=e.id
        JOIN users u ON b.user_id=u.id
        ORDER BY b.booking_date DESC LIMIT 8
    """)
    recent = [floatify(b, 'total_price') for b in cur.fetchall()]
    cur.close(); db.close()
    return render_template('admin/dashboard.html', total_events=total_events,
                           total_users=total_users, total_bookings=total_bookings,
                           revenue=revenue, recent=recent)


@app.route('/admin/events')
@admin_required
def admin_events():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT e.*, v.name AS venue_name, c.name AS category_name
        FROM events e JOIN venues v ON e.venue_id=v.id
        JOIN categories c ON e.category_id=c.id ORDER BY e.date DESC
    """)
    events_list = [floatify(e, 'price') for e in cur.fetchall()]

    # Need venues and categories for the add-event form dropdowns
    cur.execute("SELECT * FROM venues ORDER BY name")
    venues = cur.fetchall()
    cur.execute("SELECT id, name FROM categories ORDER BY name")
    categories = cur.fetchall()
    cur.close(); db.close()
    return render_template('admin/events.html', events=events_list,
                           venues=venues, categories=categories)


@app.route('/admin/events/add', methods=['POST'])
@admin_required
def admin_add_event():
    f = request.form
    db = get_db(); cur = db.cursor()
    tickets = int(f.get('tickets_total', 0))
    # tickets_remaining starts equal to tickets_total for a new event
    cur.execute("""
        INSERT INTO events (name, description, date, time, venue_id, category_id,
        price, tickets_total, tickets_remaining, conditions, last_booking_date,
        is_multiday, days_count)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (f['name'], f.get('description', ''), f['date'], f.get('time'),
          int(f['venue_id']), int(f['category_id']),
          float(f.get('price', 0)), tickets, tickets,
          f.get('conditions', ''), f.get('last_booking_date') or None,
          1 if f.get('is_multiday') else 0, int(f.get('days_count', 1))))
    db.commit(); cur.close(); db.close()
    flash('Event added successfully.', 'success')
    return redirect(url_for('admin_events'))


@app.route('/admin/events/edit/<int:eid>', methods=['POST'])
@admin_required
def admin_edit_event(eid):
    f = request.form
    db = get_db(); cur = db.cursor()
    cur.execute("""
        UPDATE events SET name=%s, description=%s, price=%s,
        tickets_total=%s, conditions=%s, date=%s WHERE id=%s
    """, (f['name'], f.get('description', ''), float(f.get('price', 0)),
          int(f.get('tickets_total', 0)), f.get('conditions', ''), f['date'], eid))
    db.commit(); cur.close(); db.close()
    flash('Event updated.', 'success')
    return redirect(url_for('admin_events'))


@app.route('/admin/events/delete/<int:eid>', methods=['POST'])
@admin_required
def admin_delete_event(eid):
    db = get_db(); cur = db.cursor(dictionary=True)
    # If the event has no bookings, hard delete it; otherwise soft delete to preserve booking history
    cur.execute("SELECT COUNT(*) AS c FROM bookings WHERE event_id=%s", (eid,))
    has_bookings = cur.fetchone()['c'] > 0
    if has_bookings:
        cur.execute("UPDATE events SET is_active=0 WHERE id=%s", (eid,))
    else:
        cur.execute("DELETE FROM waiting_list WHERE event_id=%s", (eid,))
        cur.execute("DELETE FROM events WHERE id=%s", (eid,))
    db.commit(); cur.close(); db.close()
    flash('Event deleted successfully.', 'success')
    return redirect(url_for('admin_events'))


@app.route('/admin/events/reduce-price/<int:eid>', methods=['POST'])
@admin_required
def admin_reduce_price(eid):
    # Reduces the ticket price by 25% - useful when an event isn't selling well
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT price FROM events WHERE id=%s", (eid,))
    event = cur.fetchone()
    new_price = round(float(event['price']) * 0.75, 2)
    cur.execute("UPDATE events SET price=%s WHERE id=%s", (new_price, eid))
    db.commit(); cur.close(); db.close()
    flash(f'Price reduced by 25% to £{new_price:.2f}', 'success')
    return redirect(url_for('admin_events'))


@app.route('/admin/bookings')
@admin_required
def admin_bookings():
    # Shows all bookings across all users - admin only
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT b.*, e.name AS event_name, e.date AS event_date,
               u.full_name AS user_name, u.email AS user_email
        FROM bookings b JOIN events e ON b.event_id=e.id
        JOIN users u ON b.user_id=u.id ORDER BY b.booking_date DESC
    """)
    bookings = [floatify(b, 'total_price', 'cancellation_charge') for b in cur.fetchall()]
    cur.close(); db.close()
    return render_template('admin/bookings.html', bookings=bookings)


@app.route('/admin/bookings/cancel/<int:bid>', methods=['POST'])
@admin_required
def admin_cancel_booking(bid):
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT b.*, e.date AS event_date
        FROM bookings b JOIN events e ON b.event_id=e.id
        WHERE b.id=%s AND b.status='confirmed'
    """, (bid,))
    bk = cur.fetchone()
    if not bk:
        cur.close(); db.close(); abort(404)

    charge = calc_cancellation_charge(bk['event_date'], bk['total_price'])
    cur.execute("UPDATE bookings SET status='cancelled', cancellation_charge=%s WHERE id=%s",
                (charge, bid))
    cur.execute("UPDATE events SET tickets_remaining=tickets_remaining+%s WHERE id=%s",
                (bk['quantity'], bk['event_id']))
    db.commit(); cur.close(); db.close()
    flash(f'Booking {bk["reference"]} cancelled.', 'success')
    return redirect(url_for('admin_bookings'))


@app.route('/admin/users')
@admin_required
def admin_users():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = cur.fetchall()
    cur.close(); db.close()
    return render_template('admin/users.html', users=users)


@app.route('/admin/users/reset/<int:uid>', methods=['POST'])
@admin_required
def admin_reset_password(uid):
    new_pwd = request.form.get('new_password', '')
    if len(new_pwd) < 8:
        flash('Password must be at least 8 characters.', 'danger')
        return redirect(url_for('admin_users'))
    db = get_db(); cur = db.cursor()
    cur.execute("UPDATE users SET password_hash=%s WHERE id=%s",
                (generate_password_hash(new_pwd), uid))
    db.commit(); cur.close(); db.close()
    flash('Password reset successfully.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/edit/<int:uid>', methods=['POST'])
@admin_required
def admin_edit_user(uid):
    first_name = request.form.get('first_name', '').strip()
    last_name  = request.form.get('last_name', '').strip()
    email      = request.form.get('email', '').strip()
    new_pwd    = request.form.get('new_password', '').strip()
    is_student = 1 if request.form.get('is_student') else 0
    full_name  = (first_name + ' ' + last_name).strip()
    if not full_name or not email:
        flash('Name and email are required.', 'danger')
        return redirect(url_for('admin_users'))
    db = get_db(); cur = db.cursor()
    # Only update the password if the admin actually typed a new one - otherwise leave it alone
    if new_pwd:
        if len(new_pwd) < 8:
            flash('New password must be at least 8 characters.', 'danger')
            cur.close(); db.close()
            return redirect(url_for('admin_users'))
        cur.execute("UPDATE users SET full_name=%s, email=%s, is_student=%s, password_hash=%s WHERE id=%s",
                    (full_name, email, is_student, generate_password_hash(new_pwd), uid))
    else:
        cur.execute("UPDATE users SET full_name=%s, email=%s, is_student=%s WHERE id=%s",
                    (full_name, email, is_student, uid))
    db.commit(); cur.close(); db.close()
    flash('User updated successfully.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/delete/<int:uid>', methods=['POST'])
@admin_required
def admin_delete_user(uid):
    if uid == session.get('user_id'):
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin_users'))
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT is_admin FROM users WHERE id=%s", (uid,))
    u = cur.fetchone()
    if not u:
        flash('User not found.', 'danger')
        cur.close(); db.close()
        return redirect(url_for('admin_users'))
    if u['is_admin']:
        flash('Cannot delete an admin account.', 'danger')
        cur.close(); db.close()
        return redirect(url_for('admin_users'))
    cur.execute("DELETE FROM waiting_list WHERE user_id=%s", (uid,))
    cur.execute("DELETE FROM bookings WHERE user_id=%s", (uid,))
    cur.execute("DELETE FROM users WHERE id=%s", (uid,))
    db.commit(); cur.close(); db.close()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin_users'))



@app.route('/admin/venues')
@admin_required
def admin_venues():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM venues ORDER BY name")
    venues = cur.fetchall()
    cur.close(); db.close()
    return render_template('admin/venues.html', venues=venues)


@app.route('/admin/venues/add', methods=['POST'])
@admin_required
def admin_add_venue():
    name        = request.form.get('name', '').strip()
    address     = request.form.get('address', '').strip()
    capacity    = request.form.get('capacity', '').strip()
    suitable_for = request.form.get('suitable_for', '').strip()
    if not name or not capacity:
        flash('Venue name and capacity are required.', 'danger')
        return redirect(url_for('admin_venues'))
    db = get_db(); cur = db.cursor()
    cur.execute("INSERT INTO venues (name, address, capacity, suitable_for) VALUES (%s,%s,%s,%s)",
                (name, address, int(capacity), suitable_for))
    db.commit(); cur.close(); db.close()
    flash(f'Venue "{name}" added successfully.', 'success')
    return redirect(url_for('admin_venues'))


@app.route('/admin/venues/edit/<int:vid>', methods=['POST'])
@admin_required
def admin_edit_venue(vid):
    name         = request.form.get('name', '').strip()
    address      = request.form.get('address', '').strip()
    capacity     = request.form.get('capacity', '').strip()
    suitable_for = request.form.get('suitable_for', '').strip()
    if not name or not capacity:
        flash('Venue name and capacity are required.', 'danger')
        return redirect(url_for('admin_venues'))
    db = get_db(); cur = db.cursor()
    cur.execute("UPDATE venues SET name=%s, address=%s, capacity=%s, suitable_for=%s WHERE id=%s",
                (name, address, int(capacity), suitable_for, vid))
    db.commit(); cur.close(); db.close()
    flash('Venue updated successfully.', 'success')
    return redirect(url_for('admin_venues'))


@app.route('/admin/venues/delete/<int:vid>', methods=['POST'])
@admin_required
def admin_delete_venue(vid):
    db = get_db(); cur = db.cursor()
    # Don't allow deleting a venue that still has events - it would break those event pages
    cur.execute("SELECT COUNT(*) AS c FROM events WHERE venue_id=%s", (vid,))
    if cur.fetchone()[0] > 0:
        flash('Cannot delete venue — it has events assigned to it.', 'danger')
        cur.close(); db.close()
        return redirect(url_for('admin_venues'))
    cur.execute("DELETE FROM venues WHERE id=%s", (vid,))
    db.commit(); cur.close(); db.close()
    flash('Venue deleted successfully.', 'success')
    return redirect(url_for('admin_venues'))


@app.route('/admin/reports')
@admin_required
def admin_reports():
    db = get_db(); cur = db.cursor(dictionary=True)

    # Revenue by event
    cur.execute("""
        SELECT e.name, c.name AS category_name, COUNT(b.id) AS bookings,
               COALESCE(SUM(b.total_price), 0) AS revenue
        FROM events e
        JOIN categories c ON e.category_id=c.id
        LEFT JOIN bookings b ON e.id=b.event_id AND b.status='confirmed'
        GROUP BY e.id, e.name, c.name ORDER BY revenue DESC
    """)
    revenue_report = [floatify(r, 'revenue') for r in cur.fetchall()]

    # Upcoming events occupancy
    cur.execute("""
        SELECT e.name, e.date, e.price, e.tickets_total, e.tickets_remaining,
               v.name AS venue_name,
               ROUND((e.tickets_total - e.tickets_remaining) * 100.0 / e.tickets_total, 0) AS pct_booked
        FROM events e JOIN venues v ON e.venue_id=v.id
        WHERE e.date >= CURDATE() AND e.is_active=1 ORDER BY e.date ASC
    """)
    upcoming = [floatify(e, 'price') for e in cur.fetchall()]

    # Waiting list
    cur.execute("""
        SELECT wl.joined_at, wl.notified, u.full_name, u.email, e.name AS event_name
        FROM waiting_list wl JOIN users u ON wl.user_id=u.id
        JOIN events e ON wl.event_id=e.id ORDER BY wl.joined_at ASC
    """)
    waitlist = cur.fetchall()

    # Monthly bookings count (last 6 months)
    cur.execute("""
        SELECT DATE_FORMAT(booking_date,'%b %Y') AS month,
               COUNT(*) AS total
        FROM bookings WHERE status='confirmed'
        GROUP BY YEAR(booking_date), MONTH(booking_date), DATE_FORMAT(booking_date,'%b %Y')
        ORDER BY YEAR(booking_date), MONTH(booking_date)
        LIMIT 6
    """)
    monthly = cur.fetchall()

    # Bookings by category
    cur.execute("""
        SELECT c.name AS category, COUNT(b.id) AS total
        FROM bookings b JOIN events e ON b.event_id=e.id
        JOIN categories c ON e.category_id=c.id
        WHERE b.status='confirmed'
        GROUP BY c.id, c.name ORDER BY total DESC
    """)
    by_category = cur.fetchall()

    # Top 5 spending users
    cur.execute("""
        SELECT u.full_name, COALESCE(SUM(b.total_price),0) AS spent
        FROM users u JOIN bookings b ON u.id=b.user_id
        WHERE b.status='confirmed'
        GROUP BY u.id, u.full_name ORDER BY spent DESC LIMIT 5
    """)
    top_users = [floatify(r, 'spent') for r in cur.fetchall()]

    # Bookings by venue
    cur.execute("""
        SELECT v.name AS venue, COUNT(b.id) AS total
        FROM bookings b JOIN events e ON b.event_id=e.id
        JOIN venues v ON e.venue_id=v.id
        WHERE b.status='confirmed'
        GROUP BY v.id, v.name ORDER BY total DESC
    """)
    by_venue = cur.fetchall()

    cur.close(); db.close()
    return render_template('admin/reports.html',
                           revenue_report=revenue_report,
                           upcoming=upcoming,
                           waitlist=waitlist,
                           monthly=monthly,
                           by_category=by_category,
                           top_users=top_users,
                           by_venue=by_venue)


# Error handlers - show friendly pages instead of the default Flask error screens

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    # This gets triggered when a non-admin tries to access an admin route
    return render_template('403.html'), 403


if __name__ == '__main__':
    app.run(debug=True)


