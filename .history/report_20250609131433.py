import sqlite3
from datetime import datetime
import pandas as pd
from database import connect_to_database

def generate_report(start_date, end_date, user_type="all", output_file="report.csv"):
    """
    Generate a report of tickets within a specified timeline, filterable by user type.
    Outputs to a CSV file for easy printing or sharing.
    
    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format
        user_type (str): 'admin', 'technician', 'staff', or 'all'
        output_file (str): Name of the output CSV file
    """
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        
        # Base query for tickets
        query = """
            SELECT t.ticket_id, t.title, t.description, t.status, t.created_date, 
                   t.resolved_date, u1.username AS created_by, u2.username AS assigned_to
            FROM tickets t
            LEFT JOIN users u1 ON t.created_by = u1.user_id
            LEFT JOIN users u2 ON t.assigned_to = u2.user_id
            WHERE t.created_date BETWEEN ? AND ?
        """
        params = [start_date, end_date]
        
        # Filter by user type if not 'all'
        if user_type != "all":
            query += " AND u1.role = ?"
            params.append(user_type)
        
        # Execute query
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Get column names from cursor
        columns = [desc[0] for desc in cursor.description]
        
        # Convert to DataFrame for easy manipulation and export
        df = pd.DataFrame(rows, columns=columns)
        
        # Add a timestamp to the report
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df['report_generated'] = report_time
        
        # Sort by created_date for better readability
        df = df.sort_values(by='created_date')
        
        # Export to CSV
        df.to_csv(output_file, index=False)
        print(f"Report generated successfully and saved to {output_file}")
        
        # Return DataFrame for potential in-app display
        return df
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"Error generating report: {e}")
        return None
    finally:
        if conn:
            conn.close()

# Example usage in admin_dashboard.py
def admin_generate_report():
    start_date = input("Enter start date (YYYY-MM-DD): ")
    end_date = input("Enter end date (YYYY-MM-DD): ")
    user_type = input("Enter user type (admin, technician, staff, or all): ").lower()
    output_file = input("Enter output file name (e.g., report.csv): ")
    
    report_df = generate_report(start_date, end_date, user_type, output_file)
    if report_df is not None:
        print("\nReport Preview:")
        print(report_df.head())  # Show first few rows for preview

# Add to admin_dashboard.py
if __name__ == "__main__":
    # Assuming admin is logged in, add this to your admin menu
    print("1. Add User")
    print("2. View Users")
    print("3. Delete User")
    print("4. View Tickets")
    print("5. Generate Report")
    choice = input("Select an option: ")
    if choice == "5":
        admin_generate_report()

# Note: Ensure your database.py has a 'connect_to_database' function that returns a connection
# and your 'tickets' table has columns: ticket_id, title, description, status, created_date, 
# resolved_date, created_by, assigned_to
# Also, ensure 'users' table has columns: user_id, username, role