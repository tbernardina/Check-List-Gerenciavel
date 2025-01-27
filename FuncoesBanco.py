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
    Retorna uma informação específica de um usuário (e.g., CARGO, SETOR).
    """
    query = f"SELECT {coluna} FROM usuarios WHERE NOME = %s AND SENHA = %s"
    resultado = executar_query(query, (usuario, senha), fetchone=True)
    return resultado[coluna] if resultado else None

def select_tarefas(id_tarefa):
    query = """select t.TAREFAS_ID, t.TITULO, t.DESCRICAO, t.STATUS, t.TAREFA_SOLUCAO, t.DATA_CONCLUSAO, 
    s.NOME_SETOR, 
    us.NOME as FUNCIONARIO_SOLUCAO_NOME, ud.NOME as FUNCIONARIO_DESTINO_NOME from tarefas t
    left join setores s on t.SETOR = s.SETOR_ID 
    left join usuarios us on t.FUNCIONARIO_SOLUCAO = us.USER_ID 
    left join usuarios ud on t.FUNCIONARIO_DESTINO = ud.USER_ID
    WHERE TAREFAS_ID = %s"""
    return executar_query(query, (id_tarefa,), fetchone=True)

def carregar_tarefas(nivel_acesso, setor_exec,tarefa_status, usuario_id):
    print(f"Este é o nivel de acesso: {nivel_acesso}, esse é o status selecionado: {tarefa_status} e esse é o id do usuário {usuario_id}")

    if nivel_acesso == 3 and tarefa_status != "TODOS":
        query = "SELECT * FROM tarefas WHERE STATUS = %s AND FUNCIONARIO_DESTINO = %s"
        return executar_query(query, (tarefa_status, usuario_id ), fetchall=True)
    
    elif nivel_acesso == 3 and tarefa_status == "TODOS":
        query = "SELECT * FROM tarefas WHERE FUNCIONARIO_DESTINO = %s"
        return executar_query(query, (usuario_id), fetchall=True)
    
    elif nivel_acesso == 2 and tarefa_status != "TODOS":
        query = """
        SELECT t.* FROM tarefas t
        JOIN grupo_permissoes gp ON t.SETOR = gp.SETOR_ID
        JOIN usuarios u ON u.GRUPO_ID = gp.GRUPO_ID
        WHERE u.USER_ID = %s AND t.STATUS = %s;
        """
        return executar_query(query, (usuario_id, tarefa_status), fetchall=True)
    
    elif nivel_acesso == 2 and tarefa_status == "TODOS":
        query = """
        SELECT t.* FROM tarefas t
        JOIN grupo_permissoes gp ON t.SETOR = gp.SETOR_ID
        JOIN usuarios u ON u.GRUPO_ID = gp.GRUPO_ID
        WHERE u.USER_ID = %s;
        """
        return executar_query(query, (usuario_id), fetchall=True)
    
    elif nivel_acesso == 1 and tarefa_status != "TODOS":
        query = "SELECT * FROM tarefas WHERE STATUS = %s"
        return executar_query(query, (tarefa_status), fetchall=True)
    
    elif nivel_acesso == 1 and tarefa_status == "TODOS":
        query = "SELECT * FROM tarefas"
        return executar_query(query, fetchall=True)

def adicionar_tarefa_db(titulo, descricao, setor, id_funcionarios):
    """
    Adiciona uma ou mais tarefas no banco de dados.
    Se 'id_funcionarios' for uma lista, adiciona uma tarefa para cada funcionário.
    """
    if isinstance(id_funcionarios, list):  # Caso seja uma lista de IDs (quando "TODOS" for selecionado)
        for id_funcionario in id_funcionarios:
            query = "INSERT INTO tarefas (TITULO, DESCRICAO, SETOR, FUNCIONARIO_DESTINO) VALUES (%s, %s, %s, %s)"
            executar_query(query, (titulo, descricao, setor, id_funcionario))

    else:  # Caso seja apenas um ID
        query = "INSERT INTO tarefas (TITULO, DESCRICAO, SETOR, FUNCIONARIO_DESTINO) VALUES (%s, %s, %s, %s)"
        executar_query(query, (titulo, descricao, setor, id_funcionarios))

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

def carregar_cargos():
    """
    Busca os cargos existentes no banco de dados.
    """
    query = "SELECT CARGOS_ID, NOME_CARGO FROM cargos"
    return executar_query(query, fetchall=True)

def criar_usuario(nome, senha, cargo_id, setor_id):
    query = """
        INSERT INTO usuarios (NOME, SENHA, CARGO, SETOR)
        VALUES (%s, %s, %s, %s)
    """
    executar_query(query, (nome, senha, cargo_id, setor_id))

def carregar_funcionarios_por_setor(setor):
    query = "SELECT USER_ID ,NOME FROM usuarios WHERE SETOR = %s"
    resultados = executar_query(query, (setor), fetchall=True)
    return [resultado["NOME"] for resultado in resultados]

def buscar_id_funcionario(nome_funcionario):
    """
    Retorna o ID do funcionário com base no nome.
    """
    query = "SELECT USER_ID FROM usuarios WHERE NOME = %s"
    resultado = executar_query(query, (nome_funcionario,), fetchone=True)
    return resultado["USER_ID"] if resultado else None

def carregar_funcionarios_por_id(setor):
    """
    Carrega os IDs dos funcionários vinculados ao setor selecionado.
    """
    query = "SELECT USER_ID FROM usuarios WHERE SETOR = %s"
    print(f"Query: {query} | Parâmetro: {setor}")  # Debug
    resultados = executar_query(query, (setor,), fetchall=True)
    print(f"Resultados da Query: {resultados}")  # Debug
    return [resultado["USER_ID"] for resultado in resultados] if resultados else []