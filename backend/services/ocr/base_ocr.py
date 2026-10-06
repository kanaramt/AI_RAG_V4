from abc import ABC, abstractmethod
import numpy as np

class BaseOCR(ABC):
    @abstractmethod
    def extract_text(self, img_array: np.ndarray) -> str:
        """
        Extract text from a decoded image array.
        """
        pass
