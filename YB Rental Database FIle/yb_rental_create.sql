--
-- File generated with SQLiteStudio v3.4.21 on Sat Jun 13 20:49:09 2026
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: Branches
CREATE TABLE Branches (
    BranchID      INTEGER        PRIMARY KEY AUTOINCREMENT
                                 UNIQUE
                                 NOT NULL,
    BranchName    NVARCHAR (100) NOT NULL,
    StreetAddress NVARCHAR (150) NOT NULL,
    Barangay      NVARCHAR (50)  NOT NULL,
    City          NVARCHAR (50)  NOT NULL,
    Province      NVARCHAR (50)  NOT NULL,
    Phone         VARCHAR (20)   NOT NULL
);

-- Table: Customers
CREATE TABLE Customers (
    CustomerID     INTEGER       PRIMARY KEY AUTOINCREMENT
                                 UNIQUE
                                 NOT NULL,
    FirstName      NVARCHAR (50) NOT NULL,
    LastName       NVARCHAR (50) NOT NULL,
    Email          VARCHAR (100) UNIQUE
                                 NOT NULL,
    Phone          VARCHAR (20)  NOT NULL,
    DriversLicense VARCHAR (30)  UNIQUE
                                 NOT NULL,
    LicenseExpiry  DATE          NOT NULL,
    IsActive       BIT           NOT NULL
                                 DEFAULT (1) 
);

-- Table: Damage_Reports
CREATE TABLE Damage_Reports (
    ReportID            INTEGER         PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
    RentalID            INT             REFERENCES Rentals (RentalID) 
                                        NOT NULL,
    IncidentDate        DATETIME        NOT NULL,
    Description         TEXT            NOT NULL,
    EstimatedRepairCost DECIMAL (10, 2) NOT NULL,
    Status              VARCHAR (20)    NOT NULL
);

-- Table: Employees
CREATE TABLE Employees (
    EmployeeID   INTEGER       PRIMARY KEY AUTOINCREMENT
                               UNIQUE
                               NOT NULL,
    FirstName    NVARCHAR (50) NOT NULL,
    LastName     NVARCHAR (50) NOT NULL,
    Email        VARCHAR (100) UNIQUE
                               NOT NULL,
    Role         NVARCHAR (50) NOT NULL,
    BranchID     INT           REFERENCES Branches (BranchID) 
                               NOT NULL,
    SupervisorID INT           REFERENCES Employees (EmployeeID) 
);

-- Table: Maintenance_Logs
CREATE TABLE Maintenance_Logs (
    LogID       INTEGER         PRIMARY KEY AUTOINCREMENT
                                NOT NULL
                                UNIQUE,
    VehicleID   INT             REFERENCES Vehicles (VehicleID) 
                                NOT NULL,
    StartDate   DATETIME        NOT NULL,
    EndDate     DATETIME,
    Cost        DECIMAL (10, 2),
    Description TEXT            NOT NULL,
    Status      VARCHAR (20)    NOT NULL
);

-- Table: Payments
CREATE TABLE Payments (
    PaymentID     INTEGER         PRIMARY KEY AUTOINCREMENT
                                  UNIQUE
                                  NOT NULL,
    RentalID      INT             REFERENCES Rentals (RentalID) 
                                  NOT NULL,
    PaidOn        DATETIME        NOT NULL,
    BaseAmount    DECIMAL (10, 2) NOT NULL,
    PenaltyAmount DECIMAL (10, 2) NOT NULL
                                  DEFAULT (0),
    TotalAmount   DECIMAL (10, 2) NOT NULL,
    PaymentMethod VARCHAR (30)    NOT NULL
);

-- Table: Rentals
CREATE TABLE Rentals (
    RentalID        INTEGER      PRIMARY KEY AUTOINCREMENT
                                 UNIQUE
                                 NOT NULL,
    EmployeeID      INT          REFERENCES Employees (EmployeeID) 
                                 NOT NULL,
    CustomerID      INT          REFERENCES Customers (CustomerID) 
                                 NOT NULL,
    VehicleID       INT          REFERENCES Vehicles (VehicleID) 
                                 NOT NULL,
    PickUpBranchID  INT          REFERENCES Branches (BranchID) 
                                 NOT NULL,
    DropOffBranchID INT          REFERENCES Branches (BranchID),
    RentedOn        DATETIME     NOT NULL,
    ExpectedReturn  DATETIME     NOT NULL,
    ActualReturn    DATETIME,
    StartMileage    INT          NOT NULL,
    EndMileage      INT,
    Status          VARCHAR (20) NOT NULL
                                 DEFAULT Active
);

-- Table: Vehicle_Categories
CREATE TABLE Vehicle_Categories (
    CategoryID         INTEGER         PRIMARY KEY
                                       UNIQUE
                                       NOT NULL,
    CategoryName       NVARCHAR (50)   NOT NULL,
    DailyRate          DECIMA (10, 2)  NOT NULL,
    OverdueRatePerHour DECIMAL (10, 2) NOT NULL
);

-- Table: Vehicle_Models
CREATE TABLE Vehicle_Models (
    ModelID      INTEGER        PRIMARY KEY AUTOINCREMENT
                                UNIQUE
                                NOT NULL,
    Brand        NVARCHAR (50)  NOT NULL,
    ModelName    NVARCHAR (100) NOT NULL,
    FuelType     VARCHAR (20)   NOT NULL,
    Transmission VARCHAR (20)   NOT NULL,
    CategoryID   INT            REFERENCES Vehicle_Categories (CategoryID) 
                                NOT NULL
);

-- Table: Vehicles
CREATE TABLE Vehicles (
    VehicleID       INTEGER      PRIMARY KEY AUTOINCREMENT
                                 UNIQUE
                                 NOT NULL,
    ModelID         INT          REFERENCES Vehicle_Models (ModelID) 
                                 NOT NULL,
    LicensePlate    VARCHAR (20) NOT NULL
                                 UNIQUE,
    CurrentMileage  INT          NOT NULL,
    Status          VARCHAR (20) NOT NULL,
    CurrentBranchID INT          REFERENCES Branches (BranchID) 
                                 NOT NULL
);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
