from plyer import notification

def enviar_notificacao(mensagem):
    notification.notify(
        title="Tarefa Pendente",
        message=mensagem,
        app_name="Gerenciador de Tarefas",
        timeout=5  # Tempo em segundos para a notificação desaparecer
    )