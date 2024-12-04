import pymysql
from Conexao import conexao_db

def verificar_credenciais(usuario, senha):
    conexao = conexao_db()
    with conexao.cursor() as cursor:

        cursor.execute("""SELECT ADMINISTRADOR FROM usuarios WHERE NOME = %s AND SENHA = %s""", (usuario, senha))
        resultado = cursor.fetchone()
    conexao.close()

    return resultado["ADMINISTRADOR"] if resultado else None

def verificar_setor(usuario, senha):
    conexao = conexao_db()
    with conexao.cursor() as cursor:
        cursor.execute("""SELECT SETOR FROM usuarios WHERE NOME = %s AND SENHA = %s""", (usuario,senha))
        resultado = cursor.fetchone()
    conexao.close()
    return resultado["SETOR"] if resultado else None

def select_tarefas(id_tarefa):
    conexao = conexao_db()
    with conexao.cursor() as cursor:
        cursor.execute("""SELECT * FROM tarefas WHERE TAREFAS_ID = %s""", (id_tarefa))
        resultado = cursor.fetchone()
    conexao.close()
    return resultado if resultado else None

def carregar_tarefas(nivel_acesso, setor_destino):
    conexao = conexao_db()
    with conexao.cursor() as cursor:
        verificar_credenciais
        if nivel_acesso == "0":
            cursor.execute("SELECT * FROM tarefas where SETOR = %s", (setor_destino))
            tarefas = cursor.fetchall()
        else:
            cursor.execute("SELECT * FROM tarefas")
            tarefas = cursor.fetchall()
    conexao.close()

    return tarefas

def adicionar_tarefa_db(titulo, descricao, setor):
    conexao = conexao_db()
    with conexao.cursor() as cursor:
        cursor.execute("INSERT INTO tarefas (TITULO, DESCRICAO, SETOR) VALUES (%s, %s, %s)", (titulo, descricao, setor))
    conexao.commit()
    conexao.close()

def remover_tarefa_bd(id_tarefa):
    conexao = conexao_db()
    with conexao.cursor() as cursor:
        cursor.execute("DELETE FROM tarefas WHERE TAREFAS_ID = %s", (id_tarefa,))
    conexao.commit()
    conexao.close()

def atualizar_status_tarefa(id_tarefa, status, descricao, usuario):
    conexao = conexao_db()
    with conexao.cursor() as cursor:

        cursor.execute("UPDATE tarefas SET STATUS = %s WHERE TAREFAS_ID = %s", (status, id_tarefa))
        cursor.execute("UPDATE tarefas SET TAREFA_SOLUCAO = %s, DATA_CONCLUSAO = CURRENT_TIMESTAMP, FUNCIONARIO_SOLUCAO = %s  WHERE TAREFAS_ID = %s", (descricao, usuario, id_tarefa))
    conexao.commit()
    conexao.close()