import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from views.veiculo_list_view import JanelaListagemVeiculos
from views.locacao_list_view import JanelaListagemLocacoes
from views.locacao_usuario_view import JanelaLocacaoUsuario


class JanelaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Locadora de Veículos")
        self.geometry("400x220")
        self.resizable(True, True)

        self._criar_menu()
        self._criar_tela_inicial()

    def _criar_menu(self):
        barra_menu = tk.Menu(self)
        self.config(menu=barra_menu)

        menu_cadastro = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Cadastro", menu=menu_cadastro)
        menu_cadastro.add_command(label="Veículos", command=self._abrir_veiculos)
        menu_cadastro.add_command(label="Locações (Admin)", command=self._abrir_locacoes_admin)

        menu_acao = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Ação", menu=menu_acao)
        menu_acao.add_command(label="Locar Veículo", command=self._abrir_locacoes_usuario)

    def _criar_tela_inicial(self):
        tk.Label(self, text="Locadora de Veículos", font=("Helvetica", 18, "bold")).pack(pady=(30, 5))
        tk.Label(self, text="Utilize o menu acima para navegar pelo sistema.", font=("Helvetica", 10), fg="gray").pack(pady=5)
        tk.Frame(self, height=1, bg="lightgray").pack(fill="x", padx=20, pady=12)
        tk.Label(self, text="Cadastro: Veículos / Locações (Admin)  |  Ação: Locar Veículo", font=("Helvetica", 8), fg="gray").pack()

    def _abrir_veiculos(self):
        janela = JanelaListagemVeiculos(self)
        self.wait_window(janela)

    def _abrir_locacoes_admin(self):
        janela = JanelaListagemLocacoes(self)
        self.wait_window(janela)

    def _abrir_locacoes_usuario(self):
        janela = JanelaLocacaoUsuario(self)
        self.wait_window(janela)