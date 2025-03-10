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
from plyer.platforms.win.notification import WindowsNotification
from config import timeout_notify

def enviar_notificacao(mensagem):
    try:
        notifier = WindowsNotification()
        notifier.notify(
            title="Tarefas Pendentes",
            message=mensagem,
            app_name="CheckList",
            timeout=timeout_notify
        )
        print("Notificação enviada com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar notificação: {e}")