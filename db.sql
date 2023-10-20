/* Accounts table */
CREATE TABLE Accounts(
	id int NOT NULL IDENTITY(1,1),
	username varchar(50) NOT NULL,
	password varchar(255) NOT NULL,
	email varchar(100) NOT NULL,
	PRIMARY KEY(id),
)

/* ProjMachines table */
CREATE TABLE ProjMachines(
	Line_ID int NOT NULL,
	Machine_Name varchar(100) NULL,
	Product_ID int NOT NULL,
	Process_time float NOT NULL)
INSERT INTO ProjMachines VALUES (8, 'NXT_A1', 12345, 66)
INSERT INTO ProjMachines VALUES (8, 'NXT_A2', 12343, 45)
INSERT INTO ProjMachines VALUES (8, 'CP-341-MM_C3', 12344, 55)

