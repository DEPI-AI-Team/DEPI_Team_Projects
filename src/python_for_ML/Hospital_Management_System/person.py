class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def view_info(self):
        return f"Name: {self.name}, Age: {self.age}"

    def __str__(self):
        return f"person (name= '{self.name}', age={self.age})"


    
