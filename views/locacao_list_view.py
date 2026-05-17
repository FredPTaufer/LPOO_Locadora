import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox
from control.locacao_controller import LocacaoController
from model.StatusLocacao import StatusLocacao
from views.locacao_cadastro_view import JanelaCadastroLocacao



class JanelaListagemLocacoes(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Locações - Admin")
        self.geometry("750x430")

        self.controller = LocacaoController()

        self.criar_widgets()
        self.carregar_dados()

    def criar_widgets(self):
        tk.Label(self, text="Gerenciamento de Locações (Admin)", font=("Arial", 16, "bold")).pack(pady=10)

        frame_tree = tk.Frame(self)
        frame_tree.pack(expand=True, fill="both", padx=20, pady=5)

        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side="right", fill="y")

        colunas = ("ID", "Placa", "Início", "Fim", "Status", "Estratégia")
        self.tree = ttk.Treeview(frame_tree, columns=colunas, show="headings", yscrollcommand=scrollbar.set)
        larguras = {"ID": 40, "Placa": 90, "Início": 100, "Fim": 100, "Status": 90, "Estratégia": 90}
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=larguras[col])

        self.tree.pack(expand=True, fill="both")
        scrollbar.config(command=self.tree.yview)

        frame_botoes = tk.Frame(self)
        frame_botoes.pack(fill="x", padx=20, pady=5)

        tk.Button(frame_botoes, text="Novo", width=10, command=self.abrir_novo).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Editar", width=10, command=self.abrir_editar).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Ver Detalhes", width=14, command=self.ver_detalhes).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Remover", width=10, command=self.remover_locacao).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Fechar", width=10, command=self.destroy).pack(side="right", padx=5)

    def carregar_dados(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        locacoes = self.controller.listar_locacoes()

        for loc in locacoes:
            self.tree.insert("", "end", iid=str(loc.id), values=(
                loc.id,
                loc.veiculo.placa,
                loc.data_inicio.strftime("%d/%m/%Y"),
                loc.data_fim.strftime("%d/%m/%Y"),
                loc.status.value.capitalize(),
                "VIP" if "vip" in type(loc.estrategia).__name__.lower() else "Padrao"
            ))

    def abrir_novo(self):
        janela = JanelaCadastroLocacao(self)
        self.wait_window(janela)
        self.carregar_dados()

    def abrir_editar(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma locação para editar.", parent=self)
            return

        id_loc  = int(self.tree.item(selecionado[0])["values"][0])
        locacao = self.controller.buscar_por_id(id_loc)

        if not locacao:
            messagebox.showerror("Erro", "Locação nao encontrada.", parent=self)
            return

        janela = JanelaCadastroLocacao(self, locacao=locacao)
        self.wait_window(janela)
        self.carregar_dados()

    def ver_detalhes(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma locação para ver detalhes.", parent=self)
            return

        id_loc  = int(self.tree.item(selecionado[0])["values"][0])
        locacao = self.controller.buscar_por_id(id_loc)

        if not locacao:
            messagebox.showerror("Erro", "Locação nao encontrada.", parent=self)
            return

        dias  = (locacao.data_fim - locacao.data_inicio).days or 1
        valor = locacao.calcular_valor_locacao()
        estrategia_str = "VIP" if "vip" in type(locacao.estrategia).__name__.lower() else "Padrao"

        msg = (
            f"ID:          {locacao.id}\n"
            f"Veiculo:     {locacao.veiculo.placa}  ({type(locacao.veiculo).__name__})\n"
            f"Status:      {locacao.status.value.capitalize()}\n"
            f"Estratégia:  {estrategia_str}\n\n"
            f"Início:      {locacao.data_inicio.strftime('%d/%m/%Y')}\n"
            f"Fim:         {locacao.data_fim.strftime('%d/%m/%Y')}\n"
            f"Diárias:     {dias}\n"
            f"Valor total: R$ {valor:.2f}"
        )
        messagebox.showinfo("Detalhes da Locação", msg, parent=self)

    def remover_locacao(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma locação para remover.", parent=self)
            return

        id_loc = int(self.tree.item(selecionado[0])["values"][0])
        placa  = self.tree.item(selecionado[0])["values"][1]

        resposta = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja remover a locação #{id_loc} do veículo {placa}?",
            parent=self
        )
        if resposta:
            sucesso, msg = self.controller.remover_locacao(id_loc)
            if sucesso:
                self.carregar_dados()
                messagebox.showinfo("Sucesso", msg, parent=self)
            else:
                messagebox.showerror("Erro", msg, parent=self)