from datetime import datetime, date
from .Veiculo import Veiculo
from .LocacaoStrategy import CalculoLocacaoStrategy, CalculoPadraoStrategy, CalculoVIPStrategy
from .ExcecoesPersonalizadas import DataInvalidaError, ExcecaoValorInvalido


class Locacao:
    def __init__(self, veiculo: Veiculo, data_inicio: date, data_fim: date, estrategia: CalculoLocacaoStrategy = CalculoPadraoStrategy()):
        
        if data_inicio > data_fim:
            raise DataInvalidaError("Data de início deve ser anterior ou igual à data de fim")
        
        
        self.veiculo = veiculo
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.estrategia = estrategia

    
    @property
    def veiculo(self):
        return self.__veiculo
    
    @veiculo.setter
    def veiculo(self, valor):
        if(valor is not None):
            self.__veiculo = valor
        else:
            raise Exception("Objeto Veículo não pode ser None!")
    
    @property
    def data_inicio(self):
        return self.__data_inicio
    
    @data_inicio.setter
    def data_inicio(self, valor):
        self.__data_inicio = valor
    
    @property
    def data_fim(self):
        return self.__data_fim
    
    @data_fim.setter
    def data_fim(self, valor):
        self.__data_fim = valor
    
    def calcular_valor_locacao(self) -> float:
        dias = (self.data_fim - self.data_inicio).days
        
        if dias == 0:
            dias = 1
        
        if dias < 0:
            raise ExcecaoValorInvalido("Número de dias não pode ser negativo")
        
        #diaria = self.veiculo.calcular_diaria()
        #seguro = self.veiculo.valor_seguro
        #valor_total = (diaria * dias) + seguro
        valor_total = self.estrategia.calcular_diarias(self.veiculo, dias)
        
        if valor_total < 0:
            raise ExcecaoValorInvalido("Valor total não pode ser negativo")
        
        return valor_total
    
    
    def __str__(self):
        dias = (self.data_fim - self.data_inicio).days
        dias_cobrados = 1 if dias == 0 else dias
        valor = self.calcular_valor_locacao()
        return (f"Locação: {self.veiculo.placa}\n"
                f"  De: {self.data_inicio.strftime('%d/%m/%Y')} "
                f"até {self.data_fim.strftime('%d/%m/%Y')}\n"
                f"  Dias: {dias_cobrados}\n"
                f"  Valor Total: R$ {valor:.2f}")
