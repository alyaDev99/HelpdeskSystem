import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import filedialog
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
from fpdf import FPDF
from hashlib import sha256
import os
import platform
import tempfile

class AdminDashboard:
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.db_config = {
            'host': '172.16.30.95',
            'user': 'root',
            'password': '',
            'database': 'helpdesk_db'
        }
        self.create_dashboard()
        self.polling_active = False
        self.ticket_tree = None
        self.last_ticket_count = 0

    def connect_db(self):
        try:
            return mysql.connector.connect(**self.db_config)
        except Error as e:
            messagebox.showerror("Database Error", f"Connection failed: {str(e)}")
            return None

    def create_dashboard(self):
        self.dashboard = tk.Tk()
        self.dashboard.title("Admin Dashboard")
        self.dashboard.geometry("1990x1200")
        self.dashboard.configure(bg="#e9edf0")

        sidebar = tk.Frame(self.dashboard, bg="#2c3e50", width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Style().configure("TButton", font=("Segoe UI", 11), padding=5)

        tk.Label(sidebar, text="Admin Menu", bg="#2c3e50", fg="white",
                 font=("Segoe UI", 14, "bold")).pack(pady=20)
        ttk.Button(sidebar, text="👥 View Users", width=20, command=self.view_users).pack(pady=10)
        ttk.Button(sidebar, text="➕ Add User", width=20, command=self.add_user).pack(pady=10)
        ttk.Button(sidebar, text="🗑 Delete User", width=20, command=self.delete_user).pack(pady=10)
        ttk.Button(sidebar, text="📊 View Tickets", width=20, command=self.view_tickets).pack(pady=10)
        ttk.Button(sidebar, text="📈 Reports", width=20, command=self.view_reports).pack(pady=10)
        ttk.Button(sidebar, text="🚪 Logout", width=20, command=self.dashboard.destroy).pack(pady=20)

        self.content_frame = tk.Frame(self.dashboard, bg="#f7f9fa")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.show_welcome()
        self.dashboard.mainloop()

    def clear_content(self):
        self.polling_active = False
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_welcome(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Welcome to the Admin Dashboard",
                 font=("Segoe UI", 18, "bold"), bg="#f7f9fa").pack(pady=50)

    def view_users(self):
        self.clear_content()
        tk.Label(self.content_frame, text="User List", font=("Segoe UI", 16, "bold"),
                 bg="#f7f9fa").pack(pady=20)

        columns = ("ID", "Username", "Role", "Department")
        tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")
        tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        try:
            conn = self.connect_db()
            if not conn:
                return
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role, department FROM users")
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
        except Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

    def add_user(self):
        self.clear_content()
        frame = tk.Frame(self.content_frame, bg="#f7f9fa")
        frame.pack(pady=20)

        tk.Label(frame, text="Username:", bg="#f7f9fa").pack(pady=5)
        username_entry = tk.Entry(frame, width=40)
        username_entry.pack(pady=5)

        tk.Label(frame, text="Password:", bg="#f7f9fa").pack(pady=5)
        password_entry = tk.Entry(frame, width=40, show="*")
        password_entry.pack(pady=5)

        tk.Label(frame, text="Department:", bg="#f7f9fa").pack(pady=5)
        department_entry = tk.Entry(frame, width=40)
        department_entry.pack(pady=5)

        tk.Label(frame, text="Role:", bg="#f7f9fa").pack(pady=5)
        role_var = tk.StringVar(value="Staff")
        ttk.OptionMenu(frame, role_var, "Staff", "Technician", "Admin").pack(pady=5)

        def submit_user():
            u = username_entry.get().strip()
            p = password_entry.get()
            d = department_entry.get().strip()
            r = role_var.get()
            if not u or not p or not d:
                return messagebox.showerror("Error", "All fields are required.")

            hashed = sha256(p.encode()).hexdigest()
            try:
                conn = self.connect_db()
                if not conn:
                    return
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password, role, department) VALUES (%s,%s,%s,%s)",
                    (u, hashed, r, d)
                )
                conn.commit()
                messagebox.showinfo("Success", f"User '{u}' added.")
                self.view_users()
            except Error as e:
                messagebox.showerror("Database Error", str(e))
            finally:
                conn.close()

        ttk.Button(self.content_frame, text="Add User", command=submit_user).pack(pady=10)

    def delete_user(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Delete User", font=("Segoe UI", 16, "bold"),
                 bg="#f7f9fa").pack(pady=20)

        columns = ("ID", "Username", "Role", "Department")
        tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")
        tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        try:
            conn = self.connect_db()
            if not conn:
                return
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role, department FROM users")
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
        except Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

        def submit_delete():
            try:
                sel = tree.selection()[0]
                user_id = tree.item(sel)["values"][0]
                conn = self.connect_db()
                if not conn:
                    return
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
                conn.commit()
                messagebox.showinfo("Deleted", f"User ID {user_id} removed.")
                self.view_users()
            except IndexError:
                messagebox.showerror("No Selection", "Please select a user first.")
            except Error as e:
                messagebox.showerror("Database Error", str(e))
            finally:
                conn.close()

        ttk.Button(self.content_frame, text="Delete Selected User", command=submit_delete).pack(pady=10)

    def view_tickets(self):
        self.clear_content()
        tk.Label(self.content_frame, text="All Tickets", font=("Segoe UI", 16, "bold"),
                 bg="#f7f9fa").pack(pady=20)

        tree_frame = tk.Frame(self.content_frame)
        tree_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        y_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        columns = ("ID", "Staff", "Department", "Title", "Description", "Priority",
                   "Technician", "Status", "Resolution Notes", "Created At", "Closed At")

        self.ticket_tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                        xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set, height=15)
        x_scroll.config(command=self.ticket_tree.xview)
        y_scroll.config(command=self.ticket_tree.yview)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.ticket_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col in columns:
            width = 250 if col in ("Description", "Resolution Notes") else 120
            self.ticket_tree.heading(col, text=col)
            self.ticket_tree.column(col, width=width, anchor="center")

        def show_details(event):
            selected_item = self.ticket_tree.selection()
            if selected_item:
                values = self.ticket_tree.item(selected_item)["values"]
                detail_window = tk.Toplevel(self.dashboard)
                detail_window.title(f"Ticket Details — ID {values[0]}")
                detail_window.geometry("700x600")
                detail_window.configure(bg="#f7f9fa")

                fields = columns
                for i, value in enumerate(values):
                    label = tk.Label(detail_window, text=f"{fields[i]}:", font=("Helvetica", 10, "bold"),
                                     bg="#f7f9fa")
                    label.pack(anchor="w", padx=10, pady=(8, 2))
                    text = tk.Text(detail_window, wrap=tk.WORD, height=2 if len(str(value)) < 60 else 4)
                    text.insert(tk.END, str(value))
                    text.config(state=tk.DISABLED, bg="#ffffff", relief=tk.FLAT)
                    text.pack(fill=tk.X, padx=10, pady=2)

        self.ticket_tree.bind("<Double-1>", show_details)

        def refresh_tickets():
            if not self.polling_active:
                return
            try:
                conn = self.connect_db()
                if not conn:
                    return
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT
                      t.id,
                      su.username AS staff_name,
                      su.department AS staff_department,
                      t.title,
                      t.description,
                      t.priority,
                      tu.username AS technician_name,
                      t.status,
                      t.resolution_notes,
                      t.created_at,
                      t.resolved_at
                    FROM tickets t
                    LEFT JOIN users su ON t.staff_id = su.id
                    LEFT JOIN users tu ON t.technician_id = tu.id
                    ORDER BY t.id
                ''')
                rows = cursor.fetchall()
                current_ticket_count = len(rows)

                if current_ticket_count != self.last_ticket_count:
                    for item in self.ticket_tree.get_children():
                        self.ticket_tree.delete(item)
                    for row in rows:
                        clean = tuple("" if v is None else v for v in row)
                        self.ticket_tree.insert("", tk.END, values=clean)
                    self.last_ticket_count = current_ticket_count

            except Error as e:
                print(f"Error during ticket refresh: {str(e)}")
            finally:
                conn.close()

            if self.polling_active:
                self.dashboard.after(5000, refresh_tickets)

        self.polling_active = True
        self.last_ticket_count = 0
        refresh_tickets()

    def view_reports(self):
        self.clear_content()
        canvas = tk.Canvas(self.content_frame, bg="#f7f9fa")
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f7f9fa")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        main_container = tk.Frame(scrollable_frame, bg="#f7f9fa")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        filter_frame = tk.Frame(main_container, bg="#f7f9fa")
        filter_frame.pack(fill=tk.X, pady=10)

        tk.Label(filter_frame, text="Date Range:", bg="#f7f9fa").pack(side=tk.LEFT, padx=5)
        date_range_var = tk.StringVar(value="All Time")
        date_ranges = ["All Time", "Today", "Last 7 Days", "Last 30 Days", "Custom"]
        date_range_menu = ttk.Combobox(filter_frame, textvariable=date_range_var, values=date_ranges, 
                                       state="readonly", width=15)
        date_range_menu.pack(side=tk.LEFT, padx=5)

        tk.Label(filter_frame, text="Start Date (YYYY-MM-DD):", bg="#f7f9fa").pack(side=tk.LEFT, padx=5)
        start_date_entry = tk.Entry(filter_frame, width=15)
        start_date_entry.pack(side=tk.LEFT, padx=5)
        start_date_entry.insert(0, "")
        start_date_entry.config(state="disabled")

        tk.Label(filter_frame, text="End Date (YYYY-MM-DD):", bg="#f7f9fa").pack(side=tk.LEFT, padx=5)
        end_date_entry = tk.Entry(filter_frame, width=15)
        end_date_entry.pack(side=tk.LEFT, padx=5)
        end_date_entry.insert(0, "")
        end_date_entry.config(state="disabled")

        button_frame = tk.Frame(main_container, bg="#d3d3d3")
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Style().configure("Big.TButton", font=("Segoe UI", 12), padding=10)
        ttk.Button(button_frame, text="📄 Generate Report", style="Big.TButton", command=lambda: fetch_report()).pack(side=tk.LEFT, padx=20)
        ttk.Button(button_frame, text="❌ Clear Filter", style="Big.TButton", 
                   command=lambda: [date_range_var.set("All Time"), start_date_entry.delete(0, tk.END), 
                                    end_date_entry.delete(0, tk.END), toggle_date_fields(), fetch_report()]).pack(side=tk.LEFT, padx=20)
        ttk.Button(button_frame, text="💾 Save Report", style="Big.TButton", command=lambda: generate_report(save_to_file=True)).pack(side=tk.LEFT, padx=20)
        ttk.Button(button_frame, text="🖨 Print Report", style="Big.TButton", command=lambda: print_report()).pack(side=tk.LEFT, padx=20)

        summary_frame = tk.Frame(main_container, bg="#f7f9fa")
        summary_frame.pack(fill=tk.X, pady=10)

        summary_labels = {
            'total_tickets': tk.Label(summary_frame, text="Total Tickets: 0", font=("Helvetica", 12), bg="#f7f9fa"),
            'total_resolved': tk.Label(summary_frame, text="Total Resolved: 0", font=("Helvetica", 12), bg="#f7f9fa"),
            'total_users': tk.Label(summary_frame, text="Total Staff: 0", font=("Helvetica", 12), bg="#f7f9fa")
        }
        for label in summary_labels.values():
            label.pack(anchor="w", padx=20, pady=5)

        status_frame = tk.Frame(main_container, bg="#f7f9fa")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Label(status_frame, text="Technician Ticket Distribution", font=("Segoe UI", 14, "bold"),
                 bg="#f7f9fa").pack(anchor="w", pady=10)

        tech_columns = ("Technician", "Resolved Tickets")
        tech_tree = ttk.Treeview(status_frame, columns=tech_columns, show="headings", height=5)
        for col in tech_columns:
            tech_tree.heading(col, text=col)
            tech_tree.column(col, width=150, anchor="center")
        tech_tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        tk.Label(status_frame, text="Ticket Status Distribution", font=("Segoe UI", 14, "bold"),
                 bg="#f7f9fa").pack(anchor="w", pady=10)

        status_tree_frame = tk.Frame(status_frame, bg="#f7f9fa")
        status_tree_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        x_scroll = ttk.Scrollbar(status_tree_frame, orient=tk.HORIZONTAL)
        y_scroll = ttk.Scrollbar(status_tree_frame, orient=tk.VERTICAL)
        columns = ("Status", "Number of Tickets")
        tree = ttk.Treeview(status_tree_frame, columns=columns, show="headings", height=5,
                            xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
        x_scroll.config(command=tree.xview)
        y_scroll.config(command=tree.yview)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")

        details_frame = tk.Frame(main_container, bg="#f7f9fa")
        details_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Label(details_frame, text="Detailed Ticket List", font=("Segoe UI", 14, "bold"),
                 bg="#f7f9fa").pack(anchor="w", pady=10)

        tree_frame = tk.Frame(details_frame)
        tree_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        y_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        detail_columns = ("ID", "Description", "Priority", "Title", "Staff", "Status", 
                          "Resolution Notes", "Technician", "Created At", "Closed At")

        detail_tree = ttk.Treeview(tree_frame, columns=detail_columns, show="headings", height=10,
                                   xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
        x_scroll.config(command=detail_tree.xview)
        y_scroll.config(command=detail_tree.yview)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        detail_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col in detail_columns:
            width = 200 if col in ("Description", "Resolution Notes") else 120
            detail_tree.heading(col, text=col)
            detail_tree.column(col, width=width, anchor="center")

        def toggle_date_fields(*args):
            if date_range_var.get() == "Custom":
                start_date_entry.config(state="normal")
                end_date_entry.config(state="normal")
            else:
                start_date_entry.config(state="disabled")
                end_date_entry.config(state="disabled")
                start_date_entry.delete(0, tk.END)
                end_date_entry.delete(0, tk.END)

        date_range_menu.bind("<<ComboboxSelected>>", toggle_date_fields)

        def fetch_report():
            date_range = date_range_var.get()
            start_date = start_date_entry.get().strip()
            end_date = end_date_entry.get().strip()
            date_filter_clause = ""
            query_params = []

            today = datetime.now()
            if date_range == "Today":
                start_date = today.strftime('%Y-%m-%d')
                end_date = start_date
                date_filter_clause = " AND t.created_at BETWEEN %s AND %s"
                query_params = [f"{start_date} 00:00:00", f"{end_date} 23:59:59"]
            elif date_range == "Last 7 Days":
                start_date = (today.date() - timedelta(days=7)).strftime('%Y-%m-%d')
                end_date = today.strftime('%Y-%m-%d')
                date_filter_clause = " AND t.created_at BETWEEN %s AND %s"
                query_params = [f"{start_date} 00:00:00", f"{end_date} 23:59:59"]
            elif date_range == "Last 30 Days":
                start_date = (today.date() - timedelta(days=30)).strftime('%Y-%m-%d')
                end_date = today.strftime('%Y-%m-%d')
                date_filter_clause = " AND t.created_at BETWEEN %s AND %s"
                query_params = [f"{start_date} 00:00:00", f"{end_date} 23:59:59"]
            elif date_range == "Custom":
                if start_date and end_date:
                    date_filter_clause = " AND t.created_at BETWEEN %s AND %s"
                    query_params = [f"{start_date} 00:00:00", f"{end_date} 23:59:59"]
                elif start_date:
                    date_filter_clause = " AND t.created_at >= %s"
                    query_params = [f"{start_date} 00:00:00"]
                elif end_date:
                    date_filter_clause = " AND t.created_at <= %s"
                    query_params = [f"{end_date} 23:59:59"]

            conn = self.connect_db()
            if not conn:
                return None
            cursor = conn.cursor(dictionary=True)

            cursor.execute(f"SELECT COUNT(*) AS total_tickets FROM tickets t WHERE 1=1{date_filter_clause}", query_params)
            total_tickets = cursor.fetchone()['total_tickets'] or 0
            summary_labels['total_tickets'].config(text=f"Total Tickets: {total_tickets:,}")

            cursor.execute(f"SELECT COUNT(*) AS total_resolved FROM tickets t WHERE t.status = 'Resolved'{date_filter_clause}", query_params)
            total_resolved = cursor.fetchone()['total_resolved'] or 0
            summary_labels['total_resolved'].config(text=f"Total Resolved: {total_resolved:,}")

            cursor.execute("SELECT COUNT(*) AS total_users FROM users WHERE role = 'Staff'")
            total_users = cursor.fetchone()['total_users'] or 0
            summary_labels['total_users'].config(text=f"Total Staff: {total_users:,}")

            for item in tree.get_children():
                tree.delete(item)
            sql_status = f"SELECT t.status, COUNT(*) AS count FROM tickets t WHERE 1=1{date_filter_clause} GROUP BY t.status"
            cursor.execute(sql_status, query_params)
            status_order = ['Pending', 'In Progress', 'Resolved', 'Not Resolved']
            ticket_status = {row['status']: row['count'] for row in cursor.fetchall()}

            for status in status_order:
                count = ticket_status.get(status, 0)
                tree.insert("", tk.END, values=(status, f"{count:,}"))
            for status, count in sorted(ticket_status.items()):
                if status not in status_order:
                    tree.insert("", tk.END, values=(status, f"{count:,}"))

            for item in tech_tree.get_children():
                tech_tree.delete(item)
            sql_tech = f"""
                SELECT u.username AS technician_name, COUNT(*) AS count
                FROM tickets t
                LEFT JOIN users u ON t.technician_id = u.id
                WHERE t.status = 'Resolved'{date_filter_clause}
                GROUP BY u.username
                ORDER BY count DESC
            """
            cursor.execute(sql_tech, query_params)
            tech_distribution = cursor.fetchall()
            for row in tech_distribution:
                tech_tree.insert("", tk.END, values=(row['technician_name'] or "Unassigned", f"{row['count']:,}"))

            for item in detail_tree.get_children():
                detail_tree.delete(item)
            sql_details = f"""
                SELECT
                    t.id,
                    t.description,
                    t.priority,
                    t.title,
                    su.username AS staff_name,
                    t.status,
                    t.resolution_notes,
                    tu.username AS technician_name,
                    t.created_at,
                    t.resolved_at
                FROM tickets t
                LEFT JOIN users su ON t.staff_id = su.id
                LEFT JOIN users tu ON t.technician_id = tu.id
                WHERE 1=1{date_filter_clause}
                ORDER BY t.created_at DESC
            """
            cursor.execute(sql_details, query_params)
            tickets = cursor.fetchall()
            for row in tickets:
                clean_row = tuple(
                    "" if v is None else str(v).strip()[:100] if col == "Description" else str(v).strip()[:200] if col == "Resolution Notes" else str(v)
                    for col, v in zip(detail_columns, row.values())
                )
                detail_tree.insert("", tk.END, values=clean_row)

            conn.close()
            return {
                'total_tickets': total_tickets,
                'total_resolved': total_resolved,
                'total_users': total_users,
                'ticket_status': ticket_status,
                'tickets': tickets,
                'tech_distribution': tech_distribution
            }

        class PDFReport(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, 'Help Desk Report', 0, 1, 'C')
                date_range_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                if date_range_var.get() == "Custom":
                    if start_date_entry.get() and end_date_entry.get():
                        date_range_text += f" ({start_date_entry.get()} to {end_date_entry.get()})"
                    elif start_date_entry.get():
                        date_range_text += f" (From {start_date_entry.get()})"
                    elif end_date_entry.get():
                        date_range_text += f" (To {end_date_entry.get()})"
                else:
                    date_range_text += f" ({date_range_var.get()})"
                self.set_font('Arial', '', 10)
                self.cell(0, 10, date_range_text, 0, 1, 'C')
                self.ln(10)

            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

            def add_table(self, headers, rows, col_widths, max_col_widths):
                # Setting up margins and auto page break
                self.set_left_margin(10)
                self.set_right_margin(10)
                self.set_auto_page_break(True, margin=15)
                self.set_font('Arial', 'B', 9)
                self.set_fill_color(200, 200, 200)
                self.set_line_width(0.3)

                # Draw header
                for header, width in zip(headers, col_widths):
                    self.cell(width, 8, header, border=1, align='C', fill=True)
                self.ln()

                # Draw rows
                self.set_font('Arial', '', 8)
                self.set_fill_color(255, 255, 255)
                for row in rows:
                    max_lines = 1
                    # Calculate the number of lines needed for each cell
                    for value, width in zip(row, col_widths):
                        text = str(value)
                        # Estimate lines based on text length and max column width
                        lines = max(1, int(self.get_string_width(text) / (width - 2)) + 1)
                        max_lines = max(max_lines, lines)
                    row_height = max_lines * 5  # 5mm per line

                    # Check for page break
                    if self.get_y() + row_height > self.page_break_trigger:
                        self.add_page()

                    start_y = self.get_y()
                    for value, width in zip(row, col_widths):
                        text = str(value)
                        x = self.get_x()
                        y = self.get_y()
                        # Use multi_cell for text wrapping, respecting max width
                        self.multi_cell(width, 5, text, border=1, align='L', fill=False)
                        self.set_xy(x + width, start_y)
                    self.set_y(start_y + row_height)

        def generate_report(save_to_file=True):
            report_data = fetch_report()
            if not report_data:
                return None
            total_tickets = report_data['total_tickets']
            total_resolved = report_data['total_resolved']
            total_users = report_data['total_users']
            ticket_status = report_data['ticket_status']
            tickets = report_data.get('tickets', [])
            tech_distribution = report_data.get('tech_distribution', [])

            # Calculate maximum text width for each column
            headers = ["ID", "Staff", "Title", "Description", "Priority", "Technician", "Status", 
                       "Resolution Notes", "Created At", "Closed At"]
            base_widths = [10, 20, 20, 35, 15, 20, 15, 35, 15, 20]
            page_width = 190  # Usable page width in mm
            total_base_width = sum(base_widths)
            col_widths = [w * page_width / total_base_width for w in base_widths]

            # Calculate maximum text width for Description and Title
            max_widths = {h: w for h, w in zip(headers, col_widths)}
            for ticket in tickets:
                for header, value in zip(headers, (
                    str(ticket.get('id', '') or ''),
                    str(ticket.get('staff_name', '') or ''),
                    str(ticket.get('title', '') or ''),
                    str(ticket.get('description', '') or '')[:100],
                    str(ticket.get('priority', '') or ''),
                    str(ticket.get('technician_name', '') or ''),
                    str(ticket.get('status', '') or ''),
                    str(ticket.get('resolution_notes', '') or '')[:100],
                    str(ticket.get('created_at', '') or ''),
                    str(ticket.get('resolved_at', '') or '')
                )):
                    pdf = PDFReport()
                    pdf.set_font('Arial', '', 8)
                    text_width = pdf.get_string_width(value)
                    max_widths[header] = max(max_widths[header], text_width + 2)  # Add padding

            # Normalize column widths to fit page width
            total_max_width = sum(max_widths.values())
            if total_max_width > page_width:
                scale_factor = page_width / total_max_width
                col_widths = [max_widths[h] * scale_factor for h in headers]
            else:
                col_widths = [max_widths[h] for h in headers]

            pdf = PDFReport()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Overall Summary', 0, 1)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 10, f"Total Tickets: {total_tickets:,}", 0, 1)
            pdf.cell(0, 10, f"Total Resolved: {total_resolved:,}", 0, 1)
            pdf.cell(0, 10, f"Total Staff: {total_users:,}", 0, 1)
            pdf.ln(10)

            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Ticket Status Distribution', 0, 1)
            pdf.ln(5)
            status_headers = ["Status", "Number of Tickets"]
            status_col_widths = [50, 50]
            total_width = sum(status_col_widths)
            status_col_widths = [w * page_width / total_width for w in status_col_widths]
            status_rows = []
            status_order = ['Pending', 'In Progress', 'Resolved', 'Not Resolved']
            for status in status_order:
                count = ticket_status.get(status, 0)
                status_rows.append((status, f"{count:,}"))
            for status, count in sorted(ticket_status.items()):
                if status not in status_order:
                    status_rows.append((status, f"{count:,}"))
            pdf.add_table(status_headers, status_rows, status_col_widths, status_col_widths)

            pdf.ln(10)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Technician Ticket Distribution', 0, 1)
            pdf.ln(5)
            tech_headers = ["Technician", "Resolved Tickets"]
            tech_col_widths = [50, 50]
            tech_col_widths = [w * page_width / total_width for w in tech_col_widths]
            tech_rows = [
                (str(t.get('technician_name', 'Unassigned')), f"{t.get('count', 0):,}")
                for t in tech_distribution
            ]
            pdf.add_table(tech_headers, tech_rows, tech_col_widths, tech_col_widths)

            pdf.ln(10)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Detailed Ticket List', 0, 1)
            pdf.ln(5)
            rows = [
                (
                    str(t.get('id', '') or ''),
                    str(t.get('staff_name', '') or ''),
                    str(t.get('title', '') or ''),
                    str(t.get('description', '') or '')[:100],
                    str(t.get('priority', '') or ''),
                    str(t.get('technician_name', '') or ''),
                    str(t.get('status', '') or ''),
                    str(t.get('resolution_notes', '') or '')[:100],
                    str(t.get('created_at', '') or ''),
                    str(t.get('resolved_at', '') or '')
                ) for t in tickets
            ]
            pdf.add_table(headers, rows, col_widths, max_widths)

            if save_to_file:
                pdf_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    title="Save Report As"
                )
                if not pdf_path:
                    return None  # User canceled the save dialog
            else:
                temp_dir = tempfile.gettempdir()
                pdf_path = os.path.join(temp_dir, f"helpdesk_report_{os.urandom(8).hex()}.pdf")

            try:
                pdf.output(pdf_path)
                if save_to_file:
                    messagebox.showinfo("Success", f"Report saved as '{pdf_path}'.")
                return pdf_path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save PDF: {str(e)}")
                return None

        def print_report():
            pdf_path = generate_report(save_to_file=False)
            if not pdf_path:
                return
            try:
                if platform.system() == "Windows":
                    os.startfile(pdf_path, "print")
                elif platform.system() == "Darwin":
                    os.system(f"open -a Preview {pdf_path}")
                elif platform.system() == "Linux":
                    os.system(f"xdg-open {pdf_path}")
                messagebox.showinfo("Success", "Print dialog opened for the report.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open print dialog: {str(e)}")
            finally:
                if os.path.exists(pdf_path):
                    try:
                        os.remove(pdf_path)
                    except Exception:
                        pass

        fetch_report()

if __name__ == "__main__":
    AdminDashboard()