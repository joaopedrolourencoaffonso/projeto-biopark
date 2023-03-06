#Logging
import logging
Log_Format = "%(levelname)s ;; %(asctime)s ;; %(message)s ;;"
logging.basicConfig(level=logging.INFO,filename = "sistema.log",format=Log_Format)
logger = logging.getLogger();

'''O arquivo config.py deve estar no mesmo diretório/folder que o app.py'''
from config import mysql_host, mysql_port, mysql_user, mysql_password, database, certificado, chave_privada, my_host, my_port

try:
    from flask import Flask, render_template, redirect, request, make_response, jsonify
    import mysql.connector
    from random import randint
    import json
    
    mydb = mysql.connector.connect(
      host=mysql_host,
      port=mysql_port,
      user=mysql_user,
      password=mysql_password,
      database=database
    )
    
    cursor = mydb.cursor();

    app = Flask(__name__)
    log = logging.getLogger('werkzeug')
    log.disabled = True

except Exception as e:
    logger.error(f"Erro durante processo de inicializaçao: {str(e)}");

'''Pagina de login ('Landing Page'), foi usada como base para os demais endpoints'''
@app.route('/')
def index():
    try:
        '''Verificando se o usuario já tem cookies no browser dele.'''
        num = request.cookies.get('biopark-num');
        user = request.cookies.get('biopark-user');
        
        '''Se o usuario não tem cookies, ele é direcionado para a tela de login'''
        if not num or not user:
            return render_template("login.html");
        
        '''A query abaixo retorna 1 se os cookies são válidos, 2 se são inválidos e nada se não há correspondência'''
        cursor.execute(f"select IF(data > DATE_SUB(NOW(), INTERVAL '1' HOUR),1,2) from cookies where user_name = %s and num = %s;",(user,num));
        resultado = cursor.fetchall();
        
        '''Se o usuario tem cookies, mas não batem com nada na base de dados, ele também é enviado para a tela de login'''
        if resultado == []:
            return render_template("login.html");
        
        if resultado[0][0] == 1:
            '''Atualizando os cookies do usuário'''
            cursor.execute(f"update cookies set data = NOW() where user_name = %s and num = %s;",(user,num));
            mydb.commit();
            
            '''Primeira página após o usuário fazer login'''
            return render_template("welcome.html");
        
        else:
            '''Deletando cookies inválidos'''
            cursor.execute(f"delete from cookies where user_name = %s and num = %s;",(user,num));
            mydb.commit();
            
            return render_template("login.html");

    except Exception as e:
        logger.error(f"Erro no servidor {str(e)}")
        return jsonify({'result':'100'});
    
'''Endpoint de login: Basicamente forma de fornecer os cookies ao usuário com base nas informações obtidas do formulário'''
@app.route('/login', methods=['POST'])
def login():
    try:
        user = request.form.get('nome');
        senha = request.form.get('senha');
        
        cursor.execute(f"SELECT count(1) FROM users where user_name = %s and password = %s;",(user, senha));
        resultado = cursor.fetchall();
        
        if resultado[0][0] == 1:
            num = randint(1000000,9999999);
            
            cursor.execute(f"insert into cookies (user_name, num, data) values (%s,%s,now());",(user, num));
            mydb.commit();
            
            response = make_response(render_template("welcome.html"));
            response.set_cookie('biopark-num',f"{num}");
            response.set_cookie('biopark-user',f"{user}");
            
            logger.info(f"Acesso concedido a {user}, IP: {request.remote_addr}.");
            
            return response;
            
        else:
            logger.info(f"Acesso negado ao IP: {request.remote_addr}.");
            return f"Desculpe, usuário ou senha errados."
                  
    except Exception as e:
        logger.error(f"Erro no servidor {str(e)}")
        return jsonify({'result':'100'});

'''Primeira página que o usuário acessa após login. Têm dois links de onde o usuário pode acessar as funcionalidades'''        
@app.route('/welcome')
def welcome():
    try:
        num = request.cookies.get('biopark-num');
        user = request.cookies.get('biopark-user');
        
        if not num or not user:
            return redirect("/");
        
        cursor.execute(f"select IF(data > DATE_SUB(NOW(), INTERVAL '1' HOUR),1,2) from cookies where user_name = %s and num = %s;",(user,num));
        resultado = cursor.fetchall();
        
        if resultado == []:
            return redirect("/");
        
        if resultado[0][0] == 1:
            cursor.execute(f"update cookies set data = NOW() where user_name = %s and num = %s;",(user, num));
            mydb.commit();
            
            return render_template("welcome.html");
        
        else:
            cursor.execute(f"delete from cookies where user_name = %s and num = %s;",(user, num));
            mydb.commit();
            
            return redirect("/");
            
    except Exception as e:
        logger.error(f"Erro no servidor {str(e)}")
        return jsonify({'result':'100'});

'''Tela para cadastro de edificios e apartamentos'''        
@app.route('/cadastro')
def cadastro():
    try:
        num = request.cookies.get('biopark-num');
        user = request.cookies.get('biopark-user');
        
        if not num or not user:
            return redirect("/");
        
        cursor.execute(f"select IF(data > DATE_SUB(NOW(), INTERVAL '1' HOUR),1,2) from cookies where user_name = %s and num = %s;",(user, num));
        resultado = cursor.fetchall();
        
        if resultado == []:
            return redirect("/");
        
        if resultado[0][0] == 1:
            cursor.execute(f"update cookies set data = NOW() where user_name = %s and num = %s;",(user, num));
            mydb.commit();
                   
            return render_template("cadastro.html");
        
        else:
            cursor.execute(f"delete from cookies where user_name = %s and num = %s;",(user, num));
            mydb.commit();
            
            return redirect("/");
            
    except Exception as e:
        logger.error(f"Erro no servidor {str(e)}")
        return jsonify({'result':'100'});

'''Endpoint para cadastrar edificios'''       
@app.route('/edificio_cadastro/<data>', methods=['GET'])
def edificio_cadastro(data):
    try:
        num = request.cookies.get('biopark-num');
        user = request.cookies.get('biopark-user');
        
        if not num or not user:
            return redirect("/");
        
        cursor.execute(f"select IF(data > DATE_SUB(NOW(), INTERVAL '1' HOUR),1,2) from cookies where user_name = %s and num = %s;",(user, num));
        resultado = cursor.fetchall();
        
        if resultado == []:
            return redirect("/");
        
        if resultado[0][0] == 1:
            cursor.execute(f"update cookies set data = NOW() where user_name = %s and num = %s;",(user, num));
            mydb.commit();
            
            data = json.loads(data);
            
            '''Verificando se já existe um edifício com esse nome'''
            cursor.execute("select count(*) from edificios where nome_edificio like %s;",("%" + data['edificio_nome'] + "%",));
            resultado = cursor.fetchall();
            
            if resultado[0][0]:
                return jsonify({'result':'4'});
            
            '''Inserindo edifício e logando ação'''
            cursor.execute(f"insert into edificios (nome_edificio, endereco) values (%s,%s);",(data['edificio_nome'],data['edificio_endereco']));
            mydb.commit();
            
            logger.info(f"Usuario {user} adicionou o edificio {data['edificio_nome']} a partir do IP: {request.remote_addr}.");
            
            return jsonify({'result':'1'});
        
        else:
            cursor.execute(f"delete from cookies where user_name = %s and num = %s;",(user, num));
            mydb.commit();
            
            return redirect("/");
    
    except Exception as e:
        logger.error(f"Erro no servidor {str(e)}")
        return jsonify({'result':'100'});

'''Endpoint para cadastrar apartamentos''' 
@app.route('/apartamento_cadastro/<data>', methods=['GET'])
def apartamento_cadastro(data):
    try:
        num = request.cookies.get('biopark-num');
        user = request.cookies.get('biopark-user');
        
        if not num or not user:
            return redirect("/");
        
        cursor.execute(f"select IF(data > DATE_SUB(NOW(), INTERVAL '1' HOUR),1,2) from cookies where user_name = %s and num = %s;",(user, num));
        resultado = cursor.fetchall();
        
        if resultado == []:
            return redirect("/");
        
        if resultado[0][0] == 1:
            cursor.execute(f"update cookies set data = NOW() where user_name = %s and num = %s;",(user, num));
            mydb.commit();
            
            data = json.loads(data);
            '''Pegando id do edificio'''
            cursor.execute(f"select id_edificio from edificios where nome_edificio = %s;",(data['edificio'],));
            resultado = cursor.fetchall();
        
            if resultado == []:
                return jsonify({'result':'3'});
            else:
                '''Inserindo apartamento e logando a ação'''
                cursor.execute(f"insert into apartamentos (id_edificio, nome_apartamento, nome_locatario, preco) values (%s,%s,%s,%s);",(resultado[0][0],data['apartamento'],data['locatario'],data['preco']));
                mydb.commit();
                
                logger.info(f"Usuario {user} adicionou o apartamento {data['apartamento']} a partir do IP: {request.remote_addr}.");
            
            return jsonify({'result':'1'});
        
        else:
            cursor.execute(f"delete from cookies where user_name = %s and num = %s;",(user, num));
            mydb.commit();
            
            return redirect("/");

    except Exception as e:
        logger.error(f"Erro no servidor {str(e)}")
        return jsonify({'result':'100'});

''''Endpoint para a página de pesquisa de apartamentos. Contém um formulário com múltiplas opções de pesquisa'''
@app.route('/pagina_pesquisa')
def pagina_pesquisa():
    try:
        num = request.cookies.get('biopark-num');
        user = request.cookies.get('biopark-user');
        
        if not num or not user:
            return redirect("/");
        
        cursor.execute(f"select IF(data > DATE_SUB(NOW(), INTERVAL '1' HOUR),1,2) from cookies where user_name = %s and num = %s;",(user,num));
        resultado = cursor.fetchall();
        
        if resultado == []:
            return redirect("/");
        
        if resultado[0][0] == 1:
            cursor.execute("update cookies set data = NOW() where user_name = %s and num = %s;",(user,num));
            mydb.commit();
            
            return render_template("pagina_pesquisa.html");
        
        else:
            cursor.execute("delete from cookies where user_name = %s and num = %s;",(user, num));
            mydb.commit();
            
            return redirect("/");
            
    except Exception as e:
        logger.error(f"Erro no servidor {str(e)}")
        return jsonify({'result':'100'});

'''Endpoint de pesquisa em si. Utiliza os dados do json (data) para procurar na BD com base em diferentes parâmetros'''
@app.route('/busca/<data>', methods=['GET'])
def busca(data):
    try:
        num = request.cookies.get('biopark-num');
        user = request.cookies.get('biopark-user');
        
        if not num or not user:
            return redirect("/");
        
        cursor.execute(f"select IF(data > DATE_SUB(NOW(), INTERVAL '1' HOUR),1,2) from cookies where user_name = %s and num = %s;",(user, num));
        resultado = cursor.fetchall();
        
        if resultado == []:
            return redirect("/");
        
        if resultado[0][0] == 1:
            cursor.execute("update cookies set data = NOW() where user_name = %s and num = %s;",(user, num));
            mydb.commit();
            
            data = json.loads(data);
            
            '''MONTANDO QUERY SQL'''
            temp = f"select e.endereco, e.nome_edificio, a.nome_apartamento, a.nome_locatario, a.preco, a.id_apartamento from edificios as e inner join apartamentos as a where a.id_edificio = e.id_edificio";
            tupla = ();
            
            '''Checamos se um determinado parâmetro existe na busca realizada e caso positivio adicionamos a query, com o valor do parâmetro sendo adicionado por meio da "tupla"'''
            if data['edificio']:
                temp = temp + f" and e.nome_edificio like %s";
                tupla = tupla + ("%" + data['edificio'] + "%",);
                
            if data['apartamento']:
                temp = temp + f" and a.nome_apartamento like %s";
                tupla = tupla + ("%" + data['apartamento'] + "%",);
                
            if data['endereco']:
                temp = temp + f" and e.endereco like %s";
                tupla = tupla + ("%" + data['endereco'] + "%",);
                
            if data['locatario']:
                temp = temp + f" and a.nome_locatario like %s";
                tupla = tupla + ("%" + data['locatario'] + "%",);
                
            if data['vago'] == "1":
                temp = temp + f" and a.nome_locatario != 'vago'";
                
            if data['vago'] == "2":
                temp = temp + f" and a.nome_locatario = 'vago'";
                
            temp = temp + ";";
                
            if tupla == ():
                cursor.execute(temp);
                
            else:
                cursor.execute(temp,tupla);
            
            resultado = cursor.fetchall();
            
            if resultado == []:
                return '0';
            
            resultado = json.dumps(resultado)    
            
            '''RETORNANDO RESULTADO'''
            return resultado;
        
        else:
            cursor.execute("delete from cookies where user_name = %s and num = %s;",(user, num));
            mydb.commit();
            
            return redirect("/");
    
    except Exception as e:
        logger.error(f"Erro no servidor {str(e)}")
        return jsonify({'result':'100'});
        
'''A partir da página de pesquisa, o usuário pode clicar em "atualizar" um apartamento. Esse endpoint se refere a página de atualização'''
@app.route('/atualizar/<ID>', methods=['GET'])
def atualizar(ID):
    try:
        num = request.cookies.get('biopark-num');
        user = request.cookies.get('biopark-user');
        
        if not num or not user:
            return redirect("/");
        
        cursor.execute("select IF(data > DATE_SUB(NOW(), INTERVAL '1' HOUR),1,2) from cookies where user_name = %s and num = %s;",(user,num));
        resultado = cursor.fetchall();
        
        if resultado == []:
            return redirect("/");
        
        if resultado[0][0] == 1:
            cursor.execute("update cookies set data = NOW() where user_name = %s and num = %s;",(user,num));
            mydb.commit();
            
            cursor.execute(f"select e.nome_edificio, a.nome_apartamento, a.nome_locatario, a.preco from apartamentos as a inner join edificios as e where a.id_apartamento = %s and e.id_edificio = a.id_edificio;",(ID,));
            resultado = cursor.fetchall();
            
            return render_template("atualizar.html",ID=ID,nome_edificio=resultado[0][0],nome_apartamento=resultado[0][1],nome_locatario=resultado[0][2],preco=resultado[0][3]);
        
        else:
            cursor.execute("delete from cookies where user_name = %s and num = %s;",(user, num));
            mydb.commit();
            
            return redirect("/");
    
    except Exception as e:
        logger.error(f"Erro no servidor {str(e)}")
        return jsonify({'result':'100'});

'''Endpoint para atualização da base de dados em si'''
@app.route('/atualizar_db/<data>', methods=['GET'])
def atualizar_db(data):
    try:
        num = request.cookies.get('biopark-num');
        user = request.cookies.get('biopark-user');
        
        if not num or not user:
            return redirect("/");
        
        cursor.execute("select IF(data > DATE_SUB(NOW(), INTERVAL '1' HOUR),1,2) from cookies where user_name = %s and num = %s;",(user,num));
        resultado = cursor.fetchall();
        
        if resultado == []:
            return redirect("/");
        
        if resultado[0][0] == 1:
            cursor.execute(f"update cookies set data = NOW() where user_name = %s and num = %s;",(user, num));
            mydb.commit();
            
            data = json.loads(data);
            
            '''Option 1 significa que é apenas uma atualização de um ou mais campos'''
            if data['option'] == "1":
                cursor.execute(f"delete from apartamentos where id_apartamento = %s;",(data['id'],));
                mydb.commit();
                logger.info(f"Usuario {user} deletou o apartamento {data['id']} a partir do IP: {request.remote_addr}.");
                return jsonify({'result':'1'});
            
            cursor.execute(f"select id_edificio from edificios where nome_edificio = %s;",(data['edificio'],));
            resultado = cursor.fetchall();
            
            if resultado == []:
                return jsonify({'result':'3'});
            
            cursor.execute(f"update apartamentos set id_edificio = %s, nome_apartamento = %s, nome_locatario = %s, preco = %s where id_apartamento = %s;",(resultado[0][0],data['apartamento'],data['locatario'],data['preco'],data['id']))
            mydb.commit();
            
            logger.info(f"Usuario {user} atualizou o apartamento {data['id']} a partir do IP: {request.remote_addr}.");
            
            return jsonify({'result':'1'});
        
        else:
            '''Aqui, deletamos a entrada da tabela apartamentos'''
            cursor.execute("delete from cookies where user_name = %s and num = %s;",(user, num));
            mydb.commit();
            
            return redirect("/");
    
    except Exception as e:
        logger.error(f"Erro no servidor {str(e)}")
        return jsonify({'result':'100'});
        
if __name__ == "__main__":
    cursor.execute(f"delete from cookies where data < DATE_SUB(NOW(), INTERVAL '1' HOUR);");
    mydb.commit();
    
    logger.info("Servidor iniciado.");
    
    if not (certificado or chave_privada):
        app.run(debug=False,host=my_host,port=my_port);
    
    else:
        app.run(debug=False,host=my_host,port=my_port,ssl_context=(certificado, chave_privada));
    
    mydb.close();

    logger.info("Servidor finalizado.");
