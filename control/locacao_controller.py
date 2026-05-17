from datetime import date
from dao.locacao_dao import LocacaoDAO
from dao.veiculo_dao import VeiculoDAO
from model.Locacao import Locacao
from model.StatusLocacao import StatusLocacao
from model.LocacaoStrategy import CalculoPadraoStrategy, CalculoVIPStrategy
from model.Categoria import Categoria


def _string_para_estrategia(valor: str):
    return CalculoVIPStrategy() if valor.strip().lower() == "vip" else CalculoPadraoStrategy()


class LocacaoController:
    def __init__(self):
        self.locacao_dao = LocacaoDAO()
        self.veiculo_dao = VeiculoDAO()

    def listar_locacoes(self):
        try:
            return self.locacao_dao.listar_todos()
        except Exception as e:
            print(f"Erro ao listar locações: {e}")
            return []

    def buscar_por_id(self, id_locacao: int):
        try:
            return self.locacao_dao.buscar_por_id(id_locacao)
        except Exception as e:
            print(f"Erro ao buscar locação: {e}")
            return None

    def buscar_veiculos_disponiveis(self, data_inicio_str: str, data_fim_str: str, categoria_str: str):
        try:
            data_inicio = date.fromisoformat(data_inicio_str)
            data_fim    = date.fromisoformat(data_fim_str)
            if data_inicio > data_fim:
                return None, "Data de início deve ser anterior ou igual à data de fim."

            categoria = Categoria[categoria_str.upper()]
            veiculos  = self.locacao_dao.buscar_veiculos_disponiveis(data_inicio, data_fim, categoria.value)
            return veiculos, None
        except KeyError:
            return None, "Categoria inválida."
        except ValueError as e:
            return None, f"Formato de data inválido: {e}"
        except Exception as e:
            return None, f"Erro ao buscar veículos disponíveis: {e}"

    def salvar_locacao_admin(self, placa: str, data_inicio_str: str, data_fim_str: str, estrategia_str: str, status_str: str):
        try:
            data_inicio = date.fromisoformat(data_inicio_str)
            data_fim    = date.fromisoformat(data_fim_str)

            if data_inicio > data_fim:
                return False, "Data de início deve ser anterior ou igual à data de fim."

            veiculo = self.veiculo_dao.buscar_por_placa(placa.strip().upper())
            if not veiculo:
                return False, "Veículo não encontrado."

            estrategia = _string_para_estrategia(estrategia_str)
            status = StatusLocacao(status_str.strip().lower())
            locacao = Locacao(veiculo, data_inicio, data_fim, estrategia, status)

            return self.locacao_dao.salvar(locacao)

        except ValueError as e:
            return False, f"Dados inválidos: {e}"
        except Exception as e:
            return False, f"Erro ao salvar locação: {e}"

    def atualizar_locacao_admin(self, id_locacao: int, placa: str, data_inicio_str: str, data_fim_str: str, estrategia_str: str, status_str: str):
        try:
            data_inicio = date.fromisoformat(data_inicio_str)
            data_fim    = date.fromisoformat(data_fim_str)

            if data_inicio > data_fim:
                return False, "Data de início deve ser anterior ou igual à data de fim."

            veiculo = self.veiculo_dao.buscar_por_placa(placa.strip().upper())
            if not veiculo:
                return False, "Veículo não encontrado."

            estrategia = _string_para_estrategia(estrategia_str)
            status     = StatusLocacao(status_str.strip().lower())
            locacao    = Locacao(veiculo, data_inicio, data_fim, estrategia, status, id=id_locacao)

            return self.locacao_dao.atualizar(locacao)

        except ValueError as e:
            return False, f"Dados inválidos: {e}"
        except Exception as e:
            return False, f"Erro ao atualizar locação: {e}"

    def remover_locacao(self, id_locacao: int):
        try:
            return self.locacao_dao.remover(id_locacao)
        except Exception as e:
            return False, f"Erro ao remover locação: {e}"

    def criar_reserva(self, placa: str, data_inicio_str: str, data_fim_str: str):
        try:
            data_inicio = date.fromisoformat(data_inicio_str)
            data_fim    = date.fromisoformat(data_fim_str)

            if data_inicio > data_fim:
                return False, "Data de início deve ser anterior ou igual à data de fim."

            veiculo = self.veiculo_dao.buscar_por_placa(placa.strip().upper())
            if not veiculo:
                return False, "Veículo não encontrado."

            locacao = Locacao(
                veiculo=veiculo,
                data_inicio=data_inicio,
                data_fim=data_fim,
                estrategia=CalculoPadraoStrategy(),
                status=StatusLocacao.RESERVADO
            )
            return self.locacao_dao.salvar(locacao)

        except ValueError as e:
            return False, f"Dados inválidos: {e}"
        except Exception as e:
            return False, f"Erro ao criar reserva: {e}"

    def locar(self, id_locacao: int):
        try:
            locacao = self.locacao_dao.buscar_por_id(id_locacao)
            if not locacao:
                return False, "Locação não encontrada."

            if locacao.status != StatusLocacao.RESERVADO:
                return False, "Só é possível locar uma reserva com status 'Reservado'."

            hoje = date.today()
            nova_data_inicio = hoje if locacao.data_inicio != hoje else None

            return self.locacao_dao.atualizar_status(
                id_locacao,
                StatusLocacao.LOCADO,
                nova_data_inicio=nova_data_inicio
            )
        except Exception as e:
            return False, f"Erro ao realizar locação: {e}"

    def devolver(self, id_locacao: int):
        try:
            locacao = self.locacao_dao.buscar_por_id(id_locacao)
            if not locacao:
                return False, "Locação não encontrada."

            if locacao.status != StatusLocacao.LOCADO:
                return False, "Só é possível devolver uma locação com status 'Locado'."

            hoje = date.today()
            if locacao.data_inicio > hoje:
                return False, (
                    "A data de início deve ser anterior à data atual para realizar a devolução. "
                    "Utilize a ação 'Cancelar' se desejar encerrar esta reserva."
                )

            sucesso, msg = self.locacao_dao.atualizar_status(
                id_locacao,
                StatusLocacao.DEVOLVIDO,
                nova_data_fim=hoje
            )
            if not sucesso:
                return False, msg

            locacao.data_fim = hoje
            dias = (hoje - locacao.data_inicio).days or 1
            valor = locacao.calcular_valor_locacao()

            detalhes = {
                "data_inicio" : locacao.data_inicio.strftime("%d/%m/%Y"),
                "data_fim"    : hoje.strftime("%d/%m/%Y"),
                "dias"        : dias,
                "valor_total" : valor
            }
            return True, detalhes

        except Exception as e:
            return False, f"Erro ao devolver veículo: {e}"

    def cancelar(self, id_locacao: int):
        try:
            locacao = self.locacao_dao.buscar_por_id(id_locacao)
            if not locacao:
                return False, "Locação não encontrada."

            if locacao.status != StatusLocacao.RESERVADO:
                return False, "Só é possível cancelar uma locação com status 'Reservado'."

            return self.locacao_dao.atualizar_status(id_locacao, StatusLocacao.CANCELADO)

        except Exception as e:
            return False, f"Erro ao cancelar locação: {e}"
