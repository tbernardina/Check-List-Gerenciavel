import pymysql
import pymysql.cursors
import config as cfg

def conexao_db():
    return pymysql.connect(
        host= cfg.server_ip,
        user = cfg.user,
        password = cfg.password,
        database = cfg.database,
        charset = "utf8mb4",
        cursorclass = pymysql.cursors.DictCursor 
)