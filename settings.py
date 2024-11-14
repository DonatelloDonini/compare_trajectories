import json

class Settings:
    def __init__(self, path) -> None:
        self.path= path
        with open(path) as settings:
            self.data = json.load(settings)

    def get(self, setting_name, default=None):
        nestings= setting_name.split(".")

        current= self.data
        for nesting in nestings:
            current= current.get(nesting, None)
            if current is None:
                return default

        try:
            if current.get("value") is not None:
                return current["value"]
        except AttributeError:
            return current

    def describe(self, setting_name):
        if self.data.get(setting_name, None) is not None and self.data[setting_name].get("description", None) is not None:
            return self.data[setting_name]["description"]
        else:
            return "This setting does not have a description specified."

    def get_type(self, setting_name):
        if self.data.get(setting_name, None) is not None and self.data[setting_name].get("type", None) is not None:
            return self.data[setting_name]["type"]
        else:
            return "This setting does not have a type specified."

    def __str__(self) -> str:
        return str(self.data)