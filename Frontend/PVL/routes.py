from flask import current_app as app, render_template, request

usuarios = [ ]
acesso = {'logado':0}
livros = []

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/feed')
def feed():
    if(acesso['logado']==1):
        for i in usuarios:
            nome = i['nome']
            sobrenome = i['sobrenome']
        return render_template("feed.html", nome = nome, sobrenome = sobrenome )
    else:
        falha = 'Você precisa se cadastrar (ou fazer login) para ter acesso a esta página!'
        return render_template("index.html", erro = falha)


@app.route('/cadastro')
def cadastro():
    return render_template("cadastro.html")


@app.route('/perfil-usuario', methods=['POST'])
def perfil_log():
    nome = request.form ['name']
    sobrenome = request.form ['lastname']
    email = request.form ['email']
    senha = request.form ['password']
    confirma_senha = request.form ['passconfirmation']
    
    if (senha == confirma_senha):
        usuario = {'nome':nome, 'sobrenome':sobrenome, 'email':email, 'senha':senha}
        usuarios.append(usuario)
        acesso['logado']=1

        return render_template("perfil.html", nome = usuario['nome'], sobrenome = usuario['sobrenome'], email = usuario['email'])
    else:
        erro = 'Senha no campo de confirmação escrita incorretamente!'

        return render_template('cadastro.html', erro = erro)


@app.route('/dom-quixote')
def item1():
    return render_template("item1.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/feed-usuario', methods=['POST'])
def feed_log():
    email = request.form ['email']
    password = request.form['senha']

    encontrado = 0
    for usuario in usuarios:
        if (email == usuario['email'] and password == usuario['senha']):
            encontrado = 1
            break

    if(encontrado == 1):
        acesso['logado']=1
        return render_template('feed.html', nome = usuario['nome'], sobrenome = usuario['sobrenome'])
    else:
        erro = 'Usuário não encontrado'

        return render_template('login.html', erro = erro)


@app.route('/pequeno-principe')
def item2():
    return render_template("item2.html")


@app.route('/perfil')
def perfil():
    for i in usuarios:
        nome = i['nome']
        sobrenome = i['sobrenome']
        email = i['email']
    return render_template("perfil.html", nome = nome, sobrenome = sobrenome, email = email)


@app.route('/estante')
def estante():
    return render_template("estante.html")


@app.route('/livro-cadastrado', methods=['POST'])
def livro_cadastrado():
    titulo = request.form["titulo"]
    if (titulo != ""):
        livro = {'titulo' : titulo}
        livros.append(livro)

    return render_template("estante.html", livros = livros[:8], titulo = titulo)


@app.route('/cadastrolivros')
def cadlivros():
    return render_template("cadastrolivros.html")


@app.route('/buscas')
def buscas():
    existe = 0
    busca = request.args.get('pesquisass')
    buscaz = busca.lower()
    sites = ["página inicial", "feed", "estante", "meu perfil", "dom quixote", "pequeno príncipe", "cadastro", "login"]
    links = ["/", "/feed", "/estante", "/perfil", "/dom-quixote", "/pequeno-principe", "/cadastro", "/login"]

    for item in range(8):
        if buscaz == sites[item]:
            existe = 1

    return render_template('buscas.html', busca = buscaz, sites = sites, links = links, existe = existe)


@app.route('/amigos')
def amigo():
    return render_template('amigos.html')