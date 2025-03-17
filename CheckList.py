# Copyright 2025 Thiago Reis Dalla Bernardina
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
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkcalendar import DateEntry
from datetime import datetime
from Conexao import conexao_db
import FuncoesBanco as FB
import Notifications as NF
from config import server_ip, caminhoIcone, timeout_notify, ESTILOS
import os
import time
import shutil
import uuid
from smb.SMBConnection import SMBConnection

class App:
    def __init__(self):
        self.id_usuario = None
        self.usuario = None
        self.senha = None
        self.nivel_acesso = None
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
        id = FB.verificar_informacao_usuario(usuario, senha, "USER_ID") 
        senha_usuario = FB.verificar_informacao_usuario(usuario, senha, "SENHA")
        if nivel:
            self.usuario = usuario
            self.senha = senha_usuario
            self.nivel_acesso = nivel
            self.id_usuario = id
            self.janela_login.destroy()
            self.abrir_interface_principal()
        else:
            messagebox.showerror("Erro de Login", "Usuário ou senha incorretos.")

    def conectar_SMB(self):
        """Cria a conexão para troca de arquivos com o servidor"""
        try:
            conn = SMBConnection("dev", "Lac19252819*", "CLIENTE", "DEV-SERV", use_ntlm_v2=True, is_direct_tcp=True)
            conn.connect(server_ip, 445)
            return conn
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na conexão SMB: {e}")
            return

    def detalhes_tarefa(self, event):
        try:
            # Recuperar índice da tarefa selecionada
            index_selecionado = self.lista_tarefas.curselection()[0]
            id_tarefa = self.lista_tarefas.get(index_selecionado).split(" - ")[0].strip(" ● ").strip()
            detalhes = FB.select_tarefas(id_tarefa)
            anexos_criacao = [anexo["CAMINHO_ARQUIVO"] for anexo in FB.select_anexo(id_tarefa, "CRIAÇÃO")]
            anexos_solucao = [anexo["CAMINHO_ARQUIVO"] for anexo in FB.select_anexo(id_tarefa, "SOLUÇÃO")] if detalhes["STATUS"] == "CONCLUÍDA" else []
            print(f"Esses são os anexos da tarefa: {anexos_criacao}")

            popup = tk.Toplevel()
            popup.geometry("339x600")
            popup.title(f"DETALHES DA TAREFA {id_tarefa}")
            popup.iconbitmap(caminhoIcone)
            popup.configure(**ESTILOS["janela"])
            popup.transient(self.janela_principal)
            popup.grab_set()

            # popup_conteudo = tk.Frame(popup, **ESTILOS["janela"])
            # popup_conteudo.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Criar um frame principal para conter Canvas e Scrollbar
            frame_principal = tk.Frame(popup)
            frame_principal.pack(fill="both", expand=True)

            # Criar Canvas para rolagem
            canvas = tk.Canvas(frame_principal)
            canvas.pack(side="left", fill="both", expand=True)

            # Criar Scrollbar e vinculá-la ao Canvas
            scrollbar = tk.Scrollbar(frame_principal, orient="vertical", command=canvas.yview)
            scrollbar.pack(side="right", fill="y")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Criar um frame dentro do Canvas para os conteúdos
            popup_conteudo = tk.Frame(canvas, **ESTILOS["janela"])
            popup_conteudo.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            # Adicionar o frame ao Canvas como uma janela rolável
            canvas_window = canvas.create_window((0, 0), window=popup_conteudo, anchor="center")

            def ajustar_tamanho(event):
                """ Ajustar largura do frame para o tamanho do canvas. """
                canvas.itemconfig(canvas_window, width=event.width)
                if detalhes["STATUS"] == "CONCLUÍDA":
                    canvas.configure(scrollregion=canvas.bbox("all"))
                else:
                    canvas.itemconfig(canvas_window, height=event.height)
            canvas.bind("<Configure>", ajustar_tamanho)
            
            def on_mouse_wheel(event):
                canvas.yview_scroll(-1 * (event.delta // 120), "units")

            canvas.bind_all("<MouseWheel>", on_mouse_wheel)

            def baixar_anexo(anexos):
                conn = self.conectar_SMB()
                pasta_destino = filedialog.askdirectory(title="Selecione a pasta para salvar os anexos")
                if not pasta_destino:  # Se o usuário cancelar a seleção
                    return
                
                erros = []

                for anexo in anexos:
                    try:
                        nome_arquivo = anexo.split("/")[-1]
                        destino = os.path.join(pasta_destino, nome_arquivo)

                        with open(destino, "wb") as arquivo_local:
                            conn.retrieveFile("uploads", anexo, arquivo_local)
                        print(f"Arquivo salvo em: {destino}")
                    except Exception as e:
                        erros.append(f"Erro ao salvar {nome_arquivo}: {e}")
                conn.close()

            campos = [
                ("ID da Tarefa:", detalhes["TAREFAS_ID"]),
                ("Título da Tarefa:", detalhes["TITULO"]),
                ("Setor Destinado:", detalhes["NOME_SETOR"]),
                ("Status Atual:", detalhes["STATUS"]),
                ("Tarefa destinada a:", detalhes["FUNCIONARIO_DESTINO_NOME"])
                
            ]

            for titulo, valor in campos:
                self.criar_campo(popup_conteudo, titulo, valor)

            # Verificar se há anexo da criação
            if anexos_criacao:
                tk.Label(popup_conteudo, text="Anexos de Criação:", **ESTILOS['texto']).pack(anchor="center", pady=5)
                tk.Label(popup_conteudo, text="\n".join([os.path.basename(a) for a in anexos_criacao]), **ESTILOS["texto"]).pack(anchor="center", pady=5)
                baixar_criacao = tk.Button(
                    popup_conteudo, text="Baixar Anexos",
                    command=lambda: baixar_anexo(anexos_criacao)
                )
                baixar_criacao.pack(anchor="center", pady=5)


            self.criar_texto_campo(popup_conteudo, "Descrição da Tarefa:", detalhes["DESCRICAO"])

            if detalhes["STATUS"] == "CONCLUÍDA":
                if anexos_solucao:
                    tk.Label(popup_conteudo, text="Anexos de Solução:", **ESTILOS["texto"]).pack(anchor="center", pady=5)
                    tk.Label(popup_conteudo, text="\n".join([os.path.basename(a) for a in anexos_solucao]), **ESTILOS["texto"]).pack(anchor="center", pady=5)
                    baixar_solucao = tk.Button(
                        popup_conteudo, text="Baixar Anexos",
                        command=lambda: baixar_anexo(anexos_solucao)
                    )
                    baixar_solucao.pack(anchor="center", pady=5)
                    
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

        botao_salvar = tk.Button(popup, text="Finalizar", command=popup.destroy)
        botao_salvar.pack(pady=10)

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
            ("Atualizar", self.carregar_lista_tarefas),
            ("Alterar minha senha", self.alterar_senha_usuario),
        ]

        # Criando os botões e verificando o estado com base no nível de acesso
        for texto, comando in botoes_cabecalho:
            estado = "normal"  # Estado padrão
            if texto in ["Remover", "Adicionar", "Criar Usuário"] and self.nivel_acesso == 3:
                estado = "disabled"  # Desativa se o usuário não for administrador
            
            print(f"Botão: {texto}, Estado: {estado}")  # Debug para verificar o estado do botão

            tk.Button(frame_botoes_cabecalho, text=texto, command=comando, state=estado).pack(side=tk.LEFT, padx=5) # Verificar se o botão é criado dentro do loop

        opcoes = ["TODOS", "CONCLUÍDA", "PENDENTE"]
        self.status_selecionado = tk.StringVar(value=opcoes[2])  # Valor inicial
        tk.OptionMenu(frame_botoes_rodape, self.status_selecionado, *opcoes).pack(side=tk.LEFT, padx=15)

        for texto, comando in botoes_rodape:
            tk.Button(frame_botoes_rodape, text=texto, command=comando).pack(side=tk.LEFT, padx=5)

        self.lista_tarefas = tk.Listbox(frame_lista, width=100, height=15, **ESTILOS["lista_tarefas"])
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
        tarefas = FB.carregar_tarefas(self.nivel_acesso, self.tarefa_status, self.id_usuario)
        
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
        tk.Label(frame, text=titulo, **ESTILOS["texto"]).pack(anchor="center", pady=2)
        campo = tk.Entry(frame, width=55)
        campo.insert(0, valor)
        campo.configure(state="disabled")
        campo.pack(anchor="center", pady=2)

    def criar_texto_campo(self, frame, titulo, valor):
        tk.Label(frame, text=titulo, **ESTILOS["texto"]).pack()
        campo = tk.Text(frame, width=40, height=7)
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

        popup, popup_conteudo = self.criar_popup("Adicionar Nova Tarefa", lambda: self.salvar_adicao_tarefa(popup, self.caminhos_completos))

        self.check_data = tk.BooleanVar(value=False)
        horas=[f"{h:02}" for h in range(24)]
        minutos=[f"{m:02}" for m in range(60)]
        self.data_agenda = DateEntry(popup_conteudo, state="disabled", date_pattern='dd/mm/yyyy')
        self.data_hora = ttk.Combobox(popup_conteudo, values=horas, state="disabled", width=3)
        self.data_minutos = ttk.Combobox(popup_conteudo, values=minutos, state="disabled", width=5)
        self.caminhos_completos = None

        def hab_data():
            if self.check_data.get():
                self.data_agenda.configure(state="normal")
                self.data_hora.configure(state="normal")
                self.data_minutos.configure(state="normal")
            else:
                self.data_agenda.configure(state="disabled")
                self.data_hora.configure(state="disabled")
                self.data_minutos.configure(state="disabled")

        # Campo para título da tarefa
        self.criar_rotulo(popup_conteudo, "Título da Tarefa:", 0, 0, **ESTILOS["texto"])
        self.campo_titulo = tk.Entry(popup_conteudo, width=50)
        self.campo_titulo.grid(row=0, column=1, pady=5)
        
        # Campo para descrição da tarefa
        self.criar_rotulo(popup_conteudo, "Descrição da Tarefa:", 1, 0, **ESTILOS["texto"])
        self.campo_descricao = tk.Text(popup_conteudo, width=40, height=5)
        self.campo_descricao.grid(row=1, column=1, pady=5)

        # Campo para anexo de imagem
        caminho_arquivo = "Nenhum Arquivo Selecionado"
        lbl_caminho = tk.Label(popup_conteudo, text=caminho_arquivo, **ESTILOS["texto"])
        lbl_caminho.grid(row=2, column=0,pady=5)
        def selecionar_arquivo():
            caminhos = filedialog.askopenfilenames(
                title="Selecione um arquivo",
                filetypes=[("Imagens e PDFs", "*.jpg;*.jpeg;*.png;*.pdf")]
            )
            if caminhos:
                self.caminhos_completos = list(caminhos)
                nomes_arquivos = [os.path.basename(c) for c in caminhos]
                lbl_caminho.configure(text=';'.join(nomes_arquivos))
                print(f"Esses são os caminhos selecionados: {self.caminhos_completos}")
        # Botões do anexo de imagem
        tk.Button(popup_conteudo, text="Selecionar arquivo", command=selecionar_arquivo).grid(row=2, column=1, pady=5)
        
        # Dropdown para selecionar o setor
        self.criar_rotulo(popup_conteudo, "Setor:", 3, 0, **ESTILOS["texto"])
        setores = FB.carregar_setores()  # Função que retorna uma lista de setores do banco
        self.setores_dict = {setor[1]: setor[0] for setor in setores}  # mapeando nome para id

        # Opção de menu com nomes de setores
        setores_nomes = [setor[1] for setor in setores]
        self.setor_selecionado = tk.StringVar(value=setores_nomes[0])
        self.setor_selecionado.set("Selecione um setor")
        setor_menu = tk.OptionMenu(popup_conteudo, self.setor_selecionado, *setores_nomes, command=self.atualizar_funcionarios)
        setor_menu.grid(row=3, column=1, pady=5)

        # Dropdown para selecionar o funcionário (inicialmente vazio)
        self.criar_rotulo(popup_conteudo, "Funcionário Responsável:", 4, 0, **ESTILOS["texto"])
        self.funcionario_selecionado = tk.StringVar()
        self.funcionario_selecionado.set("Selecione um funcionário")
        self.funcionarios_menu = tk.OptionMenu(popup_conteudo, self.funcionario_selecionado, "")
        self.funcionarios_menu.grid(row=4, column=1, pady=5)

        # Área destinada ao agendamento de tarefas
        tk.Checkbutton(popup_conteudo, text="Agendar tarefa?", variable=self.check_data, command=hab_data).grid(row=5, column=1)

        self.criar_rotulo(popup_conteudo, "Data:", 6,0,**ESTILOS["texto"])
        self.criar_rotulo(popup_conteudo, "Hora: ", 7,0, **ESTILOS["texto"])
        self.criar_rotulo(popup_conteudo, "Minutos: ", 8,0,**ESTILOS["texto"])
        self.data_agenda.grid(row=6, column=1)
        self.data_hora.grid(row=7, column=1)
        self.data_minutos.grid(row=8, column=1)
        

    def alterar_senha_usuario(self):
        popup, popup_conteudo = self.criar_popup("Alterar Minha Senha", lambda: self.salvar_senha(senha_antiga, senha_nova, confirmar_senha_nova, popup))

        self.criar_rotulo(popup_conteudo, "Senha Antiga:", 0,0,**ESTILOS["texto"])
        senha_antiga = tk.Entry(popup_conteudo, width=40)
        senha_antiga.grid(row=0, column=1, pady=5)

        self.criar_rotulo(popup_conteudo, "Senha Nova:",1,0,**ESTILOS["texto"])
        senha_nova = tk.Entry(popup_conteudo, width=40, show="*")
        senha_nova.grid(row=1, column=1, pady=5)

        self.criar_rotulo(popup_conteudo, "Confirmar Senha:",2,0,**ESTILOS["texto"])
        confirmar_senha_nova = tk.Entry(popup_conteudo, width=40, show="*")
        confirmar_senha_nova.grid(row=2, column=1, pady=5)

    def criar_usuario(self):
        # Criar o popup
        popup, popup_conteudo = self.criar_popup("Criar Novo Usuário", lambda: self.salvar_usuario(campo_nome, campo_senha, cargos_dict[cargo_selecionado.get()], popup))

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

    def marcar_concluida(self):
        try:
            # Obtemos o ID da tarefa selecionada
            index_selecionado = self.lista_tarefas.curselection()[0]
            id_tarefa = self.lista_tarefas.get(index_selecionado).split(" - ")[0].strip(" ● ").strip()
            
            # Abrir popup para a descrição da solução
            popup, popup_conteudo = self.criar_popup("Concluir Tarefa", lambda: self.salvar_tarefa_concluida(id_tarefa, popup, self.caminhos_completos))

            # Label e campo para a descrição da solução
            self.criar_rotulo(popup_conteudo, "Descrição da Solução:", 0, 0, **ESTILOS["texto"])
            self.descricao_solucao = tk.Text(popup_conteudo, width=40, height=5)
            self.descricao_solucao.grid(row=1, column=0, pady=10, padx=10)

            # Área para envio de arquivos ao servidor
            caminhos_solucao = tk.Label(popup_conteudo, text="Nenhum Arquivo Selecionado", **ESTILOS["texto"])
            caminhos_solucao.grid(row=2, column=0, pady=5)
            def selecionar_arquivo():
                caminhos = filedialog.askopenfilenames(
                    title="Selecione um arquivo",
                    filetypes=[("Imagens e PDFs", "*.jpg;*.jpeg;*.png;*.pdf")]
                )
                if caminhos:
                    self.caminhos_completos = list(caminhos)
                    nomes_arquivos = [os.path.basename(c) for c in caminhos]
                    caminhos_solucao.configure(text=';'.join(nomes_arquivos))
                    print(f"Esses são os caminhos selecionados: {self.caminhos_completos}")
            tk.Button(popup_conteudo, text="Selecionar arquivo", command=selecionar_arquivo).grid(row=3, column=0, pady=5)
            

        except IndexError:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para marcar como concluída.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao marcar tarefa como concluída: {e}")

    def salvar_tarefa_concluida(self, id_tarefa, popup, caminhos_completos):
        """
        Salva a conclusão da tarefa no banco de dados, incluindo a descrição da solução.
        """
        try:
            # Obter as variaveis da solução da tarefa
            caminhos_arquivos = caminhos_completos if caminhos_completos else []
            tarefas_criadas = []
            descricao = self.descricao_solucao.get("1.0", tk.END).strip()

            if not descricao:
                messagebox.showwarning("Campos Incompletos", "Por favor, preencha a descrição da solução.")
                return
            
            
            print(f"Tarefa_id: {id_tarefa}")
            tarefas_criadas.append(id_tarefa)
            print(f"tarefas criadas:{tarefas_criadas}")

            # Envio de arquivos(unica vez)
            if caminhos_arquivos and caminhos_arquivos[0] != "Nenhum Arquivo Selecionado":
                conn = self.conectar_SMB()
                try:
                    try:
                        conn.listPath("uploads", f"{id_tarefa}")
                        print("A pasta já existe no servidor")
                    except Exception as e:
                        if "STATUS_OBJECT_NAME_NOT_FOUND" in str(e) or "Path not found" in str(e):
                            conn.createDirectory("uploads", f"{id_tarefa}")
                    conn.createDirectory("uploads",f"{id_tarefa}/solucao")
                    for caminho in caminhos_arquivos:
                        if caminho:
                            nome_arquivo = os.path.basename(caminho)
                            for id_tarefa in tarefas_criadas:
                                destino = f"{id_tarefa}/solucao/{nome_arquivo}"
                                try:
                                    with open(caminho, "rb") as arquivo_original:
                                        conn.storeFile("uploads", destino, arquivo_original)
                                        print(f"Esse é o id da tarefa: {id_tarefa}")
                                        print(f"Esse é o nome do arquivo: {nome_arquivo}")
                                        print(f"Esse é o destino do arquivo: {destino}")
                                    FB.adicionar_tarefa_anexo_db(id_tarefa, nome_arquivo, destino, "SOLUÇÃO")
                                    print(f"Arquivo {nome_arquivo} enviado para {destino}")
                                except FileNotFoundError:
                                    print(f"Erro: Arquivo {caminho} não encontrado para upload.")
                                except Exception as e:
                                    print(f"Erro ao enviar arquivo: {e}")
                    conn.close()
                    print(f"Diretório criado: {destino}")
                except Exception as e:
                    print(f"Erro na conexão SMB: {e}")
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

    def salvar_senha(self, senha_antiga, senha_nova, confirmar_senha_nova, popup):
        s_antiga = senha_antiga.get().strip()
        s_nova = senha_nova.get().strip()
        c_s_nova = confirmar_senha_nova.get().strip()

        if s_antiga != self.senha:
            messagebox.showerror("Erro", "A sua senha antiga está incorreta.")
        elif s_nova != c_s_nova:
            messagebox.showinfo("Problemas na alteração de senha", "As senhas não estão iguais")
        else:
            FB.alterar_senha(self.id_usuario, s_nova)
            messagebox.showinfo("Sucesso", "Sua senha foi alterada com sucesso.")
            popup.destroy()
        
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

    def salvar_adicao_tarefa(self, popup, caminhos_completos):
        """
        Salva a nova tarefa no banco de dados.
        """
        titulo = self.campo_titulo.get()
        descricao = self.campo_descricao.get("1.0", tk.END).strip()
        setores = self.setor_selecionado.get()
        setor_id = self.setores_dict[setores]
        funcionario = self.funcionario_selecionado.get()
        caminhos_arquivos = caminhos_completos if caminhos_completos else []
        tarefas_criadas = []
        if not titulo or not descricao or setor_id == "Selecione um setor" or funcionario == "Selecione um funcionário":
            messagebox.showwarning("Campos Incompletos", "Por favor, preencha todos os campos antes de salvar.")
            return

        try:
            data_agendada = None
            status = "PENDENTE"
            if self.check_data.get():
                data = self.data_agenda.get()
                hora = self.data_hora.get()
                minuto = self.data_minutos.get()
                data_agendada = datetime.strptime(f"{data} {hora}:{minuto}:00", "%d/%m/%Y %H:%M:%S")
                status = "AGENDADA"
            print(f"A data agendada foi: {data_agendada}")

            # Verificar se "TODOS" foi selecionado
            if funcionario == "TODOS":
                ids_funcionarios = FB.carregar_funcionarios_por_id (setor_id)
                if ids_funcionarios:
                    tarefa_id_int = FB.adicionar_tarefa_db(titulo, descricao, setor_id, funcionario_id, data_agendada, status)
                tarefa_id_anexo = str(tarefa_id_int)
                print(f"Tarefa_id: {tarefa_id_anexo}")
                tarefas_criadas.append(tarefa_id_anexo)
                print(f"tarefas criadas:{tarefas_criadas}")
                # Envio de arquivos(unica vez)
                if caminhos_arquivos and caminhos_arquivos[0] != "Nenhum Arquivo Selecionado":
                    conn = self.conectar_SMB()
                    try:
                        conn.createDirectory("uploads",tarefa_id_anexo)
                        conn.createDirectory("uploads",f"{tarefa_id_anexo}/criacao")
                        for caminho in caminhos_arquivos:
                            if caminho:
                                nome_arquivo = os.path.basename(caminho)
                                for tarefa_id_anexo in tarefas_criadas:
                                    destino = f"{tarefa_id_anexo}/criacao/{nome_arquivo}"
                                    try:
                                        with open(caminho, "rb") as arquivo_original:
                                            conn.storeFile("uploads", destino, arquivo_original)
                                            print(f"Esse é o id da tarefa: {tarefa_id_anexo}")
                                            print(f"Esse é o nome do arquivo: {nome_arquivo}")
                                            print(f"Esse é o destino do arquivo: {destino}")
                                        FB.adicionar_tarefa_anexo_db(tarefa_id_anexo, nome_arquivo, destino, "CRIAÇÃO")
                                        print(f"Arquivo `{nome_arquivo} enviado para {destino}")
                                    except FileNotFoundError:
                                        print(f"Erro: Arquivo {caminho} não encontrado para upload.")
                                    except Exception as e:
                                        print(f"Erro ao enviar arquivo: {e}")
                        conn.close()
                        print(f"Diretório criado: {destino}")
                    except Exception as e:
                        print(f"Erro na conexão SMB: {e}")
                else:
                    messagebox.showwarning("Sem Funcionários", "Não há funcionários vinculados a este setor.")
                    return
            else:
                # Buscar o ID do funcionário específico
                funcionario_id = FB.buscar_id_funcionario(funcionario)
                tarefa_id_int = FB.adicionar_tarefa_db(titulo, descricao, setor_id, funcionario_id, data_agendada, status)
                tarefa_id_anexo = str(tarefa_id_int)
                print(f"Tarefa_id: {tarefa_id_anexo}")
                tarefas_criadas.append(tarefa_id_anexo)
                print(f"tarefas criadas:{tarefas_criadas}")
                # Envio de arquivos(unica vez)
                if caminhos_arquivos and caminhos_arquivos[0] != "Nenhum Arquivo Selecionado":
                    conn = self.conectar_SMB()
                    try:
                        conn.createDirectory("uploads",tarefa_id_anexo)
                        conn.createDirectory("uploads",f"{tarefa_id_anexo}/criacao")
                        for caminho in caminhos_arquivos:
                            if caminho:
                                nome_arquivo = os.path.basename(caminho)
                                for tarefa_id_anexo in tarefas_criadas:
                                    destino = f"{tarefa_id_anexo}/criacao/{nome_arquivo}"
                                    try:
                                        with open(caminho, "rb") as arquivo_original:
                                            conn.storeFile("uploads", destino, arquivo_original)
                                            print(f"Esse é o id da tarefa: {tarefa_id_anexo}")
                                            print(f"Esse é o nome do arquivo: {nome_arquivo}")
                                            print(f"Esse é o destino do arquivo: {destino}")
                                        FB.adicionar_tarefa_anexo_db(tarefa_id_anexo, nome_arquivo, destino, "CRIAÇÃO")
                                        print(f"Arquivo `{nome_arquivo} enviado para {destino}")
                                    except FileNotFoundError:
                                        print(f"Erro: Arquivo {caminho} não encontrado para upload.")
                                    except Exception as e:
                                        print(f"Erro ao enviar arquivo: {e}")
                        conn.close()
                        print(f"Diretório criado: {destino}")
                    except Exception as e:
                        print(f"Erro na conexão SMB: {e}")
                tarefas_criadas.clear()
            messagebox.showinfo("Sucesso", "Tarefa adicionada com sucesso!")
            popup.destroy()
        except Exception as e:
            print("Erro", f"Erro ao salvar tarefa: {e}")

if os.path.exists(caminhoIcone):
    if __name__ == "__main__":
        App()