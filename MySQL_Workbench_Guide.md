# MySQL Workbench Guide for Blood Bank Application

## Introduction

This guide provides instructions on how to set up and use MySQL Workbench with the Blood Bank Application. MySQL Workbench is a visual database design tool that integrates SQL development, administration, database design, creation, and maintenance into a single integrated development environment.

## Installation

1. Download MySQL Workbench from the [official MySQL website](https://dev.mysql.com/downloads/workbench/)
2. Follow the installation instructions for your operating system
3. Make sure you also have MySQL Server installed

## Setting Up the Blood Bank Database

### Method 1: Using the init_database.bat Script

1. Run the `init_database.bat` script provided in the project root directory
2. Enter your MySQL username (default is 'root')
3. Enter your MySQL password
4. The script will create the database and all required tables

### Method 2: Manual Setup Using MySQL Workbench

1. Open MySQL Workbench and connect to your local MySQL server
2. Create a new schema (database):
   - Click on the 'Create a new schema' button in the Navigator panel
   - Name it `blood_bank`
   - Click 'Apply'
3. Import and run the SQL script:
   - Go to File > Open SQL Script
   - Navigate to the project's `database/init_db.sql` file and open it
   - Click on the lightning bolt icon to execute the script
   - This will create all the necessary tables

## Configuring the Application to Use MySQL

1. Open the `.env` file in the `backend` directory
2. Update the `DATABASE_URL` with your MySQL credentials:
   ```
   DATABASE_URL=mysql+mysqlconnector://username:password@localhost:3306/blood_bank
   ```
   Replace `username` and `password` with your MySQL credentials

## Verifying the Database Setup

1. Open MySQL Workbench and connect to your local MySQL server
2. Expand the `blood_bank` schema in the Navigator panel
3. You should see the following tables:
   - users
   - donors
   - receiver_requests
   - donation_records
4. You can right-click on any table and select 'Select Rows - Limit 1000' to view the data

## Common Database Operations in MySQL Workbench

### Viewing Table Structure

1. Right-click on a table in the Navigator panel
2. Select 'Table Inspector'
3. Navigate through the tabs to see columns, indexes, foreign keys, etc.

### Running SQL Queries

1. Click on the 'Create a new SQL tab for executing queries' button
2. Write your SQL query, for example:
   ```sql
   SELECT * FROM blood_bank.users;
   ```
3. Click on the lightning bolt icon to execute the query

### Backing Up the Database

1. Go to Server > Data Export
2. Select the `blood_bank` schema
3. Choose the tables you want to export
4. Select 'Export to Self-Contained File'
5. Click 'Start Export'

### Restoring the Database

1. Go to Server > Data Import
2. Select 'Import from Self-Contained File'
3. Browse to your backup file
4. Select 'New' in the 'Default Schema to be Imported To' section and enter `blood_bank`
5. Click 'Start Import'

## Troubleshooting

### Connection Issues

- Ensure MySQL Server is running
- Verify your username and password
- Check that the port (default 3306) is not blocked by a firewall

### Import/Export Issues

- Make sure you have sufficient privileges
- Check disk space for large exports
- Verify the file path is correct and accessible

## Additional Resources

- [MySQL Workbench Manual](https://dev.mysql.com/doc/workbench/en/)
- [MySQL Documentation](https://dev.mysql.com/doc/)