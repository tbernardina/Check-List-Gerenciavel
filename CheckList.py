import tkinter as tk
from tkinter import messagebox
from Conexao import conexao_db
import FuncoesBanco as FB

# Configurações gerais de estilo
ESTILO_JANELA = {"bg": "#FFF8C6"}
ESTILO_TEXTO = {"font": ("Arial", 12), "bg": "#FFF8C6", "fg": "#6D4C41"}
ESTILO_TITULO = {"font": ("Comic Sans MS", 18, "bold"), "bg": "#FFF8C6", "fg": "#6D4C41"}
ESTILO_TEXTO_LOGIN = {"font": ("Arial", 12)}
ESTILO_LISTA_TAREFAS = {"font": ("Arial", 12), "fg": "#6D4C41"}

class App:
    def __init__(self):
        self.usuario = None
        self.nivel_acesso = None
        self.setor_exec = None

        self.iniciar_login()
    
    #TELA PARA VERIFICAR O NIVEL DE ACESSO E O SETOR DO USUARIO
    def iniciar_login(self):
        self.janela_login = tk.Tk()
        self.janela_login.title("Login")

        frame_login = tk.Frame(self.janela_login, padx=20, pady=20)
        frame_login.pack()

        tk.Label(frame_login, text="Usuário:", **ESTILO_TEXTO_LOGIN).grid(row=0, column=0, pady=5)
        self.entrada_usuario = tk.Entry(frame_login)
        self.entrada_usuario.grid(row=0, column=1, pady=5)

        tk.Label(frame_login, text="Senha:", **ESTILO_TEXTO_LOGIN).grid(row=1, column=0, pady=5)
        self.entrada_senha = tk.Entry(frame_login, show="*")
        self.entrada_senha.grid(row=1, column=1, pady=5)

        botao_login = tk.Button(frame_login, text="Login", command=self.verificar_login)
        botao_login.grid(row=2, columnspan=2, pady=10)

        conexao_db()
        self.janela_login.mainloop()

    def verificar_login(self):
        usuario = self.entrada_usuario.get()
        senha = self.entrada_senha.get()

        nivel = FB.verificar_credenciais(usuario, senha)
        setor = FB.verificar_setor(usuario, senha)

        if nivel:
            self.usuario = usuario
            self.nivel_acesso = nivel
            self.setor_exec = setor
            self.janela_login.destroy()
            self.abrir_interface_principal()
        else:
            messagebox.showerror("Erro de Login", "Usuário ou senha incorretos.")
    def detalhes_tarefa(self, event):
        try:
            # Recuperar índice da tarefa selecionada
            index_selecionado = self.lista_tarefas.curselection()[0]
            tarefa_selecionada = self.lista_tarefas.get(index_selecionado)
            id_tarefa = tarefa_selecionada.split(" - ")[0].strip(" ● ").strip()
            detalhes = FB.select_tarefas(id_tarefa)
            popup, popup_conteudo = self.criar_popup(f"DETALHES DA TAREFA {id_tarefa}", lambda: popup.destroy())

            tk.Label(popup_conteudo, text=)
    #INTERFACE PRINC
    def abrir_interface_principal(self):
        self.janela_principal = tk.Tk()
        self.janela_principal.title("Gerenciador de Checklists")
        self.janela_principal.geometry("400x450")
        self.janela_principal.configure(**ESTILO_JANELA)

        frame_titulo = tk.Frame(self.janela_principal, **ESTILO_JANELA)
        frame_titulo.pack(pady=10)
        tk.Label(frame_titulo, text="Bloco de Anotações", **ESTILO_TITULO).pack()

        frame_lista = tk.Frame(self.janela_principal, **ESTILO_JANELA)
        frame_lista.pack(pady=20)

        self.lista_tarefas = tk.Listbox(frame_lista, width=50, height=15, **ESTILO_LISTA_TAREFAS)
        self.lista_tarefas.pack(side=tk.LEFT, padx=5)
        self.lista_tarefas.bind("<Double-Button-1>", sel.detalhes_tarefa)

        scrollbar = tk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.lista_tarefas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.lista_tarefas.config(yscrollcommand=scrollbar.set)

        frame_botoes = tk.Frame(self.janela_principal, **ESTILO_JANELA)
        frame_botoes.pack(pady=10)

        botao_remover = tk.Button(frame_botoes, text="Remover", command=self.remover_tarefa)
        botao_remover.pack(side=tk.LEFT, padx=5)

        botao_concluida = tk.Button(frame_botoes, text="Marcar como Concluída", command=self.marcar_concluida)
        botao_concluida.pack(side=tk.LEFT, padx=5)

        botao_adicionar = tk.Button(frame_botoes, text="Adicionar", command=self.adicionar_tarefa)
        botao_adicionar.pack(side=tk.LEFT, padx=5)

        if self.nivel_acesso != "1":
            botao_remover.config(state=tk.DISABLED)
            botao_adicionar.config(state=tk.DISABLED)

        self.carregar_lista_tarefas()
        self.janela_principal.mainloop()

    def carregar_lista_tarefas(self):
        self.lista_tarefas.delete(0, tk.END)
        tarefas = FB.carregar_tarefas(self.nivel_acesso, self.setor_exec)
        for tarefa in tarefas:
            self.lista_tarefas.insert(tk.END, f" ● {tarefa['TAREFAS_ID']} - {tarefa['DESCRICAO']} ({tarefa['STATUS']})")

    def criar_popup(self, titulo, comando_salvar):
        popup = tk.Toplevel()
        popup.title(titulo)
        popup.configure(**ESTILO_JANELA)
        popup.transient(self.janela_principal)
        popup.grab_set()

        popup_conteudo = tk.Frame(popup, **ESTILO_JANELA)
        popup_conteudo.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        popup_salvar = tk.Frame(popup, **ESTILO_JANELA)
        popup_salvar.pack(fill=tk.X, expand=True, padx=10, pady=10)

        botao_salvar = tk.Button(popup_salvar, text="Salvar", command=comando_salvar)
        botao_salvar.pack(pady=10)
        return popup, popup_conteudo

    def adicionar_tarefa(self):
        def salvar_tarefa():
            titulo = entrada_titulo.get().strip()
            descricao = entrada_tarefa.get("1.0", tk.END).strip()
            setor = escolha_opcoes.get()
            if titulo and descricao and setor:
                FB.adicionar_tarefa_db(titulo, descricao, setor)
                self.carregar_lista_tarefas()
                popup.destroy()
            else:
                messagebox.showwarning("Aviso", "Preencha todos os campos antes de salvar.")
        popup, popup_conteudo = self.criar_popup("Adicionar Tarefa", salvar_tarefa)
        tk.Label(popup_conteudo, text="Título da Tarefa:", **ESTILO_TEXTO).pack(pady=5)
        entrada_titulo = tk.Entry(popup_conteudo, width=40)
        entrada_titulo.pack(pady=5)

        tk.Label(popup_conteudo, text="Descrição da Tarefa:", **ESTILO_TEXTO).pack(pady=5)
        entrada_tarefa = tk.Text(popup_conteudo, height=5, width=40)
        entrada_tarefa.pack(pady=5)
    
        opcoes = ["RECEPÇÃO", "ADMINISTRADOR", "FINANCEIRO", "FATURAMENTO"]
        escolha_opcoes = tk.StringVar(value=opcoes[0])
        tk.OptionMenu(popup_conteudo, escolha_opcoes, *opcoes).pack(pady=10)

    def remover_tarefa(self):
        try:
            index_selecionado = self.lista_tarefas.curselection()[0]
            id_tarefa = self.lista_tarefas.get(index_selecionado).split(" - ")[0].strip("● ").strip()
            FB.remover_tarefa_bd(id_tarefa)
            self.carregar_lista_tarefas()
        except IndexError:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para remover.")

    def marcar_concluida(self):
        try:
            index_selecionado = self.lista_tarefas.curselection()[0]
            id_tarefa = self.lista_tarefas.get(index_selecionado).split(" - ")[0]

            def salvar_descricao():
                descricao = entrada_descricao.get("1.0", tk.END).strip()
                if descricao:
                    FB.atualizar_status_tarefa(id_tarefa, "Concluída", descricao, self.usuario)
                    self.carregar_lista_tarefas()
                    popup.destroy()
                else:
                    messagebox.showwarning("Aviso", "A descrição não pode estar vazia.")

            popup, popup_conteudo = self.criar_popup("Descrição da Conclusão", salvar_descricao)
            tk.Label(popup_conteudo, text="Descreva como concluiu a tarefa:", **ESTILO_TEXTO).pack(pady=5)
            entrada_descricao = tk.Text(popup_conteudo, height=5, width=40)
            entrada_descricao.pack(pady=10)
        except IndexError:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para marcar como concluída.")

if __name__ == "__main__":
    App()