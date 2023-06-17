class ParameterType:
    string = "string"
    integer = "integer"
    number = "number"
    boolean = "boolean"


class Parameter:
    def __init__(
        self,
        name: str,
        parameter_type: ParameterType,
        description: str,
        enum: list | None = None,
    ):
        self.name = name
        self.parameter_type = parameter_type
        self.description = description
        self.enum = enum

    def __repr__(self):
        return f"<Parameter name={self.name} type={self.parameter_type} >"

    def make_dict(self):
        detail = {}
        detail["type"] = self.parameter_type
        detail["description"] = self.description
        if self.enum:
            detail["enum"] = self.enum
        return {self.name: detail}


class ParameterManager:
    def __init__(self):
        self.parameters: list[Parameter] = []
        self.required_names: list[str] = []

    def __repr__(self) -> str:
        return f"<ParameterManager {self.parameters}>"

    def add_parameter(
        self,
        name: str,
        parameter_type: ParameterType,
        description: str,
        enum: list | None = None,
        required: bool = True,
    ):
        parameter = Parameter(
            name=name,
            parameter_type=parameter_type,
            description=description,
            enum=enum,
        )
        self.parameters.append(parameter)
        if required:
            self.required_names.append(name)

    def make_dict(self):
        parameters = {}
        for parameter in self.parameters:
            parameters.update(parameter.make_dict())
        return {
            "type": "object",
            "parameters": parameters,
            "required": self.required_names,
        }


class Function:
    name: str
    description: str

    def __init__(self):
        self.parameters = ParameterManager()

    def set_parameter(self):
        raise NotImplementedError

    async def run(self, **kwargs):
        raise NotImplementedError

    def make_dict(self):
        if not self.name or not self.description:
            ValueError("name or description is not set")
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters.make_dict(),
        }


class Myfunction(Function):
    name = "get_current_weather"
    description = "Get the current weather in a given location"

    async def run():
        pass


class FunctionManager:
    def __init__(self):
        self.function_list = []
        self.find_subclasses()

    def find_subclasses(self):
        for cls in Function.__subclasses__():
            if cls not in self.function_list:
                self.function_list.append(cls)
