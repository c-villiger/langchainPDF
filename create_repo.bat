@echo off
SETLOCAL

REM Check if the virtual environment already exists, if not, create and activate it
IF NOT EXIST .venv (
    echo Creating a new virtual environment...
    python -m venv .venv
    echo Activating the virtual environment...
    call .venv\Scripts\activate.bat
) ELSE (
    echo Virtual environment already exists.
    echo Activating the existing virtual environment...
    call .venv\Scripts\activate.bat
)


REM Check if requirements.txt exists and install packages or create one
IF EXIST requirements.txt (
    echo Installing packages from requirements.txt...
    pip install -r requirements.txt
) ELSE (
    echo Creating a new requirements.txt file...
    type nul > requirements.txt
    echo "Delete this line! Note: include version of dependency, e.g.: pandas== 2.0.1" >> requirements.txt
)

REM Create a .gitignore file if not exists
IF NOT EXIST .gitignore (
    echo Creating a .gitignore file...
    echo __pycache__ >> .gitignore
    echo .venv >> .gitignore
)

REM Create a README.md file with the title of the working directory folder
IF NOT EXIST README.md (
    echo Creating a README.md file...
    FOR %%i IN ("%CD%") DO echo # %%~ni > README.md
)

REM Create a folder with the working directory name in lowercase
FOR %%i IN ("%CD%") DO SET "folder_name=%%~ni"
SET "folder_name_lower=%folder_name:~0%"
echo Creating a new folder: %folder_name_lower%
mkdir %folder_name_lower%

REM Add an empty __init__.py file
echo Creating an empty __init__.py file...
echo. 2> %folder_name_lower%\__init__.py

REM Create a main.py file in the working directory
IF NOT EXIST main.py (
    echo Creating a main.py file...
    echo. 2> main.py
)

REM Create a lib folder
mkdir lib

REM Initialize a Git repository
echo Initializing a Git repository...
git init

echo Done!

pause
ENDLOCAL