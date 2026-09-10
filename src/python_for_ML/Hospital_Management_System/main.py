from hospital import Hospital
from department import Department
from patient import Patient
from staff import Staff


def show_menu():
    print("\n" + "=" * 40)
    print("     HOSPITAL MANAGEMENT SYSTEM")
    print("=" * 40)

    print("1. Add Department")
    print("2. Add Patient")
    print("3. Add Staff")
    print("4. View Departments")
    print("5. View Patients")
    print("6. View Staff")
    print("7. Exit")


def add_department(hospital):
    name = input("Enter department name: ")

    department = Department(name)
    hospital.add_department(department)

    print("Department added successfully!")


def find_department(hospital):
    name = input("Enter department name: ")

    for department in hospital.departments:
        if department.name.lower() == name.lower():
            return department

    return None


def add_patient(hospital):
    if not hospital.departments:
        print("Please add a department first.")
        return

    name = input("Enter patient name: ")
    age = int(input("Enter patient age: "))
    patient_id = input("Enter patient ID: ")
    ailment = input("Enter patient ailment: ")

    department = find_department(hospital)

    if department:
        patient = Patient(name, age, patient_id, ailment)
        department.add_patient(patient)
        print("Patient added successfully!")
    else:
        print("Department not found.")


def add_staff(hospital):
    if not hospital.departments:
        print("Please add a department first.")
        return

    name = input("Enter staff name: ")
    age = int(input("Enter staff age: "))
    position = input("Enter staff position: ")

    department = find_department(hospital)

    if department:
        staff = Staff(name, age, position)
        department.add_staff(staff)
        print("Staff added successfully!")
    else:
        print("Department not found.")


def view_departments(hospital):
    print("\nDepartments:")

    if not hospital.departments:
        print("No departments available.")
    else:
        for department in hospital.departments:
            print("-", department.name)


def view_patients(hospital):
    print("\nPatients:")

    for department in hospital.departments:
        if department.patients:
            print(f"\n{department.name}:")

            for patient in department.patients:
                print(patient.view_info())


def view_staff(hospital):
    print("\nStaff:")

    for department in hospital.departments:
        if department.staff:
            print(f"\n{department.name}:")

            for staff in department.staff:
                print(staff.view_info())


def main():
    hospital_name = input("Enter hospital name: ")
    hospital_location = input("Enter hospital location: ")

    hospital = Hospital(hospital_name, hospital_location)

    print("\nHospital created successfully!")

    while True:
        show_menu()
        choice = input("\nEnter your choice: ")

        if choice == "1":
            add_department(hospital)

        elif choice == "2":
            add_patient(hospital)

        elif choice == "3":
            add_staff(hospital)

        elif choice == "4":
            view_departments(hospital)

        elif choice == "5":
            view_patients(hospital)

        elif choice == "6":
            view_staff(hospital)

        elif choice == "7":
            print("\nThank you for using Hospital Management System!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

