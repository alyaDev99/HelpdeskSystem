```python
def view_reports(self):
    self.clear_content()
    tk.Label(self.content_frame, text="Ticket Details Report", font=("Segoe UI", 16, "bold"),
             bg="#f7f9fa").pack(pady=20)

    # Main container frame to manage layout
    main_container = tk.Frame(self.content_frame, bg="#f7f9fa")
    main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    # Filter Frame
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

    # Summary Frame
    summary_frame = tk.Frame(main_container, bg="#f7f9fa")
    summary_frame.pack(fill=tk.X, pady=10)

    summary_labels = {
        'total_tickets': tk.Label(summary_frame, text="Total Tickets: 0", font=("Helvetica", 12), bg="#f7f9fa"),
        'total_resolved': tk.Label(summary_frame, text="Total Resolved: 0", font=("Helvetica", 12), bg="#f7f9fa"),
        'total_users': tk.Label(summary_frame, text="Total Staff: 0", font=("Helvetica", 12), bg="#f7f9fa")
    }
    for label in summary_labels.values():
        label.pack(anchor="w", padx=20, pady=5)

    # Status Distribution Frame
    status_frame = tk.Frame(main_container, bg="#f7f9fa")
    status_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    tk.Label(status_frame, text="Ticket Status Distribution", font=("Segoe UI", 14, "bold"),
             bg="#f7f9fa").pack(anchor="w", pady=10)

    columns = ("Status", "Number of Tickets")
    tree = ttk.Treeview(status_frame, columns=columns, show="headings", height=5)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor="center")
    tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    # Detailed Tickets Frame
    details_frame = tk.Frame(main_container, bg="#f7f9fa")
    details_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    tk.Label(details_frame, text="Detailed Ticket List", font=("Segoe UI", 14, "bold"),
             bg="#f7f9fa").pack(anchor="w", pady=10)

    tree_frame = tk.Frame(details_frame)
    tree_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
    y_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
    detail_columns = ("ID", "Staff", "Title", "Description", "Priority", "Technician", "Status", 
                     "Resolution Notes", "Created At", "Closed At")

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

        # Date range logic
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
            try:
                if start_date and end_date:
                    datetime.strptime(start_date, '%Y-%m-%d')
                    datetime.strptime(end_date, '%Y-%m-%d')
                    date_filter_clause = " AND t.created_at BETWEEN %s AND %s"
                    query_params = [f"{start_date} 00:00:00", f"{end_date} 23:59:59"]
                elif start_date:
                    datetime.strptime(start_date, '%Y-%m-%d')
                    date_filter_clause = " AND t.created_at >= %s"
                    query_params = [f"{start_date} 00:00:00"]
                elif end_date:
                    datetime.strptime(end_date, '%Y-%m-%d')
                    date_filter_clause = " AND t.created_at <= %s"
                    query_params = [f"{end_date} 23:59:59"]
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
                return None

        conn = self.connect_db()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)

        # Total Tickets
        cursor.execute(f"SELECT COUNT(*) AS total_tickets FROM tickets t WHERE 1=1{date_filter_clause}", query_params)
        total_tickets = cursor.fetchone()['total_tickets'] or 0
        summary_labels['total_tickets'].config(text=f"Total Tickets: {total_tickets:,}")

        # Total Resolved
        cursor.execute(f"SELECT COUNT(*) AS total_resolved FROM tickets t WHERE t.status = 'Resolved'{date_filter_clause}", query_params)
        total_resolved = cursor.fetchone()['total_resolved'] or 0
        summary_labels['total_resolved'].config(text=f"Total Resolved: {total_resolved:,}")

        # Total Staff
        cursor.execute("SELECT COUNT(*) AS total_users FROM users WHERE role = 'Staff'")
        total_users = cursor.fetchone()['total_users'] or 0
        summary_labels['total_users'].config(text=f"Total Staff: {total_users:,}")

        # Status Distribution
        for item in tree.get_children():
            tree.delete(item)
        sql_status = f"SELECT status, COUNT(*) AS count FROM tickets t WHERE 1=1{date_filter_clause} GROUP BY status"
        cursor.execute(sql_status, query_params)
        status_order = ['Pending', 'In Progress', 'Resolved', 'Not Resolved']
        ticket_status = {row['status']: row['count'] for row in cursor.fetchall()}

        for status in status_order:
            count = ticket_status.get(status, 0)
            tree.insert("", tk.END, values=(status, f"{count:,}"))
        for status, count in ticket_status.items():
            if status not in status_order:
                tree.insert("", tk.END, values=(status, f"{count:,}"))

        # Detailed Tickets
        for item in detail_tree.get_children():
            detail_tree.delete(item)
        sql_details = f"""
            SELECT
                t.id,
                su.username AS staff_name,
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
            WHERE 1=1{date_filter_clause}
            ORDER BY t.created_at DESC
        """
        cursor.execute(sql_details, query_params)
        for row in cursor.fetchall():
            clean_row = tuple("" if v is None else str(v)[:100] if col == "Description" else str(v)[:200] if col == "Resolution Notes" else str(v) for col, v in zip(detail_columns, row.values()))
            detail_tree.insert("", tk.END, values=clean_row)

        conn.close()
        return {
            'total_tickets': total_tickets,
            'total_resolved': total_resolved,
            'total_users': total_users,
            'ticket_status': ticket_status,
            'tickets': cursor.fetchall()
        }

    # PDF Report Generator
    class PDFReport(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'Help Desk Report - LEVI27', 0, 1, 'C')
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

        def add_table(self, headers, rows, col_widths):
            self.set_font('Arial', 'B', 9)
            for header, width in zip(headers, col_widths):
                self.cell(width, 10, header, 1, 0, 'C')
            self.ln()
            self.set_font('Arial', '', 8)
            for row in rows:
                row_height = 10
                for col, value, width in zip(headers, row, col_widths):
                    text = str(value)[:100] if col in ["Description", "Resolution Notes"] else str(value)
                    self.multi_cell(width, 5, text, 1, 'L')
                self.ln(row_height)

    def generate_report(save_to_file=True):
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
            try:
                if start_date and end_date:
                    datetime.strptime(start_date, '%Y-%m-%d')
                    datetime.strptime(end_date, '%Y-%m-%d')
                    date_filter_clause = " AND t.created_at BETWEEN %s AND %s"
                    query_params = [f"{start_date} 00:00:00", f"{end_date} 23:59:59"]
                elif start_date:
                    datetime.strptime(start_date, '%Y-%m-%d')
                    date_filter_clause = " AND t.created_at >= %s"
                    query_params = [f"{start_date} 00:00:00"]
                elif end_date:
                    datetime.strptime(end_date, '%Y-%m-%d')
                    date_filter_clause = " AND t.created_at <= %s"
                    query_params = [f"{end_date} 23:59:59"]
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
                return None

        conn = self.connect_db()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)

        # Fetch summary data
        cursor.execute(f"SELECT COUNT(*) AS total_tickets FROM tickets t WHERE 1=1{date_filter_clause}", query_params)
        total_tickets = cursor.fetchone()['total_tickets'] or 0

        cursor.execute(f"SELECT COUNT(*) AS total_resolved FROM tickets t WHERE t.status = 'Resolved'{date_filter_clause}", query_params)
        total_resolved = cursor.fetchone()['total_resolved'] or 0

        cursor.execute("SELECT COUNT(*) AS total_users FROM users WHERE role = 'Staff'")
        total_users = cursor.fetchone()['total_users'] or 0

        cursor.execute(f"SELECT status, COUNT(*) AS count FROM tickets t WHERE 1=1{date_filter_clause} GROUP BY status")
        ticket_status = {row['status']: row['count'] for row in cursor.fetchall()}

        # Fetch detailed tickets
        sql_details = f"""
        SELECT
            t.id,
            su.username AS staff_name,
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
        WHERE 1=1{date_filter_clause}
        ORDER BY t.created_at DESC
        """
        cursor.execute(sql_details, query_params)
        tickets = cursor.fetchall()
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
        pdf.cell(0, 10, f"Total Staff: {total_users:,}", 0, 1)
        pdf.ln(10)

        # Status Distribution Section
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Ticket Status Distribution', 0, 1)
        pdf.set_font('Arial', '', 10)
        status_order = ['Pending', 'In Progress', 'Resolved', 'Not Resolved']
        for status in status_order:
            count = ticket_status.get(status, 0)
            pdf.cell(0, 10, f"{status:20}: {count:,}", 0, 1)
        for status, count in ticket_status.items():
            if status not in status_order:
                pdf.cell(0, 10, f"{status:20}: {count:,}", 0, 1)
        pdf.ln(10)

        # Detailed Tickets Section
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Detailed Ticket List', 0, 1)
        pdf.ln(5)
        headers = ["ID", "Staff", "Title", "Description", "Priority", "Technician", "Status", 
                   "Resolution Notes", "Created At", "Closed At"]
        col_widths = [15, 25, 25, 30, 15, 25, 15, 30, 25, 25]
        rows = [(t['id'], t['staff_name'], t['title'], t['description'][:100], t['priority'], 
                 t['technician_name'] or '', t['status'], t['resolution_notes'][:100] or '', 
                 str(t['created_at']), str(t['resolved_at']) or '') for t in tickets]
        pdf.add_table(headers, rows, col_widths)

        # Save or return PDF path
        pdf_path = 'help_desk_report.pdf' if save_to_file else 'temp_help_desk_report.pdf'
        try:
            pdf.output(pdf_path, 'F')
            if save_to_file:
                messagebox.showinfo("Success", f"Report saved as '{pdf_path}' in the current directory.")
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
            elif platform.system() == "Darwin":  # macOS
                os.system(f"open -a Preview {pdf_path}")
            elif platform.system() == "Linux":
                os.system(f"xdg-open {pdf_path}")
            messagebox.showinfo("Success", "Print dialog opened for the report.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open print dialog: {str(e)}")
        finally:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)  # Clean up temporary file

    # Button Frame (placed at the bottom)
    button_frame = tk.Frame(main_container, bg="#f7f9fa")
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

    ttk.Button(button_frame, text="📄 Generate Report", command=fetch_report).pack(side=tk.LEFT, padx=10)
    ttk.Button(button_frame, text="❌ Clear Filter", 
               command=lambda: [date_range_var.set("All Time"), start_date_entry.delete(0, tk.END), 
                                end_date_entry.delete(0, tk.END), toggle_date_fields(), fetch_report()]).pack(side=tk.LEFT, padx=10)
    ttk.Button(button_frame, text="💾 Save Report", command=lambda: generate_report(save_to_file=True)).pack(side=tk.LEFT, padx=10)
    ttk.Button(button_frame, text="🖨 Print Report", command=print_report).pack(side=tk.LEFT, padx=10)

    # Debug: Confirm buttons are created
    print("Buttons created: Generate Report, Clear Filter, Save Report, Print Report")

    # Initial fetch
    fetch_report()


### Changes Made:
1. **Layout Improvements**:
   - Added a `main_container` frame to manage the overall layout, ensuring all sections (filter, summary, status, details, buttons) are properly organized.
   - Changed `button_frame` to pack at the `side=tk.BOTTOM` of the `main_container` with `fill=tk.X` to ensure it spans the width and stays at the bottom.
   - Increased `pady=20` for the `button_frame` to add spacing and make it more visible.
   - Adjusted other frames (`summary_frame`, `status_frame`, `details_frame`) to use `fill=tk.X` or `fill=tk.BOTH` appropriately to prevent overlap or clipping.

2. **Button Placement**:
   - The buttons are now explicitly packed side-by-side (`side=tk.LEFT`) with `padx=10` for spacing.
   - Used `ttk.Button` with clear labels and emojis for visibility: "📄 Generate Report", "❌ Clear Filter", "💾 Save Report", "🖨 Print Report".

3. **Debugging**:
   - Added a `print` statement to confirm the buttons are created when the reports section loads: `"Buttons created: Generate Report, Clear Filter, Save Report, Print Report"`. Check your console/terminal for this output when you open the reports section.
   - If the buttons still don't appear, the console output will confirm whether the code reaches the button creation step.

4. **Preserved Functionality**:
   - The `fetch_report`, `generate_report`, and `print_report` functions remain unchanged, ensuring the report still includes:
     - Summary (total tickets, resolved, staff count).
     - Status distribution (ticket counts by status).
     - Detailed ticket list with ID, Staff, Title, Description, Priority, Technician, Status, Resolution Notes, Created At, and Closed At.
   - The PDF generation and printing functionality works as before.

### Troubleshooting Steps:
1. **Replace the Method**:
   - Open your `admin_dashboard.py` file.
   - Replace the entire `view_reports` method (from `def view_reports(self):` to its closing brace) with the code above. The rest of the file (e.g., `view_tickets`, `add_user`, etc.) can stay as is.
   - Save and run your application (`main.py`).

2. **Check Console Output**:
   - When you navigate to the "Reports" section in the AdminDashboard, check your terminal/console for the message: `"Buttons created: Generate Report, Clear Filter, Save Report, Print Report"`.
   - If you see this message but no buttons, the issue is likely with the Tkinter rendering or window size.

3. **Verify Window Size**:
   - Your dashboard is set to `geometry("1990x1200")`, which is quite large. If your screen resolution is lower, the buttons might be off-screen.
   - Try reducing the geometry temporarily to `geometry("1280x720")` in the `create_dashboard` method to see if the buttons appear:
     ```python
     self.dashboard.geometry("1280x720")
     ```
   - Alternatively, scroll down in the reports section to check if the buttons are at the bottom but not visible due to the window size.

4. **Inspect Layout**:
   - If the buttons still don't show, add a bright background color to the `button_frame` to make it stand out:
     ```python
     button_frame = tk.Frame(main_container, bg="yellow")  # Change bg="#f7f9fa" to bg="yellow"
     ```
     - If you see a yellow bar at the bottom, the frame is there but the buttons might not be packing correctly.

5. **Check for Errors**:
   - If there’s an error when loading the reports section, it might prevent the buttons from rendering. Check your terminal for any Tkinter or Python errors and share them with me.
   - Ensure your MySQL database (`helpdesk_db`) is running and accessible, as a database error could halt the `fetch_report` function.

6. **Test Button Functionality**:
   - If the buttons appear, test them:
     - **Generate Report**: Updates the UI with the filtered report.
     - **Clear Filter**: Resets the date range to "All Time" and refreshes the report.
     - **Save Report**: Saves `help_desk_report.pdf` in your project directory.
     - **Print Report**: Opens the system print dialog for the report.

### Additional Notes:
- **Dependencies**: Ensure `fpdf`, `mysql-connector-python`, and `tkinter` are installed:
  ```bash
  pip install fpdf mysql-connector-python
  ```
  On Linux, you may need `sudo apt-get install python3-tk`.
- **Database**: The code assumes your `tickets` and `users` tables exist in `helpdesk_db`. Populate some test data to ensure the report has content.
- **ImportError**: You previously mentioned an `ImportError` in `main.py`. If this persists, please share `main.py` and `login_screen.py`, as the issue might be related to module imports affecting the dashboard rendering.
- **UI Overlap**: If other widgets (e.g., the detailed ticket table) are expanding too much, they might push the buttons off-screen. The new `main_container` and `side=tk.BOTTOM` for the `button_frame` should fix this.

If the buttons still don’t show up after applying the updated code and trying the troubleshooting steps, please:
- Confirm whether you see the `"Buttons created..."` message in the console.
- Share any error messages from the terminal.
- Describe what you see in the reports section (e.g., do you see the filter frame, summary, tables?).
- Optionally, share a screenshot of the reports section or the full `admin_dashboard.py` if you’ve made other changes.

I’ll get those buttons shining for you! 😄 Let me know how it goes or if you need further tweaks.