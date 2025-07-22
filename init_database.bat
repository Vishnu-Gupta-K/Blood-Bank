@echo off
echo This script will initialize the Blood Bank database in MySQL
echo Make sure MySQL is running and you have the necessary permissions

set /p MYSQL_USER=Enter MySQL username (default: root): 
if "%MYSQL_USER%"=="" set MYSQL_USER=root

set /p MYSQL_PASSWORD=Enter MySQL password: 

echo Creating database and tables...

REM Try to find MySQL executable in common installation paths
set MYSQL_PATH="C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"

if not exist %MYSQL_PATH% (
    set MYSQL_PATH="C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe"
)

if not exist %MYSQL_PATH% (
    set MYSQL_PATH="mysql"
    echo MySQL executable not found in standard locations, trying to use 'mysql' command directly.
)

%MYSQL_PATH% -u %MYSQL_USER% -p%MYSQL_PASSWORD% < database/init_db.sql

if %ERRORLEVEL% EQU 0 (
    echo Database initialization completed successfully!
) else (
    echo Failed to initialize database. Please check your MySQL credentials and try again.
)

pause