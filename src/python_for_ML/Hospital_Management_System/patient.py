from person import Person
class Patient(Person):
    def __init__(self, name, age, patient_id, ailment):
        super().__init__(name, age)
        self.patient_id = patient_id
        self.ailment = ailment

    def view_info(self):
        return f"Patient ID: {self.patient_id}, Name: {self.name}, Age: {self.age}, Ailment: {self.ailment}"

    def __str__(self):
        return f"patient (patient_id={self.patient_id}, name='{self.name}', age={self.age}, ailment='{self.ailment}')"

if __name__ == "__main__":
    patient = Patient("abdulrrahman", 30, "P12345", "Flu")
    print(patient.view_info())
    print(patient)    