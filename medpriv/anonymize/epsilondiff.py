from .anonymizer import Anonymizer
from medpriv.data_processing import EpsilonData
from medpriv.utils import sample_geometric
import numpy as np


class EpsilonAnonymizer(Anonymizer):
    """Epsilon Differential Privacy."""

    def __init__(self, epsilon: float, data: EpsilonData):
        super().__init__(data)
        self.epsilon = epsilon

    def anonymize(self) -> None:
        """Geometric algorithm to achieve epsilon-differential privacy."""
        sensitivity = 1
        b = sensitivity / self.epsilon
        noise = np.random.laplace(0, b, size=self.data.histogram.shape)
        noisy_result = self.data.histogram + noise
        self.data.histogram = noisy_result

    def geometric_algorithm(self):
        """Geometric algorithm to achieve epsilon-differential privacy."""
        sensitivity = 1

        # calculate alpha
        alpha = np.exp(-self.epsilon / sensitivity)

        # Generate geometric noise for each element in the histogram
        shape = self.data.histogram.shape
        noise = np.array([[sample_geometric(alpha) for _ in range(shape[1])] for _ in range(shape[0])])

        # Add noise to the query result
        noisy_result = self.data.histogram + noise

        self.data.histogram = noisy_result
