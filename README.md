# Gerenciador de Tarefas LACSM

## Descrição do Projeto
O **Gerenciador de Tarefas LACSM** é uma aplicação desenvolvida em Python com interface gráfica usando Tkinter. O objetivo é facilitar a gestão de tarefas em um ambiente corporativo, permitindo a criação, remoção e marcação de tarefas como concluídas. A aplicação conta com um sistema de login e níveis de acesso para diferentes cargos, além de configurações externas que podem ser ajustadas facilmente sem recompilar o código.

## Funcionalidades
- **Login de Usuários**: Sistema de login com níveis de acesso (Administrador, Supervisor e Usuário).
- **Gerenciamento de Tarefas**:
  - Criar novas tarefas associadas a setores e funcionários.
  - Remover tarefas (apenas administradores).
  - Marcar tarefas como concluídas, incluindo descrição da solução.
- **Notificações**: Notificações locais sobre tarefas pendentes.
- **Configuração Externa**: Uso de arquivos externos para alterar estilos e configurações sem necessidade de recompilar o aplicativo.

## Estrutura do Projeto

### Estrutura do banco de dados

#### Tabela de usuários
```sql 
CREATE TABLE `usuarios` (
  `USER_ID` int NOT NULL AUTO_INCREMENT,
  `NOME` varchar(35) DEFAULT NULL,
  `SENHA` varchar(16) NOT NULL,
  `CARGO` int DEFAULT NULL,
  `SETOR` int DEFAULT NULL,
  PRIMARY KEY (`USER_ID`),
  UNIQUE KEY `NOME` (`NOME`),
  KEY `FK_SETOR` (`SETOR`),
  KEY `fk_cargo` (`CARGO`),
  CONSTRAINT `fk_cargo` FOREIGN KEY (`CARGO`) REFERENCES `cargos` (`CARGOS_ID`),
  CONSTRAINT `FK_SETOR` FOREIGN KEY (`SETOR`) REFERENCES `setores` (`SETOR_ID`)
);
```

#### Tabela de tarefas
```sql
CREATE TABLE `tarefas` (
  `TAREFAS_ID` int NOT NULL AUTO_INCREMENT,
  `TITULO` varchar(30) DEFAULT NULL,
  `DESCRICAO` varchar(400) NOT NULL,
  `STATUS` enum('PENDENTE','CONCLUÍDA') DEFAULT 'PENDENTE',
  `SETOR` int DEFAULT NULL,
  `TAREFA_SOLUCAO` varchar(500) DEFAULT NULL,
  `DATA_CONCLUSAO` timestamp NULL DEFAULT NULL,
  `FUNCIONARIO_SOLUCAO` int DEFAULT NULL,
  `FUNCIONARIO_DESTINO` int DEFAULT NULL,
  PRIMARY KEY (`TAREFAS_ID`),
  KEY `FK_USER` (`FUNCIONARIO_DESTINO`),
  CONSTRAINT `FK_FUNCIONARIO` FOREIGN KEY (`FUNCIONARIO_DESTINO`) REFERENCES `usuarios` (`USER_ID`),
  CONSTRAINT `FK_USER` FOREIGN KEY (`FUNCIONARIO_DESTINO`) REFERENCES `usuarios` (`USER_ID`)
);
```

#### Tabela de setores
```sql
CREATE TABLE `setores` (
  `SETOR_ID` int NOT NULL AUTO_INCREMENT,
  `NOME_SETOR` varchar(50) NOT NULL,
  PRIMARY KEY (`SETOR_ID`)
);
```

#### Tabela de cargos
```sql
CREATE TABLE `cargos` (
  `CARGOS_ID` int NOT NULL AUTO_INCREMENT,
  `NOME_CARGO` varchar(30) NOT NULL,
  PRIMARY KEY (`CARGOS_ID`)
);
```

### Principais Arquivos
- **`CheckList.py`**: Arquivo principal que inicializa a aplicação e gerencia a interface gráfica.
- **`Conexao.py`**: Responsável pela conexão com o banco de dados.
- **`FuncoesBanco.py`**: Contém as funções para manipulação de dados no banco.
- **`Notifications.py`**: Gerencia as notificações locais usando a biblioteca Plyer.
- **`config.py`**: Arquivo de configuração com estilos e outras configurações.
- **`Check_List_LACSM_Icone.ico`**: Ícone do aplicativo.

### Estrutura do Banco de Dados
- **Tabelas Principais**:
  - `usuarios`: Armazena informações de login e cargos dos usuários.
  - `tarefas`: Contém as tarefas e seus status.
  - `setores`: Lista os setores da organização.
  - `cargos`: Define os níveis de acesso (Administrador, Supervisor, Usuário).

## Requisitos

### Ambiente de Desenvolvimento
- **Python**: Versão 3.10 ou superior.
- **Bibliotecas**:
  - `tkinter`: Interface gráfica.
  - `pymysql`: Conexão com o banco de dados MySQL.
  - `plyer`: Notificações do sistema.

### Banco de Dados
- Servidor MySQL para armazenamento das informações de usuários, tarefas, setores e cargos.

### Dependências do Sistema
- Windows (recomendado).
- Inno Setup para criar o instalador.

## Instalação

### Compilação do Executável
Para compilar o aplicativo em um executável utilizando PyInstaller:

1. Instale o PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Execute o comando para criar o executável no modo **`onedir`**:
   ```bash
   pyinstaller --onedir --icon=Check_List_LACSM_Icone.ico CheckList.py
   ```

### Configurar o Instalador
1. Utilize o Inno Setup para criar o instalador.
2. Adicione os seguintes arquivos no instalador:
   - `CheckList.exe`
   - Todos os arquivos `.py` (como arquivos externos).
   - `config.py` e `Check_List_LACSM_Icone.ico`.

Exemplo de entrada no arquivo `.iss` do Inno Setup:
```ini
[Files]
Source: "C:\caminho\para\CheckList.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\caminho\para\*.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\caminho\para\config.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\caminho\para\Check_List_LACSM_Icone.ico"; DestDir: "{app}"; Flags: ignoreversion
```

## Configurações Externas
O arquivo `config.py` permite alterar as configurações do aplicativo sem necessidade de recompilação. Por exemplo:

```python
# Configurações do estilo dos elementos
ESTILOS = {
    "janela": {"bg": "#2A5D48"},
    "texto": {"font": ("Sans-Serif Bold", 12, "bold"), "bg": "#2A5D48", "fg": "#C34E17"},
    "titulo": {"font": ("Comic Sans MS", 18, "bold"), "bg": "#2A5D48", "fg": "#C34E17"},
    "texto_login": {"font": ("Arial", 12)},
    "lista_tarefas": {"font": ("Arial", 12), "fg": "#37515F"},
}

# Timer para controlar a frequencia das notificações
timeout_notify = 10000

# Variavel para definição do icone do aplicativo
caminhoIcone = "Check_List_LACSM_Icone.ico"
```

## Uso do Aplicativo
1. Abra o aplicativo e realize login com suas credenciais.
2. Dependendo do seu cargo, acesse as funcionalidades:
   - Administradores: Criar, remover e editar tarefas.
   - Supervisores: Visualizar e concluir tarefas.
   - Usuários: Visualizar tarefas atribuídas.
3. Notificações serão exibidas para tarefas pendentes.

## Manutenção
### Alterar o IP do Servidor
Abra o arquivo `config.py` e edite as seguintes variáveis:
```python
# Variaveis de configuração de conexão com o servidor
server_ip = ""
user = ""
password = ""
database = ""
```

### Atualizar Estilos
Os estilos podem ser modificados diretamente no `config.py` na seção `ESTILOS`.

## Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para criar um fork do repositório e enviar pull requests.

## Licença
Este projeto é propriedade de Thiago Reis Dalla Bernardina e está licenciado sob a [Apache License 2.0](LICENSE). Veja o arquivo `LICENSE` para mais detalhes.
