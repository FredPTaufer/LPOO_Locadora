import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from tkcalendar import DateEntry
from control.locacao_controller import LocacaoController


class JanelaNovaReserva(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Nova Reserva")
        self.geometry("420x400")

        self.controller = LocacaoController()
        self._veiculos_disponiveis = []

        self.criar_widgets()

    def criar_widgets(self):
        tk.Label(self, text="Nova Reserva", font=("Arial", 16, "bold")).pack(pady=10)

        frame_cat = tk.Frame(self)
        frame_cat.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_cat, text="Categoria:").pack(side="left")
        self.cb_categoria = ttk.Combobox(frame_cat, values=["Economico", "Executivo", "Luxo"], state="readonly", width=20)
        self.cb_categoria.current(0)
        self.cb_categoria.pack(side="right", expand=True, fill="x")

        frame_inicio = tk.Frame(self)
        frame_inicio.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_inicio, text="Data de Início:").pack(side="left")
        self.cal_inicio = DateEntry(frame_inicio, width=20, date_pattern="yyyy-mm-dd", mindate=date.today())
        self.cal_inicio.pack(side="right", expand=True, fill="x")

        frame_fim = tk.Frame(self)
        frame_fim.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_fim, text="Data de Fim:").pack(side="left")
        self.cal_fim = DateEntry(frame_fim, width=20, date_pattern="yyyy-mm-dd", mindate=date.today())
        self.cal_fim.pack(side="right", expand=True, fill="x")

        tk.Button(self, text="Buscar Veículos Disponíveis", command=self.buscar_veiculos, width=30).pack(pady=8)

        tk.Label(self, text="Veículos disponíveis:").pack(anchor="w", padx=20)

        frame_lista = tk.Frame(self, padx=20)
        frame_lista.pack(fill="x")
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical")
        self.lb_veiculos = tk.Listbox(frame_lista, height=5, yscrollcommand=scrollbar.set, selectmode="single")
        scrollbar.config(command=self.lb_veiculos.yview)
        self.lb_veiculos.pack(side="left", fill="x", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame_botoes = tk.Frame(self)
        frame_botoes.pack(fill="x", padx=20, pady=10)
        tk.Button(frame_botoes, text="Confirmar Reserva", width=18, command=self.solicitar_reserva).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Fechar", width=10, command=self.destroy).pack(side="right", padx=5)

    def buscar_veiculos(self):
        data_inicio = self.cal_inicio.get_date().isoformat()
        data_fim    = self.cal_fim.get_date().isoformat()
        categoria   = self.cb_categoria.get().strip()

        veiculos, erro = self.controller.buscar_veiculos_disponiveis(data_inicio, data_fim, categoria)
        if erro:
            messagebox.showerror("Erro", erro, parent=self)
            return

        self.lb_veiculos.delete(0, tk.END)
        self._veiculos_disponiveis = veiculos

        if not veiculos:
            self.lb_veiculos.insert(tk.END, "Nenhum veículo disponível para este período.")
            return

        for v in veiculos:
            self.lb_veiculos.insert(
                tk.END,
                f"{v.placa}  |  {type(v).__name__}  |  R$ {v.taxa_diaria:.2f}/dia"
            )

    def solicitar_reserva(self):
        selecionado = self.lb_veiculos.curselection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um veículo da lista.", parent=self)
            return

        if not self._veiculos_disponiveis:
            messagebox.showwarning("Aviso", "Busque os veículos disponíveis primeiro.", parent=self)
            return

        veiculo     = self._veiculos_disponiveis[selecionado[0]]
        data_inicio = self.cal_inicio.get_date().isoformat()
        data_fim    = self.cal_fim.get_date().isoformat()

        sucesso, msg = self.controller.criar_reserva(veiculo.placa, data_inicio, data_fim)

        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self.destroy()
        else:
            messagebox.showerror("Erro", msg, parent=self)