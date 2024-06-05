class Material:
    def __init__(self, name: str, maxDeformation: float):
        self.name = name
        self.maximum_deformation = maxDeformation
    
    def get_name(self) -> str:
        return self.name
    
    def get_max_deformation(self) -> float:
        return self.maximum_deformation
    
    def get_dict(self) -> 'dict[str,object]':
        return {"Name": self.name, "MaximumDeformation": self.maximum_deformation}