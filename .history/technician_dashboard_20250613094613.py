import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime

class TechnicianDashboard:
    def __init__(self, technician_id):
        self.technician_id = technician_id
        self.db_config = {
            'host': '172.16.30.95',
            'user': 'root',
            'password': '',
            'database': 'helpdesk_db'
        }
        self.polling_active = False  # Flag to control polling
        self.available_tree = None  # Treeview for available tickets
        self.my_tickets_tree = None  # Treeview for claimed tickets
        self.resolved_tree = None  # Treeview for resolved/non-resolved tickets
        self.available_ticket_count = 0  # Track available tickets count
        self.my_tickets_count = 0  # Track claimed tickets count
        self.resolved_ticket_count = 0  # Track resolved/non-resolved tickets count
        self.create_dashboard()

    def connect_db(self):
        return mysql.connector.connect(**self.db_config)

    def create_dashboard(self):
        self.dashboard = tk.Tk()
        self.dashboard.title("Technician Dashboard")
        self.dashboard.geometry("1990x1200")
        self.dashboard.configure(bg="#e9edf0")

        sidebar = tk.Frame(self.dashboard, bg="#2c3e50", width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.content_frame = tk.Frame(self.dashboard, bg="#f7f9fa")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Style().configure("TButton", font=("Segoe UI", 11), padding=5)

        tk.Label(sidebar, text="Technician Menu", bg="#2c3e50", fg="white", font=("Segoe UI", 14, "bold")).pack(pady=20)

        ttk.Button(sidebar, text="🧾 Available Tickets", width=20, command=self.view_available_tickets).pack(pady=10)
        ttk.Button(sidebar, text="🛠 My Claimed Tickets", width=20, command=self.view_my_tickets).pack(pady=10)
        ttk.Button(sidebar, text="📂 Resolved / Not Resolved", width=20, command=self.view_resolved_non_resolved_tickets).pack(pady=10)
        ttk.Button(sidebar, text="🚪 Logout", width=20, command=self.dashboard.destroy).pack(pady=20)

        self.show_welcome()
        self.dashboard.mainloop()

    def clear_content(self):
        self.polling_active = False
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_welcome(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Welcome to the Technician Dashboard", font=("Segoe UI", 18, "bold"), bg="#f7f9fa").pack(pady=50)

    def view_available_tickets(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Available Tickets", font=("Segoe UI", 16, "bold"), bg="#f7f9fa").pack(pady=20)

        columns = ("ID", "Title", "Priority", "Created At")
        self.available_tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.available_tree.heading(col, text=col)
            self.available_tree.column(col, width=150, anchor="center")
        self.available_tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        def refresh_available_tickets():
            if not self.polling_active:
                return
            conn = self.connect_db()
            cursor = conn.cursor()

            cursor.execute('''SELECT COUNT(*) FROM tickets 
                              WHERE technician_id = %s AND status NOT IN ('Resolved', 'Not Resolved')''', 
                           (self.technician_id,))
            claimed_count = cursor.fetchone()[0]

            if claimed_count >= 2:
                for item in self.available_tree.get_children():
                    self.available_tree.delete(item)
                tk.Label(self.content_frame, text="You can only claim up to 2 active tickets.", 
                         font=("Segoe UI", 12), bg="#f7f9fa").pack(pady=20)
                self.available_ticket_count = 0
                conn.close()
                if self.polling_active:
                    self.dashboard.after(5000, refresh_available_tickets)
                return

            cursor.execute('''SELECT id, title, description, priority, created_at 
                              FROM tickets 
                              WHERE status = 'Pending' AND technician_id IS NULL''')
            tickets = cursor.fetchall()
            current_count = len(tickets)

            if current_count != self.available_ticket_count:
                for item in self.available_tree.get_children():
                    self.available_tree.delete(item)
                for ticket in tickets:
                    self.available_tree.insert("", tk.END, values=(ticket[0], ticket[1], ticket[3], ticket[4]))
                self.available_ticket_count = current_count

            conn.close()
            if self.polling_active:
                self.dashboard.after(5000, refresh_available_tickets)

        def claim_ticket():
            selected_item = self.available_tree.selection()
            if not selected_item:
                messagebox.showerror("No Selection", "Please select a ticket first.")
                return

            ticket_id = self.available_tree.item(selected_item[0])['values'][0]
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute('SELECT technician_id FROM tickets WHERE id = %s', (ticket_id,))
            assigned = cursor.fetchone()
            if assigned and assigned[0] is not None:
                messagebox.showerror("Already Claimed", "This ticket has already been claimed by another technician.")
                conn.close()
                return

            cursor.execute('''UPDATE tickets 
                              SET status = 'In Progress', technician_id = %s 
                              WHERE id = %s AND technician_id IS NULL''',
                           (self.technician_id, ticket_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Ticket claimed successfully.")
            refresh_available_tickets()

        ttk.Button(self.content_frame, text="✅ Claim Selected Ticket", command=claim_ticket).pack(pady=10)

        self.polling_active = True
        self.available_ticket_count = 0
        refresh_available_tickets()

    def view_my_tickets(self):
        self.clear_content()
        tk.Label(self.content_frame, text="My Claimed Tickets", font=("Segoe UI", 16, "bold"), bg="#f7f9fa").pack(pady=20)

        columns = ("ID", "Title", "Priority", "Status", "Created At", "Description")
        self.my_tickets_tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.my_tickets_tree.heading(col, text=col)
            self.my_tickets_tree.column(col, width=150, anchor="center")
        self.my_tickets_tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        def refresh_my_tickets():
            if not self.polling_active:
                return
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute('''SELECT id, title, priority, status, created_at, description 
                              FROM tickets 
                              WHERE technician_id = %s AND status = 'In Progress' ''', 
                           (self.technician_id,))
            tickets = cursor.fetchall()
            current_count = len(tickets)

            if current_count != self.my_tickets_count:
                for item in self.my_tickets_tree.get_children():
                    self.my_tickets_tree.delete(item)
                for ticket in tickets:
                    self.my_tickets_tree.insert("", tk.END, values=ticket)
                self.my_tickets_count = current_count

            conn.close()
            if self.polling_active:
                self.dashboard.after(5000, refresh_my_tickets)

        def update_ticket_status(resolved=True):
            selected_item = self.my_tickets_tree.selection()
            if not selected_item:
                messagebox.showerror("No Selection", "Please select a ticket first.")
                return

            ticket_id = self.my_tickets_tree.item(selected_item[0])['values'][0]
            notes_label = "Enter your resolution notes:" if resolved else "Reason for not resolving:"
            status_text = "Resolved" if resolved else "Not Resolved"

            notes_popup = tk.Toplevel(self.dashboard)
            notes_popup.title(status_text)
            notes_popup.geometry("500x300")
            tk.Label(notes_popup, text=notes_label).pack(pady=10)
            notes_text = tk.Text(notes_popup, height=6, width=60)
            notes_text.pack(pady=10)

            def save():
                notes = notes_text.get("1.0", tk.END).strip()
                resolved_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                conn = self.connect_db()
                cursor = conn.cursor()
                cursor.execute('''UPDATE tickets 
                                  SET status = %s, resolution_notes = %s, resolved_at = %s 
                                  WHERE id = %s''',
                               (status_text, notes, resolved_at, ticket_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Updated", f"Ticket marked as {status_text}.")
                notes_popup.destroy()
                refresh_my_tickets()

            ttk.Button(notes_popup, text="💾 Save", command=save).pack(pady=10)

        ttk.Button(self.content_frame, text="✔ Mark as Resolved", command=lambda: update_ticket_status(True)).pack(pady=5)
        ttk.Button(self.content_frame, text="✖ Mark as Not Resolved", command=lambda: update_ticket_status(False)).pack(pady=5)

        self.polling_active = True
        self.my_tickets_count = 0
        refresh_my_tickets()

    def view_resolved_non_resolved_tickets(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Resolved / Not Resolved Tickets", font=("Segoe UI", 16, "bold"), bg="#f7f9fa").pack(pady=20)

        columns = ("ID", "Title", "Priority", "Status", "Created At", "Resolved At", "Notes", "Staff", "Description")
        tree_frame = tk.Frame(self.content_frame)
        tree_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        vertical_scrollbar = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        horizontal_scrollbar = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.resolved_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15,
                                          yscrollcommand=vertical_scrollbar.set, xscrollcommand=horizontal_scrollbar.set)
        for col in columns:
            self.resolved_tree.heading(col, text=col)
            self.resolved_tree.column(col, width=130, anchor="center")
        self.resolved_tree.pack(fill=tk.BOTH, expand=True)

        vertical_scrollbar.config(command=self.resolved_tree.yview)
        horizontal_scrollbar.config(command=self.resolved_tree.xview)

        def refresh_resolved_tickets():
            if not self.polling_active:
                return
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute('''SELECT 
                              t.id, t.title, t.priority, t.status, t.created_at, t.resolved_at, 
                              t.resolution_notes, su.username AS staff_name, t.description 
                              FROM tickets t
                              LEFT JOIN users su ON t.staff_id = su.id
                              WHERE t.technician_id = %s AND t.status IN ('Resolved', 'Not Resolved')''', 
                           (self.technician_id,))
            tickets = cursor.fetchall()
            current_count = len(tickets)

            if current_count != self.resolved_ticket_count:
                for item in self.resolved_tree.get_children():
                    self.resolved_tree.delete(item)
                if not tickets:
                    tk.Label(self.content_frame, text="No resolved or non-resolved tickets found.", 
                             font=("Segoe UI", 12), bg="#f7f9fa").pack(pady=20)
                else:
                    for ticket in tickets:
                        self.resolved_tree.insert("", tk.END, values=ticket)
                self.resolved_ticket_count = current_count

            conn.close()
            if self.polling_active:
                self.dashboard.after(5000, refresh_resolved_tickets)

        self.polling_active = True
        self.resolved_ticket_count = 0
        refresh_resolved_tickets()

if __name__ == "__main__":
    TechnicianDashboard(technician_id=1)  # Example technician_id