from person import Person

class Staff (Person):

    """Represents hospital staff with name, age, and position attributes."""

    def __init__(self, name , age , position):
        super().__init__(name, age)
        self.position = position

    def view_info (self) -> str:
        """
        Returns staff details.

        Returns:
            Name, age, and position info.
        """
        return f" Staff Name :{self.name} , age : {self.age} , position : {self.position}"    
