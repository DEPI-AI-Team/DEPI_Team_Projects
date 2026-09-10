class Department:
    """Represents a hospital department."""

    def __init__(self, name):
        """Initialize a department with a name and empty patient and staff lists."""
        self.name = name
        self.patients = []
        self.staff = []

    def add_patient(self, patient):
        """Add a patient to the department."""
        self.patients.append(patient)

    def add_staff(self, staff):
        """Add a staff member to the department."""
        self.staff.append(staff)