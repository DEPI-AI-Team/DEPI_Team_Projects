# Hospital Management System

## Description

The Hospital Management System is a Python project developed using Object-Oriented Programming (OOP).

The system is designed to manage basic hospital information, departments, patients, and staff members.

## Project Structure

* `person.py` - Contains the base `Person` class.
* `patient.py` - Contains the `Patient` class.
* `staff.py` - Contains the `Staff` class.
* `department.py` - Manages patients and staff within a department.
* `hospital.py` - Manages hospital information and departments.
* `main.py` - Runs the Hospital Management System and provides the user interface.

## Classes

### Person

The base class that contains common information such as name and age.

### Patient

Inherits from `Person` and stores patient information such as patient ID and ailment.

### Staff

Inherits from `Person` and stores staff information such as their position.

### Department

Manages the patients and staff members belonging to a department.

### Hospital

Stores hospital information and manages its departments.

## OOP Concepts

The project demonstrates:

* Classes and Objects
* Inheritance
* Methods
* Object Relationships

## How to Run

Run the `main.py` file:

```bash
python main.py
```

Then follow the instructions displayed in the terminal.

## Technologies

* Python
* Object-Oriented Programming (OOP)

## Project Goal

The goal of this project is to practice Object-Oriented Programming concepts by building a simple Hospital Management System.
