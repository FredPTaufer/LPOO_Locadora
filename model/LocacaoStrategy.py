from abc import ABC, abstractmethod
from .Veiculo import Veiculo

class CalculoLocacaoStrategy(ABC):
    @abstractmethod
    def calcular_diarias(self, veiculo: Veiculo, dias: int):
        pass

class CalculoPadraoStrategy(CalculoLocacaoStrategy):
    def calcular_diarias(self, veiculo: Veiculo, dias: int):
        valor_diarias = veiculo.taxa_diaria * dias
        return (valor_diarias + veiculo.valor_seguro)
    

class CalculoVIPStrategy(CalculoLocacaoStrategy):
    def calcular_diarias(self, veiculo: Veiculo, dias: int) -> float:
        valor_diarias = (veiculo.taxa_diaria * dias) * 0.8
        return (valor_diarias + veiculo.valor_seguro) 