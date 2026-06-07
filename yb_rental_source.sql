--
-- File generated with SQLiteStudio v3.4.21 on Sun Jun 7 17:50:49 2026
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: Branches
CREATE TABLE IF NOT EXISTS Branches (BranchID INT IDENTITY (1, 1) PRIMARY KEY UNIQUE NOT NULL, BranchName NVARCHAR (100) NOT NULL, StreetAddress NVARCHAR (150) NOT NULL, Barangay NVARCHAR (50) NOT NULL, City NVARCHAR (50) NOT NULL, Province NVARCHAR (50) NOT NULL, Phone VARCHAR (20) NOT NULL);
INSERT INTO Branches (BranchID, BranchName, StreetAddress, Barangay, City, Province, Phone) VALUES (1, 'PUPQC Campus Hub', 'Don Fabian Street', 'Commonwealth', 'Quezon City', 'Metro Manila', '02-8921-2345');
INSERT INTO Branches (BranchID, BranchName, StreetAddress, Barangay, City, Province, Phone) VALUES (2, 'Makati Business District', '6789 Ayala Avenue', 'San Lorenzo', 'Makati', 'Metro Manila ', '02-8812-3456');
INSERT INTO Branches (BranchID, BranchName, StreetAddress, Barangay, City, Province, Phone) VALUES (3, 'NAIA Terminal 3 Office', 'Arrival Ventilation Road', 'Vitalez', 'Pasay', 'Metro Manila', '02-8851-7890');

-- Table: Customers
CREATE TABLE IF NOT EXISTS Customers (CustomerID INT IDENTITY (1, 1) PRIMARY KEY UNIQUE NOT NULL, FirstName NVARCHAR (50) NOT NULL, LastName NVARCHAR (50) NOT NULL, Email VARCHAR (100) UNIQUE NOT NULL, Phone VARCHAR (20) NOT NULL, DriversLicense VARCHAR (30) UNIQUE NOT NULL, LicenseExpiry DATE NOT NULL, IsActive BIT NOT NULL DEFAULT (1));
INSERT INTO Customers (CustomerID, FirstName, LastName, Email, Phone, DriversLicense, LicenseExpiry, IsActive) VALUES (1, 'Juan', 'Dela Cruz', 'juan.delacruz@gmail.com', '09171234567', 'N01-12-345678', '2029-05-12', 1);
INSERT INTO Customers (CustomerID, FirstName, LastName, Email, Phone, DriversLicense, LicenseExpiry, IsActive) VALUES (2, 'Maria', 'Santos', 'maria.santos@yahoo.com', '09189876543', 'N02-23-876543', '2028-11-20', 1);
INSERT INTO Customers (CustomerID, FirstName, LastName, Email, Phone, DriversLicense, LicenseExpiry, IsActive) VALUES (3, 'Matteo', 'Rizal', 'm.rizal@outlook.com', '09225554433', 'N03-34-112233', '2027-08-15', 1);

-- Table: Damage_Reports
CREATE TABLE IF NOT EXISTS Damage_Reports (ReportID INT IDENTITY (1, 1) PRIMARY KEY UNIQUE NOT NULL, RentalID INT REFERENCES Rentals (RentalID) NOT NULL, IncidentDate DATETIME NOT NULL, Description TEXT NOT NULL, EstimatedRepairCost DECIMAL (10, 2) NOT NULL, Status VARCHAR (20) NOT NULL);

-- Table: Employees
CREATE TABLE IF NOT EXISTS Employees (EmployeeID INT IDENTITY (1, 1) PRIMARY KEY UNIQUE NOT NULL, FirstName NVARCHAR (50) NOT NULL, LastName NVARCHAR (50) NOT NULL, Email VARCHAR (100) UNIQUE NOT NULL, Role NVARCHAR (50) NOT NULL, BranchID INT REFERENCES Branches (BranchID) NOT NULL, SupervisorID INT REFERENCES Employees (EmployeeID));
INSERT INTO Employees (EmployeeID, FirstName, LastName, Email, Role, BranchID, SupervisorID) VALUES (1, 'James Mathew', 'Calayag', 'j.calayag@ybrental.com', 'Chief Executive Officer', 1, NULL);
INSERT INTO Employees (EmployeeID, FirstName, LastName, Email, Role, BranchID, SupervisorID) VALUES (2, 'Don', 'Noriesta', 'd.noriesta@ybrental.com', 'General Manager', 1, 1);
INSERT INTO Employees (EmployeeID, FirstName, LastName, Email, Role, BranchID, SupervisorID) VALUES (3, 'Ceaser Ivan', 'Caiga', 'ci.caiga@ybrental.com', 'Rental Desk Agent', 1, 2);
INSERT INTO Employees (EmployeeID, FirstName, LastName, Email, Role, BranchID, SupervisorID) VALUES (4, 'Marc Arthur', 'Clarete', 'ma.clarete@ybrental.com', 'Rental Desk Agent', 2, 2);
INSERT INTO Employees (EmployeeID, FirstName, LastName, Email, Role, BranchID, SupervisorID) VALUES (5, 'Benjamin', 'Magsila', 'b.magsila@ybrental.com', 'Rental Desk Agent', 3, 2);

-- Table: Maintenance_Logs
CREATE TABLE IF NOT EXISTS Maintenance_Logs (LogID INT IDENTITY (1, 1) PRIMARY KEY NOT NULL UNIQUE, VechileID INT REFERENCES Vehicles (VehicleID) NOT NULL, StartDate DATETIME NOT NULL, EndDate DATETIME, Cost DECIMAL (10, 2), Description TEXT NOT NULL, Status VARCHAR (20) NOT NULL);

-- Table: Payments
CREATE TABLE IF NOT EXISTS Payments (PaymentID PRIMARY KEY UNIQUE NOT NULL, RentalID INT REFERENCES Rentals (RentalID) NOT NULL, PaidOn DATETIME NOT NULL, BaseAmount DECIMAL (10, 2) NOT NULL, PenaltyAmount DECIMAL (10, 2) NOT NULL DEFAULT (0), TotalAmount DECIMAL (10, 2) NOT NULL, PaymentMethod VARCHAR (30) NOT NULL);

-- Table: Rentals
CREATE TABLE IF NOT EXISTS Rentals (RentalID INT IDENTITY (1, 1) PRIMARY KEY UNIQUE NOT NULL, EmployeeID INT REFERENCES Employees (EmployeeID) NOT NULL, CustomerID INT REFERENCES Customers (CustomerID) NOT NULL, VehicleID INT REFERENCES Vehicles (VehicleID) NOT NULL, PickUpBranchID INT REFERENCES Branches (BranchID) NOT NULL, DropOffBranch INT REFERENCES Branches (BranchID) NOT NULL, RentedOn DATETIME NOT NULL, ExpectedReturn DATETIME NOT NULL, ActualReturn DATETIME, StartMileage INT NOT NULL, EndMileage INT, Status VARCHAR (20) NOT NULL);
INSERT INTO Rentals (RentalID, EmployeeID, CustomerID, VehicleID, PickUpBranchID, DropOffBranch, RentedOn, ExpectedReturn, ActualReturn, StartMileage, EndMileage, Status) VALUES (1, 3, 1, 1, 1, 1, '2026-05-01 9:00:00', '2026-05-03 8:30:00', '2026-05-03 8:30:00', 14800, 15200, 'Completed');
INSERT INTO Rentals (RentalID, EmployeeID, CustomerID, VehicleID, PickUpBranchID, DropOffBranch, RentedOn, ExpectedReturn, ActualReturn, StartMileage, EndMileage, Status) VALUES (2, 4, 2, 2, 2, 2, '2026-06-04 10:00:00', '2026-06-07 10:00:00', NULL, 42100, NULL, 'Overdue');
INSERT INTO Rentals (RentalID, EmployeeID, CustomerID, VehicleID, PickUpBranchID, DropOffBranch, RentedOn, ExpectedReturn, ActualReturn, StartMileage, EndMileage, Status) VALUES (3, 5, 3, 3, 1, 3, '2026-06-07 13:00:00', '2026-06-09 13:00:00', NULL, 28000, NULL, 'Active');

-- Table: Vehicle_Categories
CREATE TABLE IF NOT EXISTS Vehicle_Categories (CategoryID INT IDENTITY (1, 1) PRIMARY KEY UNIQUE NOT NULL, CategoryName NVARCHAR (50) NOT NULL, DailyRate DECIMA (10, 2) NOT NULL, OverdueRatePerHour DECIMAL (10, 2) NOT NULL);
INSERT INTO Vehicle_Categories (CategoryID, CategoryName, DailyRate, OverdueRatePerHour) VALUES (1, 'Economy Sedan', 1500, 150);
INSERT INTO Vehicle_Categories (CategoryID, CategoryName, DailyRate, OverdueRatePerHour) VALUES (2, 'Family SUV', 3500, 300);
INSERT INTO Vehicle_Categories (CategoryID, CategoryName, DailyRate, OverdueRatePerHour) VALUES (3, 'Premium Passenger Van', 5000, 450);

-- Table: Vehicles
CREATE TABLE IF NOT EXISTS Vehicles (VehicleID INT IDENTITY (1, 1) PRIMARY KEY UNIQUE NOT NULL, ModelID INT REFERENCES Vehiicle_Models (ModelID) NOT NULL, LicensePlate VARCHAR (20) NOT NULL UNIQUE, CurrentMilieage INT NOT NULL, Status VARCHAR (20) NOT NULL, CurrentBranchID INT REFERENCES Branches (BranchID) NOT NULL);
INSERT INTO Vehicles (VehicleID, ModelID, LicensePlate, CurrentMilieage, Status, CurrentBranchID) VALUES (1, 1, 'NDG1234', 15200, 'Available', 1);
INSERT INTO Vehicles (VehicleID, ModelID, LicensePlate, CurrentMilieage, Status, CurrentBranchID) VALUES (2, 2, 'NQC5678', 42100, 'Rented', 2);
INSERT INTO Vehicles (VehicleID, ModelID, LicensePlate, CurrentMilieage, Status, CurrentBranchID) VALUES (3, 2, 'NCP9012', 28500, 'Maintenance', 1);
INSERT INTO Vehicles (VehicleID, ModelID, LicensePlate, CurrentMilieage, Status, CurrentBranchID) VALUES (4, 3, 'NWD3456', 61000, 'Available', 3);

-- Table: Vehiicle_Models
CREATE TABLE IF NOT EXISTS Vehiicle_Models (ModelID INT IDENTITY (1, 1) PRIMARY KEY UNIQUE NOT NULL, Brand NVARCHAR (50) NOT NULL, ModelName NVARCHAR (100) NOT NULL, FuelType VARCHAR (20) NOT NULL, Transmission VARCHAR (20) NOT NULL, CategoryID INT REFERENCES Vehicle_Categories (CategoryID) NOT NULL);
INSERT INTO Vehiicle_Models (ModelID, Brand, ModelName, FuelType, Transmission, CategoryID) VALUES (1, 'Toyota', 'Vios', 'Gasoline', 'Automatic', 1);
INSERT INTO Vehiicle_Models (ModelID, Brand, ModelName, FuelType, Transmission, CategoryID) VALUES (2, 'Toyota', 'Innova', 'Diesel', 'Automatic', 2);
INSERT INTO Vehiicle_Models (ModelID, Brand, ModelName, FuelType, Transmission, CategoryID) VALUES (3, 'Nssan', 'Urvan NV350', 'Diesel', 'Manual', 3);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
