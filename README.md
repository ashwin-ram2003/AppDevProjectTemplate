# ECE 461L Project Info
Software Engineering Team Project
# Project Overview

This project is a web application for managing users, projects, and shared resources. The application uses React for the front end, Flask for the back end, and MongoDB for data storage. The main functionality includes user authentication, project management, resource availability, resource checkout/check-in, and automated testing.

## 1. Technology Stack

This file is the main entry point of the application. It sets up the Flask web server and defines various routes for handling user requests.

Front End: React.js

Back End: Python / Flask

Database: MongoDB

Testing: Pytest

Version Control: Git / GitHub

Deployment: Heroku

## 2. Application Components

**User Management:**
Handles user accounts and authentication.
Main functions:

-Create a user account

-Log in and log out

-Securely store user credentials

-Authenticate users

**Project Management**
Handles project creation and membership.
Main functions:

-Create a new project

-Access an existing project

-Join a project using a project ID

-Store project name, description, and project ID

-Track users associated with a project

**Resource Management**
Handles the application's shared resources.
Main functions:

-View resource capacity

-View current resource availability

-Request available resource units

-Check out resource units

-Reject requests exceeding available capacity

-Check resource units back in

-Prevent users from checking in more units than their project has checked out

-Update resource availability after checkout/check-in

**Database**
MongoDB stores persistent application data.
Main data collections include:

-Users

-Projects

-Resources

The database is accessed through the Flask API.

**Back-end API**
The Flask backend provides the API between the React front end and MongoDB.
Main functions:

-Handle user authentication

-Manage users

-Create and access projects

-Manage project membership

-Check resource availability

-Process resource check-in and checkout

**Front-end**
The React front end provides the user interface for the application.
Main screens/functionality include:

-User sign-in and account creation

-Project creation and access

-Project resource management

-Resource availability

-Resource check-in and checkout

## 3. Testing
Pytest is used for automated testing.
Testing includes:

-API endpoints

-Database logic

-Check-in and checkout functionality
