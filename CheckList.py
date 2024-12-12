import tkinter as tk
from tkinter import messagebox
from Conexao import conexao_db
import FuncoesBanco as FB

# Configurações gerais de estilo
ESTILOS = {
    "janela": {"bg": "#FFF8C6"},
    "texto": {"font": ("Arial", 12), "bg": "#FFF8C6", "fg": "#6D4C41"},
    "titulo": {"font": ("Comic Sans MS", 18, "bold"), "bg": "#FFF8C6", "fg": "#6D4C41"},
    "texto_login": {"font": ("Arial", 12)},
    "lista_tarefas": {"font": ("Arial", 12), "fg": "#6D4C41"},
}

class App:
    def __init__(self):
        self.usuario = None
        self.nivel_acesso = None
        self.setor_exec = None
        self.tarefa_status = "TODOS"
        self.setores_dict = None
        self.iniciar_login()

    #TELA PARA VERIFICAR O NIVEL DE ACESSO E O SETOR DO USUARIO
    def iniciar_login(self):
        self.janela_login = self.criar_janela("Login")

        frame_login = tk.Frame(self.janela_login, padx=20, pady=20)
        frame_login.pack()

        self.criar_rotulo(frame_login, "Usuário:", 0, 0, **ESTILOS["texto_login"])
        self.entrada_usuario = tk.Entry(frame_login)
        self.entrada_usuario.grid(row=0, column=1, pady=5)

        self.criar_rotulo(frame_login, "Senha:", 1, 0, **ESTILOS["texto_login"])
        self.entrada_senha = tk.Entry(frame_login, show="*")
        self.entrada_senha.grid(row=1, column=1, pady=5)

        tk.Button(frame_login, text="Login", command=self.verificar_login).grid(row=2, columnspan=2, pady=10)

        conexao_db()
        self.janela_login.mainloop()

    def verificar_login(self):
        usuario = self.entrada_usuario.get()
        senha = self.entrada_senha.get()

        nivel = FB.verificar_informacao_usuario(usuario, senha, "ADMINISTRADOR")
        setor = FB.verificar_informacao_usuario(usuario, senha, "SETOR")  # Nome alterado

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
            id_tarefa = self.lista_tarefas.get(index_selecionado).split(" - ")[0].strip(" ● ").strip()
            detalhes = FB.select_tarefas(id_tarefa)

            popup, popup_conteudo = self.criar_popup(f"DETALHES DA TAREFA {id_tarefa}", lambda: popup.destroy())

            campos = [
                ("ID da Tarefa:", detalhes["TAREFAS_ID"]),
                ("Título da Tarefa:", detalhes["TITULO"]),
                ("Setor Destinado:", detalhes["SETOR"]),
                ("Status Atual:", detalhes["STATUS"]),
            ]

            for titulo, valor in campos:
                self.criar_campo(popup_conteudo, titulo, valor)

            self.criar_texto_campo(popup_conteudo, "Descrição da Tarefa:", detalhes["DESCRICAO"])

            if detalhes["STATUS"] == "CONCLUÍDA":
                self.criar_texto_campo(popup_conteudo, "Solução:", detalhes["TAREFA_SOLUCAO"])
                campos_concluida = [
                    ("Data da Conclusão:", detalhes["DATA_CONCLUSAO"]),
                    ("Funcionário Responsável pela Conclusão:", detalhes["FUNCIONARIO_SOLUCAO"]),
                ]
                for titulo, valor in campos_concluida:
                    self.criar_campo(popup_conteudo, titulo, valor)

        except IndexError:
            messagebox.showwarning("Aviso", "Selecione uma tarefa válida.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar os detalhes da tarefa: {e}")

    #INTERFACE PRINCIPAL
    def abrir_interface_principal(self):
        self.janela_principal = self.criar_janela("Gerenciador de Checklists", "400x500")

        self.criar_frame_titulo(self.janela_principal, "Bloco de Anotações")

        frame_botoes = tk.Frame(self.janela_principal, **ESTILOS["janela"])
        frame_botoes.pack(pady=10)

        botoes = [
            ("Remover", self.remover_tarefa),
            ("Marcar como Concluída", self.marcar_concluida),
            ("Adicionar", self.adicionar_tarefa),
        ]

        # Criando os botões com estado dinâmico
        for texto in botoes:
            estado = "normal"  # Estado padrão
            if texto in ["Remover", "Adicionar"] and self.nivel_acesso == "0":
                estado = "disabled"  # Desativa se não for administrador

        # Cria o botão com o estado correspondente
        for texto, comando in botoes:
            tk.Button(frame_botoes, text=texto, command=comando, state=estado).pack(side=tk.LEFT, padx=5)

        frame_lista = tk.Frame(self.janela_principal, **ESTILOS["janela"])
        frame_lista.pack(pady=20)

        self.lista_tarefas = tk.Listbox(frame_lista, width=50, height=15, **ESTILOS["lista_tarefas"])
        self.lista_tarefas.pack(side=tk.LEFT, padx=5)
        self.lista_tarefas.bind("<Double-Button-1>", self.detalhes_tarefa)

        scrollbar = tk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.lista_tarefas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.lista_tarefas.config(yscrollcommand=scrollbar.set)
        
        self.carregar_lista_tarefas()
        self.janela_principal.mainloop()

    def carregar_lista_tarefas(self):
        self.lista_tarefas.delete(0, tk.END)
        tarefas = FB.carregar_tarefas(self.nivel_acesso, self.setor_exec, self.tarefa_status)
        for tarefa in tarefas:
            self.lista_tarefas.insert(tk.END, f" ● {tarefa['TAREFAS_ID']} - {tarefa['DESCRICAO']} ({tarefa['STATUS']})")

    # Funções auxiliares
    def criar_janela(self, titulo, dimensao=None):
        janela = tk.Tk()
        janela.title(titulo)
        janela.configure(**ESTILOS["janela"])
        if dimensao:
            janela.geometry(dimensao)
        return janela

    def criar_rotulo(self, frame, texto, linha, coluna, **estilo):
        tk.Label(frame, text=texto, **estilo).grid(row=linha, column=coluna, pady=5)

    def criar_popup(self, titulo, comando_salvar):
        popup = tk.Toplevel()
        popup.title(titulo)
        popup.configure(**ESTILOS["janela"])
        popup.transient(self.janela_principal)
        popup.grab_set()

        popup_conteudo = tk.Frame(popup, **ESTILOS["janela"])
        popup_conteudo.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        botao_salvar = tk.Button(popup, text="Finalizar", command=comando_salvar)
        botao_salvar.pack(pady=10)
        return popup, popup_conteudo

    def criar_campo(self, frame, titulo, valor):
        tk.Label(frame, text=titulo, **ESTILOS["texto"]).pack(anchor="w", pady=2)
        campo = tk.Entry(frame, width=50)
        campo.insert(0, valor)
        campo.configure(state="disabled")
        campo.pack(anchor="w", pady=2)

    def criar_texto_campo(self, frame, titulo, valor):
        tk.Label(frame, text=titulo, **ESTILOS["texto"]).pack()
        campo = tk.Text(frame, width=35, height=5)
        campo.insert("1.0", valor)
        campo.configure(state="disabled")
        campo.pack(pady=5)

    def criar_frame_titulo(self, janela, titulo):
        frame_titulo = tk.Frame(janela, **ESTILOS["janela"])
        frame_titulo.pack(pady=10)
        tk.Label(frame_titulo, text=titulo, **ESTILOS["titulo"]).pack()

    def remover_tarefa(self):
            try:
                index_selecionado = self.lista_tarefas.curselection()[0]
                id_tarefa = self.lista_tarefas.get(index_selecionado).split(" - ")[0].strip(" ● ").strip()
                FB.remover_tarefa_bd(id_tarefa)
                self.carregar_lista_tarefas()
            except IndexError:
                messagebox.showwarning("Aviso", "Selecione uma tarefa para remover.")

    def adicionar_tarefa(self):
        # Criar a janela popup para adicionar uma nova tarefa
        popup, popup_conteudo = self.criar_popup("Adicionar Nova Tarefa", lambda: self.salvar_tarefa(popup))
        
        # Campo para título da tarefa
        self.criar_rotulo(popup_conteudo, "Título da Tarefa:", 0, 0, **ESTILOS["texto"])
        self.campo_titulo = tk.Entry(popup_conteudo, width=50)
        self.campo_titulo.grid(row=0, column=1, pady=5)
        
        # Campo para descrição da tarefa
        self.criar_rotulo(popup_conteudo, "Descrição da Tarefa:", 1, 0, **ESTILOS["texto"])
        self.campo_descricao = tk.Text(popup_conteudo, width=40, height=5)
        self.campo_descricao.grid(row=1, column=1, pady=5)

        # Dropdown para selecionar o setor
        self.criar_rotulo(popup_conteudo, "Setor:", 2, 0, **ESTILOS["texto"])
        setores = FB.carregar_setores()  # Função que retorna uma lista de setores do banco
        self.setores_dict = {setor[1]: setor[0] for setor in setores}  # mapeando nome para id

        # Opção de menu com nomes de setores
        setores_nomes = [setor[1] for setor in setores]
        self.setor_selecionado = tk.StringVar(value=setores_nomes[0])
        self.setor_selecionado = tk.StringVar()
        self.setor_selecionado.set("Selecione um setor")
        setor_menu = tk.OptionMenu(popup_conteudo, self.setor_selecionado, *setores_nomes, command=self.atualizar_funcionarios)
        setor_menu.grid(row=2, column=1, pady=5)

        # Dropdown para selecionar o funcionário (inicialmente vazio)
        self.criar_rotulo(popup_conteudo, "Funcionário Responsável:", 3, 0, **ESTILOS["texto"])
        self.funcionario_selecionado = tk.StringVar()
        self.funcionario_selecionado.set("Selecione um funcionário")
        self.funcionarios_menu = tk.OptionMenu(popup_conteudo, self.funcionario_selecionado, "")
        self.funcionarios_menu.grid(row=3, column=1, pady=5)
  
    def marcar_concluida(self):
        try:
            # Obtemos o ID da tarefa selecionada
            index_selecionado = self.lista_tarefas.curselection()[0]
            id_tarefa = self.lista_tarefas.get(index_selecionado).split(" - ")[0].strip(" ● ").strip()
            
            # Atualizamos o status da tarefa no banco de dados
            FB.marcar_tarefa_concluida(id_tarefa)  # Função definida no módulo FuncoesBanco
            
            # Atualizamos a lista de tarefas
            self.carregar_lista_tarefas()
            messagebox.showinfo("Sucesso", "Tarefa marcada como concluída!")
        except IndexError:
            messagebox.showwarning("Aviso", "Selecione uma tarefa válida.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao marcar tarefa como concluída: {e}")

    def atualizar_funcionarios(self, setor_id):
        """
        Atualiza a lista de funcionários vinculados ao setor selecionado.
        """
        setor_nome = self.setor_selecionado.get()  # Pega o nome selecionado
        setor_id = self.setores_dict[setor_nome]   # Converte para ID
        try:
            funcionarios = FB.carregar_funcionarios_por_setor(setor_id) # Função que busca funcionários do setor
            if not funcionarios:
                funcionarios = ["Nenhum funcionário disponível"]
                
        except Exception as e:
            funcionarios = ["Erro ao carregar funcionários"]
            messagebox.showerror(f"Erro ao carregar funcionários: {e}")

            # Atualizar o OptionMenu dos funcionários
            self.funcionario_selecionado.set(funcionarios[0])  # Seleciona o primeiro item
            self.funcionarios_menu["menu"].delete(0, "end")  # Limpar menu atual
            for funcionario in funcionarios:
                self.funcionarios_menu["menu"].add_command(
                    label=funcionario,
                    command=lambda f=funcionario: self.funcionario_selecionado.set(f)
                )
            self.funcionario_selecionado.set("Selecione um funcionário")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar funcionários: {e}")

    def salvar_tarefa(self, popup):
        """
        Salva a nova tarefa no banco de dados.
        """
        titulo = self.campo_titulo.get()
        descricao = self.campo_descricao.get("1.0", tk.END).strip()
        setor_id = self.setor_selecionado.get()
        funcionario = self.funcionario_selecionado.get()

        if not titulo or not descricao or setor_id == "Selecione um setor" or funcionario == "Selecione um funcionário":
            messagebox.showwarning("Campos Incompletos", "Por favor, preencha todos os campos antes de salvar.")
            return

        try:
           # Verificar se "TODOS" foi selecionado
            if funcionario == "TODOS":
                funcionarios = FB.carregar_funcionarios_por_setor(setor_id)
                for funcionario in funcionarios:
                    FB.adicionar_tarefa_db(titulo,descricao, setor_id, funcionario["ID"])
            
            else:
                funcionario_id = FB.buscar_id_funcionario(funcionario)
                FB.adicionar_tarefa_db(titulo,descricao, setor_id, funcionario_id)
            
            messagebox.showinfo("Sucesso", "Tarefa adicionada com sucesso!")
            self.popup_tarefa.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar tarefa: {e}")

if __name__ == "__main__":
    App()
# Configurações gerais de estilo
# ESTILO_JANELA = {"bg": "#FFF8C6"}
# ESTILO_TEXTO = {"font": ("Arial", 12), "bg": "#FFF8C6", "fg": "#6D4C41"}
# ESTILO_TITULO = {"font": ("Comic Sans MS", 18, "bold"), "bg": "#FFF8C6", "fg": "#6D4C41"}
# ESTILO_TEXTO_LOGIN = {"font": ("Arial", 12)}
# ESTILO_LISTA_TAREFAS = {"font": ("Arial", 12), "fg": "#6D4C41"}

# class App:
#     def __init__(self):
#         self.usuario = None
#         self.nivel_acesso = None
#         self.setor_exec = None

#         self.iniciar_login()
    
#     #TELA PARA VERIFICAR O NIVEL DE ACESSO E O SETOR DO USUARIO
#     def iniciar_login(self):
#         self.janela_login = tk.Tk()
#         self.janela_login.title("Login")

#         frame_login = tk.Frame(self.janela_login, padx=20, pady=20)
#         frame_login.pack()

#         tk.Label(frame_login, text="Usuário:", **ESTILO_TEXTO_LOGIN).grid(row=0, column=0, pady=5)
#         self.entrada_usuario = tk.Entry(frame_login)
#         self.entrada_usuario.grid(row=0, column=1, pady=5)

#         tk.Label(frame_login, text="Senha:", **ESTILO_TEXTO_LOGIN).grid(row=1, column=0, pady=5)
#         self.entrada_senha = tk.Entry(frame_login, show="*")
#         self.entrada_senha.grid(row=1, column=1, pady=5)

#         botao_login = tk.Button(frame_login, text="Login", command=self.verificar_login)
#         botao_login.grid(row=2, columnspan=2, pady=10)

#         conexao_db()
#         self.janela_login.mainloop()

#     def verificar_login(self):
#         usuario = self.entrada_usuario.get()
#         senha = self.entrada_senha.get()

#         nivel = FB.verificar_credenciais(usuario, senha)
#         setor = FB.verificar_setor(usuario, senha)

#         if nivel:
#             self.usuario = usuario
#             self.nivel_acesso = nivel
#             self.setor_exec = setor
#             self.janela_login.destroy()
#             self.abrir_interface_principal()
#         else:
#             messagebox.showerror("Erro de Login", "Usuário ou senha incorretos.")

#     def detalhes_tarefa(self, event):
#         try:
#             # Recuperar índice da tarefa selecionada
#             index_selecionado = self.lista_tarefas.curselection()[0]
#             id_tarefa = self.lista_tarefas.get(index_selecionado).split(" - ")[0].strip(" ● ").strip()
#             detalhes = FB.select_tarefas(id_tarefa)
#             popup, popup_conteudo = self.criar_popup(f"DETALHES DA TAREFA {id_tarefa}", lambda: popup.destroy())

#             def criar_campo(titulo, valor):
#                 tk.Label(popup_conteudo, text=titulo, **ESTILO_TEXTO).pack(anchor="w", pady=2)
#                 campo = tk.Entry(popup_conteudo, width=50)
#                 campo.insert(0, valor)
#                 campo.configure(state="disabled")  # Desabilita o campo de entrada
#                 campo.pack(anchor="w", pady=2)
            
#             #Campos criados pela função
#             criar_campo("ID da Tarefa: ", detalhes["TAREFAS_ID"])
#             criar_campo("Título da Tarefa: ", detalhes["TITULO"])
#             tk.Label(popup_conteudo, text="Descrição da Tarefa: ", **ESTILO_TEXTO).pack()
#             campo_descricao = tk.Text(popup_conteudo, width=35, height=5)
#             campo_descricao.insert("1.0", detalhes["DESCRICAO"])
#             campo_descricao.configure(state="disabled")
#             campo_descricao.pack(pady=5)
#             criar_campo("Setor Destinado: ", detalhes["SETOR"])
#             criar_campo("Status Atual: ", detalhes["STATUS"])
#             if detalhes["STATUS"] == "CONCLUÍDA":
#                 tk.Label(popup_conteudo, text="Solução: ", **ESTILO_TEXTO).pack()
#                 campo_solucao = tk.Text(popup_conteudo, width= 35,height=5)
#                 campo_solucao.insert("1.0", detalhes["TAREFA_SOLUCAO"])
#                 campo_solucao.configure(state="disabled")
#                 campo_solucao.pack(pady=5)
#                 criar_campo("Data da Conclusão: ", detalhes["DATA_CONCLUSAO"])
#                 criar_campo("Funcionário Responsável pela Conclusão: ", detalhes["FUNCIONARIO_SOLUCAO"])
#         except IndexError:
#             messagebox.showwarning("Aviso", "Selecione uma tarefa válida.")
#         except Exception as e:
#             messagebox.showerror("Erro", f"Erro ao carregar os detalhes da tarefa: {e}")

            

#     #INTERFACE PRINCIPAL
#     def abrir_interface_principal(self):
#         self.janela_principal = tk.Tk()
#         self.janela_principal.title("Gerenciador de Checklists")
#         self.janela_principal.geometry("400x500")
#         self.janela_principal.configure(**ESTILO_JANELA)

#         frame_titulo = tk.Frame(self.janela_principal, **ESTILO_JANELA)
#         frame_titulo.pack(pady=10)
#         tk.Label(frame_titulo, text="Bloco de Anotações", **ESTILO_TITULO).pack()

#         frame_botoes = tk.Frame(self.janela_principal, **ESTILO_JANELA)
#         frame_botoes.pack(pady=10)

#         botao_remover = tk.Button(frame_botoes, text="Remover", command=self.remover_tarefa)
#         botao_remover.pack(side=tk.LEFT, padx=5)

#         botao_concluida = tk.Button(frame_botoes, text="Marcar como Concluída", command=self.marcar_concluida)
#         botao_concluida.pack(side=tk.LEFT, padx=5)

#         botao_adicionar = tk.Button(frame_botoes, text="Adicionar", command=self.adicionar_tarefa)
#         botao_adicionar.pack(side=tk.LEFT, padx=5)

#         frame_lista = tk.Frame(self.janela_principal, **ESTILO_JANELA)
#         frame_lista.pack(pady=20)

#         self.lista_tarefas = tk.Listbox(frame_lista, width=50, height=15, **ESTILO_LISTA_TAREFAS)
#         self.lista_tarefas.pack(side=tk.LEFT, padx=5)
#         self.lista_tarefas.bind("<Double-Button-1>", self.detalhes_tarefa)

#         scrollbar = tk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.lista_tarefas.yview)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#         self.lista_tarefas.config(yscrollcommand=scrollbar.set)

#         frame_atualizar = tk.Frame(self.janela_principal, **ESTILO_JANELA)
#         frame_atualizar.pack(pady=5)

#         status = ["TODOS","CONCLUÍDA", "PENDENTE"]
#         escolha_status = tk.StringVar(value=status[0])
#         botao_status = tk.OptionMenu(frame_atualizar, escolha_status, *status)
#         botao_status.pack(side=tk.LEFT)
#         botao_atualizar = tk.Button(frame_atualizar, text="Atualizar", command=self.carregar_lista_tarefas(self.nivel_acesso, self.setor_exec, botao_status))
#         botao_atualizar.pack(side=tk.RIGHT)

#         if self.nivel_acesso != "1":
#             botao_remover.config(state=tk.DISABLED)
#             botao_adicionar.config(state=tk.DISABLED)

#         self.carregar_lista_tarefas()
#         self.janela_principal.mainloop()
#     def carregar_lista_tarefas(self):
#         self.lista_tarefas.delete(0, tk.END)
#         tarefas = FB.carregar_tarefas(self.nivel_acesso, self.setor_exec, self.botao_status)
#         for tarefa in tarefas:
#             self.lista_tarefas.insert(tk.END, f" ● {tarefa['TAREFAS_ID']} - {tarefa['DESCRICAO']} ({tarefa['STATUS']})")

#     def criar_popup(self, titulo, comando_salvar):        
#         popup = tk.Toplevel()
#         popup.title(titulo)
#         popup.configure(**ESTILO_JANELA)
#         popup.transient(self.janela_principal)
#         popup.grab_set()

#         popup_conteudo = tk.Frame(popup, **ESTILO_JANELA)
#         popup_conteudo.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

#         popup_salvar = tk.Frame(popup, **ESTILO_JANELA)
#         popup_salvar.pack(fill=tk.X, expand=True, padx=10, pady=10)

#         botao_salvar = tk.Button(popup_salvar, text="Finalizar", command=comando_salvar)
#         botao_salvar.pack(pady=10)
#         return popup, popup_conteudo

#     def adicionar_tarefa(self):
#         def salvar_tarefa():
#             titulo = entrada_titulo.get().strip()
#             descricao = entrada_tarefa.get("1.0", tk.END).strip()
#             setor = escolha_opcoes.get()
#             if titulo and descricao and setor:
#                 FB.adicionar_tarefa_db(titulo, descricao, setor)
#                 self.carregar_lista_tarefas()
#                 popup.destroy()
#             else:
#                 messagebox.showwarning("Aviso", "Preencha todos os campos antes de salvar.")

#         popup, popup_conteudo = self.criar_popup("Adicionar Tarefa", salvar_tarefa)
#         tk.Label(popup_conteudo, text="Título da Tarefa:", **ESTILO_TEXTO).pack(pady=5)
#         entrada_titulo = tk.Entry(popup_conteudo, width=40)
#         entrada_titulo.pack(pady=5)

#         tk.Label(popup_conteudo, text="Descrição da Tarefa:", **ESTILO_TEXTO).pack(pady=5)
#         entrada_tarefa = tk.Text(popup_conteudo, height=5, width=40)
#         entrada_tarefa.pack(pady=5)
    
#         frame_opcoes_setor = tk.Frame(popup, **ESTILO_JANELA)
#         tk.Label(frame_opcoes_setor, text="Setor: ", **ESTILO_TEXTO).pack(pady=5)
#         opcoes = ["RECEPÇÃO", "ADMINISTRADOR", "FINANCEIRO", "FATURAMENTO"]
#         escolha_opcoes = tk.StringVar(value=opcoes[0])
#         tk.OptionMenu(frame_opcoes_setor, escolha_opcoes, *opcoes).pack(pady=10)

#     def remover_tarefa(self):
#         try:
#             index_selecionado = self.lista_tarefas.curselection()[0]
#             id_tarefa = self.lista_tarefas.get(index_selecionado).split(" - ")[0].strip(" ● ").strip()
#             FB.remover_tarefa_bd(id_tarefa)
#             self.carregar_lista_tarefas()
#         except IndexError:
#             messagebox.showwarning("Aviso", "Selecione uma tarefa para remover.")

#     def marcar_concluida(self):
#         try:
#             index_selecionado = self.lista_tarefas.curselection()[0]
#             id_tarefa = self.lista_tarefas.get(index_selecionado).split(" - ")[0].strip(" ● ").strip()

#             def salvar_descricao():
#                 descricao = entrada_descricao.get("1.0", tk.END).strip()
#                 if descricao:
#                     FB.atualizar_status_tarefa(id_tarefa, descricao, self.usuario)
#                     self.carregar_lista_tarefas()
#                     popup.destroy()
#                 else:
#                     messagebox.showwarning("Aviso", "A descrição não pode estar vazia.")

#             popup, popup_conteudo = self.criar_popup("Descrição da Conclusão", salvar_descricao)
#             tk.Label(popup_conteudo, text="Descreva como concluiu a tarefa:", **ESTILO_TEXTO).pack(pady=5)
#             entrada_descricao = tk.Text(popup_conteudo, height=5, width=40)
#             entrada_descricao.pack(pady=10)
#         except IndexError:
#             messagebox.showwarning("Aviso", "Selecione uma tarefa para marcar como concluída.")

# if __name__ == "__main__":
#     App()