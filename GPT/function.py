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
        self.properties: list[Parameter] = []
        self.required_names: list[str] = []

    def __repr__(self) -> str:
        return f"<ParameterManager {self.properties}>"

    def add_parameter(
        self,
        name: str,
        parameter_type: ParameterType,
        description: str = "",
        enum: list | None = None,
        required: bool = False,
    ):
        parameter = Parameter(
            name=name,
            parameter_type=parameter_type,
            description=description,
            enum=enum,
        )
        self.properties.append(parameter)
        if required:
            self.required_names.append(name)

    def make_dict(self):
        properties = {}
        for propertie in self.properties:
            properties.update(propertie.make_dict())

        parameters = {
            "type": "object",
            "properties": properties,
        }
        if self.required_names:
            parameters["required"] = self.required_names
        return parameters


class Function:
    name: str
    description: str

    def __init__(self):
        self.parameters = ParameterManager()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} description={self.description} >"

    def set_parameter(self):
        raise NotImplementedError

    async def run(self, **kwargs):
        raise NotImplementedError

    def make_dict(self):
        if not self.name:
            ValueError("name is not set")
        func = {
            "name": self.name,
            "parameters": self.parameters.make_dict(),
        }
        if self.description:
            func["description"] = self.description
        return func


class Myfunction(Function):
    name = "get_current_weather"
    description = "Get the current weather in a given location"

    def set_parameter(self):
        self.parameters.add_parameter(
            name="location",
            parameter_type=ParameterType.string,
            description="The city and state, e.g. San Francisco, CA",
            required=True,
        )
        self.parameters.add_parameter(
            name="unit",
            parameter_type=ParameterType.string,
            enum=["celsius", "fahrenheit"],
        )

    async def run():
        pass


class FunctionManager:
    def __init__(self):
        self.function_list: list[Function] = []
        self.find_subclasses()

    def find_subclasses(self):
        for cls in Function.__subclasses__():
            if cls not in self.function_list:
                obj = cls()
                obj.set_parameter()
                self.function_list.append(obj)

    def make_dict(self):
        functions = []
        for function in self.function_list:
            functions.append(function.make_dict())
        return functions
