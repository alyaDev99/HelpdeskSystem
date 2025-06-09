import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import mysql.connector
from mysql.connector import Error

class StaffDashboard:
    def __init__(self, user_id):
        self.user_id = user_id
        self.create_dashboard()

    def create_dashboard(self):
        self.dashboard = tk.Tk()
        self.dashboard.title("Staff Dashboard")
        self.dashboard.geometry("1990x1200")
        self.dashboard.configure(bg="#e9edf0")

        # Sidebar
        sidebar = tk.Frame(self.dashboard, bg="#2c3e50", width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Style().configure("TButton", font=("Segoe UI", 11), padding=5)

        tk.Label(sidebar, text="Menu", bg="#2c3e50", fg="white", font=("Segoe UI", 14, "bold")).pack(pady=20)
        ttk.Button(sidebar, text="🎫 Create Ticket", width=20, command=self.show_create_ticket).pack(pady=10)
        ttk.Button(sidebar, text="📋 View My Tickets", width=20, command=self.show_view_tickets).pack(pady=10)
        ttk.Button(sidebar, text="🚪 Logout", width=20, command=self.dashboard.destroy).pack(pady=10)

        # Main content area
        self.content_frame = tk.Frame(self.dashboard, bg="#f7f9fa")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.show_welcome()
        self.dashboard.mainloop()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_welcome(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Welcome to Staff Dashboard",
                 font=("Segoe UI", 18, "bold"), bg="#f7f9fa").pack(pady=50)

    def show_create_ticket(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Create a New Ticket", font=("Segoe UI", 16, "bold"), bg="#f7f9fa").pack(pady=20)

        ttk.Label(self.content_frame, text="Ticket Title:").pack(pady=5)
        title_entry = ttk.Entry(self.content_frame, width=50)
        title_entry.pack(pady=5)

        ttk.Label(self.content_frame, text="Description:").pack(pady=5)
        desc_text = tk.Text(self.content_frame, height=8, width=60)
        desc_text.pack(pady=5)

        ttk.Label(self.content_frame, text="Priority:").pack(pady=5)
        priority_var = tk.StringVar(value="Normal")
        priority_menu = ttk.Combobox(self.content_frame, textvariable=priority_var,
                                     values=["Low", "Normal", "High", "Critical"],
                                     state="readonly", width=48)
        priority_menu.pack(pady=5)

        def submit_ticket():
            title = title_entry.get()
            description = desc_text.get("1.0", tk.END).strip()
            priority = priority_var.get()

            if not title or not description:
                messagebox.showerror("Error", "Please fill in both the Title and Description.")
                return

            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            try:
                conn = mysql.connector.connect(
                    host="10.10.3.130",
                    user="root",
                    password="1111",
                    database="helpdesk_db"
                )
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO tickets (title, description, priority, status, staff_id, created_at)
                    VALUES (%s, %s, %s, 'Pending', %s, %s)
                ''', (title, description, priority, self.user_id, created_at))
                conn.commit()
                conn.close()

                messagebox.showinfo("Success", f"Ticket '{title}' created successfully!")
                self.show_view_tickets()
            except Error as e:
                messagebox.showerror("Database Error", str(e))

        ttk.Button(self.content_frame, text="✅ Submit Ticket", command=submit_ticket).pack(pady=20)

    def show_view_tickets(self):
        self.clear_content()
        tk.Label(self.content_frame, text="My Submitted Tickets", font=("Segoe UI", 16, "bold"), bg="#f7f9fa").pack(pady=20)

        tree_frame = tk.Frame(self.content_frame)
        tree_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        y_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)

        columns = ("ID", "Title", "Priority", "Status", "Created At", "Description")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15,
                            xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)

        x_scroll.config(command=tree.xview)
        y_scroll.config(command=tree.yview)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col in columns:
            width = 250 if col == "Description" else 120
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")

        try:
            conn = mysql.connector.connect(
                host="10.10.3.130",
                user="root",
                password="1111",
                database="helpdesk_db"
            )
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, priority, status, created_at, description
                FROM tickets WHERE staff_id = %s
            ''', (self.user_id,))
            tickets = cursor.fetchall()
            conn.close()

            for ticket in tickets:
                clean_ticket = tuple("" if val is None else val for val in ticket)
                tree.insert("", tk.END, values=clean_ticket)

        except Error as e:
            messagebox.showerror("Database Error", str(e))

        def mark_resolved():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("No Selection", "Please select a ticket first.")
                return

            ticket_id = tree.item(selected[0])['values'][0]

            try:
                conn = mysql.connector.connect(
                    host="10.10.",
                    user="root",
                    password="1111",
                    database="helpdesk_db"
                )
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE tickets SET status = 'Resolved' WHERE id = %s
                ''', (ticket_id,))
                conn.commit()
                conn.close()

                messagebox.showinfo("Success", "Ticket marked as Resolved.")
                self.show_view_tickets()
            except Error as e:
                messagebox.showerror("Database Error", str(e))

        ttk.Button(self.content_frame, text="✔ Mark Selected as Resolved", command=mark_resolved).pack(pady=10)

