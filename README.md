# Gerenciador de Tarefas
## Descrição do Projeto
O **Gerenciador de Tarefas** é uma aplicação desenvolvida em Python com interface gráfica usando Tkinter. O objetivo é facilitar a gestão de tarefas em um ambiente corporativo, permitindo a criação, remoção e documentar as soluções das mesmas. A aplicação conta com um sistema de login e níveis de acesso para diferentes cargos, além de configurações externas que podem ser ajustadas facilmente sem recompilar o código.

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
  PRIMARY KEY (`USER_ID`),
  UNIQUE KEY `NOME` (`NOME`),
  KEY `fk_cargo` (`CARGO`),
  CONSTRAINT `fk_cargo` FOREIGN KEY (`CARGO`) REFERENCES `cargos` (`CARGOS_ID`),
);
```

#### Tabela de tarefas
```sql
CREATE TABLE `tarefas` (
  `TAREFAS_ID` int NOT NULL AUTO_INCREMENT,
  `TITULO` varchar(30) DEFAULT NULL,
  `DESCRICAO` varchar(400) NOT NULL,
  `STATUS` enum('PENDENTE','CONCLUÍDA', 'AGENDADA', 'INATIVO') DEFAULT 'PENDENTE',
  `SETOR` int DEFAULT NULL,
  `TAREFA_SOLUCAO` varchar(500) DEFAULT NULL,
  `DATA_CONCLUSAO` timestamp NULL DEFAULT NULL,
  `DATA_AGENDADA` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`TAREFAS_ID`),
  KEY `FK_USER` (`FUNCIONARIO_DESTINO`),
  KEY `FK_SETOR_TAREFAS` (`SETOR`),
  CONSTRAINT  `FK_SETOR_TAREFAS` FOREIGN KEY (`SETOR`) REFERENCES `setores` (`SETOR_ID`),
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

#### Tabela de grupos
```sql
CREATE TABLE `grupo` (
    `GRUPO_ID` INT AUTO_INCREMENT PRIMARY KEY,
    `NOME_GRUPO` VARCHAR(100) NOT NULL UNIQUE
);
```

#### Tabela de permissões de visão das tarefas
```sql
CREATE TABLE `grupo_permissoes` (
    `GRUPO_ID` INT NOT NULL,
    `SETOR_ID` INT NOT NULL,
    PRIMARY KEY (`GRUPO_ID`, `SETOR_ID`),
    FOREIGN KEY (`GRUPO_ID`) REFERENCES grupo(`GRUPO_ID`) ON DELETE CASCADE,
    FOREIGN KEY (`SETOR_ID`) REFERENCES setores(`SETOR_ID`) ON DELETE CASCADE
);
```

#### Tabela de relacionamento de usuário para setor
```sql
CREATE TABLE `usuarios_setores` (
    `USER_ID` INT NOT NULL,
    `SETOR_ID` INT NOT NULL,
    PRIMARY KEY (`USER_ID`, `SETOR_ID`),
    FOREIGN KEY (`USER_ID`) REFERENCES usuarios(`USER_ID`) ON DELETE CASCADE,
    FOREIGN KEY (`SETOR_ID`) REFERENCES setores(`SETOR_ID`) ON DELETE CASCADE
);
```

#### Tabela de armazenamento dos caminhos de documentos anexados
```sql
CREATE TABLE `anexos_imagem` (
  `ANEXOS_ID` int NOT NULL AUTO_INCREMENT,
  `TAREFAS_ID` int NOT NULL,
  `NOME_ANEXO` varchar(255) NOT NULL,
  `caminho_arquivo` varchar(355) NOT NULL,
  `TIPO` enum('CRIAÇÃO','SOLUÇÃO') DEFAULT NULL,
  PRIMARY KEY (`ANEXOS_ID`),
  KEY `TAREFAS_ID` (`TAREFAS_ID`),
  CONSTRAINT `anexos_imagem_ibfk_1` FOREIGN KEY (`TAREFAS_ID`) REFERENCES `tarefas` (`TAREFAS_ID`) ON DELETE CASCADE
);
```

#### Tabela para usuários destinados a tarefas
```sql
CREATE TABLE `usuarios_tarefas`(
`TAREFAS_ID` int not null,
`USER_ID` int not null,
`TIPO` enum ('DESTINO','SOLUÇÃO') not null,
CONSTRAINT `id_tarefa_usuarios_tarefas` FOREIGN KEY (`TAREFAS_ID`) REFERENCES `tarefas` (`TAREFAS_ID`) ON DELETE CASCADE,
CONSTRAINT `id_usuario_usuarios_tarefas` FOREIGN KEY (`USER_ID`) REFERENCES `usuarios` (`USER_ID`) ON DELETE CASCADE
);

```

#### Evento para checagem de data e atualização de tarefas agendadas
```sql
CREATE DEFINER=`root`@`localhost` EVENT `ATUALIZAR_TAREFAS_AGENDADAS` 
  ON SCHEDULE EVERY 1 MINUTE 
  DO 
  BEGIN
  UPDATE TAREFAS 
  SET STATUS = 'PENDENTE' 
  WHERE STATUS = 'AGENDADA' AND DATA_AGENDADA <= NOW();
END
```


### Principais Arquivos
- **`CheckList.py`**: Arquivo principal que inicializa a aplicação e gerencia a interface gráfica.
- **`Conexao.py`**: Responsável pela conexão com o banco de dados.
- **`FuncoesBanco.py`**: Contém as funções para manipulação de dados no banco.
- **`Notifications.py`**: Gerencia as notificações locais usando a biblioteca Plyer.
- **`config.py`**: Arquivo de configuração com estilos e outras configurações.
- **`Check_List_Icone.ico`**: Ícone do aplicativo.

### Estrutura do Banco de Dados
- **Tabelas Principais**:
  - `usuarios`: Armazena informações de login e cargos dos usuários.
  - `tarefas`: Contém as tarefas e seus status.
  - `setores`: Lista os setores da organização.
  - `cargos`: Define os níveis de acesso (Administrador, Supervisor, Usuário).
  - `grupos`: Nomeia grupos de visualização dos supervisores.
  - `grupo_permissoes`: Define quais setores o usuário supervisor terá acesso para visualização.
  - `usuarios_setores`: Tabela utilizada para vincular um usuário para mais de um setor.
  - `anexos_imagem`: Tabela destinada a armazenar o caminho para anexo de documentos na tarefa.

- **Eventos automáticos**:
  - `atualizar_tarefas_agendadas`: Evento que atualiza o status de tarefas agendadas com base na data e hora do servidor.

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

2. Execute o comando para criar o executável no modo **`onedir`**, **`exclude-module`** e **`noconsole`**:
   ```bash
   pyinstaller --onedir --noconsole --exclude-module=config --icon=Check_List_Icone.ico CheckList.py
   ```

### Configurar o Instalador
1. Utilize o Inno Setup para criar o instalador.
2. Adicione os seguintes arquivos no instalador:
   - `CheckList.exe`
   - Todos os arquivos `.py` (como arquivos externos).
   - `config.py` e `Check_List_Icone.ico`.

Exemplo de entrada no arquivo `.iss` do Inno Setup:
```ini
[Files]
Source: "C:\caminho\para\CheckList.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\caminho\para\*.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\caminho\para\config.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\caminho\para\Check_List_Icone.ico"; DestDir: "{app}"; Flags: ignoreversion
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
caminhoIcone = "Check_List_Icone.ico"
```

## Uso do Aplicativo
1. Abra o aplicativo e realize login com suas credenciais.
2. Dependendo do seu cargo, acesse as funcionalidades:
   - Administradores: Criar tarefas, criar usuários, remover e editar tarefas.
   - Supervisores: Visualizar e criar tarefas de um setor especifico.
   - Usuários: Visualizar e concluir tarefas atribuídas.
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
