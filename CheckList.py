# Copyright 2004 Thiago Reis Dalla Bernardina
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import tkinter as tk
from tkinter import messagebox
from Conexao import conexao_db
import FuncoesBanco as FB
import Notifications as NF
from config import caminhoIcone, timeout_notify, ESTILOS

class App:
    def __init__(self):
        self.id_usuario = None
        self.usuario = None
        self.nivel_acesso = None
        self.setor_exec = None
        self.tarefa_status = "TODOS"
        self.setores_dict = None
        self.iniciar_login()

    #TELA PARA VERIFICAR O NIVEL DE ACESSO E O SETOR DO USUARIO
    def iniciar_login(self):
        self.janela_login = self.criar_janela("Login")

        # Icone janela de login
        self.janela_login.iconbitmap(caminhoIcone)

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
        print(f"usuario: {usuario}, senha: {senha}")

        nivel = FB.verificar_informacao_usuario(usuario, senha, "CARGO")
        setor = FB.verificar_informacao_usuario(usuario, senha, "SETOR")
        id = FB.verificar_informacao_usuario(usuario, senha, "USER_ID") 
        if nivel:
            self.usuario = usuario
            self.nivel_acesso = nivel
            self.setor_exec = setor
            self.id_usuario = id
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
                ("Setor Destinado:", detalhes["NOME_SETOR"]),
                ("Status Atual:", detalhes["STATUS"]),
                ("Tarefa destinada a:", detalhes["FUNCIONARIO_DESTINO_NOME"])
            ]

            for titulo, valor in campos:
                self.criar_campo(popup_conteudo, titulo, valor)

            self.criar_texto_campo(popup_conteudo, "Descrição da Tarefa:", detalhes["DESCRICAO"])

            if detalhes["STATUS"] == "CONCLUÍDA":
                self.criar_texto_campo(popup_conteudo, "Solução:", detalhes["TAREFA_SOLUCAO"])
                campos_concluida = [
                    ("Data da Conclusão:", detalhes["DATA_CONCLUSAO"]),
                    ("Funcionário Responsável pela Conclusão:", detalhes["FUNCIONARIO_SOLUCAO_NOME"]),
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

        # Altere o ícone da janela principal
        self.janela_principal.iconbitmap(caminhoIcone)

        self.criar_frame_titulo(self.janela_principal, "Afazeres")

        # Ordem em que os elementos aparecem na tela, frames utilizadas na interface principal
        frame_botoes_cabecalho = tk.Frame(self.janela_principal, **ESTILOS["janela"])
        frame_botoes_cabecalho.pack(pady=10)

        frame_lista = tk.Frame(self.janela_principal, **ESTILOS["janela"])
        frame_lista.pack(pady=20)

        frame_botoes_rodape = tk.Frame(self.janela_principal, **ESTILOS["janela"])
        frame_botoes_rodape.pack(pady=10)

        # Adicione um print para verificar o valor de self.nivel_acesso
        print(f"Nível de Acesso: {self.nivel_acesso}")

        # Configuração dos botões com estado dinâmico
        botoes_cabecalho = [
            ("Remover", self.remover_tarefa),
            ("Marcar como Concluída", self.marcar_concluida),
            ("Adicionar", self.adicionar_tarefa),
            ("Criar Usuário", self.criar_usuario),
        ]

        botoes_rodape =[
            ("Atualizar", self.carregar_lista_tarefas)
        ]

        # Criando os botões e verificando o estado com base no nível de acesso
        for texto, comando in botoes_cabecalho:
            estado = "normal"  # Estado padrão
            if texto in ["Remover", "Adicionar", "Criar Usuário"] and self.nivel_acesso == 0:
                estado = "disabled"  # Desativa se o usuário não for administrador
            
            print(f"Botão: {texto}, Estado: {estado}")  # Debug para verificar o estado do botão

            tk.Button(frame_botoes_cabecalho, text=texto, command=comando, state=estado).pack(side=tk.LEFT, padx=5) # Verificar se o botão é criado dentro do loop

        opcoes = ["TODOS", "CONCLUÍDA", "PENDENTE"]
        self.status_selecionado = tk.StringVar(value=opcoes[2])  # Valor inicial
        tk.OptionMenu(frame_botoes_rodape, self.status_selecionado, *opcoes).pack(side=tk.LEFT, padx=15)

        for texto, comando in botoes_rodape:
            tk.Button(frame_botoes_rodape, text=texto, command=comando).pack(side=tk.LEFT, padx=5)

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
        self.tarefa_status = self.status_selecionado.get()
        tarefas = FB.carregar_tarefas(self.nivel_acesso, self.setor_exec, self.tarefa_status, self.id_usuario)
        
        if self.nivel_acesso != 1:
            # Verificar se há tarefas pendentes
            tarefas_pendentes = [tarefa for tarefa in tarefas if tarefa["STATUS"] == "PENDENTE"]

            # Notificar o usuário se houver tarefas pendentes
            if tarefas_pendentes and self.nivel_acesso == 3:
                NF.enviar_notificacao(f"Você tem {len(tarefas_pendentes)} tarefas pendentes!")
                self.janela_principal.after(timeout_notify, self.carregar_lista_tarefas)
        for tarefa in tarefas:
            self.lista_tarefas.insert(tk.END, f" ● {tarefa['TAREFAS_ID']} - {tarefa['TITULO']} ({tarefa['STATUS']})")
    
    # Funções auxiliares
    def criar_janela(self, titulo, dimensao=None):
        janela = tk.Tk()
        janela.title(titulo)
        janela.iconbitmap(caminhoIcone)

        janela.configure(**ESTILOS["janela"])
        if dimensao:
            janela.geometry(dimensao)
        return janela

    def criar_rotulo(self, frame, texto, linha, coluna, **estilo):
        tk.Label(frame, text=texto, **estilo).grid(row=linha, column=coluna, pady=5)

    def criar_popup(self, titulo, comando_salvar):
        self.popup = tk.Toplevel()
        self.popup.title(titulo)
        self.popup.iconbitmap(caminhoIcone)
        self.popup.configure(**ESTILOS["janela"])
        self.popup.transient(self.janela_principal)
        self.popup.grab_set()

        popup_conteudo = tk.Frame(self.popup, **ESTILOS["janela"])
        popup_conteudo.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        botao_salvar = tk.Button(self.popup, text="Finalizar", command=comando_salvar)
        botao_salvar.pack(pady=10)
        return self.popup, popup_conteudo

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
        popup, popup_conteudo = self.criar_popup("Adicionar Nova Tarefa", lambda: self.salvar_adicao_tarefa(popup))
        
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
        self.setor_selecionado.set("Selecione um setor")
        setor_menu = tk.OptionMenu(popup_conteudo, self.setor_selecionado, *setores_nomes, command=self.atualizar_funcionarios)
        setor_menu.grid(row=2, column=1, pady=5)

        # Dropdown para selecionar o funcionário (inicialmente vazio)
        self.criar_rotulo(popup_conteudo, "Funcionário Responsável:", 3, 0, **ESTILOS["texto"])
        self.funcionario_selecionado = tk.StringVar()
        self.funcionario_selecionado.set("Selecione um funcionário")
        self.funcionarios_menu = tk.OptionMenu(popup_conteudo, self.funcionario_selecionado, "")
        self.funcionarios_menu.grid(row=3, column=1, pady=5)
  
    def criar_usuario(self):
        # Criar o popup
        popup, popup_conteudo = self.criar_popup("Criar Novo Usuário", lambda: self.salvar_usuario(campo_nome, campo_senha, cargos_dict[cargo_selecionado.get()], setores_dict[setor_selecionado.get()], popup))

        # Campo para nome do usuário
        self.criar_rotulo(popup_conteudo, "Nome do Usuário:", 0, 0, **ESTILOS["texto"])
        campo_nome = tk.Entry(popup_conteudo, width=40)
        campo_nome.grid(row=0, column=1, pady=5)

        # Campo para senha do usuário
        self.criar_rotulo(popup_conteudo, "Senha:", 1, 0, **ESTILOS["texto"])
        campo_senha = tk.Entry(popup_conteudo, show="*", width=40)
        campo_senha.grid(row=1, column=1, pady=5)

        # Dropdown para seleção de CARGO
        self.criar_rotulo(popup_conteudo, "Cargo:", 2, 0, **ESTILOS["texto"])
        cargos = FB.carregar_cargos()
        print("Cargos retornados do banco:", cargos)


        cargos_dict = {cargo['NOME_CARGO']: cargo['CARGOS_ID'] for cargo in cargos}
        cargos_nomes = list(cargos_dict.keys())
        cargo_selecionado = tk.StringVar(value=cargos_nomes[0])
        tk.OptionMenu(popup_conteudo, cargo_selecionado, *cargos_nomes).grid(row=2, column=1, pady=5)

       # Dropdown para selecionar o setor
        self.criar_rotulo(popup_conteudo, "Setor:", 3, 0, **ESTILOS["texto"])
        setores = FB.carregar_setores()  # Função que retorna uma lista de setores do banco
        setores_dict = {setor[1]: setor[0] for setor in setores}  # mapeando nome para id

        # Opção de menu com nomes de setores
        setores_nomes = [setor[1] for setor in setores]
        setor_selecionado = tk.StringVar(value=setores_nomes[0])
        setor_selecionado.set("Selecione um setor")
        setor_menu = tk.OptionMenu(popup_conteudo, setor_selecionado, *setores_nomes)
        setor_menu.grid(row=3, column=1, pady=5)

    def marcar_concluida(self):
        try:
            # Obtemos o ID da tarefa selecionada
            index_selecionado = self.lista_tarefas.curselection()[0]
            id_tarefa = self.lista_tarefas.get(index_selecionado).split(" - ")[0].strip(" ● ").strip()
            
            # Abrir popup para a descrição da solução
            popup, popup_conteudo = self.criar_popup("Concluir Tarefa", lambda: self.salvar_tarefa_concluida(id_tarefa, popup))

            # Label e campo para a descrição da solução
            self.criar_rotulo(popup_conteudo, "Descrição da Solução:", 0, 0, **ESTILOS["texto"])
            self.descricao_solucao = tk.Text(popup_conteudo, width=40, height=5)
            self.descricao_solucao.grid(row=1, column=0, pady=10, padx=10)

        except IndexError:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para marcar como concluída.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao marcar tarefa como concluída: {e}")

    def salvar_tarefa_concluida(self, id_tarefa, popup):
        """
        Salva a conclusão da tarefa no banco de dados, incluindo a descrição da solução.
        """
        try:
            # Obter a descrição da solução do campo Text
            descricao = self.descricao_solucao.get("1.0", tk.END).strip()
            if not descricao:
                messagebox.showwarning("Campos Incompletos", "Por favor, preencha a descrição da solução.")
                return

            # Atualizar a tarefa no banco de dados
            FB.atualizar_status_tarefa(id_tarefa, descricao, self.id_usuario)  # Salva a solução no banco

            # Mensagem de sucesso e atualização da lista
            messagebox.showinfo("Sucesso", "Tarefa concluída com sucesso!")
            popup.destroy()  # Fechar o popup
            self.carregar_lista_tarefas()  # Atualizar a lista de tarefas

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar conclusão da tarefa: {e}")
    
    def salvar_usuario(self, campo_nome, campo_senha, cargo_id, setor_id, popup):
        nome = campo_nome.get().strip()
        senha = campo_senha.get().strip()
        print(f"Nome: {nome}, Senha: {senha}, Cargo ID: {cargo_id}, Setor ID: {setor_id}")
        # Validação
        if not nome or not senha:
            messagebox.showwarning("Campos Obrigatórios", "Por favor, preencha todos os campos.")
            return

        try:
            # Lógica para salvar no banco de dados
            FB.criar_usuario(nome, senha, cargo_id, setor_id)
            messagebox.showinfo("Sucesso", f"Usuário '{nome}' criado com sucesso!")
            popup.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar usuário: {e}")

    def atualizar_funcionarios(self, setor_id=None):
        """
        Atualiza a lista de funcionários vinculados ao setor selecionado.
        """
        try:
            setor_nome = self.setor_selecionado.get()  # Pega o nome selecionado
            setor_id = self.setores_dict[setor_nome]   # Converte para ID

            if not setor_id:
                raise ValueError("Setor inválido ou não selecionado.")  # Validar se o setor é válido

            funcionarios = FB.carregar_funcionarios_por_setor(setor_id) # Função que busca funcionários do setor 

            # Caso não haja funcionários, usar a mensagem padrão como opção única
            if not funcionarios:
                funcionarios = ["Nenhum funcionário disponível"]
            else:
                funcionarios.insert(0, "TODOS")  # Adicionar 'TODOS' se houver funcionários

            # Atualizar o OptionMenu dos funcionários
            self.funcionario_selecionado.set(funcionarios[0])  # Seleciona o primeiro item
            self.funcionarios_menu["menu"].delete(0, "end")  # Limpar menu atual
            for funcionario in funcionarios:
                self.funcionarios_menu["menu"].add_command(
                    label=funcionario,
                    command=lambda f=funcionario: self.funcionario_selecionado.set(f)
                )
        except Exception as e:
            # Gerenciar erros ao carregar funcionários
            messagebox.showerror("Erro", f"Erro ao carregar funcionários: {e}")
            self.funcionario_selecionado.set("Erro ao carregar funcionários")
            self.funcionarios_menu["menu"].delete(0, "end")

    def salvar_adicao_tarefa(self, popup):
        """
        Salva a nova tarefa no banco de dados.
        """
        titulo = self.campo_titulo.get()
        descricao = self.campo_descricao.get("1.0", tk.END).strip()
        setores = self.setor_selecionado.get()
        setor_id = self.setores_dict[setores]
        funcionario = self.funcionario_selecionado.get()
        print(setor_id)
        if not titulo or not descricao or setor_id == "Selecione um setor" or funcionario == "Selecione um funcionário":
            messagebox.showwarning("Campos Incompletos", "Por favor, preencha todos os campos antes de salvar.")
            return

        try:
           # Verificar se "TODOS" foi selecionado
            if funcionario == "TODOS":
                ids_funcionarios = FB.carregar_funcionarios_por_id(setor_id)
                if ids_funcionarios:
                    FB.adicionar_tarefa_db(titulo, descricao, setor_id, ids_funcionarios)
                else:
                    messagebox.showwarning("Sem Funcionários", "Não há funcionários vinculados a este setor.")
            
            else:
                # Buscar o ID do funcionário específico
                funcionario_id = FB.buscar_id_funcionario(funcionario)
                FB.adicionar_tarefa_db(titulo, descricao, setor_id, funcionario_id)
            
            messagebox.showinfo("Sucesso", "Tarefa adicionada com sucesso!")
            self.popup.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar tarefa: {e}")

if __name__ == "__main__":
    App()