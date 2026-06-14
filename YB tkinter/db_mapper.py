import sqlite3

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
    cat = cursor.execute("SELECT CategoryID FROM Vehicle_Categories WHERE CategoryName=?", (values[4],)).fetchone()
    cat_id = cat[0] if cat else None
    cursor.execute("UPDATE Vehicle_Models SET Brand=?, ModelName=?, FuelType=?, Transmission=?, CategoryID=? WHERE ModelID=?",
                   (values[0], values[1], values[2], values[3], cat_id, raw_id))

def update_vehicles(cursor, values, raw_id):
    model = cursor.execute("SELECT ModelID FROM Vehicle_Models WHERE Brand || ' ' || ModelName = ?", (values[0],)).fetchone()
    model_id = model[0] if model else None
    branch = cursor.execute("SELECT BranchID FROM Branches WHERE BranchName=?", (values[4],)).fetchone()
    branch_id = branch[0] if branch else None
    cursor.execute("UPDATE Vehicles SET ModelID=?, LicensePlate=?, CurrentMilieage=?, Status=?, CurrentBranchID=? WHERE VehicleID=?",
                   (model_id, values[1], values[2], values[3], branch_id, raw_id))

def update_customers(cursor, values, raw_id):
    names = values[0].split(' ', 1)
    fname = names[0]
    lname = names[1] if len(names) > 1 else ""
    is_active = 1 if str(values[4]).lower() == 'yes' else 0
    cursor.execute("UPDATE Customers SET FirstName=?, LastName=?, Email=?, Phone=?, DriversLicense=?, IsActive=? WHERE CustomerID=?",
                   (fname, lname, values[1], values[2], values[3], is_active, raw_id))

def update_rentals(cursor, values, raw_id):
    emp = cursor.execute("SELECT EmployeeID FROM Employees WHERE FirstName || ' ' || LastName = ?", (values[0],)).fetchone()
    emp_id = emp[0] if emp else None
    cust = cursor.execute("SELECT CustomerID FROM Customers WHERE FirstName || ' ' || LastName = ?", (values[1],)).fetchone()
    cust_id = cust[0] if cust else None
    vhc_id = parse_id(values[2])
    pub = cursor.execute("SELECT BranchID FROM Branches WHERE BranchName=?", (values[3],)).fetchone()
    pub_id = pub[0] if pub else None
    dob = cursor.execute("SELECT BranchID FROM Branches WHERE BranchName=?", (values[4],)).fetchone()
    dob_id = dob[0] if dob else None
    cursor.execute("UPDATE Rentals SET EmployeeID=?, CustomerID=?, VehicleID=?, PickUpBranchID=?, DropOffBranchID=?, RentedOn=?, ExpectedReturn=?, ActualReturn=?, StartMileage=?, EndMileage=?, Status=? WHERE RentalID=?",
                   (emp_id, cust_id, vhc_id, pub_id, dob_id, values[5], values[6], values[7], values[8], values[9], values[10], raw_id))

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
    branch = cursor.execute("SELECT BranchID FROM Branches WHERE BranchName=?", (values[3],)).fetchone()
    branch_id = branch[0] if branch else None
    sup = cursor.execute("SELECT EmployeeID FROM Employees WHERE FirstName || ' ' || LastName = ?", (values[4],)).fetchone()
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
    finally:
        conn.close()
