PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Branches
INSERT INTO Branches (
                         BranchID,
                         BranchName,
                         StreetAddress,
                         Barangay,
                         City,
                         Province,
                         Phone
                     )
                     VALUES (
                         1,
                         'PUPQC Campus Hub',
                         'Don Fabian Street',
                         'Commonwealth',
                         'Quezon City',
                         'Metro Manila',
                         '02-8921-2345'
                     ),
                     (
                         2,
                         'Makati Business District',
                         '6789 Ayala Avenue',
                         'San Lorenzo',
                         'Makati',
                         'Metro Manila ',
                         '02-8812-3456'
                     ),
                     (
                         3,
                         'NAIA Terminal 3 Office',
                         'Arrival Ventilation Road',
                         'Vitalez',
                         'Pasay',
                         'Metro Manila',
                         '02-8851-7890'
                     );

-- Customers
INSERT INTO Customers (
                          CustomerID,
                          FirstName,
                          LastName,
                          Email,
                          Phone,
                          DriversLicense,
                          LicenseExpiry,
                          IsActive
                      )
                      VALUES (
                          1,
                          'Juan',
                          'Dela Cruz',
                          'juan.delacruz@gmail.com',
                          '09171234567',
                          'N01-12-345678',
                          '2029-05-12',
                          1
                      ),
                      (
                          2,
                          'Maria',
                          'Santos',
                          'maria.santos@yahoo.com',
                          '09189876543',
                          'N02-23-876543',
                          '2028-11-20',
                          1
                      ),
                      (
                          3,
                          'Matteo',
                          'Rizal',
                          'm.rizal@outlook.com',
                          '09225554433',
                          'N03-34-112233',
                          '2027-08-15',
                          1
                      );

-- Damage Reports
INSERT INTO Damage_Reports (
                               ReportID,
                               RentalID,
                               IncidentDate,
                               Description,
                               EstimatedRepairCost,
                               Status
                           )
                           VALUES (
                               1,
                               1,
                               '2026-05-02 17:45:00',
                               'Minor deep scratch on the rear passenger door panel from grocery parking',
                               4500,
                               'Settled'
                           );

-- Employees
INSERT INTO Employees (
                          EmployeeID,
                          FirstName,
                          LastName,
                          Email,
                          Role,
                          BranchID,
                          SupervisorID
                      )
                      VALUES (
                          1,
                          'James Mathew',
                          'Calayag',
                          'j.calayag@ybrental.com',
                          'Chief Executive Officer',
                          1,
                          NULL
                      ),
                      (
                          2,
                          'Don',
                          'Noriesta',
                          'd.noriesta@ybrental.com',
                          'General Manager',
                          1,
                          1
                      ),
                      (
                          3,
                          'Ceaser Ivan',
                          'Caiga',
                          'ci.caiga@ybrental.com',
                          'Rental Desk Agent',
                          1,
                          2
                      ),
                      (
                          4,
                          'Marc Arthur',
                          'Clarete',
                          'ma.clarete@ybrental.com',
                          'Rental Desk Agent',
                          2,
                          2
                      ),
                      (
                          5,
                          'Benjamin',
                          'Magsila',
                          'b.magsila@ybrental.com',
                          'Rental Desk Agent',
                          3,
                          2
                      );


-- Maintenance Logs
INSERT INTO Maintenance_Logs (
                                 LogID,
                                 VechileID,
                                 StartDate,
                                 EndDate,
                                 Cost,
                                 Description,
                                 Status
                             )
                             VALUES (
                                 1,
                                 3,
                                 '2026-06-04 8:00:00',
                                 NULL,
                                 NULL,
                                 'Routiine 30,000lm PMS Checkup and brake pad replacement.',
                                 'Under Repair'
                             );


-- Payments
INSERT INTO Payments (
                         PaymentID,
                         RentalID,
                         PaidOn,
                         BaseAmount,
                         PenaltyAmount,
                         TotalAmount,
                         PaymentMethod
                     )
                     VALUES (
                         1,
                         1,
                         '2026-05-03 8:35:00',
                         3000,
                         0,
                         3000,
                         'GCash'
                     );


-- Rentals
INSERT INTO Rentals (
                        RentalID,
                        EmployeeID,
                        CustomerID,
                        VehicleID,
                        PickUpBranchID,
                        DropOffBranch,
                        RentedOn,
                        ExpectedReturn,
                        ActualReturn,
                        StartMileage,
                        EndMileage,
                        Status
                    )
                    VALUES (
                        1,
                        3,
                        1,
                        1,
                        1,
                        1,
                        '2026-05-01 9:00:00',
                        '2026-05-03 8:30:00',
                        '2026-05-03 8:30:00',
                        14800,
                        15200,
                        'Completed'
                    ),
                    (
                        2,
                        4,
                        2,
                        2,
                        2,
                        2,
                        '2026-06-04 10:00:00',
                        '2026-06-07 10:00:00',
                        NULL,
                        42100,
                        NULL,
                        'Overdue'
                    ),
                    (
                        3,
                        5,
                        3,
                        3,
                        1,
                        3,
                        '2026-06-07 13:00:00',
                        '2026-06-09 13:00:00',
                        NULL,
                        28000,
                        NULL,
                        'Active'
                    );


-- Vehicle Categories
INSERT INTO Vehicle_Categories (
                                   CategoryID,
                                   CategoryName,
                                   DailyRate,
                                   OverdueRatePerHour
                               )
                               VALUES (
                                   1,
                                   'Economy Sedan',
                                   1500,
                                   150
                               ),
                               (
                                   2,
                                   'Family SUV',
                                   3500,
                                   300
                               ),
                               (
                                   3,
                                   'Premium Passenger Van',
                                   5000,
                                   450
                               );


-- Vehicle Models
INSERT INTO Vehicle_Models (
                               ModelID,
                               Brand,
                               ModelName,
                               FuelType,
                               Transmission,
                               CategoryID
                           )
                           VALUES (
                               1,
                               'Toyota',
                               'Vios',
                               'Gasoline',
                               'Automatic',
                               1
                           ),
                           (
                               2,
                               'Toyota',
                               'Innova',
                               'Diesel',
                               'Automatic',
                               2
                           ),
                           (
                               3,
                               'Nssan',
                               'Urvan NV350',
                               'Diesel',
                               'Manual',
                               3
                           );


-- Vehicles
INSERT INTO Vehicles (
                         VehicleID,
                         ModelID,
                         LicensePlate,
                         CurrentMilieage,
                         Status,
                         CurrentBranchID
                     )
                     VALUES (
                         1,
                         1,
                         'NDG1234',
                         15200,
                         'Available',
                         1
                     ),
                     (
                         2,
                         2,
                         'NQC5678',
                         42100,
                         'Rented',
                         2
                     ),
                     (
                         3,
                         2,
                         'NCP9012',
                         28500,
                         'Maintenance',
                         1
                     ),
                     (
                         4,
                         3,
                         'NWD3456',
                         61000,
                         'Available',
                         3
                     );


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
