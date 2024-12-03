import pymysql
import pymysql.cursors

def conexao_db():
    return pymysql.connect(
        host="192.168.1.44",
        user = "GerenciadorCheckList",
        password = "Reis2004_",
        database = "PROJETOPYTHON",
        charset = "utf8mb4",
        cursorclass = pymysql.cursors.DictCursor 
)