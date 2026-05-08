import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.VeiculoFactory import VeiculoFactory
from model.Categoria import Categoria
from dao.db_config import DatabaseConfig
from dao.generic_dao import GenericDAO


class VeiculoDAO(GenericDAO):
    def __init__(self):
        self.conexao = DatabaseConfig.get_connection()

    def salvar(self, objeto_veiculo):
        if not self.conexao:
            raise Exception("Não foi possível conectar ao banco de dados.")
        
        try:
            cursor = self.conexao.cursor()
            query = """
                INSERT INTO tb_veiculos (vei_placa, vei_categoria, vei_taxa_diaria, vei_estado_atual, vei_tipo)
                VALUES (%s, %s, %s, %s, %s)
            """

            cursor.execute(query, (
                objeto_veiculo.placa,
                objeto_veiculo.categoria.value,
                objeto_veiculo.taxa_diaria,
                objeto_veiculo.estado_atual.__class__.__name__.lower(),
                objeto_veiculo.__class__.__name__
            ))
            self.conexao.commit()
            return True, "Veículo cadastrado com sucesso!"

        except Exception as e:
            print(f"Erro ao inserir o veiculo: {objeto_veiculo.placa}: {e}")
            self.conexao.rollback()
            return False, "Erro ao cadastrar veículo!"
        
        finally:
            if cursor:
                cursor.close()
            
    def listar_todos(self):
        if not self.conexao:
            return []
        
        try:
            cursor = self.conexao.cursor()
            query = "SELECT vei_tipo, vei_placa, vei_taxa_diaria, vei_categoria FROM tb_veiculos"
            cursor.execute(query)
            linhas = cursor.fetchall()
            veiculos = []
            for linha in linhas:
                categoria = Categoria(linha[3])
                obj = VeiculoFactory.criar_veiculo(linha[0], linha[1], float(linha[2]), categoria)
                veiculos.append(obj)

            return veiculos
        
        except Exception as e:
            print(f"Erro ao listar veículos: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def remover(self, placa):
        if not self.conexao:
            return False, "Não foi possível conectar ao banco de dados."

        try:
            cursor = self.conexao.cursor()
            query = "DELETE FROM tb_veiculos WHERE vei_placa = %s"
            cursor.execute(query, (placa.strip().upper(),))
            if cursor.rowcount == 0:
                self.conexao.rollback()
                return False, "Veículo não encontrado para remoção."

            self.conexao.commit()
            return True, "Veículo removido com sucesso!"
        except Exception as e:
            print(f"Erro ao remover veículo {placa}: {e}")
            self.conexao.rollback()
            return False, "Erro ao remover veículo."
        finally:
            if cursor:
                cursor.close()

    def atualizar(self, objeto):
        if not self.conexao:
            return False, "Não foi possível conectar ao banco de dados."

        try:
            cursor = self.conexao.cursor()
            query = """
                UPDATE tb_veiculos
                SET vei_tipo = %s,
                    vei_categoria = %s,
                    vei_taxa_diaria = %s
                WHERE vei_placa = %s
            """
            cursor.execute(query, (
                objeto.__class__.__name__.lower(),
                objeto.categoria.value,
                objeto.taxa_diaria,
                objeto.placa
            ))

            if cursor.rowcount == 0:
                self.conexao.rollback()
                return False, "Veículo não encontrado para atualização."

            self.conexao.commit()
            return True, "Veículo atualizado com sucesso!"
        except Exception as e:
            print(f"Erro ao atualizar veículo {objeto.placa}: {e}")
            self.conexao.rollback()
            return False, "Erro ao atualizar veículo."
        finally:
            if cursor:
                cursor.close()

    def buscar_por_placa(self, placa_str : str):
        if not self.conexao:
            return None

        try:
            cursor = self.conexao.cursor()
            query = "SELECT vei_tipo, vei_placa, vei_taxa_diaria, vei_categoria FROM tb_veiculos WHERE vei_placa = %s"
            cursor.execute(query, (placa_str.strip().upper(),))
            linha = cursor.fetchone()
            if linha:
                categoria = Categoria(linha[3])
                return VeiculoFactory.criar_veiculo(linha[0], linha[1], float(linha[2]), categoria)
            return None
        except Exception as e:
            print(f"Erro ao buscar veículo por placa: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
