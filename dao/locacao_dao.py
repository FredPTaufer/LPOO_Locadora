import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date
from dao.db_config import DatabaseConfig
from dao.generic_dao import GenericDAO
from model.VeiculoFactory import VeiculoFactory
from model.Categoria import Categoria
from model.LocacaoStrategy import CalculoPadraoStrategy, CalculoVIPStrategy
from model.StatusLocacao import StatusLocacao
from model.Locacao import Locacao


def _estrategia_para_string(estrategia) -> str:
    return "vip" if isinstance(estrategia, CalculoVIPStrategy) else "padrao"


def _string_para_estrategia(valor: str):
    return CalculoVIPStrategy() if valor == "vip" else CalculoPadraoStrategy()


class LocacaoDAO(GenericDAO):
    def __init__(self):
        self.conexao = DatabaseConfig.get_connection()

    def salvar(self, locacao: Locacao):
        if not self.conexao:
            return False, "Não foi possível conectar ao banco de dados."
        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """
                INSERT INTO tb_locacoes
                    (loc_placa_veiculo, loc_data_inicio, loc_data_fim, loc_status, loc_estrategia)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING loc_id
            """
            cursor.execute(query, (
                locacao.veiculo.placa,
                locacao.data_inicio,
                locacao.data_fim,
                locacao.status.value,
                _estrategia_para_string(locacao.estrategia)
            ))
            novo_id = cursor.fetchone()[0]
            self.conexao.commit()
            locacao.id = novo_id
            return True, "Locação cadastrada com sucesso!"
        except Exception as e:
            self.conexao.rollback()
            return False, f"Erro ao cadastrar locação: {e}"
        finally:
            if cursor:
                cursor.close()

    def listar_todos(self):
        if not self.conexao:
            return []
        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """
                SELECT l.loc_id, l.loc_placa_veiculo, l.loc_data_inicio,
                       l.loc_data_fim, l.loc_status, l.loc_estrategia,
                       v.vei_tipo, v.vei_taxa_diaria, v.vei_categoria
                FROM tb_locacoes l
                JOIN tb_veiculos v ON v.vei_placa = l.loc_placa_veiculo
                ORDER BY
                    CASE l.loc_status
                        WHEN 'locado'    THEN 1
                        WHEN 'reservado' THEN 2
                        WHEN 'devolvido' THEN 3
                        WHEN 'cancelado' THEN 4
                    END,
                    l.loc_data_fim ASC
            """
            cursor.execute(query)
            return [self._montar_locacao(linha) for linha in cursor.fetchall()]
        except Exception as e:
            print(f"Erro ao listar locações: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def remover(self, id_locacao: int):
        if not self.conexao:
            return False, "Não foi possível conectar ao banco de dados."
        cursor = None
        try:
            cursor = self.conexao.cursor()
            cursor.execute("DELETE FROM tb_locacoes WHERE loc_id = %s", (id_locacao,))
            if cursor.rowcount == 0:
                self.conexao.rollback()
                return False, "Locação não encontrada para remoção."
            self.conexao.commit()
            return True, "Locação removida com sucesso!"
        except Exception as e:
            self.conexao.rollback()
            return False, f"Erro ao remover locação: {e}"
        finally:
            if cursor:
                cursor.close()

    def atualizar(self, locacao: Locacao):
        if not self.conexao:
            return False, "Não foi possível conectar ao banco de dados."
        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """
                UPDATE tb_locacoes
                SET loc_placa_veiculo = %s,
                    loc_data_inicio   = %s,
                    loc_data_fim      = %s,
                    loc_status        = %s,
                    loc_estrategia    = %s
                WHERE loc_id = %s
            """
            cursor.execute(query, (
                locacao.veiculo.placa,
                locacao.data_inicio,
                locacao.data_fim,
                locacao.status.value,
                _estrategia_para_string(locacao.estrategia),
                locacao.id
            ))
            if cursor.rowcount == 0:
                self.conexao.rollback()
                return False, "Locação não encontrada para atualização."
            self.conexao.commit()
            return True, "Locação atualizada com sucesso!"
        except Exception as e:
            self.conexao.rollback()
            return False, f"Erro ao atualizar locação: {e}"
        finally:
            if cursor:
                cursor.close()

    def buscar_por_id(self, id_locacao: int):
        if not self.conexao:
            return None
        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """
                SELECT l.loc_id, l.loc_placa_veiculo, l.loc_data_inicio,
                       l.loc_data_fim, l.loc_status, l.loc_estrategia,
                       v.vei_tipo, v.vei_taxa_diaria, v.vei_categoria
                FROM tb_locacoes l
                JOIN tb_veiculos v ON v.vei_placa = l.loc_placa_veiculo
                WHERE l.loc_id = %s
            """
            cursor.execute(query, (id_locacao,))
            linha = cursor.fetchone()
            return self._montar_locacao(linha) if linha else None
        except Exception as e:
            print(f"Erro ao buscar locação: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def atualizar_status(self, id_locacao: int, novo_status: StatusLocacao, nova_data_inicio: date = None, nova_data_fim: date = None):
        if not self.conexao:
            return False, "Não foi possível conectar ao banco de dados."
        cursor = None
        try:
            cursor = self.conexao.cursor()

            campos = ["loc_status = %s"]
            valores = [novo_status.value]

            if nova_data_inicio is not None:
                campos.append("loc_data_inicio = %s")
                valores.append(nova_data_inicio)

            if nova_data_fim is not None:
                campos.append("loc_data_fim = %s")
                valores.append(nova_data_fim)

            valores.append(id_locacao)
            query = f"UPDATE tb_locacoes SET {', '.join(campos)} WHERE loc_id = %s"

            cursor.execute(query, tuple(valores))
            if cursor.rowcount == 0:
                self.conexao.rollback()
                return False, "Locação não encontrada."
            self.conexao.commit()
            return True, "Status atualizado com sucesso!"
        except Exception as e:
            self.conexao.rollback()
            return False, f"Erro ao atualizar status: {e}"
        finally:
            if cursor:
                cursor.close()

    def buscar_veiculos_disponiveis(self, data_inicio: date, data_fim: date, categoria: str):
        if not self.conexao:
            return []
        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """
                SELECT v.vei_tipo, v.vei_placa, v.vei_taxa_diaria, v.vei_categoria
                FROM tb_veiculos v
                WHERE v.vei_categoria = %s
                AND NOT EXISTS (
                    SELECT 1 FROM tb_locacoes l
                    WHERE l.loc_placa_veiculo = v.vei_placa
                    AND   l.loc_status IN ('reservado', 'locado')
                    AND   l.loc_data_inicio <= %s
                    AND   l.loc_data_fim    >= %s
                )
            """
            cursor.execute(query, (categoria, data_fim, data_inicio))
            linhas = cursor.fetchall()
            veiculos = []
            for linha in linhas:
                cat = Categoria(linha[3])
                obj = VeiculoFactory.criar_veiculo(linha[0], linha[1], float(linha[2]), cat)
                veiculos.append(obj)
            return veiculos
        except Exception as e:
            print(f"Erro ao buscar veículos disponíveis: {e}")
            return []
        finally:
            if cursor:
                cursor.close()


    def _montar_locacao(self, linha):
        (loc_id, placa, data_inicio, data_fim, status_str, estrategia_str, vei_tipo, vei_taxa, vei_cat) = linha

        categoria  = Categoria(vei_cat)
        veiculo    = VeiculoFactory.criar_veiculo(vei_tipo, placa, float(vei_taxa), categoria)
        estrategia = _string_para_estrategia(estrategia_str)
        status     = StatusLocacao(status_str)

        return Locacao(
            veiculo=veiculo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            estrategia=estrategia,
            status=status,
            id=loc_id
        )
