# Sistema de Gerenciamento Biopark
## Intepretação
Conforme explicado na apresentação, alguns pontos foram deixados para serem interpretados pelo candidado. Na minha interpretação, o sistema é voltado para trabalhadores do próprio Biopark, como ferramenta de gestão **interna** e como tal:

- Não há ferramenta para cadastro de usuários, sendo necessário inseri-los manualmente na base de dados.
- Idealmente, o sistema seria usado em uma rede interna ou VPN, mas a opção de utilizar certificados digitais é oferecida.
- Um endpoint para atualização de informações sobre apartamentos é fornecido. Por meio dele, é possível registrar que um apartamento que estava vago agora está ocupado, isto é, alugar o apartamento.

## Dependências Python
Para executar o ```app.py``` são necessárias as seguintes dependências:
```bash
pip install flask
pip install mysql.connector
pip install mysql-connector-python
```
Também são necessárias as bibliotecas: ```logging```, ```random``` e ```json```, mas essas são nativas do Python, então não deve haver problemas.

## Base de dados
A base de dados utilizada foi o MySQL por questões de familiaridade. Para correta execução do sistema, você precisa de um usuário e uma base de dados. Os nomes podem variar, já que são definidos no arquivo [config.py](https://github.com/joaopedrolourencoaffonso/projeto-biopark/blob/main/config.py), utilize os comandos abaixo para criar uma base dados chamada ```biopark``` acessível a um usuário ```sistema_remoto``` a partir de ```seu_endereço_IP```:

```bash
joao@Ubuntu:~/Desktop$ sudo mysql

mysql> CREATE USER sistema_remoto@seu_endereco_IP identified by 'senha';
Query OK, 0 rows affected (0,10 sec)

mysql> create DATABASE biopark;
Query OK, 1 row affected (0,06 sec)

mysql> grant all privileges on biopark.* to sistema_remoto@seu_endereco_IP;

mysql> flush privileges;
Query OK, 0 rows affected (0,08 sec)
```
Agora, acesse a base de dados com o usuário sistema_remoto e crie as bases de dados necessárias:
```bash
joao@Ubuntu:~/Desktop$ mysql -u sistema -p
Enter password:

mysql> use biopark;
Database changed

mysql> create table edificios (id_edificio int not null auto_increment, nome_edificio char(255), endereco char(255), primary key (id_edificio));

mysql> create table apartamentos (id_apartamento int not null auto_increment, id_edificio int, nome_apartamento char(255), nome_locatario char(255), preco int, primary key (id_apartamento));

mysql> create table users (user_id int not null auto_increment, user_name char(255), password char(255), primary key (user_id));

mysql>commit;

mysql> insert into users (user_name, password) values (joao, senha);

mysql>commit;
```
_Nota: Os nomes acima podem variar, mas lembre-se de editar o arquivo [config.py](https://github.com/joaopedrolourencoaffonso/projeto-biopark/blob/main/config.py) de acordo, **sendo inteiramente possível utilizar o MySQL na mesma máquina que o app.py**_ 

## Utilizando o TLS

Um exemplo de arquivo de configuração está disponível [aqui](https://github.com/joaopedrolourencoaffonso/projeto-biopark/blob/main/config.py). É necessário que o arquivo contenha TODAS as variáveis descritas.

As variáveis ```chave_privada``` e ```certificado```, em específico devem conter o caminho para, respectivamente, uma chave privada e um certificado correspondente. Nesse diretório, você pode encontrar um par de [chave privada](https://github.com/joaopedrolourencoaffonso/projeto-biopark/blob/main/sistema.pem) e [certificado auto-assinado](https://github.com/joaopedrolourencoaffonso/projeto-biopark/blob/main/sistema_crt.pem). Caso você não deseje utilizar HTTPS, basta salvar ambas as variáveis como "False", conforme o exemplo.

## Utilizando o Sistema
Para iniciar o sistema, basta utilizar:
```bash
python3 app.py
```
Uma vez iniciada, acesso o par endereço porta que você salvou (ex: "http://localhost:5000/"). Se você estiver utilizando HTTPS, mas não estiver usando a porta padrão, não esqueça de adicionar o ```https://``` no início do endereço, já que seu browser **não** vai identificar automaticamente.
