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
import pymysql.cursors
import config as cfg

def conexao_db():
    if cfg.server_ip == "192.168.1.76":
        print("Você está no servidor de produção")
    else:
        print("Você está no servidor de teste")
    return pymysql.connect(
        host= cfg.server_ip,
        user = cfg.user,
        password = cfg.password,
        database = cfg.database,
        charset = "utf8mb4",
        cursorclass = pymysql.cursors.DictCursor 
    )