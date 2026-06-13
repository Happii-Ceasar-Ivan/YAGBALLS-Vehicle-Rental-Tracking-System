--
-- File generated with SQLiteStudio v3.4.21 on Sat Jun 13 20:45:51 2026
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- View: v_Branches
CREATE VIEW v_Branches AS
    SELECT 'BRA-' || PRINTF('%03d', BranchID) AS [Branch ID],
           BranchName AS [Branch Name],
           StreetAddress AS Street,
           Barangay,
           City,
           Province,
           Phone
      FROM Branches;


-- View: v_Customers
CREATE VIEW v_Customers AS
    SELECT 'CUS-' || PRINTF('%03d', CustomerID) AS [Customer ID],
           FirstName || ' ' || LastName AS [Customer Name],
           Email,
           Phone AS [Phone No.],
           DriversLicense AS [License No.],
           CASE
               WHEN IsActive = 1 THEN PRINTF('Yes') 
               ELSE PRINTF('No') 
           END AS [Is Active?]
      FROM Customers;


-- View: v_Damage_Reports
CREATE VIEW v_Damage_Reports AS
    SELECT 'REP-' || PRINTF('%03d', dr.ReportID) AS [Report ID],
           'RNT-' || PRINTF('%03d', r.RentalID) AS [Rental ID],
           dr.IncidentDate [Incident Date],
           dr.Description,
           PRINTF('%.2f', dr.EstimatedRepairCost) AS [Est. Repair Cost],
           dr.Status
      FROM Damage_Reports AS dr
           INNER JOIN
           Rentals AS r ON dr.RentalID = r.RentalID;


-- View: v_Employees
CREATE VIEW v_Employees AS
    SELECT 'EMP-' || PRINTF('%03d', e.EmployeeID) AS [Employee ID],
           CONCAT_WS(' ', e.FirstName, e.LastName) AS [Employee Name],
           e.Email,
           e.Role,
           b.BranchName AS [Branch Assigned],
           CONCAT_WS(' ', s.FirstName, s.LastName) AS [Supervisor Name]
      FROM Employees AS e
           LEFT OUTER JOIN
           Branches AS b ON e.BranchID = b.BranchID
           LEFT OUTER JOIN
           Employees AS s ON s.EmployeeID = e.SupervisorID;


-- View: v_Maintenance_Logs
CREATE VIEW v_Maintenance_Logs AS
    SELECT 'LOG-' || PRINTF('%03d', LogID) AS [Log ID],
           VehicleID AS [Vehicle ID],
           StartDate AS [Start Date],
           EndDate AS [End Date],
           CASE
               WHEN Cost IS NOT NULL THEN PRINTF('%.2f', Cost) 
               ELSE NULL-- Keeps it completely empty/null in the database response
           END AS Cost,
           Description,
           Status
      FROM Maintenance_Logs;


-- View: v_Payments
CREATE VIEW v_Payments AS
    SELECT 'PAY-' || PRINTF('%03d', p.PaymentID) AS [Payment ID],
           'RNT-' || PRINTF('%03d', p.PaymentID) AS [Rental ID],
           p.PaidOn AS [Paid On],
           p.BaseAmount AS [Base Amount],
           p.PenaltyAmount AS [Penalty Amount],
           p.TotalAmount AS [Total Amount],
           p.PaymentMethod AS [Payment Method]
      FROM Payments AS p
           INNER JOIN
           Rentals AS r ON p.RentalID = r.RentalID;


-- View: v_Rentals
CREATE VIEW v_Rentals AS
    SELECT 'RNT-' || PRINTF('%03d', r.RentalID) AS [Rental ID],
           CONCAT_WS(' ', e.FirstName, e.LastName) AS [Handled By],
           CONCAT_WS(' ', c.FirstName, c.LastName) AS [Customer Name],
           CONCAT_WS('-', 'VHC', PRINTF('%03d', v.VehicleID) ) AS [Vehicle ID],
           pub.BranchName AS [Pickup Branch],
           dob.BranchName AS [Dropoff Branch],
           r.RentedOn,
           r.ExpectedReturn,
           r.ActualReturn,
           r.StartMileage,
           r.EndMileage,
           r.Status
      FROM Rentals AS r
           INNER JOIN
           Employees AS e ON r.EmployeeID = e.EmployeeID
           INNER JOIN
           Customers AS c ON r.CustomerID = c.CustomerID
           INNER JOIN
           Vehicles AS v ON r.VehicleID = v.VehicleID
           INNER JOIN
           Branches AS pub ON r.PickUpBranchID = pub.BranchID
           LEFT OUTER JOIN
           Branches AS dob ON r.DropOffBranchID = dob.BranchID;


-- View: v_Vehicle_Categories
CREATE VIEW v_Vehicle_Categories AS
    SELECT 'CAT-' || PRINTF('%03d', CategoryID) AS [Category ID],
           CategoryName AS [Category Name],
           PRINTF('%.2f', DailyRate) AS [Daily Rate],
           PRINTF('%.2f', OverdueRatePerHour) AS [Overdue Rate Per Hour]
      FROM Vehicle_Categories;


-- View: v_Vehicle_Models
CREATE VIEW v_Vehicle_Models AS
    SELECT 'MOD-' || PRINTF('%03d', vm.ModelID) AS [Model ID],
           vm.Brand,
           vm.ModelName AS [Model Name],
           vm.FuelType AS [Fuel Type],
           vm.Transmission,
           vc.CategoryName AS [Category Name]
      FROM Vehicle_Models AS vm
           LEFT OUTER JOIN
           Vehicle_Categories vc ON vm.CategoryID = vc.CategoryID;


-- View: v_Vehicles
CREATE VIEW v_Vehicles AS
    SELECT/* 'VHC-' || PRINTF('%03d', v.VehicleID) AS 'Vehicle ID', */ CONCAT_WS('-', 'VHC', PRINTF('%03d', v.VehicleID) ) AS [Vehicle ID],
           CONCAT_WS(' ', vm.Brand, vm.ModelName) AS Model,
           v.LicensePlate AS [License Plate],
           v.CurrentMileage AS [Current Mileage],
           v.Status AS Status,
           b.BranchName AS [Current Branch]
      FROM Vehicles AS v
           LEFT OUTER JOIN
           Vehicle_Models AS vm ON v.ModelID = vm.ModelID
           LEFT OUTER JOIN
           Branches AS b ON v.CurrentBranchID = b.BranchID;


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
