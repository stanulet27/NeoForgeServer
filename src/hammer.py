class Hammer:
    def __init__(self, name: str, size_x: float, size_y: float):
        self.name = name
        self.size_x = size_x
        self.size_y = size_y
    
    def get_dict(self) -> 'dict[str,object]':
        return {"Name": self.name, "SizeX": self.size_x, "SizeY": self.size_y}