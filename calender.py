from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime, timedelta
import calendar
import json
import os
import sys

# Print current working directory for debugging
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Check if templates directory exists
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

print(f"Templates directory: {templates_dir}")
print(f"Templates directory exists: {os.path.exists(templates_dir)}")
print(f"Static directory: {static_dir}")
print(f"Static directory exists: {os.path.exists(static_dir)}")

# Create directories if they don't exist
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)
    print(f"Created templates directory: {templates_dir}")

if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    print(f"Created static directory: {static_dir}")

# File to store events
EVENTS_FILE = 'events.json'

def load_events():
    """Load events from JSON file"""
    if os.path.exists(EVENTS_FILE):
        try:
            with open(EVENTS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_events(events):
    """Save events to JSON file"""
    with open(EVENTS_FILE, 'w') as f:
        json.dump(events, f, indent=2)

@app.route('/')
def index():
    """Main calendar view"""
    try:
        # Get current date or date from query params
        year = request.args.get('year', default=datetime.now().year, type=int)
        month = request.args.get('month', default=datetime.now().month, type=int)
        
        # Handle month navigation
        if month > 12:
            month = 1
            year += 1
        elif month < 1:
            month = 12
            year -= 1
        
        # Get calendar data
        cal = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]
        
        # Load events
        events = load_events()
        
        # Previous and next month
        prev_month = month - 1
        prev_year = year
        if prev_month < 1:
            prev_month = 12
            prev_year -= 1
        
        next_month = month + 1
        next_year = year
        if next_month > 12:
            next_month = 1
            next_year += 1
        
        # Check if template exists
        template_path = os.path.join(templates_dir, 'calendar.html')
        if not os.path.exists(template_path):
            return f"""
            <h1>Template Not Found</h1>
            <p>The calendar.html template was not found at: {template_path}</p>
            <p>Please make sure the file exists in the templates directory.</p>
            <p>Current working directory: {os.getcwd()}</p>
            """
        
        return render_template('calendar.html',
                             calendar=cal,
                             year=year,
                             month=month,
                             month_name=month_name,
                             events=events,
                             prev_month=prev_month,
                             prev_year=prev_year,
                             next_month=next_month,
                             next_year=next_year,
                             today=datetime.now().day,
                             current_month=datetime.now().month,
                             current_year=datetime.now().year)
    except Exception as e:
        return f"""
        <h1>Error</h1>
        <p>An error occurred: {str(e)}</p>
        <p>Current working directory: {os.getcwd()}</p>
        <p>Templates directory: {templates_dir}</p>
        <p>Template exists: {os.path.exists(os.path.join(templates_dir, 'calendar.html'))}</p>
        """

@app.route('/add_event', methods=['POST'])
def add_event():
    """Add a new event"""
    date = request.form.get('date')
    title = request.form.get('title')
    time = request.form.get('time', '')
    description = request.form.get('description', '')
    
    if date and title:
        events = load_events()
        
        if date not in events:
            events[date] = []
        
        events[date].append({
            'title': title,
            'time': time,
            'description': description,
            'id': datetime.now().timestamp()
        })
        
        save_events(events)
    
    # Redirect back to the calendar
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    return redirect(url_for('index', year=date_obj.year, month=date_obj.month))

@app.route('/delete_event/<date>/<float:event_id>')
def delete_event(date, event_id):
    """Delete an event"""
    events = load_events()
    
    if date in events:
        events[date] = [e for e in events[date] if e['id'] != event_id]
        if not events[date]:
            del events[date]
        save_events(events)
    
    # Redirect back to the calendar
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    return redirect(url_for('index', year=date_obj.year, month=date_obj.month))

@app.route('/get_events/<date>')
def get_events(date):
    """Get events for a specific date"""
    events = load_events()
    return jsonify(events.get(date, []))

@app.route('/test')
def test():
    """Test route to check if Flask is working"""
    return f"""
    <h1>Flask is working!</h1>
    <p>Current working directory: {os.getcwd()}</p>
    <p>Templates directory: {templates_dir}</p>
    <p>Templates directory exists: {os.path.exists(templates_dir)}</p>
    <p>Calendar.html exists: {os.path.exists(os.path.join(templates_dir, 'calendar.html'))}</p>
    <p>Static directory: {static_dir}</p>
    <p>Static directory exists: {os.path.exists(static_dir)}</p>
    <br>
    <a href="/">Go to Calendar</a>
    """

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Starting Flask Calendar App...")
    print(f"Working directory: {os.getcwd()}")
    print(f"Templates directory: {templates_dir}")
    print(f"Static directory: {static_dir}")
    print("="*50 + "\n")
    print("Visit http://localhost:5000/test to check setup")
    print("Visit http://localhost:5000 for the calendar")
    print("\n" + "="*50 + "\n")
    
    app.run(debug=True, port=5000)