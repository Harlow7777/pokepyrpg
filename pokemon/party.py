class Party:
    def __init__(self):
        self.members = []  # List of Pokemon

    def add_pokemon(self, pokemon):
        if len(self.members) < 4:
            self.members.append(pokemon)
        else:
            print("Party is full.")
