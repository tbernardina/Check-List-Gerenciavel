import pymysql
from Conexao import conexao_db

def verificar_credenciais(usuario, senha):
    conexao = conexao_db()
    with conexao.cursor() as cursor:

        cursor.execute("""SELECT ADMINISTRADOR FROM usuarios WHERE NOME = %s AND SENHA = %s""", (usuario, senha))
        resultado = cursor.fetchone()
    conexao.close()

    return resultado["ADMINISTRADOR"] if resultado else None

def carregar_tarefas():
    conexao = conexao_db()
    with conexao.cursor() as cursor:

        cursor.execute("SELECT * FROM tarefas")
        tarefas = cursor.fetchall()
    conexao.close()

    return tarefas

def adicionar_tarefa_db(descricao):
    conexao = conexao_db()
    with conexao.cursor() as cursor:

        cursor.execute("INSERT INTO tarefas (DESCRICAO) VALUES (%s)", (descricao,))
    conexao.commit()
    conexao.close()

def remover_tarefa_bd(id_tarefa):
    conexao = conexao_db()
    with conexao.cursor() as cursor:
        cursor.execute("DELETE FROM tarefas WHERE TAREFAS_ID = %s", (id_tarefa,))
    conexao.commit()
    conexao.close()

def atualizar_status_tarefa(id_tarefa, status):
    conexao = conexao_db()
    with conexao.cursor() as cursor:

        cursor.execute("UPDATE tarefas SET STATUS = %s WHERE TAREFAS_ID = %s", (status, id_tarefa))
    conexao.commit()
    conexao.close()

