from tkinter import ttk


def apply_treeview_theme(widget):
    """
    Library Management System ke tables ko dark theme dene ke liye
    Common style function.
    """
    style = ttk.Style(widget)

    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(
        "Treeview",
        background="#101C30",
        fieldbackground="#101C30",
        foreground="#E5EDF8",
        rowheight=34,
        borderwidth=0,
        relief="flat",
        font=("Arial", 10)
    )

    style.configure(
        "Treeview.Heading",
        background="#1D4ED8",
        foreground="#FFFFFF",
        font=("Arial", 10, "bold"),
        relief="flat",
        padding=(8, 10)
    )

    style.map(
        "Treeview",
        background=[("selected", "#2563EB")],
        foreground=[("selected", "#FFFFFF")]
    )

    style.map(
        "Treeview.Heading",
        background=[("active", "#2563EB")]
    )
