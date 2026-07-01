import sqlite3
from datetime import datetime


def parse_id(s):
    try:
        return int(s.split('-')[-1])
    except:
        return None


def update_branches(cursor, values, raw_id):
    cursor.execute("UPDATE Branches SET BranchName=?, StreetAddress=?, Barangay=?, City=?, Province=?, Phone=? WHERE BranchID=?",
                   (*values, raw_id))


def update_vehicle_categories(cursor, values, raw_id):
    cursor.execute("UPDATE Vehicle_Categories SET CategoryName=?, DailyRate=?, OverdueRatePerHour=? WHERE CategoryID=?",
                   (*values, raw_id))


def update_vehicle_models(cursor, values, raw_id):
    cat = cursor.execute(
        "SELECT CategoryID FROM Vehicle_Categories WHERE CategoryName=?", (values[4],)).fetchone()
    cat_id = cat[0] if cat else None
    cursor.execute("UPDATE Vehicle_Models SET Brand=?, ModelName=?, FuelType=?, Transmission=?, CategoryID=? WHERE ModelID=?",
                   (values[0], values[1], values[2], values[3], cat_id, raw_id))


def update_vehicles(cursor, values, raw_id):
    model = cursor.execute(
        "SELECT ModelID FROM Vehicle_Models WHERE Brand || ' ' || ModelName = ?", (values[0],)).fetchone()
    model_id = model[0] if model else None
    branch = cursor.execute(
        "SELECT BranchID FROM Branches WHERE BranchName=?", (values[4],)).fetchone()
    branch_id = branch[0] if branch else None
    cursor.execute("UPDATE Vehicles SET ModelID=?, LicensePlate=?, CurrentMileage=?, Status=?, CurrentBranchID=? WHERE VehicleID=?",
                   (model_id, values[1], values[2], values[3], branch_id, raw_id))


def update_customers(cursor, values, raw_id):
    names = values[0].split(' ', 1)
    fname = names[0]
    lname = names[1] if len(names) > 1 else ""
    is_active = 1 if str(values[4]).lower() == 'yes' else 0
    cursor.execute("UPDATE Customers SET FirstName=?, LastName=?, Email=?, Phone=?, DriversLicense=?, IsActive=? WHERE CustomerID=?",
                   (fname, lname, values[1], values[2], values[3], is_active, raw_id))


def _handle_rental_automations(cursor, values, raw_id, vhc_id):
    status = str(values[10]).strip().lower()
    if status == 'completed':
        # 1. Update Vehicle Status & Mileage
        end_mileage = values[9] if (values[9] and str(values[9]).lower() != "none") else values[8]
        cursor.execute("UPDATE Vehicles SET CurrentMileage=?, Status='Available' WHERE VehicleID=?", (end_mileage, vhc_id))
        
        # 2. Calculate Penalties & Auto-Generate Payment Record
        rates = cursor.execute("""
            SELECT c.DailyRate, c.OverdueRatePerHour 
            FROM Vehicles v 
            JOIN Vehicle_Models m ON v.ModelID = m.ModelID 
            JOIN Vehicle_Categories c ON m.CategoryID = c.CategoryID 
            WHERE v.VehicleID = ?
        """, (vhc_id,)).fetchone()
        
        if rates:
            try:
                daily_rate = float(rates[0])
                overdue_rate = float(rates[1])
                
                def parse_dt(dt_str):
                    if not dt_str or str(dt_str).strip().lower() == "none": return None
                    s = str(dt_str).strip()
                    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", 
                                "%y-%m-%d %H:%M:%S", "%y-%m-%d %H:%M", "%y-%m-%d", 
                                "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M", "%m/%d/%Y",
                                "%m/%d/%y %H:%M:%S", "%m/%d/%y %H:%M", "%m/%d/%y"):
                        try: return datetime.strptime(s, fmt)
                        except ValueError: continue
                    raise ValueError(f"Invalid date format: {s}")
                
                rented_on = parse_dt(values[5])
                expected = parse_dt(values[6])
                
                actual_dt_str = values[7] if (values[7] and str(values[7]).lower() != "none") else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                actual = parse_dt(actual_dt_str)
                
                days_rented = (expected - rented_on).days
                if days_rented < 1: days_rented = 1
                
                base_amount = daily_rate * days_rented
                penalty_amount = 0.0
                
                if actual > expected:
                    diff = actual - expected
                    hours_overdue = diff.total_seconds() / 3600.0
                    penalty_amount = overdue_rate * hours_overdue
                    
                total_amount = base_amount + penalty_amount
                
                # Check if payment already exists
                existing = cursor.execute("SELECT PaymentID FROM Payments WHERE RentalID=?", (raw_id,)).fetchone()
                if existing:
                    cursor.execute("UPDATE Payments SET PaidOn=?, BaseAmount=?, PenaltyAmount=?, TotalAmount=?, PaymentMethod='Cash' WHERE RentalID=?",
                                   (actual_dt_str, round(base_amount, 2), round(penalty_amount, 2), round(total_amount, 2), raw_id))
                else:
                    cursor.execute("INSERT INTO Payments (RentalID, PaidOn, BaseAmount, PenaltyAmount, TotalAmount, PaymentMethod) VALUES (?, ?, ?, ?, ?, 'Cash')",
                                   (raw_id, actual_dt_str, round(base_amount, 2), round(penalty_amount, 2), round(total_amount, 2)))
            except Exception as e:
                print(f"Penalty automation failed: {e}")

def update_rentals(cursor, values, raw_id):
    emp = cursor.execute(
        "SELECT EmployeeID FROM Employees WHERE FirstName || ' ' || LastName = ?", (values[0],)).fetchone()
    emp_id = emp[0] if emp else None
    if emp_id is None: raise ValueError(f"Could not find Employee '{values[0]}'")
    
    cust = cursor.execute(
        "SELECT CustomerID FROM Customers WHERE FirstName || ' ' || LastName = ?", (values[1],)).fetchone()
    cust_id = cust[0] if cust else None
    if cust_id is None: raise ValueError(f"Could not find Customer '{values[1]}'")
    
    vhc_id = parse_id(values[2])
    pub = cursor.execute(
        "SELECT BranchID FROM Branches WHERE BranchName=?", (values[3],)).fetchone()
    pub_id = pub[0] if pub else None
    dob = cursor.execute(
        "SELECT BranchID FROM Branches WHERE BranchName=?", (values[4],)).fetchone()
    dob_id = dob[0] if dob else None
    
    cursor.execute("UPDATE Rentals SET EmployeeID=?, CustomerID=?, VehicleID=?, PickUpBranchID=?, DropOffBranchID=?, RentedOn=?, ExpectedReturn=?, ActualReturn=?, StartMileage=?, EndMileage=?, Status=? WHERE RentalID=?",
                   (emp_id, cust_id, vhc_id, pub_id, dob_id, values[5], values[6], values[7], values[8], values[9], values[10], raw_id))
                   
    # ── AUTOMATIONS ──
    _handle_rental_automations(cursor, values, raw_id, vhc_id)


def update_payments(cursor, values, raw_id):
    rnt_id = parse_id(values[0])
    cursor.execute("UPDATE Payments SET RentalID=?, PaidOn=?, BaseAmount=?, PenaltyAmount=?, TotalAmount=?, PaymentMethod=? WHERE PaymentID=?",
                   (rnt_id, values[1], values[2], values[3], values[4], values[5], raw_id))


def update_maintenance_logs(cursor, values, raw_id):
    vhc_id = parse_id(values[0])
    cursor.execute("UPDATE Maintenance_Logs SET VehicleID=?, StartDate=?, EndDate=?, Cost=?, Description=?, Status=? WHERE LogID=?",
                   (vhc_id, values[1], values[2], values[3], values[4], values[5], raw_id))


def update_damage_reports(cursor, values, raw_id):
    rnt_id = parse_id(values[0])
    cursor.execute("UPDATE Damage_Reports SET RentalID=?, IncidentDate=?, Description=?, EstimatedRepairCost=?, Status=? WHERE ReportID=?",
                   (rnt_id, values[1], values[2], values[3], values[4], raw_id))


def update_employees(cursor, values, raw_id):
    names = values[0].split(' ', 1)
    fname = names[0]
    lname = names[1] if len(names) > 1 else ""
    branch = cursor.execute(
        "SELECT BranchID FROM Branches WHERE BranchName=?", (values[3],)).fetchone()
    branch_id = branch[0] if branch else None
    sup = cursor.execute(
        "SELECT EmployeeID FROM Employees WHERE FirstName || ' ' || LastName = ?", (values[4],)).fetchone()
    sup_id = sup[0] if sup else None
    cursor.execute("UPDATE Employees SET FirstName=?, LastName=?, Email=?, Role=?, BranchID=?, SupervisorID=? WHERE EmployeeID=?",
                   (fname, lname, values[1], values[2], branch_id, sup_id, raw_id))


# Dictionary mapping table names to their respective update functions
TABLE_HANDLERS = {
    "Branches": update_branches,
    "Vehicle_Categories": update_vehicle_categories,
    "Vehicle_Models": update_vehicle_models,
    "Vehicles": update_vehicles,
    "Customers": update_customers,
    "Rentals": update_rentals,
    "Payments": update_payments,
    "Maintenance_Logs": update_maintenance_logs,
    "Damage_Reports": update_damage_reports,
    "Employees": update_employees
}


def insert_branches(cursor, values):
    cursor.execute(
        "INSERT INTO Branches (BranchName, StreetAddress, Barangay, City, Province, Phone) VALUES (?, ?, ?, ?, ?, ?)",
        tuple(values))


def insert_vehicle_categories(cursor, values):
    cursor.execute(
        "INSERT INTO Vehicle_Categories (CategoryName, DailyRate, OverdueRatePerHour) VALUES (?, ?, ?)",
        tuple(values))


def insert_vehicle_models(cursor, values):
    cat = cursor.execute(
        "SELECT CategoryID FROM Vehicle_Categories WHERE CategoryName=?", (values[4],)).fetchone()
    cat_id = cat[0] if cat else None
    cursor.execute(
        "INSERT INTO Vehicle_Models (Brand, ModelName, FuelType, Transmission, CategoryID) VALUES (?, ?, ?, ?, ?)",
        (values[0], values[1], values[2], values[3], cat_id))


def insert_vehicles(cursor, values):
    model = cursor.execute(
        "SELECT ModelID FROM Vehicle_Models WHERE Brand || ' ' || ModelName = ?", (values[0],)).fetchone()
    model_id = model[0] if model else None
    branch = cursor.execute(
        "SELECT BranchID FROM Branches WHERE BranchName=?", (values[4],)).fetchone()
    branch_id = branch[0] if branch else None
    cursor.execute(
        "INSERT INTO Vehicles (ModelID, LicensePlate, CurrentMileage, Status, CurrentBranchID) VALUES (?, ?, ?, ?, ?)",
        (model_id, values[1], values[2], values[3], branch_id))


def insert_customers(cursor, values):
    names = values[0].split(' ', 1)
    fname = names[0]
    lname = names[1] if len(names) > 1 else ""
    is_active = 1 if str(values[4]).lower() == 'yes' else 0
    cursor.execute(
        "INSERT INTO Customers (FirstName, LastName, Email, Phone, DriversLicense, LicenseExpiry, IsActive) VALUES (?, ?, ?, ?, ?, DATE('now', '+1 year'), ?)",
        (fname, lname, values[1], values[2], values[3], is_active))


def insert_rentals(cursor, values):
    emp = cursor.execute(
        "SELECT EmployeeID FROM Employees WHERE FirstName || ' ' || LastName = ?", (values[0],)).fetchone()
    emp_id = emp[0] if emp else None
    if emp_id is None: raise ValueError(f"Could not find Employee '{values[0]}'")
    
    cust = cursor.execute(
        "SELECT CustomerID FROM Customers WHERE FirstName || ' ' || LastName = ?", (values[1],)).fetchone()
    cust_id = cust[0] if cust else None
    if cust_id is None: raise ValueError(f"Could not find Customer '{values[1]}'")
    
    vhc_id = parse_id(values[2])
    pub = cursor.execute(
        "SELECT BranchID FROM Branches WHERE BranchName=?", (values[3],)).fetchone()
    pub_id = pub[0] if pub else None
    dob = cursor.execute(
        "SELECT BranchID FROM Branches WHERE BranchName=?", (values[4],)).fetchone()
    dob_id = dob[0] if dob else None
    cursor.execute(
        "INSERT INTO Rentals (EmployeeID, CustomerID, VehicleID, PickUpBranchID, DropOffBranchID, RentedOn, ExpectedReturn, ActualReturn, StartMileage, EndMileage, Status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (emp_id, cust_id, vhc_id, pub_id, dob_id, values[5], values[6], values[7], values[8], values[9], values[10]))
    raw_id = cursor.lastrowid
    
    # ── AUTOMATIONS ──
    _handle_rental_automations(cursor, values, raw_id, vhc_id)


def insert_payments(cursor, values):
    rnt_id = parse_id(values[0])
    cursor.execute(
        "INSERT INTO Payments (RentalID, PaidOn, BaseAmount, PenaltyAmount, TotalAmount, PaymentMethod) VALUES (?, ?, ?, ?, ?, ?)",
        (rnt_id, values[1], values[2], values[3], values[4], values[5]))


def insert_maintenance_logs(cursor, values):
    vhc_id = parse_id(values[0])
    cursor.execute(
        "INSERT INTO Maintenance_Logs (VehicleID, StartDate, EndDate, Cost, Description, Status) VALUES (?, ?, ?, ?, ?, ?)",
        (vhc_id, values[1], values[2], values[3], values[4], values[5]))


def insert_damage_reports(cursor, values):
    rnt_id = parse_id(values[0])
    cursor.execute(
        "INSERT INTO Damage_Reports (RentalID, IncidentDate, Description, EstimatedRepairCost, Status) VALUES (?, ?, ?, ?, ?)",
        (rnt_id, values[1], values[2], values[3], values[4]))


def insert_employees(cursor, values):
    names = values[0].split(' ', 1)
    fname = names[0]
    lname = names[1] if len(names) > 1 else ""
    branch = cursor.execute(
        "SELECT BranchID FROM Branches WHERE BranchName=?", (values[3],)).fetchone()
    branch_id = branch[0] if branch else None
    sup = cursor.execute(
        "SELECT EmployeeID FROM Employees WHERE FirstName || ' ' || LastName = ?", (values[4],)).fetchone()
    sup_id = sup[0] if sup else None
    cursor.execute(
        "INSERT INTO Employees (FirstName, LastName, Email, Role, BranchID, SupervisorID) VALUES (?, ?, ?, ?, ?, ?)",
        (fname, lname, values[1], values[2], branch_id, sup_id))


TABLE_INSERT_HANDLERS = {
    "Branches": insert_branches,
    "Vehicle_Categories": insert_vehicle_categories,
    "Vehicle_Models": insert_vehicle_models,
    "Vehicles": insert_vehicles,
    "Customers": insert_customers,
    "Rentals": insert_rentals,
    "Payments": insert_payments,
    "Maintenance_Logs": insert_maintenance_logs,
    "Damage_Reports": insert_damage_reports,
    "Employees": insert_employees
}


def insert_record_to_db(db_path, table_name, cols, values):
    handler = TABLE_INSERT_HANDLERS.get(table_name)
    if not handler:
        raise ValueError(f"Unknown table name: {table_name}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        handler(cursor, values)
        conn.commit()
    except sqlite3.IntegrityError as e:
        if "NOT NULL" in str(e):
            col = str(e).split('.')[-1] if '.' in str(e) else str(e)
            raise ValueError(f"Invalid reference. A related record for '{col}' was not found. Please ensure it is typed correctly.")
        raise
    finally:
        conn.close()


def delete_record_from_db(db_path, table_name, pk_col, pk_val):
    raw_id = parse_id(pk_val)
    if raw_id is None:
        raise ValueError(f"Invalid ID format: {pk_val}")

    real_pk_col = pk_col.replace(" ", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            f'DELETE FROM {table_name} WHERE "{real_pk_col}"=?', (raw_id,))
        if cursor.rowcount == 0:
            raise ValueError("Record not found or already deleted.")
        conn.commit()
    finally:
        conn.close()


def save_record_to_db(db_path, table_name, cols, values, pk_val):
    raw_id = parse_id(pk_val)
    if raw_id is None:
        raise ValueError(f"Invalid ID format: {pk_val}")

    handler = TABLE_HANDLERS.get(table_name)
    if not handler:
        raise ValueError(f"Unknown table name: {table_name}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        handler(cursor, values, raw_id)
        conn.commit()
    except sqlite3.IntegrityError as e:
        if "NOT NULL" in str(e):
            col = str(e).split('.')[-1] if '.' in str(e) else str(e)
            raise ValueError(f"Invalid reference. A related record for '{col}' was not found. Please ensure it is typed correctly.")
        raise
    finally:
        conn.close()


def auto_update_overdue(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Update vehicles tied to overdue rentals first
        cursor.execute("""
            UPDATE Vehicles 
            SET Status = 'Overdue'
            WHERE VehicleID IN (
                SELECT VehicleID FROM Rentals 
                WHERE Status = 'Ongoing' 
                AND ExpectedReturn < DATETIME('now', 'localtime')
            )
        """)
        
        # Update the rentals themselves
        cursor.execute("""
            UPDATE Rentals
            SET Status = 'Overdue'
            WHERE Status = 'Ongoing' 
            AND ExpectedReturn < DATETIME('now', 'localtime')
        """)
        
        conn.commit()
    except Exception as e:
        print(f"Failed to auto-update overdue records: {e}")
    finally:
        conn.close()

def run_automation_sweep(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    fixes = 0
    try:
        rentals = cursor.execute('''
            SELECT r.RentalID, r.VehicleID, r.RentedOn, r.ExpectedReturn, r.ActualReturn, r.StartMileage, r.EndMileage 
            FROM Rentals r
            LEFT JOIN Payments p ON r.RentalID = p.RentalID
            WHERE r.Status = 'Completed' AND p.PaymentID IS NULL
        ''').fetchall()
        
        for r in rentals:
            rental_id, vhc_id, rented_on, expected, actual, start_m, end_m = r
            
            # Check Vehicle
            veh = cursor.execute("SELECT CurrentMileage, Status FROM Vehicles WHERE VehicleID=?", (vhc_id,)).fetchone()
            if veh:
                veh_m, veh_status = veh
                target_m = end_m if (end_m and str(end_m).lower() != "none") else start_m
                if str(veh_m) != str(target_m) or veh_status != 'Available':
                    cursor.execute("UPDATE Vehicles SET CurrentMileage=?, Status='Available' WHERE VehicleID=?", (target_m, vhc_id))
            
            # Create Payment
            rates = cursor.execute("""
                SELECT c.DailyRate, c.OverdueRatePerHour 
                FROM Vehicles v 
                JOIN Vehicle_Models m ON v.ModelID = m.ModelID 
                JOIN Vehicle_Categories c ON m.CategoryID = c.CategoryID 
                WHERE v.VehicleID = ?
            """, (vhc_id,)).fetchone()
            
            if rates:
                daily_rate = float(rates[0])
                overdue_rate = float(rates[1])
                
                def parse_dt(dt_str):
                    if not dt_str or str(dt_str).strip().lower() == "none": return None
                    s = str(dt_str).strip()
                    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", 
                                "%y-%m-%d %H:%M:%S", "%y-%m-%d %H:%M", "%y-%m-%d", 
                                "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M", "%m/%d/%Y",
                                "%m/%d/%y %H:%M:%S", "%m/%d/%y %H:%M", "%m/%d/%y"):
                        try: return datetime.strptime(s, fmt)
                        except ValueError: continue
                    raise ValueError(f"Invalid date format: {s}")
                
                r_on = parse_dt(rented_on)
                e_ret = parse_dt(expected)
                
                actual_dt_str = actual if (actual and str(actual).lower() != "none") else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                a_ret = parse_dt(actual_dt_str)
                
                days_rented = (e_ret - r_on).days
                if days_rented < 1: days_rented = 1
                
                base_amount = daily_rate * days_rented
                penalty_amount = 0.0
                
                if a_ret > e_ret:
                    diff = a_ret - e_ret
                    hours_overdue = diff.total_seconds() / 3600.0
                    penalty_amount = overdue_rate * hours_overdue
                    
                total_amount = base_amount + penalty_amount
                
                cursor.execute("INSERT INTO Payments (RentalID, PaidOn, BaseAmount, PenaltyAmount, TotalAmount, PaymentMethod) VALUES (?, ?, ?, ?, ?, 'Cash')",
                               (rental_id, actual_dt_str, round(base_amount, 2), round(penalty_amount, 2), round(total_amount, 2)))
                fixes += 1
                
        conn.commit()
    except Exception as e:
        print(f"Sweep failed: {e}")
    finally:
        conn.close()
    
    return fixes

def get_dropdown_options(db_path, table_name, col_name):
    if col_name == "Status":
        if table_name == "Vehicles":
            return ["Available", "Rented", "Maintenance", "Overdue"]
        if table_name == "Rentals":
            return ["Ongoing", "Completed", "Cancelled", "Overdue"]
        if table_name in ("Maintenance_Logs", "Damage_Reports"):
            return ["Pending", "In Progress", "Resolved", "Cancelled"]
    
    if table_name == "Employees" and col_name == "Role":
        return ["Admin", "Manager", "Staff"]
    if col_name == "Payment Method":
        return ["Cash", "Credit Card", "Debit Card", "Bank Transfer", "E-Wallet"]
    if col_name == "Is Active?":
        return ["Yes", "No"]
    if col_name == "Fuel Type":
        return ["Gasoline", "Diesel", "Electric", "Hybrid"]
    if col_name == "Transmission":
        return ["Automatic", "Manual", "CVT"]
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    options = []
    try:
        if col_name in ("Current Branch", "Pickup Branch", "Dropoff Branch", "Branch Assigned"):
            rows = cursor.execute("SELECT BranchName FROM Branches ORDER BY BranchName").fetchall()
            options = [r[0] for r in rows]
        elif col_name == "Category Name":
            rows = cursor.execute("SELECT CategoryName FROM Vehicle_Categories ORDER BY CategoryName").fetchall()
            options = [r[0] for r in rows]
        elif col_name == "Model":
            rows = cursor.execute("SELECT Brand || ' ' || ModelName FROM Vehicle_Models ORDER BY Brand").fetchall()
            options = [r[0] for r in rows]
        elif col_name in ("Handled By", "Supervisor Name"):
            rows = cursor.execute("SELECT FirstName || ' ' || LastName FROM Employees ORDER BY FirstName").fetchall()
            options = [r[0] for r in rows]
        elif col_name == "Customer Name":
            rows = cursor.execute("SELECT FirstName || ' ' || LastName FROM Customers ORDER BY FirstName").fetchall()
            options = [r[0] for r in rows]
        elif col_name == "Vehicle ID":
            rows = cursor.execute("SELECT 'VHC-' || VehicleID || ' (' || LicensePlate || ')' FROM Vehicles ORDER BY VehicleID").fetchall()
            options = [r[0] for r in rows]
        elif col_name == "Rental ID":
            rows = cursor.execute("SELECT 'RNT-' || RentalID FROM Rentals ORDER BY RentalID").fetchall()
            options = [r[0] for r in rows]
    except Exception as e:
        print(f"Error fetching dropdowns: {e}")
    finally:
        conn.close()
    
    return options
