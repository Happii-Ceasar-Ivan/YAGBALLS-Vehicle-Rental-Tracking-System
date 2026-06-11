import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from PIL import Image
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_db_path():
    """ Determine the database path robustly for both script and .exe modes """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_dir = os.path.dirname(sys.executable)
        # If the exe is inside a "dist" folder, go up two levels
        if os.path.basename(base_dir).lower() == 'dist':
            return os.path.join(base_dir, "..", "..", "YB Rental Database FIle", "yb_rental.db")
        else:
            return os.path.join(base_dir, "..", "YB Rental Database FIle", "yb_rental.db")
    else:
        # Running as a python script
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "YB Rental Database FIle", "yb_rental.db")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── COLORS ──
BG       = "#0A0B0D"
SURFACE  = "#111318"
PANEL    = "#181C24"
BORDER   = "#252B38"
ACCENT   = "#3D7BFF"
TEXT     = "#E8EAF0"
TEXT_DIM = "#7A8299"
DANGER   = "#E84040"

TABLE_COLUMNS = {
    "Branches":           ("BranchID", "BranchName", "City", "Province", "Phone"),
    "Vehicle_Categories": ("CategoryID", "CategoryName", "DailyRate", "OverdueRatePerHour"),
    "Vehicle_Models":     ("ModelID", "Brand", "ModelName", "FuelType", "Transmission"),
    "Vehicles":           ("VehicleID", "LicensePlate", "CurrentMileage", "Status", "CurrentBranchID"),
    "Customers":          ("CustomerID", "FirstName", "LastName", "Email", "Phone"),
    "Rentals":            ("RentalID", "CustomerID", "VehicleID", "RentedOn", "Status"),
    "Payments":           ("PaymentID", "RentalID", "PaidOn", "TotalAmount", "PaymentMethod"),
    "Maintenance_Logs":   ("LogID", "VehicleID", "StartDate", "EndDate", "Status"),
    "Damage_Reports":     ("ReportID", "RentalID", "IncidentDate", "EstimatedRepairCost", "Status"),
    "Employees":          ("EmployeeID", "FirstName", "LastName", "BranchID", "SupervisorID"),
}

TABLES = list(TABLE_COLUMNS.keys())

app = ctk.CTk()
app.title("YB Vehicle Rental System")
app.geometry("1280x720")
app.resizable(False, False)
app.minsize(1280, 720)
app.maxsize(1280, 720)
app.configure(fg_color=BG)

logo_img_large = ctk.CTkImage(Image.open(resource_path("yblogo.png")), size=(220, 88))
logo_img_small = ctk.CTkImage(Image.open(resource_path("yblogo.png")), size=(80, 32))

# ════════════════════════════════════════
#  SCREENS
# ════════════════════════════════════════

landing_frame  = ctk.CTkFrame(app, fg_color=BG, corner_radius=0)
main_frame     = ctk.CTkFrame(app, fg_color=BG, corner_radius=0)

def show_landing():
    main_frame.place_forget()
    landing_frame.place(x=0, y=0, relwidth=1, relheight=1)

def show_main():
    landing_frame.place_forget()
    main_frame.place(x=0, y=0, relwidth=1, relheight=1)

# ════════════════════════════════════════
#  LANDING SCREEN
# ════════════════════════════════════════

logo_label = ctk.CTkLabel(landing_frame, image=logo_img_large, text="")
logo_label.place(relx=0.5, rely=0.32, anchor="center")

welcome_label = ctk.CTkLabel(landing_frame,
                              text="Welcome",
                              font=("Arial", 28, "bold"),
                              text_color=TEXT)
welcome_label.place(relx=0.5, rely=0.48, anchor="center")

sub_label = ctk.CTkLabel(landing_frame,
                          text="Please select a database to use.",
                          font=("Arial", 13),
                          text_color=TEXT_DIM)
sub_label.place(relx=0.5, rely=0.54, anchor="center")

db_var = ctk.StringVar(value="YB_Rentals_DB")
db_dropdown = ctk.CTkOptionMenu(landing_frame,
                                 values=["YB_Rentals_DB", "YB_Rentals_Test"],
                                 variable=db_var,
                                 width=280, height=36,
                                 fg_color=SURFACE,
                                 button_color=ACCENT,
                                 button_hover_color="#2D6AEF",
                                 text_color=TEXT,
                                 font=("Arial", 12))
db_dropdown.place(relx=0.5, rely=0.62, anchor="center")

load_btn_landing = ctk.CTkButton(landing_frame,
                                  text="Load",
                                  width=280, height=40,
                                  fg_color=ACCENT,
                                  hover_color="#2D6AEF",
                                  text_color=TEXT,
                                  font=("Arial", 13, "bold"),
                                  corner_radius=8,
                                  command=show_main)
load_btn_landing.place(relx=0.5, rely=0.71, anchor="center")

# ════════════════════════════════════════
#  MAIN SCREEN — NAVBAR
# ════════════════════════════════════════

navbar = ctk.CTkFrame(main_frame, height=48, fg_color=SURFACE, corner_radius=0)
navbar.pack(fill="x", side="top")
navbar.pack_propagate(False)

nav_logo = ctk.CTkLabel(navbar, image=logo_img_small, text="")
nav_logo.pack(side="left", padx=12, pady=8)

load_btn = ctk.CTkButton(navbar, text="Load Database", width=130, height=32,
                          fg_color=PANEL, text_color=TEXT_DIM, hover_color=BORDER,
                          corner_radius=6, command=show_landing)
load_btn.pack(side="right", padx=6, pady=8)

edit_record_btn = ctk.CTkButton(navbar, text="Edit Record", width=120, height=32,
                                 fg_color=PANEL, text_color=TEXT_DIM, hover_color=BORDER,
                                 corner_radius=6)
edit_record_btn.pack(side="right", padx=6, pady=8)

db_editor_btn = ctk.CTkButton(navbar, text="Database Editor", width=140, height=32,
                               fg_color=ACCENT, text_color=TEXT, hover_color="#2D6AEF",
                               corner_radius=6)
db_editor_btn.pack(side="right", padx=6, pady=8)

# ════════════════════════════════════════
#  MAIN SCREEN — BODY
# ════════════════════════════════════════

body = ctk.CTkFrame(main_frame, fg_color=BG, corner_radius=0)
body.pack(fill="both", expand=True)

# ── SIDEBAR ──
sidebar = ctk.CTkFrame(body, width=200, fg_color=SURFACE, corner_radius=0)
sidebar.pack(fill="y", side="left")
sidebar.pack_propagate(False)

ctk.CTkLabel(sidebar, text="TABLES", font=("Arial", 10, "bold"),
             text_color=TEXT_DIM).pack(anchor="w", padx=16, pady=(16, 8))

# ── MAIN CONTENT ──
main_content = ctk.CTkFrame(body, fg_color=BG, corner_radius=0)
main_content.pack(fill="both", expand=True, side="left", padx=12, pady=12)

# ── FILTER BAR ──
filter_frame = ctk.CTkFrame(main_content, fg_color=SURFACE, corner_radius=8)
filter_frame.pack(fill="x", pady=(0, 8))

filter_top = ctk.CTkFrame(filter_frame, fg_color="transparent")
filter_top.pack(fill="x", padx=10, pady=8)

for label, color, tcolor in [
    ("+ Add Condition", PANEL, TEXT_DIM),
    ("Filter ▾",        PANEL, TEXT_DIM),
    ("Clear",           PANEL, TEXT_DIM),
    ("Apply Filter",    ACCENT, TEXT),
]:
    ctk.CTkButton(filter_top, text=label, width=110, height=28,
                  fg_color=color, text_color=tcolor, hover_color=BORDER,
                  corner_radius=6, font=("Arial", 11)).pack(side="left", padx=4)

# ── TREEVIEW STYLE ──
style = ttk.Style()
style.theme_use("default")
style.configure("Custom.Treeview",
                background=SURFACE, foreground=TEXT,
                fieldbackground=SURFACE, borderwidth=0,
                rowheight=36, font=("Arial", 11))
style.configure("Custom.Treeview.Heading",
                background=PANEL, foreground=TEXT_DIM,
                borderwidth=0, font=("Arial", 10, "bold"))
style.map("Custom.Treeview",
          background=[("selected", ACCENT)],
          foreground=[("selected", TEXT)])

# ── DATA GRID ──
grid_frame = ctk.CTkFrame(main_content, fg_color=SURFACE, corner_radius=8)
grid_frame.pack(fill="both", expand=True, pady=(0, 8))

tree = ttk.Treeview(grid_frame, style="Custom.Treeview",
                    show="headings", selectmode="browse")
tree.pack(fill="both", expand=True, padx=1, pady=1)

# ── BOTTOM BAR ──
bottom = ctk.CTkFrame(main_content, height=40, fg_color=SURFACE, corner_radius=8)
bottom.pack(fill="x", side="bottom")
bottom.pack_propagate(False)

records_label = ctk.CTkLabel(bottom, text="Select a table.",
                              text_color=TEXT_DIM, font=("Arial", 11))
records_label.pack(side="left", padx=12)

for label, color in [("Remove", DANGER), ("Duplicate", PANEL),
                      ("Add", PANEL), ("Edit", ACCENT)]:
    b = ctk.CTkButton(bottom, text=label, width=90, height=28,
                  fg_color=color, text_color=TEXT,
                  hover_color=BORDER, corner_radius=6,
                  font=("Arial", 11),
                  command=lambda l=label: show_edit() if l == "Edit" else None)
    b.pack(side="right", padx=4, pady=6)

# ── TABLE LOADER ──
def load_table(name):
    for btn in table_buttons:
        if btn.cget("text") == name:
            btn.configure(fg_color=ACCENT, text_color=TEXT)
        else:
            btn.configure(fg_color="transparent", text_color=TEXT_DIM)

    cols = TABLE_COLUMNS.get(name, ("ID", "Value"))
    tree["columns"] = cols
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=240, anchor="w", minwidth=80)

    for row in tree.get_children():
        tree.delete(row)

    import sqlite3
    db_path = get_db_path()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Handle the typo in the SQL schema for Vehicles
        query_cols = [c if c != "CurrentMileage" else "CurrentMilieage" for c in cols]
        
        cursor.execute(f"SELECT {', '.join(query_cols)} FROM {name}")
        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)
        conn.close()
        records_label.configure(text=f"{len(rows)} Records Found.  |  {name}")
    except sqlite3.Error as e:
        records_label.configure(text=f"Error loading {name}: {e}")

# ── SIDEBAR BUTTONS ──
table_buttons = []
for table in TABLES:
    btn = ctk.CTkButton(sidebar, text=table, height=32, anchor="w",
                         fg_color="transparent", text_color=TEXT_DIM,
                         hover_color=PANEL, corner_radius=6,
                         font=("Arial", 12),
                         command=lambda t=table: load_table(t))
    btn.pack(fill="x", padx=8, pady=2)
    table_buttons.append(btn)

load_table("Branches")

# ════════════════════════════════════════
#  EDIT RECORD SCREEN
# ════════════════════════════════════════

edit_frame = ctk.CTkFrame(app, fg_color=BG, corner_radius=0)

def show_edit():
    selected = tree.selection()
    if not selected:
        return
    main_frame.place_forget()
    edit_frame.place(x=0, y=0, relwidth=1, relheight=1)
    populate_edit_form()

def show_main_from_edit():
    edit_frame.place_forget()
    main_frame.place(x=0, y=0, relwidth=1, relheight=1)
    
    table_str = records_label.cget("text")
    if "|" in table_str:
        table_name = table_str.split("|")[-1].strip()
        load_table(table_name)

# ── EDIT NAVBAR ──
edit_navbar = ctk.CTkFrame(edit_frame, height=48, fg_color=SURFACE, corner_radius=0)
edit_navbar.pack(fill="x", side="top")
edit_navbar.pack_propagate(False)

edit_nav_logo = ctk.CTkLabel(edit_navbar, image=logo_img_small, text="")
edit_nav_logo.pack(side="left", padx=12, pady=8)

ctk.CTkButton(edit_navbar, text="Load Database", width=130, height=32,
              fg_color=PANEL, text_color=TEXT_DIM, hover_color=BORDER,
              corner_radius=6, command=show_landing).pack(side="right", padx=6, pady=8)

ctk.CTkButton(edit_navbar, text="Edit Record", width=120, height=32,
              fg_color=ACCENT, text_color=TEXT, hover_color="#2D6AEF",
              corner_radius=6).pack(side="right", padx=6, pady=8)

ctk.CTkButton(edit_navbar, text="Database Editor", width=140, height=32,
              fg_color=PANEL, text_color=TEXT_DIM, hover_color=BORDER,
              corner_radius=6, command=show_main_from_edit).pack(side="right", padx=6, pady=8)

# ── EDIT BODY ──
edit_body = ctk.CTkFrame(edit_frame, fg_color=BG, corner_radius=0)
edit_body.pack(fill="both", expand=True, padx=24, pady=(20, 0))

form_frame = ctk.CTkFrame(edit_body, fg_color=SURFACE, corner_radius=8)
form_frame.pack(fill="both", expand=True, pady=(0,8))

form_inner = ctk.CTkFrame(form_frame, fg_color="transparent")
form_inner.pack(fill="both", expand=True, padx=24, pady=20)

edit_entries = {}

def populate_edit_form():
    # Clear existing widgets
    for widget in form_inner.winfo_children():
        widget.destroy()
    edit_entries.clear()

    selected = tree.selection()
    if not selected:
        return

    values = tree.item(selected[0])["values"]
    table_name = records_label.cget("text").split("|")[-1].strip()
    cols = TABLE_COLUMNS.get(table_name, ())

    # Two-column layout
    for i, col in enumerate(cols):
        row = i // 2
        col_pos = i % 2

        label = ctk.CTkLabel(form_inner, text=col,
                              font=("Arial", 12), text_color=TEXT_DIM,
                              anchor="w")
        label.grid(row=row, column=col_pos * 2, padx=(0, 12),
                   pady=10, sticky="w")

        val = values[i] if i < len(values) else ""

        # PK fields (first column) are read-only
        if i == 0:
            entry = ctk.CTkEntry(form_inner, width=480, height=34,
                                  fg_color=PANEL, text_color=TEXT_DIM,
                                  border_color=BORDER, font=("Arial", 12),
                                  state="disabled")
        else:
            entry = ctk.CTkEntry(form_inner, width=480, height=34,
                                  fg_color=PANEL, text_color=TEXT,
                                  border_color=BORDER, font=("Arial", 12))

        entry.grid(row=row, column=col_pos * 2 + 1,
                   padx=(0, 40), pady=10, sticky="ew")

        if i == 0:
            entry.configure(state="normal")
            entry.insert(0, str(val))
            entry.configure(state="disabled")
        else:
            entry.insert(0, str(val))

        edit_entries[col] = entry

    # Configure grid columns
    form_inner.grid_columnconfigure(1, weight=1)
    form_inner.grid_columnconfigure(3, weight=1)
    form_inner.grid_columnconfigure(0, weight=1)
    form_inner.grid_columnconfigure(2, weight=1)

# ── EDIT BOTTOM BAR ──
edit_bottom = ctk.CTkFrame(edit_frame, height=40, fg_color=SURFACE, corner_radius=8)
edit_bottom.pack(fill="x", side="bottom", padx=12, pady=(0, 12))
edit_bottom.pack_propagate(False)

status_label = ctk.CTkLabel(edit_bottom, text="Record is saved in the database.",
                             text_color=TEXT_DIM, font=("Arial", 11))
status_label.pack(side="left", padx=12)

def save_record():
    import sqlite3
    import os
    table_str = records_label.cget("text")
    if "|" not in table_str: return
    table_name = table_str.split("|")[-1].strip()
        
    cols = TABLE_COLUMNS.get(table_name, ())
    if not cols: return
    
    pk_val = edit_entries[cols[0]].get()
    
    query_cols = [c if c != "CurrentMileage" else "CurrentMilieage" for c in cols]
    update_cols = query_cols[1:]
    
    set_clause = ", ".join([f"{c} = ?" for c in update_cols])
    values = [edit_entries[col].get() for col in cols[1:]]
    values.append(pk_val)
    
    db_path = get_db_path()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {query_cols[0]} = ?", values)
        conn.commit()
        conn.close()
        status_label.configure(text="Record saved successfully!", text_color="#3D7BFF")
    except sqlite3.Error as e:
        status_label.configure(text=f"Error saving: {e}", text_color=DANGER)

for label, color in [("Delete", DANGER), ("Paste", PANEL),
                      ("Copy", PANEL), ("Save", ACCENT)]:
    btn = ctk.CTkButton(edit_bottom, text=label, width=90, height=28,
                  fg_color=color, text_color=TEXT,
                  hover_color=BORDER, corner_radius=6,
                  font=("Arial", 11),
                  command=lambda l=label: save_record() if l == "Save" else None)
    btn.pack(side="right", padx=4, pady=6)

# ── WIRE EDIT BUTTON ──
edit_record_btn.configure(command=show_edit)

# ── START ──
show_landing()
app.mainloop()
