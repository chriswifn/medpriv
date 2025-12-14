import os


class File:
    """File Class to represent a file."""

    def __init__(self, name: str, check_existence=None) -> None:
        self.check_existence = check_existence if check_existence is not None else False
        if check_existence and not self._file_exists(name):
            raise ValueError(f"File {name} does not exist.")
        self.name = os.path.abspath(name)

    @staticmethod
    def _file_exists(name: str) -> bool:
        """Check if a file exists.

        Args:
            name (str): The name of the file

        Returns:
            bool: whether the file exists.
        """
        return os.path.exists(name)

    def to_dict(self) -> str:
        """Returns the file path.

        Returns:
            str: the name of the file associated with the File Object.
        """
        return self.name

    @classmethod
    def from_dict(cls, name: str) -> "File":
        """Creates a File object from a give file path."""
        return cls(name)
