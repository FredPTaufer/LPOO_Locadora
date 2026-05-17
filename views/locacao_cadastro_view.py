import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from tkcalendar import DateEntry
from control.locacao_controller import LocacaoController


class JanelaCadastroLocacao(tk.Toplevel):
    def __init__(self, master=None, locacao=None):
        super().__init__(master)
        self.locacao = locacao
        self.title("Editar Locação" if locacao else "Nova Locação (Admin)")
        self.geometry("420x400")

        self.controller = LocacaoController()

        tk.Label(self, text="Editar Locação" if locacao else "Nova Locação", font=("Arial", 16, "bold")).pack(pady=10)

        self.criar_widgets()

        if self.locacao:
            self.preencher_campos()

    def criar_widgets(self):
        frame_placa = tk.Frame(self)
        frame_placa.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_placa, text="Placa do Veículo:").pack(side="left")
        self.txt_placa = tk.Entry(frame_placa, width=15)
        self.txt_placa.pack(side="right", expand=True, fill="x")

        frame_inicio = tk.Frame(self)
        frame_inicio.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_inicio, text="Data Início:").pack(side="left")
        self.cal_inicio = DateEntry(frame_inicio, width=20, date_pattern="yyyy-mm-dd")
        self.cal_inicio.pack(side="right", expand=True, fill="x")

        frame_fim = tk.Frame(self)
        frame_fim.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_fim, text="Data Fim:").pack(side="left")
        self.cal_fim = DateEntry(frame_fim, width=20, date_pattern="yyyy-mm-dd")
        self.cal_fim.pack(side="right", expand=True, fill="x")

        frame_status = tk.Frame(self)
        frame_status.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_status, text="Status:").pack(side="left")
        self.cb_status = ttk.Combobox(frame_status, values=["Reservado", "Locado", "Devolvido", "Cancelado"], state="readonly", width=20)
        self.cb_status.current(0)
        self.cb_status.pack(side="right", expand=True, fill="x")

        frame_est = tk.Frame(self)
        frame_est.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_est, text="Estratégia:").pack(side="left")
        self.cb_estrategia = ttk.Combobox(frame_est, values=["Padrão", "VIP"], state="readonly", width=20)
        self.cb_estrategia.current(0)
        self.cb_estrategia.pack(side="right", expand=True, fill="x")

        frame_botoes = tk.Frame(self)
        frame_botoes.pack(fill="x", padx=20, pady=15)
        btn_text   = "Atualizar Locação" if self.locacao else "Salvar Locação"
        btn_action = self.solicitar_atualizacao if self.locacao else self.solicitar_cadastro
        tk.Button(frame_botoes, text=btn_text, width=18, command=btn_action).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Fechar",  width=10, command=self.destroy).pack(side="right", padx=5)

    def preencher_campos(self):
        self.txt_placa.insert(0, self.locacao.veiculo.placa)
        self.cal_inicio.set_date(self.locacao.data_inicio)
        self.cal_fim.set_date(self.locacao.data_fim)
        self.cb_status.set(self.locacao.status.value)
        estrategia_str = "VIP" if "vip" in type(self.locacao.estrategia).__name__.lower() else "Padrão"
        self.cb_estrategia.set(estrategia_str)

    def solicitar_cadastro(self):
        placa      = self.txt_placa.get().strip().upper()
        data_ini   = self.cal_inicio.get_date().isoformat()
        data_fim   = self.cal_fim.get_date().isoformat()
        status     = self.cb_status.get().strip()
        estrategia = self.cb_estrategia.get().strip()

        sucesso, msg = self.controller.salvar_locacao_admin(placa, data_ini, data_fim, estrategia, status)
        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self.destroy()
        else:
            messagebox.showerror("Erro", msg, parent=self)

    def solicitar_atualizacao(self):
        placa      = self.txt_placa.get().strip().upper()
        data_ini   = self.cal_inicio.get_date().isoformat()
        data_fim   = self.cal_fim.get_date().isoformat()
        status     = self.cb_status.get().strip()
        estrategia = self.cb_estrategia.get().strip()

        sucesso, msg = self.controller.atualizar_locacao_admin(
            self.locacao.id, placa, data_ini, data_fim, estrategia, status
        )
        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self.destroy()
        else:
            messagebox.showerror("Erro", msg, parent=self)