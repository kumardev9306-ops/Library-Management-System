import customtkinter as ctk
from datetime import datetime

from database import connect_db
from books import open_books_window
from students import open_students_window
from issue_return import open_issue_return_window
from reports import open_reports_window


# Dashboard ke colors
BG = "#080F1E"
SIDEBAR = "#0D1729"
CARD = "#131F35"
CARD_HOVER = "#1A2A45"

BLUE = "#3B82F6"
PURPLE = "#8B5CF6"
GREEN = "#10B981"
ORANGE = "#F59E0B"
RED = "#EF4444"

TEXT = "#F8FAFC"
MUTED = "#94A3B8"
BORDER = "#253550"


# Database se dashboard ke latest statistics lana
def get_dashboard_stats():

    db = connect_db()

    if db is None:
        return (0, 0, 0, 0, 0, 0)

    cursor = None

    try:
        cursor = db.cursor()

        cursor.execute(
            "SELECT COALESCE(SUM(quantity), 0) FROM books"
        )
        total_books = int(cursor.fetchone()[0] or 0)

        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = int(cursor.fetchone()[0] or 0)

        cursor.execute(
            "SELECT COUNT(*) FROM issued_books WHERE status = 'Issued'"
        )
        issued_books = int(cursor.fetchone()[0] or 0)

        cursor.execute(
            "SELECT COALESCE(SUM(available), 0) FROM books"
        )
        available_books = int(cursor.fetchone()[0] or 0)

        cursor.execute(
            "SELECT COUNT(*) FROM issued_books WHERE status = 'Returned'"
        )
        returned_books = int(cursor.fetchone()[0] or 0)

        # 2 ya usse kam available copies wali books ko low stock maan rahe hain
        cursor.execute(
            "SELECT COUNT(*) FROM books WHERE available <= 2"
        )
        low_stock_books = int(cursor.fetchone()[0] or 0)

        return (
            total_books,
            total_students,
            issued_books,
            available_books,
            returned_books,
            low_stock_books
        )

    except Exception as e:
        print("Dashboard Stats Error:", e)
        return (0, 0, 0, 0, 0, 0)

    finally:
        if cursor:
            cursor.close()
        db.close()


# Recent issue aur return records database se lana
def get_recent_activity():

    db = connect_db()

    if db is None:
        return []

    cursor = None

    try:
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                books.title,
                students.name,
                issued_books.issue_date,
                issued_books.status
            FROM issued_books
            JOIN books
                ON issued_books.book_id = books.book_id
            JOIN students
                ON issued_books.student_id = students.student_id
            ORDER BY issued_books.issue_id DESC
            LIMIT 8
        """)

        return cursor.fetchall()

    except Exception as e:
        print("Recent Activity Error:", e)
        return []

    finally:
        if cursor:
            cursor.close()
        db.close()


# Main dashboard window create karna
def create_dashboard():

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Library Management System")
    app.geometry("1250x780")
    app.minsize(1050, 700)
    app.configure(fg_color=BG)

    # ================= SIDEBAR =================

    sidebar = ctk.CTkFrame(
        app,
        width=230,
        corner_radius=0,
        fg_color=SIDEBAR
    )
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
    logo_frame.pack(fill="x", padx=22, pady=(35, 35))

    ctk.CTkLabel(
        logo_frame,
        text="LIBRARY",
        font=("Arial", 25, "bold"),
        text_color=BLUE
    ).pack(anchor="w")

    ctk.CTkLabel(
        logo_frame,
        text="MANAGEMENT SYSTEM",
        font=("Arial", 10, "bold"),
        text_color=MUTED
    ).pack(anchor="w", pady=(3, 0))

    ctk.CTkLabel(
        sidebar,
        text="WORKSPACE",
        font=("Arial", 10, "bold"),
        text_color="#64748B"
    ).pack(anchor="w", padx=25, pady=(0, 12))

    menu_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
    menu_frame.pack(fill="x", padx=12)

    menu_buttons = {}

    # Active page ke button ko highlight karna
    def set_active(name):

        for menu_name, button in menu_buttons.items():

            if menu_name == name:
                button.configure(
                    fg_color="#1D4ED8",
                    hover_color="#2563EB",
                    text_color="white"
                )
            else:
                button.configure(
                    fg_color="transparent",
                    hover_color="#1B2A42",
                    text_color="#B7C5D8"
                )

    # Sidebar navigation button banana
    def create_menu_button(name, command):

        button = ctk.CTkButton(
            menu_frame,
            text=name,
            height=45,
            corner_radius=12,
            anchor="w",
            font=("Arial", 13, "bold"),
            fg_color="transparent",
            hover_color="#1B2A42",
            text_color="#B7C5D8",
            command=command
        )
        button.pack(fill="x", pady=4)
        menu_buttons[name] = button

    sidebar_bottom = ctk.CTkFrame(sidebar, fg_color="transparent")
    sidebar_bottom.pack(side="bottom", fill="x", padx=20, pady=25)

    ctk.CTkLabel(
        sidebar_bottom,
        text="LIBRARY SYSTEM",
        font=("Arial", 11, "bold"),
        text_color="#64748B"
    ).pack(anchor="w")

    ctk.CTkLabel(
        sidebar_bottom,
        text="Version 2.1",
        font=("Arial", 10),
        text_color="#64748B"
    ).pack(anchor="w", pady=(5, 0))

    # ================= MAIN CONTENT =================

    content = ctk.CTkFrame(app, fg_color=BG)
    content.pack(
        side="left",
        fill="both",
        expand=True,
        padx=20,
        pady=20
    )

    page_container = ctk.CTkFrame(
        content,
        fg_color="transparent"
    )
    page_container.pack(fill="both", expand=True)

    # Current page ke widgets remove karna
    def clear_page():

        for widget in page_container.winfo_children():
            widget.destroy()

    # ================= PAGE NAVIGATION =================

    def show_dashboard():

        clear_page()
        set_active("Dashboard")

        dashboard_page = ctk.CTkFrame(
            page_container,
            fg_color="transparent"
        )
        dashboard_page.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(
            dashboard_page,
            fg_color="transparent"
        )
        header.pack(fill="x", pady=(5, 15))

        header_left = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )
        header_left.pack(side="left", anchor="w")

        ctk.CTkLabel(
            header_left,
            text="Dashboard Overview",
            font=("Arial", 26, "bold"),
            text_color=TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_left,
            text="Monitor and manage your library activities",
            font=("Arial", 12),
            text_color=MUTED
        ).pack(anchor="w", pady=(5, 0))

        header_right = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )
        header_right.pack(side="right", anchor="e")

        ctk.CTkLabel(
            header_right,
            text=datetime.now().strftime("%d %B %Y"),
            font=("Arial", 12, "bold"),
            text_color="#CBD5E1"
        ).pack(anchor="e", pady=(0, 8))

        # Statistics heading
        ctk.CTkLabel(
            dashboard_page,
            text="LIBRARY STATISTICS",
            font=("Arial", 12, "bold"),
            text_color=MUTED
        ).pack(anchor="w", pady=(0, 8))

        stats_frame = ctk.CTkFrame(
            dashboard_page,
            fg_color="transparent"
        )
        stats_frame.pack(fill="x")

        for col in range(3):
            stats_frame.grid_columnconfigure(
                col,
                weight=1,
                uniform="stats"
            )

        initial_values = get_dashboard_stats()

        card_data = [
            ("TOTAL BOOK COPIES", BLUE),
            ("TOTAL STUDENTS", GREEN),
            ("CURRENTLY ISSUED", ORANGE),
            ("AVAILABLE COPIES", PURPLE),
            ("RETURNED RECORDS", GREEN),
            ("LOW STOCK TITLES", RED)
        ]

        stat_value_labels = []

        # 6 statistics cards ko 2 rows mein show karna
        for i, (title, color) in enumerate(card_data):

            card = ctk.CTkFrame(
                stats_frame,
                fg_color=CARD,
                corner_radius=13,
                border_width=1,
                border_color=BORDER,
                height=95
            )

            card.grid(
                row=i // 3,
                column=i % 3,
                padx=5,
                pady=5,
                sticky="nsew"
            )
            card.grid_propagate(False)

            ctk.CTkLabel(
                card,
                text=title,
                font=("Arial", 9, "bold"),
                text_color=MUTED
            ).pack(anchor="w", padx=13, pady=(15, 3))

            value_label = ctk.CTkLabel(
                card,
                text=f"{initial_values[i]:,}",
                font=("Arial", 23, "bold"),
                text_color=color
            )
            value_label.pack(anchor="w", padx=13)

            stat_value_labels.append(value_label)

            card.bind(
                "<Enter>",
                lambda event, current_card=card:
                current_card.configure(fg_color=CARD_HOVER)
            )
            card.bind(
                "<Leave>",
                lambda event, current_card=card:
                current_card.configure(fg_color=CARD)
            )

        # Quick actions
        quick_frame = ctk.CTkFrame(
            dashboard_page,
            fg_color="transparent"
        )
        quick_frame.pack(fill="x", pady=(15, 12))

        ctk.CTkLabel(
            quick_frame,
            text="QUICK ACTIONS",
            font=("Arial", 12, "bold"),
            text_color=MUTED
        ).pack(anchor="w", pady=(0, 8))

        action_row = ctk.CTkFrame(
            quick_frame,
            fg_color="transparent"
        )
        action_row.pack(fill="x")

        def create_action_button(title, color, hover, command):

            ctk.CTkButton(
                action_row,
                text=title,
                height=37,
                corner_radius=9,
                fg_color=color,
                hover_color=hover,
                font=("Arial", 10, "bold"),
                command=command
            ).pack(side="left", padx=(0, 7))

        create_action_button(
            "Manage Books", "#1D4ED8", "#2563EB", show_books
        )
        create_action_button(
            "Manage Students", "#047857", "#059669", show_students
        )
        create_action_button(
            "Issue Book", "#6D28D9", "#7C3AED", show_issue
        )
        create_action_button(
            "Return Book", "#B45309", "#D97706", show_return
        )
        create_action_button(
            "View Reports", "#334155", "#475569", show_reports
        )

        # Recent activity card
        activity = ctk.CTkFrame(
            dashboard_page,
            fg_color=CARD,
            corner_radius=14,
            border_width=1,
            border_color=BORDER
        )
        activity.pack(fill="both", expand=True, pady=(2, 0))

        activity_header = ctk.CTkFrame(
            activity,
            fg_color="transparent"
        )
        activity_header.pack(
            fill="x",
            padx=16,
            pady=(12, 8)
        )

        ctk.CTkLabel(
            activity_header,
            text="Recent Activity",
            font=("Arial", 17, "bold"),
            text_color=TEXT
        ).pack(side="left")

        ctk.CTkLabel(
            activity_header,
            text="LATEST 8 RECORDS",
            font=("Arial", 9, "bold"),
            text_color=MUTED
        ).pack(side="right")

        activity_list = ctk.CTkScrollableFrame(
            activity,
            fg_color="transparent"
        )
        activity_list.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=(0, 8)
        )

        def load_activity():

            for widget in activity_list.winfo_children():
                widget.destroy()

            records = get_recent_activity()

            if not records:
                ctk.CTkLabel(
                    activity_list,
                    text="No recent activity found.",
                    font=("Arial", 12),
                    text_color=MUTED
                ).pack(pady=20)
                return

            for title, student, issue_date, status in records:

                row = ctk.CTkFrame(
                    activity_list,
                    fg_color="#1A2940",
                    corner_radius=9
                )
                row.pack(fill="x", padx=4, pady=3)

                left = ctk.CTkFrame(
                    row,
                    fg_color="transparent"
                )
                left.pack(
                    side="left",
                    fill="both",
                    expand=True,
                    padx=11,
                    pady=7
                )

                ctk.CTkLabel(
                    left,
                    text=str(title),
                    font=("Arial", 11, "bold"),
                    text_color=TEXT
                ).pack(anchor="w")

                ctk.CTkLabel(
                    left,
                    text=f"Student: {student}    Date: {issue_date}",
                    font=("Arial", 9),
                    text_color=MUTED
                ).pack(anchor="w", pady=(3, 0))

                status_color = GREEN if status == "Issued" else BLUE

                ctk.CTkLabel(
                    row,
                    text=str(status).upper(),
                    font=("Arial", 9, "bold"),
                    text_color=status_color,
                    fg_color="#263B54",
                    corner_radius=7,
                    width=75,
                    height=25
                ).pack(side="right", padx=10)

        # Dashboard ke numbers aur recent activity refresh karna
        def refresh_dashboard():

            refresh_button.configure(
                text="Refreshing...",
                state="disabled"
            )

            def update_dashboard():

                try:
                    new_values = get_dashboard_stats()

                    for index, label in enumerate(stat_value_labels):
                        label.configure(text=f"{new_values[index]:,}")

                    load_activity()

                except Exception as e:
                    print("Refresh Error:", e)

                finally:
                    if app.winfo_exists() and refresh_button.winfo_exists():
                        refresh_button.configure(
                            text="Refresh Dashboard",
                            state="normal"
                        )

            app.after(100, update_dashboard)

        refresh_button = ctk.CTkButton(
            header_right,
            text="Refresh Dashboard",
            width=165,
            height=35,
            corner_radius=9,
            fg_color=BLUE,
            hover_color="#1D4ED8",
            font=("Arial", 10, "bold"),
            command=refresh_dashboard
        )
        refresh_button.pack(anchor="e")

        load_activity()

        ctk.CTkLabel(
            dashboard_page,
            text="Library Management System - Efficient Library Operations",
            font=("Arial", 9),
            text_color="#64748B"
        ).pack(pady=(7, 0))

    # Books page open karna
    def show_books():
        clear_page()
        set_active("Books")
        open_books_window(page_container)

    # Students page open karna
    def show_students():
        clear_page()
        set_active("Students")
        open_students_window(page_container)

    # Issue Books page open karna
    def show_issue():
        clear_page()
        set_active("Issue Books")
        open_issue_return_window(page_container, mode="issue")

    # Return Books page open karna
    def show_return():
        clear_page()
        set_active("Return Books")
        open_issue_return_window(page_container, mode="return")

    # Reports page open karna
    def show_reports():
        clear_page()
        set_active("Reports")
        open_reports_window(page_container)

    # ================= SIDEBAR BUTTONS =================

    create_menu_button("Dashboard", show_dashboard)
    create_menu_button("Books", show_books)
    create_menu_button("Students", show_students)
    create_menu_button("Issue Books", show_issue)
    create_menu_button("Return Books", show_return)
    create_menu_button("Reports", show_reports)

    # Starting mein dashboard open hoga
    show_dashboard()

    app.mainloop()
