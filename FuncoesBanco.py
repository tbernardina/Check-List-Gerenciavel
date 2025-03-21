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
            tarefa_id = cursor.lastrowid
            if fetchone:
                return cursor.fetchone()
            if fetchall:
                return cursor.fetchall()
            conexao.commit()
            return tarefa_id
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
    left join usuarios_tarefas fs on t.TAREFAS_ID = fs.TAREFAS_ID and fs.TIPO = 'SOLUÇÃO'
    left join usuarios us on fs.USER_ID = us.USER_ID
    left join usuarios_tarefas fd on t.TAREFAS_ID = fd.TAREFAS_ID and fd.TIPO = 'DESTINO'
    left join usuarios ud on fd.USER_ID = ud.USER_ID
    WHERE t.TAREFAS_ID = %s"""
    return executar_query(query, (id_tarefa), fetchone=True)

def select_anexo(id_tarefa, tipo):
    query = """SELECT CAMINHO_ARQUIVO FROM anexos_imagem where TAREFAS_ID = %s AND TIPO = %s"""
    return executar_query(query, (id_tarefa, tipo), fetchall=True)

def carregar_tarefas(nivel_acesso, tarefa_status, usuario_id):
    print(f"Este é o nivel de acesso: {nivel_acesso}, esse é o status selecionado: {tarefa_status} e esse é o id do usuário {usuario_id}")

    if nivel_acesso == 3 and tarefa_status != "TODOS":
        query = """
        SELECT t.*, ut.USER_ID FROM tarefas t join usuarios_tarefas ut on ut.TAREFAS_ID = t.TAREFAS_ID WHERE ut.USER_ID = %s AND STATUS = %s
        """
        return executar_query(query, (usuario_id, tarefa_status), fetchall=True)
    
    elif nivel_acesso == 3 and tarefa_status == "TODOS":
        query = """
        SELECT t.*, ut.USER_ID FROM tarefas t join usuarios_tarefas ut on ut.TAREFAS_ID = t.TAREFAS_ID WHERE ut.USER_ID = %s AND STATUS != "INATIVO" AND STATUS != "AGENDADA"
        """
        return executar_query(query, (usuario_id), fetchall=True)
    
    elif nivel_acesso == 2 and tarefa_status != "TODOS":
        query = """
        SELECT t.* FROM tarefas t
        JOIN grupo_permissoes gp ON t.SETOR = gp.SETOR_ID
        JOIN usuarios u ON u.GRUPO_ID = gp.GRUPO_ID
        WHERE u.USER_ID = %s AND t.STATUS = %s
        """
        return executar_query(query, (usuario_id, tarefa_status), fetchall=True)
    
    elif nivel_acesso == 2 and tarefa_status == "TODOS":
        query = """
        SELECT t.* FROM tarefas t
        JOIN grupo_permissoes gp ON t.SETOR = gp.SETOR_ID
        JOIN usuarios u ON u.GRUPO_ID = gp.GRUPO_ID
        WHERE u.USER_ID = %s AND t.STATUS != "INATIVO"
        """
        return executar_query(query, (usuario_id), fetchall=True)
    
    elif nivel_acesso == 1 and tarefa_status != "TODOS":
        query = "SELECT * FROM tarefas WHERE STATUS = %s"
        return executar_query(query, (tarefa_status), fetchall=True)
    
    elif nivel_acesso == 1 and tarefa_status == "TODOS":
        query = """
                SELECT * FROM tarefas 
                WHERE STATUS != "INATIVO"
                """
        return executar_query(query, fetchall=True)

def adicionar_tarefa_db(titulo, descricao, setor, id_funcionarios, data_agendada, status):
    """
    Adiciona uma ou mais tarefas no banco de dados.
    Se 'id_funcionarios' for uma lista, adiciona uma tarefa para cada funcionário.
    """
    if isinstance(id_funcionarios, list):  # Caso seja uma lista de IDs (quando "TODOS" for selecionado)
        for id_funcionario in id_funcionarios:
            query = "INSERT INTO tarefas (TITULO, DESCRICAO, SETOR, DATA_AGENDADA, STATUS) VALUES (%s, %s, %s, %s, %s)"
            tarefa_id_db = executar_query(query, (titulo, descricao, setor, data_agendada, status))
            adicionar_usuario_tarefa_db(tarefa_id_db, id_funcionario, "DESTINO")
    else:  # Caso seja apenas um ID
        query = "INSERT INTO tarefas (TITULO, DESCRICAO, SETOR, DATA_AGENDADA, STATUS) VALUES (%s, %s, %s, %s, %s)"
        tarefa_id_db = executar_query(query, (titulo, descricao, setor, data_agendada, status))
        adicionar_usuario_tarefa_db(tarefa_id_db, id_funcionarios, "DESTINO")
    return tarefa_id_db

def adicionar_usuario_tarefa_db(id_tarefa, id_funcionario, tipo):
    query = "INSERT INTO usuarios_tarefas (TAREFAS_ID, USER_ID, TIPO) values(%s,%s,%s)"
    executar_query(query, (id_tarefa, id_funcionario, tipo))

def adicionar_tarefa_anexo_db(id_tarefa, nome_arquivo,caminho_arquivo, tipo_arquivo):
    query="""INSERT INTO anexos_imagem (TAREFAS_ID, NOME_ANEXO, CAMINHO_ARQUIVO, TIPO) VALUES (%s, %s, %s, %s)"""
    executar_query(query, (id_tarefa, nome_arquivo, caminho_arquivo, tipo_arquivo))

def remover_tarefa_bd(id_tarefa):
    query = """UPDATE tarefas SET STATUS = "INATIVO" WHERE TAREFAS_ID = %s"""
    executar_query(query, (id_tarefa,))

def marcar_tarefa_concluida(id_tarefa):
    """
    Marca uma tarefa como concluída no banco de dados.
    """
    query = "UPDATE tarefas SET STATUS = 'CONCLUÍDA' WHERE TAREFAS_ID = %s"
    executar_query(query, (id_tarefa,))


def atualizar_status_tarefa(id_tarefa, descricao, usuario):
    query = """
        UPDATE tarefas
        SET TAREFA_SOLUCAO = %s, DATA_CONCLUSAO = CURRENT_TIMESTAMP, STATUS = 'CONCLUÍDA'
        WHERE TAREFAS_ID = %s
    """
    adicionar_usuario_tarefa_db(id_tarefa, usuario, "SOLUÇÃO")
    executar_query(query, (descricao, id_tarefa))

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
    query = """SELECT CARGOS_ID, NOME_CARGO FROM cargos WHERE CARGOS_ID - 1"""
    return executar_query(query, fetchall=True)

def criar_usuario(nome, senha, cargo_id):
    query = """
        INSERT INTO usuarios (NOME, SENHA, CARGO)
        VALUES (%s, %s, %s)
    """
    executar_query(query, (nome, senha, cargo_id))

def carregar_funcionarios_por_setor(setor):
    query = """
        SELECT u.USER_ID, u.NOME
        FROM usuarios_setores us
        JOIN usuarios u ON us.USER_ID = u.USER_ID
        WHERE us.SETOR_ID = %s
        """
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
    query = """
    SELECT u.USER_ID FROM usuarios u 
    RIGHT JOIN usuarios_setores us ON u.USER_ID=us.USER_ID 
    WHERE us.SETOR_ID = %s
    """
    print(f"Query: {query} | Parâmetro: {setor}")  # Debug
    resultados = executar_query(query, (setor,), fetchall=True)
    print(f"Resultados da Query: {resultados}")  # Debug
    return [resultado["USER_ID"] for resultado in resultados] if resultados else []

def alterar_senha(id_usuario, s_nova):
    """
    Altera a senha do usuário
    """
    query = "UPDATE usuarios set SENHA = %s where USER_ID = %s"
    return executar_query(query, (s_nova, id_usuario))

def carregar_usuarios_admin():
    """
    Retorna todos os usuários, exceto administradores.
    """
    query = "SELECT USER_ID, NOME FROM usuarios WHERE CARGO != 1"
    resultados = executar_query(query, fetchall=True)
    
    return resultados if resultados else []