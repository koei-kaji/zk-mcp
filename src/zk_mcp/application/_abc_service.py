import abc

from .._base_models.base_model import BaseFrozenModel
from ._abc_input import ABCInput
from ._abc_output import ABCOutput


class ABCService(BaseFrozenModel):
    @abc.abstractmethod
    def handle(self, input: ABCInput) -> ABCOutput: ...
