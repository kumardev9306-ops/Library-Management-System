import csv
import customtkinter as ctk

from tkinter import ttk, messagebox, filedialog
from database import connect_db


from ui_theme import apply_treeview_theme
# Dashboard ke andar Reports page open karna
def open_reports_window(parent):

    page = ctk.CTkFrame(parent, fg_color="#080F1E")
    page.pack(fill="both", expand=True)

    ctk.CTkLabel(
        page,
        text="Library Reports",
        font=("Arial", 27, "bold"),
        text_color="#F8FAFC"
    ).pack(anchor="w", padx=20, pady=(15, 5))

    ctk.CTkLabel(
        page,
        text="View library records and export reports as CSV files",
        font=("Arial", 12),
        text_color="#94A3B8"
    ).pack(anchor="w", padx=20, pady=(0, 15))

    # Report type aur search ke controls
    controls = ctk.CTkFrame(
        page,
        fg_color="#17243A",
        corner_radius=12
    )
    controls.pack(fill="x", padx=20, pady=8)

    ctk.CTkLabel(
        controls,
        text="Select Report",
        font=("Arial", 11, "bold"),
        text_color="#F8FAFC"
    ).pack(side="left", padx=(15, 7), pady=14)

    report_box = ctk.CTkComboBox(
        controls,
        values=[
            "Inventory Report",
            "Issue History",
            "Low Stock Books"
        ],
        width=190,
        state="readonly"
    )
    report_box.pack(side="left", padx=5, pady=12)
    report_box.set("Inventory Report")

    search_entry = ctk.CTkEntry(
        controls,
        placeholder_text="Search book or student...",
        width=220
    )
    search_entry.pack(side="left", padx=8, pady=12)

    # Report ke records yahan store honge
    report_columns = []
    current_rows = []

    # Table area
    table_frame = ctk.CTkFrame(
        page,
        fg_color="#131F35",
        corner_radius=12
    )
    table_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=12
    )

    apply_treeview_theme(page)
    tree = ttk.Treeview(
        table_frame,
        show="headings",
        selectmode="browse"
    )
    tree.pack(fill="both", expand=True, padx=8, pady=8)

    # Report type ke hisaab se database se data lana
    def load_report():

        nonlocal report_columns, current_rows

        report_type = report_box.get()
        keyword = search_entry.get().strip()

        db = connect_db()

        if db is None:
            messagebox.showerror(
                "Database Error",
                "Unable to connect to database!"
            )
            return

        cursor = None

        try:
            cursor = db.cursor()

            if report_type == "Inventory Report":

                report_columns = (
                    "Book ID",
                    "Title",
                    "Author",
                    "Category",
                    "Total Quantity",
                    "Available"
                )

                cursor.execute(
                    """
                    SELECT book_id, title, author, category,
                           quantity, available
                    FROM books
                    WHERE title LIKE %s OR author LIKE %s
                       OR category LIKE %s
                    ORDER BY title
                    """,
                    (
                        "%" + keyword + "%",
                        "%" + keyword + "%",
                        "%" + keyword + "%"
                    )
                )

            elif report_type == "Issue History":

                report_columns = (
                    "Issue ID",
                    "Book",
                    "Student",
                    "Issue Date",
                    "Return Date",
                    "Status"
                )

                cursor.execute(
                    """
                    SELECT
                        ib.issue_id,
                        b.title,
                        s.name,
                        ib.issue_date,
                        ib.return_date,
                        ib.status
                    FROM issued_books ib
                    JOIN books b ON ib.book_id = b.book_id
                    JOIN students s ON ib.student_id = s.student_id
                    WHERE b.title LIKE %s OR s.name LIKE %s
                    ORDER BY ib.issue_id DESC
                    """,
                    (
                        "%" + keyword + "%",
                        "%" + keyword + "%"
                    )
                )

            else:

                report_columns = (
                    "Book ID",
                    "Title",
                    "Author",
                    "Category",
                    "Total Quantity",
                    "Available"
                )

                cursor.execute(
                    """
                    SELECT book_id, title, author, category,
                           quantity, available
                    FROM books
                    WHERE available <= 2
                      AND (title LIKE %s OR author LIKE %s
                           OR category LIKE %s)
                    ORDER BY available ASC, title
                    """,
                    (
                        "%" + keyword + "%",
                        "%" + keyword + "%",
                        "%" + keyword + "%"
                    )
                )

            current_rows = cursor.fetchall()

            # Purane table columns aur rows remove karna
            tree.delete(*tree.get_children())
            tree["columns"] = report_columns

            for column in report_columns:
                tree.heading(column, text=column)
                tree.column(
                    column,
                    width=135,
                    minwidth=90,
                    anchor="center"
                )

            # Naye records table mein show karna
            for row in current_rows:
                tree.insert("", "end", values=row)

            if not current_rows:
                messagebox.showinfo(
                    "No Records",
                    "No records found for this report."
                )

        except Exception as e:
            messagebox.showerror(
                "Report Error",
                str(e)
            )

        finally:
            if cursor:
                cursor.close()
            db.close()

    # Current report ko CSV file mein save karna
    def export_report():

        if not current_rows:
            messagebox.showwarning(
                "No Data",
                "There are no records to export!"
            )
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=report_box.get().lower().replace(" ", "_") + ".csv"
        )

        if not file_path:
            return

        try:
            with open(
                file_path,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as file:

                writer = csv.writer(file)
                writer.writerow(report_columns)
                writer.writerows(current_rows)

            messagebox.showinfo(
                "Export Successful",
                "Report exported successfully!"
            )

        except Exception as e:
            messagebox.showerror(
                "Export Error",
                str(e)
            )

    # Buttons
    ctk.CTkButton(
        controls,
        text="Load Report",
        width=110,
        command=load_report
    ).pack(side="left", padx=6, pady=12)

    ctk.CTkButton(
        controls,
        text="Export CSV",
        width=110,
        fg_color="#047857",
        hover_color="#059669",
        command=export_report
    ).pack(side="left", padx=(4, 12), pady=12)

    # Page open hote hi inventory report load karna
    load_report()
