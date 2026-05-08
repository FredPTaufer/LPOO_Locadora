from abc import ABC, abstractmethod
from .Categoria import Categoria
from .ExcecoesPersonalizadas import PlacaInvalidaError, DataInvalidaError
from .Estados_Veiculo import DisponivelState

class Veiculo(ABC):
    def __init__(self, placa: str, taxa_diaria: float, categoria: Categoria = Categoria.ECONOMICO):
        self.placa = placa
        self.categoria = categoria
        self.taxa_diaria = taxa_diaria
        self.estado_atual = DisponivelState(self)
    
    @property
    def placa(self):
        return self.__placa
    
    @placa.setter
    def placa(self, valor):
        valor_normalizado = valor.strip().replace("-", "").upper()
        if self.validar_placa(valor_normalizado):
            self.__placa = valor_normalizado
    
    @property
    def taxa_diaria(self):
        return self.__taxa_diaria
    
    @taxa_diaria.setter
    def taxa_diaria(self, valor):
        if valor <= 0:
            raise ValueError("Taxa diária deve ser um valor positivo")
        self.__taxa_diaria = valor

    def validar_placa(self, placa):
        if (len(placa) != 7):
            raise PlacaInvalidaError("Placa inválida: deve conter exatamente 7 caracteres.")
        else:
            if not placa[0:3].isalpha():
                raise PlacaInvalidaError("Placa inválida: os três primeiros caracteres devem ser letras.")
            if not placa[3].isdigit() or not placa[5:7].isdigit():
                raise PlacaInvalidaError("Placa inválida: os caracteres 4, 6 e 7 devem ser números.")
            elif not placa[4].isalnum():
                raise PlacaInvalidaError("Placa inválida: o caractere 5 deve ser uma letra ou um número.")
            else:    
                #print(f"Placa '{placa}' válida.")
                return True 
    
    @property
    def categoria(self):
        return self.__categoria
    
    @categoria.setter
    def categoria(self, valor):
        self.__categoria = valor
    
    @abstractmethod
    def calcular_diaria(self):
        pass
    
    @property
    def estado_atual(self):
        return self._estado_atual

    @estado_atual.setter
    def estado_atual(self, novo_estado):
        self._estado_atual = novo_estado
        
    def tentar_alugar(self):
        self.estado_atual.alugar()
        
    def tentar_devolver(self):
        self.estado_atual.devolver()
        
    def reter_na_frota_pra_conserto(self):
        self.estado_atual.enviar_manutencao()
    
    def exibir_dados(self):
        return (
            f"Placa: {self.placa}\n"
            f"Tipo: {self.__class__.__name__}\n"
            f"Categoria: {self.categoria.value}\n"
            f"Taxa diária: R$ {self.taxa_diaria:.2f}\n"
            f"Estado: {getattr(self.estado_atual, '__class__', type(self.estado_atual)).__name__.replace('State', '')}"
        )

    def __str__(self):
        return f"Veículo: {self.placa} - Categoria: {self.categoria.value} - Taxa: R$ {self.taxa_diaria:.2f}"
