import pymysql
from Conexao import conexao_db

def executar_query(query, parametros=(), fetchone=False, fetchall=False):
    """
    Executa uma query genérica no banco de dados.
    """
    conexao = conexao_db()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(query, parametros)
            if fetchone:
                return cursor.fetchone()
            if fetchall:
                return cursor.fetchall()
            conexao.commit()
    except pymysql.MySQLError as e:
        print(f"Erro ao executar query: {e}")
        return None
    finally:
        conexao.close()

def verificar_informacao_usuario(usuario, senha, coluna):
    """
    Retorna uma informação específica de um usuário (e.g., ADMINISTRADOR, SETOR).
    """
    query = f"SELECT {coluna} FROM usuarios WHERE NOME = %s AND SENHA = %s"
    resultado = executar_query(query, (usuario, senha), fetchone=True)
    return resultado[coluna] if resultado else None

def select_tarefas(id_tarefa):
    query = "SELECT * FROM tarefas WHERE TAREFAS_ID = %s"
    return executar_query(query, (id_tarefa,), fetchone=True)

def carregar_tarefas(nivel_acesso, setor_destino, tarefa_status):
    if nivel_acesso == "0" and tarefa_status != "TODOS":
        query = "SELECT * FROM tarefas WHERE SETOR_ID = %s AND STATUS = %s"
        return executar_query(query, (setor_destino, tarefa_status), fetchall=True)
    else:
        query = "SELECT * FROM tarefas"
        return executar_query(query, fetchall=True)

def adicionar_tarefa_db(titulo, descricao, setor, id_funcionario):
    query = "INSERT INTO tarefas (TITULO, DESCRICAO, SETOR, FUNCIONARIO_DESTINO) VALUES (%s, %s, %s, %s)"
    executar_query(query, (titulo, descricao, setor, id_funcionario))

def remover_tarefa_bd(id_tarefa):
    query = "DELETE FROM tarefas WHERE TAREFAS_ID = %s"
    executar_query(query, (id_tarefa,))

def marcar_tarefa_concluida(id_tarefa):
    """
    Marca uma tarefa como concluída no banco de dados.
    """
    query = "UPDATE tarefas SET STATUS = 'Concluída' WHERE TAREFAS_ID = %s"
    executar_query(query, (id_tarefa,))


def atualizar_status_tarefa(id_tarefa, descricao, usuario):
    query = """
        UPDATE tarefas
        SET TAREFA_SOLUCAO = %s, DATA_CONCLUSAO = CURRENT_TIMESTAMP,
        FUNCIONARIO_SOLUCAO = %s, STATUS = "Concluída"
        WHERE TAREFAS_ID = %s
    """
    executar_query(query, (descricao, usuario, id_tarefa))

def carregar_setores():
    """
    Busca os setores do banco de dados.
    """
    query = "SELECT SETOR_ID, NOME_SETOR FROM setores"
    resultados = executar_query(query, fetchall=True)
    return [(resultado["SETOR_ID"], resultado["NOME_SETOR"]) for resultado in resultados]

def carregar_funcionarios_por_setor(setor):
    query = "SELECT NOME FROM usuarios WHERE SETOR = %s"
    resultados = executar_query(query, (setor), fetchall=True)
    return [resultado["NOME"] for resultado in resultados]

def buscar_id_funcionario(nome_funcionario):
    """
    Retorna o ID do funcionário com base no nome.
    """
    query = "SELECT USER_ID FROM usuarios WHERE NOME = %s"
    resultado = executar_query(query, (nome_funcionario,), fetchone=True)
    return resultado["USER_ID"] if resultado else None