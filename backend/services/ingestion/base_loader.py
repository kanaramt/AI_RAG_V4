from abc import ABC, abstractmethod
from pathlib import Path


class BaseLoader(ABC):
    """
    Abstract base class for all document loaders.
    """

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    @abstractmethod
    def load(self) -> str:
        """
        Read the document and return its extracted text.
        """
        pass

    def exists(self) -> bool:
        """
        Check whether the document exists.
        """
        return self.file_path.exists()

    @property
    def filename(self) -> str:
        """
        Return the document filename.
        """
        return self.file_path.name

    @property
    def extension(self) -> str:
        """
        Return the document extension.
        """
        return self.file_path.suffix.lower()
