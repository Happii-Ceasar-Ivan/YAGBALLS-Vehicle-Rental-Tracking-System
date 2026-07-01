import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkfont
from PIL import Image
import sys
import os
import sqlite3
import time
import db_mapper
import json
import shutil
from datetime import datetime

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def backup_db():
    dialog = ctk.CTkInputDialog(text="Enter a name for this backup (optional):", title="Backup Database")
    custom_name = dialog.get_input()
    if custom_name is None:
        return  # User cancelled

    db_path = get_db_path()
    db_dir = os.path.dirname(db_path)
    backups_dir = os.path.join(db_dir, "backups")
    if not os.path.exists(backups_dir):
        os.makedirs(backups_dir)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    custom_suffix = ""
    if custom_name.strip() != "":
        # sanitize name to prevent file path issues
        safe_name = "".join(c if c.isalnum() else "_" for c in custom_name.strip())
        custom_suffix = f"_{safe_name}"

    backup_filename = f"yb_rental_backup_{timestamp}{custom_suffix}.db"
    backup_path = os.path.join(backups_dir, backup_filename)
    
    try:
        shutil.copy2(db_path, backup_path)
        messagebox.showinfo("Backup Successful", f"Database safely backed up to:\n{backup_filename}")
    except Exception as e:
        messagebox.showerror("Backup Failed", f"Failed to backup database:\n{e}")

def restore_db():
    from tkinter import filedialog
    db_path = get_db_path()
    db_dir = os.path.dirname(db_path)
    backups_dir = os.path.join(db_dir, "backups")
    if not os.path.exists(backups_dir):
        os.makedirs(backups_dir)
        
    filepath = filedialog.askopenfilename(initialdir=backups_dir, filetypes=[("SQLite DB", "*.db")], title="Select Backup to Restore")
    if filepath and os.path.exists(filepath):
        confirm = messagebox.askyesno("Confirm Restore", "Are you sure you want to restore this backup?\n\nWARNING: All current data will be OVERWRITTEN and cannot be recovered! This is permanent.")
        if confirm:
            try:
                shutil.copy2(filepath, db_path)
                messagebox.showinfo("Restore Successful", "Database restored successfully! Reloading data...")
                table_str = records_label.cget("text")
                if "|" in table_str:
                    apply_filters()
            except Exception as e:
                messagebox.showerror("Restore Failed", f"Failed to restore database:\n{e}")


def auto_backup_for_undo():
    db_path = get_db_path()
    db_dir = os.path.dirname(db_path)
    backups_dir = os.path.join(db_dir, "backups")
    if not os.path.exists(backups_dir):
        os.makedirs(backups_dir)
        
    undo_path = os.path.join(backups_dir, ".yb_rental_undo_state.db")
    
    try:
        shutil.copy2(db_path, undo_path)
    except Exception as e:
        print("Silent undo backup failed:", e)


def undo_last_action():
    db_path = get_db_path()
    db_dir = os.path.dirname(db_path)
    undo_path = os.path.join(db_dir, "backups", ".yb_rental_undo_state.db")
    
    if not os.path.exists(undo_path):
        messagebox.showinfo("Undo Unavailable", "There is no previous action to undo.")
        return
        
    try:
        shutil.copy2(undo_path, db_path)
        messagebox.showinfo("Undo Successful", "Successfully reverted to the previous database state.")
        table_str = records_label.cget("text")
        if "|" in table_str:
            apply_filters()
    except Exception as e:
        messagebox.showerror("Undo Failed", f"Failed to undo last action:\n{e}")


def get_db_path():
    """ Determine the database path robustly for both script and .exe modes """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_dir = os.path.dirname(sys.executable)
        # If the exe is inside a "dist" folder, go up two levels
        if os.path.basename(base_dir).lower() == 'dist':
            path = os.path.join(base_dir, "..", "..",
                                "YB Rental Database FIle", "yb_rental.db")
        else:
            path = os.path.join(
                base_dir, "..", "YB Rental Database FIle", "yb_rental.db")
    else:
        # Running as a python script
        path = os.path.join(os.path.dirname(os.path.abspath(
            __file__)), "..", "YB Rental Database FIle", "yb_rental.db")
    return os.path.abspath(path)


def get_filters_path():
    """ Determine the filters path robustly for both script and .exe modes """
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        if os.path.basename(base_dir).lower() == 'dist':
            path = os.path.join(base_dir, "..", "..", "Filters")
        else:
            path = os.path.join(base_dir, "..", "Filters")
    else:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Filters")
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return os.path.abspath(path)


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── COLORS ──
BG = "#0A0B0D"
SURFACE = "#111318"
PANEL = "#181C24"
BORDER = "#252B38"
ACCENT = "#3D7BFF"
TEXT = "#E8EAF0"
TEXT_DIM = "#7A8299"
DANGER = "#E84040"

TABLE_COLUMNS = {
    "Branches":           ("Branch ID", "Branch Name", "Street", "Barangay", "City", "Province", "Phone"),
    "Vehicle_Categories": ("Category ID", "Category Name", "Daily Rate", "Overdue Rate Per Hour"),
    "Vehicle_Models":     ("Model ID", "Brand", "Model Name", "Fuel Type", "Transmission", "Category Name"),
    "Vehicles":           ("Vehicle ID", "Model", "License Plate", "Current Mileage", "Status", "Current Branch"),
    "Customers":          ("Customer ID", "Customer Name", "Email", "Phone No.", "License No.", "Is Active?"),
    "Rentals":            ("Rental ID", "Handled By", "Customer Name", "Vehicle ID", "Pickup Branch", "Dropoff Branch", "RentedOn", "ExpectedReturn", "ActualReturn", "StartMileage", "EndMileage", "Status"),
    "Payments":           ("Payment ID", "Rental ID", "Paid On", "Base Amount", "Penalty Amount", "Total Amount", "Payment Method"),
    "Maintenance_Logs":   ("Log ID", "Vehicle ID", "Start Date", "End Date", "Cost", "Description", "Status"),
    "Damage_Reports":     ("Report ID", "Rental ID", "Incident Date", "Description", "Est. Repair Cost", "Status"),
    "Employees":          ("Employee ID", "Employee Name", "Email", "Role", "Branch Assigned", "Supervisor Name"),
}

TABLES = list(TABLE_COLUMNS.keys())

def validate_inputs(cols, values):
    """ Validates user inputs. Raises ValueError if validation fails. """
    numeric_cols = {"Daily Rate", "Overdue Rate Per Hour", "Current Mileage", 
                    "StartMileage", "EndMileage", "Base Amount", "Penalty Amount", 
                    "Total Amount", "Cost", "Est. Repair Cost"}
    phone_cols = {"Phone", "Phone No."}
    
    for col, val in zip(cols[1:], values):
        val_str = str(val).strip()
        if val_str == "" or val_str.lower() == "none":
            continue
        if col in numeric_cols:
            try:
                float(val_str)
            except ValueError:
                raise ValueError(f"'{col}' must be a valid number.")
        if col in phone_cols:
            allowed = set("0123456789+- ()")
            if not all(c in allowed for c in val_str):
                raise ValueError(f"'{col}' contains invalid characters. Only numbers and basic symbols are allowed.")

app = ctk.CTk()
app.title("YB Vehicle Rental System")
app.geometry("1280x720")
app.resizable(True, True)
app.minsize(1280, 720)
app.configure(fg_color=BG)

logo_img_large = ctk.CTkImage(Image.open(
    resource_path("yblogo.png")), size=(220, 88))
logo_img_small = ctk.CTkImage(Image.open(
    resource_path("yblogo.png")), size=(80, 32))

# ════════════════════════════════════════
#  SCREENS
# ════════════════════════════════════════

landing_frame = ctk.CTkFrame(app, fg_color=BG, corner_radius=0)
main_frame = ctk.CTkFrame(app, fg_color=BG, corner_radius=0)


def show_landing():
    main_frame.place_forget()
    landing_frame.place(x=0, y=0, relwidth=1, relheight=1)


def show_main():
    # Run overdue automation invisibly on boot
    db_mapper.auto_update_overdue(get_db_path())
    
    # Run automation sweep for missed completed rentals
    fixes = db_mapper.run_automation_sweep(get_db_path())
    if fixes > 0:
        messagebox.showinfo("Auto-Reconciler", f"Detected missed automations on startup.\nAutomatically fixed {fixes} missing payment/vehicle update(s)!")
    
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

# Edit Record button removed

db_editor_btn = ctk.CTkButton(navbar, text="Database Editor", width=140, height=32,
                              fg_color=ACCENT, text_color=TEXT, hover_color="#2D6AEF",
                              corner_radius=6)
db_editor_btn.pack(side="right", padx=6, pady=8)

backup_btn = ctk.CTkButton(navbar, text="Backup DB", width=100, height=32,
                           fg_color=PANEL, text_color=TEXT_DIM, hover_color=BORDER,
                           corner_radius=6, command=backup_db)
backup_btn.pack(side="right", padx=6, pady=8)

restore_btn = ctk.CTkButton(navbar, text="Restore DB", width=100, height=32,
                            fg_color=PANEL, text_color=TEXT_DIM, hover_color=BORDER,
                            corner_radius=6, command=restore_db)
restore_btn.pack(side="right", padx=6, pady=8)

undo_btn = ctk.CTkButton(navbar, text="Undo Last Action", width=130, height=32,
                         fg_color=PANEL, text_color=TEXT_DIM, hover_color=BORDER,
                         corner_radius=6, command=undo_last_action)
undo_btn.pack(side="right", padx=6, pady=8)

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

# Condition tracking
condition_rows = []

def repack_conditions():
    num_rows = len(condition_rows)
    if num_rows == 0:
        filter_conditions_frame.pack_forget()
    else:
        new_height = min(num_rows, 5) * 35
        filter_conditions_frame.configure(height=new_height)
        filter_conditions_frame.pack(fill="x", padx=10, pady=(0,8), after=filter_top)
            
    for i, row in enumerate(condition_rows):
        row['frame'].pack_forget()
        row['frame'].pack(fill="x", pady=2)
        
        if i == 0:
            row['logic_menu'].set("")
            row['logic_menu'].configure(state="disabled")
        else:
            row['logic_menu'].configure(state="normal")
            if row['logic_menu'].get() == "":
                row['logic_menu'].set("And")

def add_condition_row(selected_attr):
    if not selected_attr or selected_attr == "Add Condition":
        return
    
    # reset menu back to default text
    add_condition_var.set("Add Condition")

    row_frame = ctk.CTkFrame(filter_conditions_frame, fg_color="transparent")
    row_frame.pack(fill="x", pady=2)
    
    # Checkbox
    chk_var = ctk.BooleanVar(value=True)
    chk = ctk.CTkCheckBox(row_frame, text="", variable=chk_var, width=24)
    chk.pack(side="left", padx=5)

    def move_up():
        idx = condition_rows.index(row_data)
        if idx > 0:
            condition_rows[idx], condition_rows[idx-1] = condition_rows[idx-1], condition_rows[idx]
            repack_conditions()

    def move_down():
        idx = condition_rows.index(row_data)
        if idx < len(condition_rows) - 1:
            condition_rows[idx], condition_rows[idx+1] = condition_rows[idx+1], condition_rows[idx]
            repack_conditions()

    # Up/Down Arrows
    arrow_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
    arrow_frame.pack(side="left", padx=5)
    
    up_btn = ctk.CTkButton(arrow_frame, text="▲", width=20, height=14, fg_color=PANEL, hover_color=BORDER, command=move_up, font=("Arial", 10))
    up_btn.pack(side="top", pady=(0, 1))
    
    down_btn = ctk.CTkButton(arrow_frame, text="▼", width=20, height=14, fg_color=PANEL, hover_color=BORDER, command=move_down, font=("Arial", 10))
    down_btn.pack(side="bottom")

    # Logical Operator (Hide for the very first condition visually, or just disable)
    logic_var = ctk.StringVar(value="And")
    logic_menu = ctk.CTkOptionMenu(row_frame, values=["And", "Or"], variable=logic_var, width=60, height=28, fg_color=PANEL)
    if len(condition_rows) == 0:
        logic_menu.set("")
        logic_menu.configure(state="disabled")
    logic_menu.pack(side="left", padx=5)

    # Attribute Label
    attr_label = ctk.CTkLabel(row_frame, text=selected_attr, width=120, anchor="w", text_color=TEXT)
    attr_label.pack(side="left", padx=5)

    # Determine numerical columns
    monetary_cols = {"Daily Rate", "Overdue Rate Per Hour", "Cost", "Base Amount", "Total Amount", "Penalty Amount", "Est. Repair Cost"}
    is_numerical = "ID" in selected_attr or "Mileage" in selected_attr or "Age" in selected_attr or selected_attr in monetary_cols

    ops = ["Is", "Is Not", "Contains"]
    if is_numerical:
        ops = ["Is", "Is Not", ">", "<", ">=", "<="]
    
    op_var = ctk.StringVar(value="Is")
    op_menu = ctk.CTkOptionMenu(row_frame, values=ops, variable=op_var, width=100, height=28, fg_color=PANEL)
    op_menu.pack(side="left", padx=5)

    # Value Entry
    val_entry = ctk.CTkEntry(row_frame, height=28, fg_color=PANEL, border_width=1)
    val_entry.pack(side="left", expand=True, fill="x", padx=5)

    def remove_this():
        row_frame.destroy()
        condition_rows.remove(row_data)
        repack_conditions()

    # Remove button
    rm_btn = ctk.CTkButton(row_frame, text="X", width=28, height=28, fg_color=DANGER, hover_color="#C03030", command=remove_this)
    rm_btn.pack(side="left", padx=5)

    row_data = {
        'frame': row_frame,
        'chk_var': chk_var,
        'logic_var': logic_var,
        'logic_menu': logic_menu,
        'attribute': selected_attr,
        'op_var': op_var,
        'val_entry': val_entry
    }
    condition_rows.append(row_data)
    repack_conditions()

def apply_filters():
    table_str = records_label.cget("text")
    if "|" not in table_str: return
    table_name = table_str.split("|")[0].replace("Showing records for:", "").strip()

    where_parts = []
    params = []
    
    first = True
    for row in condition_rows:
        if not row['chk_var'].get():
            continue # skipped if unchecked
        
        logic = row['logic_var'].get().upper()
        if first:
            logic = ""
            first = False
            
        attr = f'"{row["attribute"]}"'
        op = row['op_var'].get()
        val = row['val_entry'].get()

        if op == "Is":
            sql_op = "="
            params.append(val)
        elif op == "Is Not":
            sql_op = "!="
            params.append(val)
        elif op == "Contains":
            sql_op = "LIKE"
            params.append(f"%{val}%")
        else: # >, <, >=, <=
            sql_op = op
            params.append(val)
            
        where_parts.append(f"{logic} {attr} {sql_op} ?".strip())
        
    where_clause = ""
    if where_parts:
        where_clause = "WHERE " + " ".join(where_parts)
        
    load_table(table_name, where_clause, tuple(params))

def clear_filters():
    for row in condition_rows:
        row['frame'].destroy()
    condition_rows.clear()
    repack_conditions()
    
    table_str = records_label.cget("text")
    if "|" in table_str:
        table_name = table_str.split("|")[0].replace("Showing records for:", "").strip()
        load_table(table_name)

def save_filters():
    filters = []
    for row in condition_rows:
        filters.append({
            "chk": row['chk_var'].get(),
            "logic": row['logic_var'].get(),
            "attribute": row["attribute"],
            "op": row['op_var'].get(),
            "val": row['val_entry'].get()
        })
    from tkinter import filedialog
    filepath = filedialog.asksaveasfilename(initialdir=get_filters_path(), defaultextension=".json", filetypes=[("JSON files", "*.json")], title="Save Filters")
    if filepath:
        with open(filepath, 'w') as f:
            json.dump(filters, f)

def load_filters():
    from tkinter import filedialog
    filepath = filedialog.askopenfilename(initialdir=get_filters_path(), filetypes=[("JSON files", "*.json")], title="Load Filters")
    if filepath and os.path.exists(filepath):
        with open(filepath, 'r') as f:
            filters = json.load(f)
        
        # clear existing
        for row in condition_rows:
            row['frame'].destroy()
        condition_rows.clear()
        
        for f_data in filters:
            add_condition_row(f_data["attribute"])
            last_row = condition_rows[-1]
            last_row['chk_var'].set(f_data["chk"])
            last_row['logic_var'].set(f_data["logic"])
            last_row['op_var'].set(f_data["op"])
            last_row['val_entry'].insert(0, f_data["val"])
            
        apply_filters()

add_condition_var = ctk.StringVar(value="Add Condition")
add_condition_menu = ctk.CTkOptionMenu(filter_top, values=[], variable=add_condition_var, width=140, height=28, fg_color=PANEL, command=add_condition_row)
add_condition_menu.pack(side="left", padx=4)

filter_btn = ctk.CTkButton(filter_top, text="Save Filters", width=90, height=28, fg_color=PANEL, text_color=TEXT_DIM, hover_color=BORDER, command=save_filters)
filter_btn.pack(side="left", padx=4)

load_filter_btn = ctk.CTkButton(filter_top, text="Load Filters", width=90, height=28, fg_color=PANEL, text_color=TEXT_DIM, hover_color=BORDER, command=load_filters)
load_filter_btn.pack(side="left", padx=4)

clear_btn = ctk.CTkButton(filter_top, text="Clear", width=80, height=28, fg_color=PANEL, text_color=TEXT_DIM, hover_color=BORDER, command=clear_filters)
clear_btn.pack(side="left", padx=4)

apply_btn = ctk.CTkButton(filter_top, text="Apply Filter", width=100, height=28, fg_color=ACCENT, text_color=TEXT, command=apply_filters)
apply_btn.pack(side="left", padx=4)

filter_conditions_frame = ctk.CTkScrollableFrame(filter_frame, height=140, fg_color="transparent")
filter_conditions_frame.pack(fill="x", padx=10, pady=(0,8))
repack_conditions()

# ── TREEVIEW STYLE ──
style = ttk.Style()
style.theme_use("default")

# Added borderwidth=1 and relief="solid" for the outer border
style.configure("Custom.Treeview",
                background=SURFACE, foreground=TEXT,
                fieldbackground=SURFACE,
                borderwidth=1, relief="solid", bordercolor=BORDER,
                rowheight=36, font=("Arial", 11))

# Added borderwidth=1 and relief="solid" for column heading borders
style.configure("Custom.Treeview.Heading",
                background=PANEL, foreground=TEXT_DIM,
                borderwidth=1, relief="solid", bordercolor=BORDER,
                font=("Arial", 10, "bold"))

style.map("Custom.Treeview",
          background=[("selected", ACCENT)],
          foreground=[("selected", TEXT)])
# ── DATA GRID ──
grid_frame = ctk.CTkFrame(main_content, fg_color=SURFACE, corner_radius=8)
grid_frame.pack(fill="both", expand=True, pady=(0, 8))

tree_scroll_y = ctk.CTkScrollbar(grid_frame, orientation="vertical")
tree_scroll_y.pack(side="right", fill="y", pady=1)

tree_scroll_x = ctk.CTkScrollbar(grid_frame, orientation="horizontal")
tree_scroll_x.pack(side="bottom", fill="x", padx=1)

tree = ttk.Treeview(grid_frame, style="Custom.Treeview",
                    show="headings", selectmode="extended",
                    yscrollcommand=tree_scroll_y.set,
                    xscrollcommand=tree_scroll_x.set)

tree_scroll_y.configure(command=tree.yview)
tree_scroll_x.configure(command=tree.xview)
tree.pack(fill="both", expand=True, padx=1, pady=1)

# ── BOTTOM BAR ──
bottom = ctk.CTkFrame(main_content, height=40,
                      fg_color=SURFACE, corner_radius=8)
bottom.pack(fill="x", side="bottom")
bottom.pack_propagate(False)

records_label = ctk.CTkLabel(bottom, text="Select a table.",
                             text_color=TEXT_DIM, font=("Arial", 11))
records_label.pack(side="left", padx=12)


def add_record():
    dialog = ctk.CTkInputDialog(text="How many records do you want to add?\n(Leave blank or enter 1 for single add)", title="Add Records")
    count_str = dialog.get_input()
    if count_str is None:
        return
    
    count = 1
    if count_str.strip() != "":
        try:
            count = int(count_str.strip())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")
            return

    main_frame.place_forget()
    if count > 1:
        multi_edit_frame.place(x=0, y=0, relwidth=1, relheight=1)
        populate_multi_edit_form(add_count=count)
    else:
        edit_frame.place(x=0, y=0, relwidth=1, relheight=1)
        populate_edit_form(blank=True)


def duplicate_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a record to duplicate.")
        return
        
    table_str = records_label.cget("text")
    if "|" not in table_str: return
    table_name = table_str.split("|")[0].replace("Showing records for:", "").strip()
    
    allowed_tables = ["Vehicle_Categories", "Vehicle_Models"]
    if table_name not in allowed_tables:
        reasons = {
            "Branches": "Physical branches cannot be duplicated.",
            "Vehicles": "License Plates must be entirely unique.",
            "Customers": "Emails and Driver's Licenses must be entirely unique.",
            "Employees": "Emails and Employee details must be entirely unique.",
            "Rentals": "Rental contracts represent specific time-bound transactions.",
            "Payments": "Financial transactions cannot be duplicated.",
            "Maintenance_Logs": "Maintenance logs are specific to exact timestamps.",
            "Damage_Reports": "Damage incidents are unique events."
        }
        reason = reasons.get(table_name, "Data integrity rules prevent duplicating this record.")
        messagebox.showerror("Cannot Duplicate", f"Cannot duplicate {table_name}!\n\n{reason}")
        return
        
    cols = TABLE_COLUMNS.get(table_name, ())
    row_values = tree.item(selected[0])['values']
    
    # Exclude PK
    values_to_insert = row_values[1:]
    db_path = get_db_path()
    try:
        db_mapper.insert_record_to_db(db_path, table_name, cols, values_to_insert)
        apply_filters()
        messagebox.showinfo("Success", "Record duplicated successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to duplicate record:\n{e}")


def remove_record():
    selected = tree.selection()
    if not selected:
        return

    table_str = records_label.cget("text")
    if "|" not in table_str:
        return
    table_name = table_str.split("|")[0].replace(
        "Showing records for:", "").strip()
    cols = TABLE_COLUMNS.get(table_name, ())
    if not cols:
        return

    pk_col = cols[0]
    is_multi = len(selected) > 1

    dialog = ctk.CTkToplevel(app)
    dialog.title("Confirm Delete")
    dialog.geometry("360x160")
    dialog.resizable(False, False)
    dialog.configure(fg_color=SURFACE)
    dialog.grab_set()

    if is_multi:
        prompt_text = f"Delete {len(selected)} records from {table_name}?"
    else:
        values = tree.item(selected[0])["values"]
        pk_val = values[0]
        prompt_text = f"Delete record with {pk_col} = {pk_val}?"

    ctk.CTkLabel(dialog,
                 text=prompt_text,
                 font=("Arial", 13), text_color=TEXT,
                 wraplength=320).pack(pady=(28, 8), padx=20)
    ctk.CTkLabel(dialog, text="This action can be reverted using the Undo button.",
                 font=("Arial", 11), text_color=TEXT_DIM).pack()

    btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
    btn_row.pack(pady=20)

    def confirm_delete():
        db_path = get_db_path()
        auto_backup_for_undo()
        try:
            for sel in selected:
                values = tree.item(sel)["values"]
                pk_val = values[0]
                db_mapper.delete_record_from_db(db_path, table_name, pk_col, pk_val)
                tree.delete(sel)
            remaining = len(tree.get_children())
            records_label.configure(
                text=f"Showing records for: {table_name}  |  {remaining} total records", text_color=TEXT_DIM)
            dialog.destroy()
        except Exception as e:
            dialog.destroy()
            records_label.configure(
                text=f"Error deleting: {e}", text_color=DANGER)

    ctk.CTkButton(btn_row, text="Cancel", width=100, height=32,
                  fg_color=PANEL, text_color=TEXT_DIM, hover_color=BORDER,
                  corner_radius=6, command=dialog.destroy).pack(side="left", padx=8)
    ctk.CTkButton(btn_row, text="Delete", width=100, height=32,
                  fg_color=DANGER, text_color=TEXT, hover_color="#C03030",
                  corner_radius=6, command=confirm_delete).pack(side="left", padx=8)


for label, color in [("Remove", DANGER), ("Duplicate", PANEL),
                     ("Add", PANEL), ("Edit", ACCENT)]:
    if label == "Edit":
        cmd = lambda: show_edit()
    elif label == "Add":
        cmd = add_record
    elif label == "Duplicate":
        cmd = duplicate_record
    elif label == "Remove":
        cmd = remove_record

    b = ctk.CTkButton(bottom, text=label, width=90, height=28,
                      fg_color=color, text_color=TEXT,
                      hover_color=BORDER, corner_radius=6,
                      font=("Arial", 11), command=cmd)
    b.pack(side="right", padx=4, pady=6)

# ── TABLE LOADER ──


def load_table(name, where_clause="", query_params=()):
    for btn in table_buttons:
        if btn.cget("text") == name:
            btn.configure(fg_color=ACCENT, text_color=TEXT)
        else:
            btn.configure(fg_color="transparent", text_color=TEXT_DIM)

    cols = TABLE_COLUMNS.get(name, ("ID", "Value"))
    tree["columns"] = cols
    
    # Update filter menu values
    add_condition_menu.configure(values=list(cols))

    # Define which columns contain monetary values
    monetary_cols = {"Daily Rate", "Overdue Rate Per Hour", "Cost", "Base Amount",
                     "Total Amount", "Penalty Amount", "Est. Repair Cost"
                     }

    # Configure colors for alternating rows
    tree.tag_configure("odd", background=SURFACE)  # "#111318"
    tree.tag_configure("even", background=PANEL)  # "#181C24"
    for row in tree.get_children():
        tree.delete(row)

    db_path = get_db_path()
    try:
        conn = None
        # Use a retry loop to prevent "database is locked/unable to open" errors
        # caused by Antivirus or Cloud Sync engines scanning the file after changes
        for attempt in range(10):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                safe_cols = [f'"{col}"' for col in cols]
                # We prefix 'v_' to use the SQL Views from Arthur
                # (e.g. v_Vehicles instead of Vehicles) for better formatting
                view_name = f"v_{name}"
                query = f"SELECT {', '.join(safe_cols)} FROM {view_name} {where_clause}"

                cursor.execute(query, query_params)
                rows = cursor.fetchall()
                break
            except sqlite3.OperationalError as e:
                if attempt == 9:
                    raise e
                time.sleep(0.5)

        # Calculate dynamic widths for each column based on data
        font = tkfont.Font(family="Arial", size=11)
        header_font = tkfont.Font(family="Arial", size=10, weight="bold")

        col_widths = {}
        for i, col in enumerate(cols):
            max_w = header_font.measure(col) + 40  # 40px padding
            for row in rows:
                val = str(row[i]) if row[i] is not None else "None"
                if col in monetary_cols:
                    val += "    "  # Add padding for width calculation
                w = font.measure(val) + 40
                if w > max_w:
                    max_w = w
            col_widths[col] = min(max_w, 800)  # Cap width at 800px

        # Configure columns with dynamic widths AND stretch to fill empty space
        for col in cols:
            tree.heading(col, text=col)
            # Right-align ("e" for east) if monetary, otherwise left-align ("w" for west)
            if col in monetary_cols:
                tree.column(
                    col, width=col_widths[col], stretch=True, anchor="e", minwidth=col_widths[col])
            else:
                tree.column(
                    col, width=col_widths[col], stretch=True, anchor="w", minwidth=col_widths[col])

        for i, row in enumerate(rows):
            display_row = []
            for j, val in enumerate(row):
                str_val = str(val) if val is not None else "None"
                if cols[j] in monetary_cols:
                    str_val += "    "  # Pad monetary columns so they don't touch the next column
                display_row.append(str_val)

            # Assign tag based on odd/even row
            row_tag = "even" if i % 2 == 0 else "odd"
            tree.insert("", "end", tags=(row_tag,), values=display_row)

        if conn:
            conn.close()
        records_label.configure(
            text=f"Showing records for: {name}  |  {len(rows)} total records", text_color=TEXT_DIM)
    except sqlite3.Error as e:
        records_label.configure(text=f"Error loading {name} at {db_path}: {e}", text_color=DANGER)


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


# ════════════════════════════════════════
#  MULTI-EDIT RECORD SCREEN
# ════════════════════════════════════════
multi_edit_frame = ctk.CTkFrame(app, fg_color=BG, corner_radius=0)

def show_main_from_multi_edit():
    multi_edit_frame.place_forget()
    main_frame.place(x=0, y=0, relwidth=1, relheight=1)
    table_str = records_label.cget("text")
    if "|" in table_str:
        apply_filters()

multi_edit_navbar = ctk.CTkFrame(multi_edit_frame, height=48, fg_color=SURFACE, corner_radius=0)
multi_edit_navbar.pack(fill="x", side="top")
multi_edit_navbar.pack_propagate(False)

ctk.CTkLabel(multi_edit_navbar, image=logo_img_small, text="").pack(side="left", padx=12, pady=8)
ctk.CTkButton(multi_edit_navbar, text="Cancel", width=100, height=32,
              fg_color=PANEL, text_color=TEXT_DIM, hover_color=BORDER,
              corner_radius=6, command=show_main_from_multi_edit).pack(side="right", padx=6, pady=8)
ctk.CTkLabel(multi_edit_navbar, text="Multi-Edit Mode", text_color=TEXT, font=("Arial", 16, "bold")).pack(side="left", padx=12)

multi_edit_body = ctk.CTkFrame(multi_edit_frame, fg_color=BG, corner_radius=0)
multi_edit_body.pack(fill="both", expand=True, padx=24, pady=(20, 0))

multi_form_inner = ctk.CTkScrollableFrame(multi_edit_body, fg_color=SURFACE, corner_radius=8)
multi_form_inner.pack(fill="both", expand=True, pady=(0, 8))

multi_edit_entries = []

def populate_multi_edit_form(selected=None, add_count=0):
    for widget in multi_form_inner.winfo_children():
        widget.destroy()
    multi_edit_entries.clear()

    table_str = records_label.cget("text")
    if "|" not in table_str: return
    table_name = table_str.split("|")[0].replace("Showing records for:", "").strip()
    cols = TABLE_COLUMNS.get(table_name, ())
    if not cols: return

    header_frame = ctk.CTkFrame(multi_form_inner, fg_color="transparent")
    header_frame.pack(fill="x", pady=(0, 10))
    for col in cols:
        ctk.CTkLabel(header_frame, text=col, font=("Arial", 12, "bold"), text_color=TEXT, width=140, anchor="w").pack(side="left", padx=5)

    if add_count > 0:
        for _ in range(add_count):
            row_frame = ctk.CTkFrame(multi_form_inner, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            row_dict = {"_pk_val": ""}
            
            for i, col in enumerate(cols):
                entry = ctk.CTkEntry(row_frame, width=140, height=28, fg_color=PANEL, text_color=TEXT, border_width=1)
                entry.pack(side="left", padx=5)
                if i == 0:
                    entry.configure(placeholder_text="Auto-assigned", state="disabled", fg_color=BG, text_color=TEXT_DIM)
                row_dict[col] = entry
            multi_edit_entries.append(row_dict)
    elif selected:
        for sel_id in selected:
            values = tree.item(sel_id)["values"]
            row_frame = ctk.CTkFrame(multi_form_inner, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            row_dict = {"_pk_val": values[0]}
            
            for i, col in enumerate(cols):
                val = "" if i >= len(values) else values[i]
                if val is None: val = ""
                entry = ctk.CTkEntry(row_frame, width=140, height=28, fg_color=PANEL, text_color=TEXT, border_width=1)
                entry.pack(side="left", padx=5)
                entry.insert(0, str(val))
                if i == 0:
                    entry.configure(state="disabled", fg_color=BG, text_color=TEXT_DIM)
                row_dict[col] = entry
            multi_edit_entries.append(row_dict)

multi_edit_bottom = ctk.CTkFrame(multi_edit_frame, height=40, fg_color=SURFACE, corner_radius=8)
multi_edit_bottom.pack(fill="x", side="bottom", padx=12, pady=(0, 12))
multi_edit_bottom.pack_propagate(False)

multi_status_label = ctk.CTkLabel(multi_edit_bottom, text="Edit multiple records simultaneously.", text_color=TEXT_DIM, font=("Arial", 11))
multi_status_label.pack(side="left", padx=12)

def save_multi_edit():
    table_str = records_label.cget("text")
    if "|" not in table_str: return
    table_name = table_str.split("|")[0].replace("Showing records for:", "").strip()
    cols = TABLE_COLUMNS.get(table_name, ())
    db_path = get_db_path()
    
    auto_backup_for_undo()
    try:
        for row_dict in multi_edit_entries:
            pk_val = row_dict["_pk_val"]
            values = [row_dict[col].get() for col in cols[1:]]
            validate_inputs(cols, values)
            if pk_val == "":
                db_mapper.insert_record_to_db(db_path, table_name, cols, values)
            else:
                db_mapper.save_record_to_db(db_path, table_name, cols, values, pk_val)
        multi_status_label.configure(text=f"Successfully updated {len(multi_edit_entries)} records!", text_color="#3D7BFF")
        app.after(1000, show_main_from_multi_edit)
    except Exception as e:
        multi_status_label.configure(text=f"Error saving: {e}", text_color=DANGER)

ctk.CTkButton(multi_edit_bottom, text="Save All", width=90, height=28, fg_color=ACCENT, text_color=TEXT, hover_color=BORDER, corner_radius=6, command=save_multi_edit).pack(side="right", padx=4, pady=6)


def show_edit():
    selected = tree.selection()
    if not selected:
        return
    main_frame.place_forget()
    if len(selected) > 1:
        multi_edit_frame.place(x=0, y=0, relwidth=1, relheight=1)
        populate_multi_edit_form(selected)
    else:
        edit_frame.place(x=0, y=0, relwidth=1, relheight=1)
        populate_edit_form()


def show_main_from_edit():
    edit_frame.place_forget()
    main_frame.place(x=0, y=0, relwidth=1, relheight=1)

    table_str = records_label.cget("text")
    if "|" in table_str:
        apply_filters()


# ── EDIT NAVBAR ──
edit_navbar = ctk.CTkFrame(edit_frame, height=48,
                           fg_color=SURFACE, corner_radius=0)
edit_navbar.pack(fill="x", side="top")
edit_navbar.pack_propagate(False)

edit_nav_logo = ctk.CTkLabel(edit_navbar, image=logo_img_small, text="")
edit_nav_logo.pack(side="left", padx=12, pady=8)

ctk.CTkButton(edit_navbar, text="Load Database", width=130, height=32,
              fg_color=PANEL, text_color=TEXT_DIM, hover_color=BORDER,
              corner_radius=6, command=show_landing).pack(side="right", padx=6, pady=8)

# Edit Record button removed

ctk.CTkButton(edit_navbar, text="Database Editor", width=140, height=32,
              fg_color=PANEL, text_color=TEXT_DIM, hover_color=BORDER,
              corner_radius=6, command=show_main_from_edit).pack(side="right", padx=6, pady=8)

# ── EDIT BODY ──
edit_body = ctk.CTkFrame(edit_frame, fg_color=BG, corner_radius=0)
edit_body.pack(fill="both", expand=True, padx=24, pady=(20, 0))

form_frame = ctk.CTkFrame(edit_body, fg_color=SURFACE, corner_radius=8)
form_frame.pack(fill="both", expand=True, pady=(0, 8))

form_inner = ctk.CTkFrame(form_frame, fg_color="transparent")
form_inner.pack(fill="both", expand=True, padx=24, pady=20)

edit_entries = {}


def populate_edit_form(blank=False, duplicate=False):
    # Clear existing widgets
    for widget in form_inner.winfo_children():
        widget.destroy()
    edit_entries.clear()

    table_str = records_label.cget("text")
    if "|" not in table_str:
        return
    table_name = table_str.split("|")[0].replace(
        "Showing records for:", "").strip()
    cols = TABLE_COLUMNS.get(table_name, ())
    if not cols:
        return

    values = []
    if not blank:
        selected = tree.selection()
        if selected:
            values = tree.item(selected[0])["values"]

    # Two-column layout
    for i, col in enumerate(cols):
        row = i // 2
        col_pos = i % 2

        label = ctk.CTkLabel(form_inner, text=col,
                             font=("Arial", 12), text_color=TEXT_DIM,
                             anchor="w")
        label.grid(row=row, column=col_pos * 2, padx=(0, 12),
                   pady=10, sticky="w")

        val = ""
        if not blank and i < len(values):
            val = values[i]
        if duplicate and i == 0:
            val = ""

        is_pk = (i == 0)
        entry = ctk.CTkEntry(form_inner, width=480, height=34,
                             fg_color=PANEL, text_color=TEXT if not is_pk else TEXT_DIM,
                             border_color=BORDER, font=("Arial", 12))
        entry.grid(row=row, column=col_pos * 2 + 1,
                   padx=(0, 40), pady=10, sticky="ew")

        if is_pk and not blank and not duplicate:
            entry.insert(0, str(val))
            entry.configure(state="disabled")
        elif is_pk:
            entry.configure(placeholder_text="Auto-assigned", state="disabled")
        else:
            entry.insert(0, str(val))

        edit_entries[col] = entry

    # Configure grid columns
    form_inner.grid_columnconfigure(1, weight=1)
    form_inner.grid_columnconfigure(3, weight=1)
    form_inner.grid_columnconfigure(0, weight=1)
    form_inner.grid_columnconfigure(2, weight=1)


# ── EDIT BOTTOM BAR ──
edit_bottom = ctk.CTkFrame(edit_frame, height=40,
                           fg_color=SURFACE, corner_radius=8)
edit_bottom.pack(fill="x", side="bottom", padx=12, pady=(0, 12))
edit_bottom.pack_propagate(False)

status_label = ctk.CTkLabel(edit_bottom, text="Record is saved in the database.",
                            text_color=TEXT_DIM, font=("Arial", 11))
status_label.pack(side="left", padx=12)


def save_record():
    table_str = records_label.cget("text")
    if "|" not in table_str:
        return

    table_name = table_str.split("|")[0].replace(
        "Showing records for:", "").strip()
    cols = TABLE_COLUMNS.get(table_name, ())
    if not cols:
        return

    pk_entry = edit_entries[cols[0]]
    pk_val = pk_entry.get().strip()
    values = [edit_entries[col].get() for col in cols[1:]]

    db_path = get_db_path()
    auto_backup_for_undo()
    try:
        validate_inputs(cols, values)
        if pk_val:
            db_mapper.save_record_to_db(
                db_path, table_name, cols, values, pk_val)
        else:
            db_mapper.insert_record_to_db(db_path, table_name, cols, values)
        status_label.configure(
            text="Record saved successfully!", text_color="#3D7BFF")
        app.after(500, show_main_from_edit)
    except Exception as e:
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
# edit_record_btn removed

# ── START ──

def on_closing():
    if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
        app.destroy()

app.protocol("WM_DELETE_WINDOW", on_closing)

show_landing()
app.mainloop()
