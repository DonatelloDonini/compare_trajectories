class FileOpeningError(Exception):
    def __init__(self, filename: str, message: str= None):
        self.filename = filename
        self.message = message if message is not None else f"Error opening file {filename}."
        super().__init__(self.message)

class EmptyFileError(Exception):
    def __init__(self, filename: str, message: str= None):
        self.filename = filename
        self.message = message if message is not None else f"File {filename} is empty."
        super().__init__(self.message)

class UnexistentRequiredColumn(Exception):
    def __init__(self, column_name: str, message: str= None, filename: str= None):
        self.column_name = column_name
        self.message = message if message is not None else f"The required column '{column_name}' does not exist in the file{' '+filename if filename is not None else ''}."
        super().__init__(self.message)