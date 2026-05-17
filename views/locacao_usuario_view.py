import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox
from control.locacao_controller import LocacaoController
from model.StatusLocacao import StatusLocacao
from views.locacao_nova_reserva_view import JanelaNovaReserva


class JanelaLocacaoUsuario(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Locar Veículo")
        self.geometry("700x420")

        self.controller = LocacaoController()

        self.criar_widgets()
        self.carregar_dados()

    def criar_widgets(self):
        tk.Label(self, text="Locações - Visão Operacional", font=("Arial", 16, "bold")).pack(pady=10)

        frame_tree = tk.Frame(self)
        frame_tree.pack(expand=True, fill="both", padx=20, pady=5)

        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side="right", fill="y")

        colunas = ("ID", "Placa", "Início", "Fim", "Status", "Estratégia")
        self.tree = ttk.Treeview(frame_tree, columns=colunas, show="headings", yscrollcommand=scrollbar.set)
        larguras = {"ID": 40, "Placa": 80, "Início": 90, "Fim": 90, "Status": 90, "Estratégia": 80}
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=larguras[col])

        self.tree.pack(expand=True, fill="both")
        scrollbar.config(command=self.tree.yview)

        self.tree.bind("<<TreeviewSelect>>", self._atualizar_botoes)

        frame_botoes = tk.Frame(self)
        frame_botoes.pack(fill="x", padx=20, pady=5)

        self.btn_nova_reserva = tk.Button(frame_botoes, text="Nova Reserva", width=14, command=self.abrir_nova_reserva)
        self.btn_nova_reserva.pack(side="left", padx=5)

        self.btn_locar = tk.Button(frame_botoes, text="Locar", width=10, command=self.locar, state="disabled")
        self.btn_locar.pack(side="left", padx=5)

        self.btn_devolver = tk.Button(frame_botoes, text="Devolver", width=10, command=self.devolver, state="disabled")
        self.btn_devolver.pack(side="left", padx=5)

        self.btn_cancelar = tk.Button(frame_botoes, text="Cancelar", width=10, command=self.cancelar, state="disabled")
        self.btn_cancelar.pack(side="left", padx=5)

        self.btn_ver_detalhes = tk.Button(frame_botoes, text="Ver Detalhes", width=12, command=self.ver_detalhes, state="disabled")
        self.btn_ver_detalhes.pack(side="left", padx=5)

        tk.Button(frame_botoes, text="Fechar", width=10, command=self.destroy).pack(side="right", padx=5)

    def carregar_dados(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        locacoes = self.controller.listar_locacoes()
        self.tree.tag_configure("atrasado", foreground="red")
        
        for loc in locacoes:
            self.tree.insert("", "end", iid=str(loc.id), values=(
                loc.id,
                loc.veiculo.placa,
                loc.data_inicio.strftime("%d/%m/%Y"),
                loc.data_fim.strftime("%d/%m/%Y"),
                loc.status.value.capitalize(),
                "VIP" if "vip" in type(loc.estrategia).__name__.lower() else "Padrão"
            ))
            
            if loc.status.value == "locado" and loc.data_fim < date.today():
                self.tree.item(str(loc.id), tags=("atrasado",))

        self._atualizar_botoes()

    def _atualizar_botoes(self, event=None):
        selecionado = self.tree.selection()

        if not selecionado:
            self.btn_locar.config(state="disabled")
            self.btn_devolver.config(state="disabled")
            self.btn_cancelar.config(state="disabled")
            self.btn_ver_detalhes.config(state="disabled")
            return

        item = self.tree.item(selecionado[0])
        status = item["values"][4]

        self.btn_ver_detalhes.config(state="normal")
        self.btn_locar.config(state="normal" if status.lower() == StatusLocacao.RESERVADO.value else "disabled")
        self.btn_cancelar.config(state="normal" if status.lower() == StatusLocacao.RESERVADO.value else "disabled")
        self.btn_devolver.config(state="normal" if status.lower() == StatusLocacao.LOCADO.value    else "disabled")

    def _id_selecionado(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma locação.", parent=self)
            return None
        return int(self.tree.item(selecionado[0])["values"][0])

    def abrir_nova_reserva(self):
        janela = JanelaNovaReserva(self)
        self.wait_window(janela)
        self.carregar_dados()

    def locar(self):
        id_loc = self._id_selecionado()
        if id_loc is None:
            return

        sucesso, msg = self.controller.locar(id_loc)
        if sucesso:
            self.carregar_dados()
            messagebox.showinfo("Sucesso", msg, parent=self)
        else:
            messagebox.showerror("Erro", msg, parent=self)

    def devolver(self):
        id_loc = self._id_selecionado()
        if id_loc is None:
            return
        locacao = self.controller.buscar_por_id(id_loc)
        if locacao and date.today() > locacao.data_fim:
            dias_atraso = (date.today() - locacao.data_fim).days
            messagebox.showwarning(
                "Devolução em Atraso",
                f"Este veículo deveria ter sido devolvido em "
                f"{locacao.data_fim.strftime('%d/%m/%Y')}.\n"
                f"Atraso: {dias_atraso} dia(s).\n\n"
                f"O valor será recalculado com a data de hoje.",
                parent=self
            )

        sucesso, resultado = self.controller.devolver(id_loc)
        if sucesso:
            self.carregar_dados()
            msg = (
                f"Devolução realizada com sucesso!\n\n"
                f"Data de Início:    {resultado['data_inicio']}\n"
                f"Data de Devolução: {resultado['data_fim']}\n"
                f"Número de Diárias: {resultado['dias']}\n"
                f"Valor total:       R$ {resultado['valor_total']:.2f}"
            )
            messagebox.showinfo("Devolução", msg, parent=self)
        else:
            messagebox.showerror("Erro", resultado, parent=self)

    def cancelar(self):
        id_loc = self._id_selecionado()
        if id_loc is None:
            return

        resposta = messagebox.askyesno(
            "Confirmar Cancelamento",
            "Tem certeza que deseja cancelar esta reserva?",
            parent=self
        )
        if resposta:
            sucesso, msg = self.controller.cancelar(id_loc)
            if sucesso:
                self.carregar_dados()
                messagebox.showinfo("Sucesso", msg, parent=self)
            else:
                messagebox.showerror("Erro", msg, parent=self)

    def ver_detalhes(self):
        id_loc = self._id_selecionado()
        if id_loc is None:
            return

        locacao = self.controller.buscar_por_id(id_loc)
        if not locacao:
            messagebox.showerror("Erro", "Locação não encontrada.", parent=self)
            return

        status = locacao.status

        if status == StatusLocacao.DEVOLVIDO:
            dias  = (locacao.data_fim - locacao.data_inicio).days or 1
            valor = locacao.calcular_valor_locacao()
            msg = (
                f"Status: {status.value.capitalize()}\n\n"
                f"Data de Início: {locacao.data_inicio.strftime('%d/%m/%Y')}\n"
                f"Data de Devolução: {locacao.data_fim.strftime('%d/%m/%Y')}\n"
                f"Número de Diárias: {dias}\n"
                f"Valor total: R$ {valor:.2f}"
            )

        elif status == StatusLocacao.CANCELADO:
            msg = (
                f"Status: {status.value.capitalize()}\n\n"
                f"Veículo: {locacao.veiculo.placa}\n"
                f"Data de Início Prevista: {locacao.data_inicio.strftime('%d/%m/%Y')}\n"
                f"Data de Fim Prevista: {locacao.data_fim.strftime('%d/%m/%Y')}\n\n"
                f"Esta locação foi cancelada."
            )

        else:
            dias  = (locacao.data_fim - locacao.data_inicio).days or 1
            valor = locacao.calcular_valor_locacao()
            msg = (
                f"Status: {status.value.capitalize()}\n\n"
                f"Veículo: {locacao.veiculo.placa}\n"
                f"Data de Início: {locacao.data_inicio.strftime('%d/%m/%Y')}\n"
                f"Data de Fim Prevista: {locacao.data_fim.strftime('%d/%m/%Y')}\n"
                f"Valor estimado: R$ {valor:.2f}"
            )

        messagebox.showinfo("Detalhes da Locação", msg, parent=self)