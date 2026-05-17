import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import messagebox, ttk
from control.veiculo_controller import VeiculoController

class JanelaCadastroVeiculo(tk.Toplevel):
    def __init__(self, master=None, veiculo=None):
        super().__init__(master)
        self.veiculo = veiculo
        self.title("Editar Veículo" if veiculo else "Cadastro de Novo Veículo")
        self.geometry("400x350")

        self.controller = VeiculoController()
        tk.Label(self, text="Editar Veículo" if veiculo else "Cadastrar Veículo", font=("Arial", 16, "bold")).pack(pady=10)

        frame_placa = tk.Frame(self)
        frame_placa.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_placa, text="Placa:").pack(side="left")
        self.txt_placa = tk.Entry(frame_placa)
        self.txt_placa.pack(side="right")

        frame_tipo = tk.Frame(self)
        frame_tipo.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_tipo, text="Tipo:").pack(side="left")
        self.cb_tipo = ttk.Combobox(frame_tipo, values=["Carro", "Motorhome"], state="readonly")
        self.cb_tipo.current(0)
        self.cb_tipo.pack(side="right", expand=True, fill="x")

        frame_cat = tk.Frame(self)
        frame_cat.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_cat, text="Categoria:").pack(side="left")
        self.cb_categoria = ttk.Combobox(frame_cat, values=["Economico", "Executivo", "Luxo"], state="readonly")
        self.cb_categoria.current(0)
        self.cb_categoria.pack(side="right", expand=True, fill="x")

        frame_taxa = tk.Frame(self)
        frame_taxa.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_taxa, text="Taxa Diária (R$):").pack(side="left")
        self.txt_taxa = tk.Entry(frame_taxa)
        self.txt_taxa.pack(side="right", expand=True, fill="x")

        btn_text   = "Atualizar Veículo" if veiculo else "Salvar Veículo"
        btn_action = self.solicitar_atualizacao if veiculo else self.solicitar_cadastro
        tk.Button(self, text=btn_text, command=btn_action).pack(pady=20)

        if self.veiculo:
            self.preencher_campos()

    def preencher_campos(self):
        self.txt_placa.insert(0, self.veiculo.placa)
        self.txt_placa.configure(state="disabled")
        self.cb_tipo.set(type(self.veiculo).__name__.lower())

        categoria_nome = self.veiculo.categoria.name if hasattr(self.veiculo.categoria, 'name') else str(self.veiculo.categoria).upper()
        self.cb_categoria.set(categoria_nome)

        self.txt_taxa.insert(0, f"{self.veiculo.taxa_diaria:.2f}".replace('.', ','))

    def solicitar_cadastro(self):
        placa      = self.txt_placa.get().strip().upper()
        tipo       = self.cb_tipo.get().strip()
        categoria  = self.cb_categoria.get().strip()
        taxa_str   = self.txt_taxa.get().strip()

        sucesso, msg = self.controller.salvar_veiculo(placa, tipo, categoria, taxa_str)

        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self.destroy()
        else:
            messagebox.showerror("Erro", msg, parent=self)

    def solicitar_atualizacao(self):
        placa      = self.txt_placa.get().strip().upper()
        tipo       = self.cb_tipo.get().strip()
        categoria  = self.cb_categoria.get().strip()
        taxa_str   = self.txt_taxa.get().strip()

        sucesso, msg = self.controller.atualizar_veiculo(placa, tipo, categoria, taxa_str)

        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self.destroy()
        else:
            messagebox.showerror("Erro", msg, parent=self)