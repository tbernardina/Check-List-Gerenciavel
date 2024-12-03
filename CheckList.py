import tkinter as tk
from tkinter import messagebox
import pymysql
from Conexao import conexao_db

# Funções do banco de dados
def verificar_credenciais(usuario, senha):
    conexao = conexao_db()
    with conexao.cursor() as cursor:

        cursor.execute("""SELECT CARGO FROM PROJETOPYHTON.USUARIOS WHERE NOME = %s AND SENHA = %s""", (usuario, senha))
        resultado = cursor.fetchone()
    conexao.close()

    return resultado["CARGO"] if resultado else None

def carregar_tarefas():
    conexao = conexao_db()
    with conexao.cursor() as cursor:

        cursor.execute("SELECT DESCRICAO, STATUS FROM PROJETOPYTHON.TAREFAS")
        tarefas = cursor.fetchall()
    conexao.close()

    return tarefas

def adicionar_tarefa_db(descricao):
    conexao = conexao_db()
    with conexao.cursor() as cursor:

        cursor.execute("INSERT INTO PROJETOPYTHON.TAREFAS (DESCRICAO) VALUES (%s)", (descricao,))
    conexao.commit()
    conexao.close()

def remover_tarefa_bd(id_tarefa):
    conexao = conexao_db()
    with conexao.cursor() as cursor:

        cursor.execute("DELETE FROM PROJETOPYTHON.TAREFAS WHERE TAREFAS_ID = %s", (id_tarefa,))
    conexao.commit()
    conexao.close()

def atualizar_status_tarefa(id_tarefa, status):
    conexao = conexao_db()
    with conexao.cursor() as cursor:

        cursor.execute("UPDATE PROJETOPYTHON.TAREFAS SET STATUS = %s WHERE TAREFAS_ID = %s", (status, id_tarefa))
    conexao.commit()
    conexao.close()

# Funções da interface
def verificar_login():
    global nivel_acesso
    usuario = entrada_usuario.get()
    senha = entrada_senha.get()

    nivel = verificar_credenciais(usuario, senha)
    if nivel:
        global nivel_acesso
        nivel_acesso = nivel
        janela_login.destroy()
        abrir_interface_principal()
    else:
        messagebox.showerror("Erro de Login", "Usuário ou senha incorretos.")

def adicionar_tarefa():
    if nivel_acesso != "ADMINISTRADOR":
        messagebox.showwarning("Permissão Negada", "Apenas supervisores podem adicionar tarefas.")
        return

    tarefa = entrada_tarefa.get()
    if tarefa:
        adicionar_tarefa_db(tarefa)
        carregar_lista_tarefas()
        entrada_tarefa.delete(0, tk.END)
    else:
        messagebox.showwarning("Aviso", "Digite uma tarefa antes de adicionar.")

def remover_tarefa():
    if nivel_acesso != "ADMINISTRADOR":
        messagebox.showwarning("Permissão Negada", "Apenas supervisores podem remover tarefas.")
        return

    try:
        index_selecionado = lista_tarefas.curselection()[0]
        id_tarefa = lista_tarefas.get(index_selecionado).split(" - ")[0]
        remover_tarefa_bd(id_tarefa)
        carregar_lista_tarefas()
    except IndexError:
        messagebox.showwarning("Aviso", "Selecione uma tarefa para remover.")

def marcar_concluida():
    try:
        index_selecionado = lista_tarefas.curselection()[0]
        id_tarefa = lista_tarefas.get(index_selecionado).split(" - ")[0]
        atualizar_status_tarefa(id_tarefa, "Concluída")
        carregar_lista_tarefas()
    except IndexError:
        messagebox.showwarning("Aviso", "Selecione uma tarefa para marcar como concluída.")

def carregar_lista_tarefas():
    lista_tarefas.delete(0, tk.END)
    tarefas = carregar_tarefas()
    for id_tarefa, descricao, status in tarefas:
        lista_tarefas.insert(tk.END, f"{id_tarefa} - {descricao} ({status})")

# Interface Principal
def abrir_interface_principal():
    janela_principal = tk.Tk()
    janela_principal.title("Gerenciador de Checklists")

    # Entrada de nova tarefa
    frame_entrada = tk.Frame(janela_principal)
    frame_entrada.pack(pady=10)

    global entrada_tarefa
    entrada_tarefa = tk.Entry(frame_entrada, width=40)
    entrada_tarefa.pack(side=tk.LEFT, padx=5)

    botao_adicionar = tk.Button(frame_entrada, text="Adicionar", command=adicionar_tarefa)
    botao_adicionar.pack(side=tk.LEFT)

    # Lista de tarefas
    frame_lista = tk.Frame(janela_principal)
    frame_lista.pack(pady=10)

    global lista_tarefas
    lista_tarefas = tk.Listbox(frame_lista, width=50, height=15)
    lista_tarefas.pack(side=tk.LEFT)

    scrollbar = tk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=lista_tarefas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    lista_tarefas.config(yscrollcommand=scrollbar.set)

    # Botões de controle
    frame_botoes = tk.Frame(janela_principal)
    frame_botoes.pack(pady=10)

    botao_remover = tk.Button(frame_botoes, text="Remover", command=remover_tarefa)
    botao_remover.pack(side=tk.LEFT, padx=5)

    botao_concluida = tk.Button(frame_botoes, text="Marcar como Concluída", command=marcar_concluida)
    botao_concluida.pack(side=tk.LEFT, padx=5)

    # Configurar permissões
    if nivel_acesso == "FUNCIONARIO":
        botao_adicionar.config(state=tk.DISABLED)
        botao_remover.config(state=tk.DISABLED)

    carregar_lista_tarefas()
    janela_principal.mainloop()

# Janela de Login
janela_login = tk.Tk()
janela_login.title("Login")

frame_login = tk.Frame(janela_login, padx=20, pady=20)
frame_login.pack()

tk.Label(frame_login, text="Usuário:").grid(row=0, column=0, pady=5)
entrada_usuario = tk.Entry(frame_login)
entrada_usuario.grid(row=0, column=1, pady=5)

tk.Label(frame_login, text="Senha:").grid(row=1, column=0, pady=5)
entrada_senha = tk.Entry(frame_login, show="*")
entrada_senha.grid(row=1, column=1, pady=5)

botao_login = tk.Button(frame_login, text="Login", command=verificar_login)
botao_login.grid(row=2, columnspan=2, pady=10)

conexao_db()
janela_login.mainloop()
