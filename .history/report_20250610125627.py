import mysql.connector
from datetime import datetime
import sys
from fpdf import FPDF
from flask import Flask, session, redirect, url_for, request, render_template_string
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'Levi27'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Connection failed: {err}")
        return None

# Check user login and admin privileges
@app.before_request
def check_auth():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login'))

# PDF Report Generator Class
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Help Desk Report - LEVI27', 0, 1, 'C')
        date_range = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        if 'start_date' in request.args and 'end_date' in request.args:
            date_range += f" ({request.args.get('start_date')} to {request.args.get('end_date')})"
        elif 'start_date' in request.args:
            date_range += f" (From {request.args.get('start_date')})"
        elif 'end_date' in request.args:
            date_range += f" (Up to {request.args.get('end_date')})"
        self.set_font('Arial', '', 10)
        self.cell(0, 10, date_range, 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# Route for report generation
@app.route('/admin_reports', methods=['GET'])
def admin_reports():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # Basic date validation
    date_filter_clause = ""
    query_params = []
    
    if start_date and end_date:
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
            date_filter_clause = " AND created_at BETWEEN %s AND %s"
            query_params = [f"{start_date} 00:00:00", f"{end_date} 23:59:59"]
        except ValueError:
            start_date = end_date = ''
    elif start_date:
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            date_filter_clause = " AND created_at >= %s"
            query_params = [f"{start_date} 00:00:00"]
        except ValueError:
            start_date = ''
    elif end_date:
        try:
            datetime.strptime(end_date, '%Y-%m-%d')
            date_filter_clause = " AND created_at <= %s"
            query_params = [f"{end_date} 23:59:59"]
        except ValueError:
            end_date = ''
    
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    
    cursor = conn.cursor(dictionary=True)
    
    # 1. Overall Summary Statistics
    total_tickets = 0
    total_resolved = 0
    total_users = 0
    ticket_status_distribution = {}
    
    # Total Tickets
    sql_tickets = f"SELECT COUNT(*) AS total_tickets FROM tickets WHERE 1=1{date_filter_clause}"
    cursor.execute(sql_tickets, query_params)
    total_tickets = cursor.fetchone()['total_tickets'] or 0
    
    # Total Resolved Tickets
    sql_resolved = f"SELECT COUNT(*) AS total_resolved FROM tickets WHERE LOWER(status) = 'resolved'{date_filter_clause}"
    cursor.execute(sql_resolved, query_params)
    total_resolved = cursor.fetchone()['total_resolved'] or 0
    
    # Total Users (assuming a users table)
    cursor.execute("SELECT COUNT(*) AS total_users FROM users WHERE user_type = 'customer'")
    total_users = cursor.fetchone()['total_users'] or 0
    
    # 2. Ticket Status Distribution
    sql_status = f"SELECT LOWER(status) AS status_lower, COUNT(*) AS count FROM tickets WHERE 1=1{date_filter_clause} GROUP BY LOWER(status)"
    cursor.execute(sql_status, query_params)
    for row in cursor.fetchall():
        ticket_status_distribution[row['status_lower']] = row['count']
    
    conn.close()
    
    # HTML Template
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Reports | LEVI27 Admin</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #4361ee;
                --primary-dark: #3a56d4;
                --secondary: #f8f9fa;
                --text: #2b2d42;
                --light-text: #8d99ae;
                --border: #e9ecef;
                --error: #ef233c;
                --success: #06d6a0;
                --warning: #ffd166;
                --info: #17a2b8;
                --blue-secondary: #eaf1fb;
                --blue-text: #2c3e50;
            }
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background-color: var(--secondary);
                color: var(--text);
                line-height: 1.6;
                margin: 0;
                padding: 0;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 0 2rem;
            }
            .admin-header {
                background: var(--primary);
                color: white;
                padding: 1rem 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                margin-bottom: 2rem;
            }
            .logo {
                font-size: 1.8rem;
                font-weight: 700;
                letter-spacing: 1px;
                background: white;
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .admin-nav a {
                color: white;
                text-decoration: none;
                font-weight: 500;
                transition: opacity 0.3s;
                margin-left: 1.5rem;
            }
            .admin-nav a:hover {
                opacity: 0.8;
            }
            .admin-nav a.active {
                font-weight: 700;
                position: relative;
            }
            .admin-nav a.active::after {
                content: '';
                position: absolute;
                left: 0;
                right: 0;
                bottom: -5px;
                height: 3px;
                background-color: white;
                border-radius: 2px;
            }
            .page-title {
                font-size: 1.8rem;
                color: var(--primary);
                margin-bottom: 1.5rem;
                border-bottom: 2px solid var(--primary);
                padding-bottom: 0.5rem;
            }
            .report-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }
            .report-card {
                background-color: white;
                padding: 1.5rem;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                border: 1px solid var(--border);
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }
            .report-card-title {
                font-size: 1.1rem;
                color: var(--light-text);
                margin-bottom: 0.5rem;
                font-weight: 500;
            }
            .report-card-value {
                font-size: 2rem;
                font-weight: 700;
                color: var(--text);
                margin-bottom: 0.5rem;
            }
            .report-card-description {
                font-size: 0.9rem;
                color: var(--light-text);
            }
            .section-title {
                font-size: 1.5rem;
                margin-bottom: 1rem;
                color: var(--primary);
                border-bottom: 2px solid var(--primary);
                padding-bottom: 0.5rem;
            }
            .data-table {
                width: 100%;
                border-collapse: collapse;
                background-color: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 5px 15px rgba(0,0,0,0.05);
                margin-bottom: 2rem;
            }
            .data-table th,
            .data-table td {
                padding: 1rem;
                text-align: left;
                border-bottom: 1px solid var(--border);
            }
            .data-table th {
                background-color: var(--blue-secondary);
                color: var(--blue-text);
                font-weight: 600;
            }
            .data-table tr:last-child td {
                border-bottom: none;
            }
            .data-table tr:hover {
                background-color: rgba(67, 97, 238, 0.05);
            }
            .status-badge {
                display: inline-block;
                padding: 0.4rem 0.8rem;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 500;
            }
            .status-open { background-color: #fff3cd; color: #856404; }
            .status-in_progress { background-color: #cce5ff; color: #004085; }
            .status-resolved { background-color: #d4edda; color: #155724; }
            .status-closed { background-color: #e2e3e5; color: #495057; }
            .report-filters {
                background-color: white;
                padding: 1.5rem;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                border: 1px solid var(--border);
                margin-bottom: 2rem;
                display: flex;
                flex-wrap: wrap;
                gap: 1rem;
                align-items: flex-end;
            }
            .report-filters label {
                font-size: 0.9rem;
                color: var(--light-text);
                margin-bottom: 0.3rem;
                display: block;
                font-weight: 500;
            }
            .report-filters input[type="date"] {
                padding: 0.75rem;
                border: 1px solid var(--border);
                border-radius: 4px;
                font-size: 1rem;
                flex-grow: 1;
                min-width: 150px;
            }
            .report-filters button {
                background-color: var(--primary);
                color: white;
                padding: 0.8rem 1.5rem;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 1rem;
                font-weight: 500;
                transition: background-color 0.3s ease;
            }
            .report-filters button:hover {
                background-color: var(--primary-dark);
            }
            @media (max-width: 768px) {
                .admin-nav {
                    flex-direction: column;
                    gap: 1rem;
                }
                .report-grid {
                    grid-template-columns: 1fr;
                }
                .data-table {
                    display: block;
                    overflow-x: auto;
                    white-space: nowrap;
                }
                .report-filters {
                    flex-direction: column;
                    align-items: stretch;
                }
            }
        </style>
    </head>
    <body>
        <header class="admin-header">
            <div class="logo">LEVI27 Admin</div>
            <nav class="admin-nav">
                <a href="/admin_dashboard"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
                <a href="/products"><i class="fas fa-boxes"></i> Products</a>
                <a href="/admin_orders"><i class="fas fa-shopping-cart"></i> Orders</a>
                <a href="/user_management"><i class="fas fa-users"></i> Users</a>
                <a href="/admin_reports" class="active"><i class="fas fa-chart-bar"></i> Reports</a>
                <a href="/store"><i class="fas fa-store"></i> View Store</a>
                <a href="/logout"><i class="fas fa-sign-out-alt"></i> Logout</a>
            </nav>
        </header>
        <div class="container">
            <h1 class="page-title">Admin Reports</h1>
            <section class="report-filter-section">
                <h2 class="section-title">Generate Reports by Date</h2>
                <form action="/admin_reports" method="GET" class="report-filters">
                    <div>
                        <label for="start_date">Start Date:</label>
                        <input type="date" id="start_date" name="start_date" value="{{ start_date }}">
                    </div>
                    <div>
                        <label for="end_date">End Date:</label>
                        <input type="date" id="end_date" name="end_date" value="{{ end_date }}">
                    </div>
                    <button type="submit"><i class="fas fa-filter"></i> Apply Filter</button>
                    <button type="button" onclick="window.location.href='/admin_reports'" style="background-color: var(--info);"><i class="fas fa-times"></i> Clear Filter</button>
                    <button type="button" onclick="downloadReport()" style="background-color: var(--success);"><i class="fas fa-download"></i> Download Report</button>
                </form>
            </section>
            <section class="report-section">
                <h2 class="section-title">Overall Summary
                    {% if start_date and end_date %}
                        ({{ start_date }} to {{ end_date }})
                    {% elif start_date %}
                        (From {{ start_date }})
                    {% elif end_date %}
                        (Up to {{ end_date }})
                    {% endif %}
                </h2>
                <div class="report-grid">
                    <div class="report-card">
                        <span class="report-card-title">Total Tickets</span>
                        <span class="report-card-value">{{ "{:,}".format(total_tickets) }}</span>
                        <span class="report-card-description">All tickets submitted.</span>
                    </div>
                    <div class="report-card">
                        <span class="report-card-title">Total Resolved</span>
                        <span class="report-card-value">{{ "{:,}".format(total_resolved) }}</span>
                        <span class="report-card-description">Tickets marked as resolved.</span>
                    </div>
                    <div class="report-card">
                        <span class="report-card-title">Total Users</span>
                        <span class="report-card-value">{{ "{:,}".format(total_users) }}</span>
                        <span class="report-card-description">Registered customer accounts.</span>
                    </div>
                </div>
            </section>
            <section class="report-section">
                <h2 class="section-title">Ticket Status Distribution
                    {% if start_date and end_date %}
                        ({{ start_date }} to {{ end_date }})
                    {% elif start_date %}
                        (From {{ start_date }})
                    {% elif end_date %}
                        (Up to {{ end_date }})
                    {% endif %}
                </h2>
                {% if ticket_status_distribution %}
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Status</th>
                                <th>Number of Tickets</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for status in ['open', 'in_progress', 'resolved', 'closed'] %}
                                {% set count = ticket_status_distribution.get(status, 0) %}
                                <tr>
                                    <td>
                                        <span class="status-badge status-{{ status|replace('_', '-') }}">
                                            {{ status|replace('_', ' ')|title }}
                                        </span>
                                    </td>
                                    <td>{{ "{:,}".format(count) }}</td>
                                </tr>
                            {% endfor %}
                            {% for status, count in ticket_status_distribution.items() if status not in ['open', 'in_progress', 'resolved', 'closed'] %}
                                <tr>
                                    <td>
                                        <span class="status-badge status-closed">
                                            {{ status|title }}
                                        </span>
                                    </td>
                                    <td>{{ "{:,}".format(count) }}</td>
                                </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                {% else %}
                    <div class="no-tickets">
                        <p>No ticket status data available yet for the selected date range.</p>
                    </div>
                {% endif %}
            </section>
        </div>
        <script>
            function downloadReport() {
                const startDate = document.getElementById('start_date').value;
                const endDate = document.getElementById('end_date').value;
                let downloadUrl = '/generate_report_pdf?';
                if (startDate) {
                    downloadUrl += 'start_date=' + startDate + '&';
                }
                if (endDate) {
                    downloadUrl += 'end_date=' + endDate;
                }
                if (downloadUrl.endsWith('&')) {
                    downloadUrl = downloadUrl.slice(0, -1);
                }
                if (downloadUrl === '/generate_report_pdf?') {
                    downloadUrl = '/generate_report_pdf';
                }
                window.location.href = downloadUrl;
            }
        </script>
    </body>
    </html>
    '''
    
    return render_template_string(html, start_date=start_date, end_date=end_date, 
                                 total_tickets=total_tickets, total_resolved=total_resolved, 
                                 total_users=total_users, ticket_status_distribution=ticket_status_distribution)

# Route for PDF download
@app.route('/generate_report_pdf', methods=['GET'])
def generate_report_pdf():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    date_filter_clause = ""
    query_params = []
    
    if start_date and end_date:
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
            date_filter_clause = " AND created_at BETWEEN %s AND %s"
            query_params = [f"{start_date} 00:00:00", f"{end_date} 23:59:59"]
        except ValueError:
            start_date = end_date = ''
    elif start_date:
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            date_filter_clause = " AND created_at >= %s"
            query_params = [f"{start_date} 00:00:00"]
        except ValueError:
            start_date = ''
    elif end_date:
        try:
            datetime.strptime(end_date, '%Y-%m-%d')
            date_filter_clause = " AND created_at <= %s"
            query_params = [f"{end_date} 23:59:59"]
        except ValueError:
            end_date = ''
    
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    
    cursor = conn.cursor(dictionary=True)
    
    # Fetch data
    sql_tickets = f"SELECT COUNT(*) AS total_tickets FROM tickets WHERE 1=1{date_filter_clause}"
    cursor.execute(sql_tickets, query_params)
    total_tickets = cursor.fetchone()['total_tickets'] or 0
    
    sql_resolved = f"SELECT COUNT(*) AS total_resolved FROM tickets WHERE LOWER(status) = 'resolved'{date_filter_clause}"
    cursor.execute(sql_resolved, query_params)
    total_resolved = cursor.fetchone()['total_resolved'] or 0
    
    cursor.execute("SELECT COUNT(*) AS total_users FROM users WHERE user_type = 'customer'")
    total_users = cursor.fetchone()['total_users'] or 0
    
    sql_status = f"SELECT LOWER(status) AS status_lower, COUNT(*) AS count FROM tickets WHERE 1=1{date_filter_clause} GROUP BY LOWER(status)"
    cursor.execute(sql_status, query_params)
    ticket_status_distribution = {row['status_lower']: row['count'] for row in cursor.fetchall()}
    
    conn.close()
    
    # Generate PDF
    pdf = PDFReport()
    pdf.add_page()
    
    # Summary Section
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Overall Summary', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f"Total Tickets: {total_tickets:,}", 0, 1)
    pdf.cell(0, 10, f"Total Resolved: {total_resolved:,}", 0, 1)
    pdf.cell(0, 10, f"Total Users: {total_users:,}", 0, 1)
    pdf.ln(10)
    
    # Status Distribution
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Ticket Status Distribution', 0, 1)
    pdf.set_font('Arial', '', 10)
    status_order = ['open', 'in_progress', 'resolved', 'closed']
    for status in status_order:
        count = ticket_status_distribution.get(status, 0)
        pdf.cell(0, 10, f"{status.title().replace('_', ' ')}: {count:,}", 0, 1)
    for status, count in ticket_status_distribution.items():
        if status not in status_order:
            pdf.cell(0, 10, f"{status.title()}: {count:,}", 0, 1)
    
    # Output PDF
    pdf_output = pdf.output(dest='S').encode('latin1')
    response = app.response_class(
        response=pdf_output,
        mimetype='application/pdf',
        headers={'Content-Disposition': 'attachment;filename=help_desk_report.pdf'}
    )
    return response

# Dummy login route (replace with your actual login logic)
@app.route('/login')
def login():
    return "Login Page - Please implement your login logic"

if __name__ == '__main__':
    app.run(debug=True)