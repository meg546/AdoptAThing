class Thing:
    def __init__(self, id, name, species, age, gender, description, images):
        self.id = id
        self.name = name
        self.species = species
        self.age = age
        self.gender = gender
        self.description = description
        self.images = images  # List of image URLs

    def to_dict(self):
        """Converts the object to a dictionary for easy JSON response or database storage."""
        return {
            "id": self.id,
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "gender": self.gender,
            "description": self.description,
            "images": self.images
        }
