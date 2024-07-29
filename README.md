# About

The Medical Directory and Information Contact System (MEDICS) was developed for an undergraduate capstone project. This repository contains the application's API written in Python using the Flask framework. This application was initially deployed using Azure infrastracture. It is designed to work with MySQL databases. It has 4 core features: medical appointment, incident reporting, medicine logging, and data analytics. The mobile application is written in Dart and uses the Flutter SDK. It is built specifically for Android users.

## Modules

The MEDICS application is modular and therefore can be expanded and shrunk according to the requirements of a medical institution.

#### api.py

This module is the core of the application. It imports all other modules. This is required by the Flask framework.

#### msgs.py

This module contains the standard JSON success and failure responses of the API.

#### app.py 

This module contains the necessary routes for the Android app to function.

#### api.py

This module contains the API, which is comprised of basic HTTPS methods ```(GET/POST/PUT/DEL)```.

#### web.py

This module contains routes that make the web console of MEDICS function. It is designed to be used by clinic nurses and doctors to create, edit, delete, and display data.

#### logger.py

This is a utility module that logs the errors of the application and outputs it into a file called ```app.log```.

#### analytics.py

This module powers the data visualization and analytics part of the application. 

## Requirements

1. Python 3.9 above (For deployment in Azure)

2. MySQL Database (Local or Web hosted)

## Required Libraries
```
Flask
flask-jwt-extended
gunicorn
pyodbc
jsonify
pandas
matplotlib
Jinja2
xhtml2pdf
sqlalchemy
```