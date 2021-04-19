from flask import current_app as app, render_template, request

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/feed', methods=['POST'])
def feed():
    return render_template("feed.html")


@app.route('/cadastro')
def cadastro():
    return render_template("cadastro.html")


@app.route('/dom-quixote')
def item1():
    return render_template("item1.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/pequeno-principe')
def item2():
    return render_template("item2.html")


@app.route('/perfil')
def perfil():
    return render_template("perfil.html")


@app.route('/estante')
def estante():
    return render_template("estante.html")


@app.route('/livro-cadastrado', methods=['POST'])
def livro_cadastrado():
    return render_template("estante.html")


@app.route('/cadastrolivros')
def cadlivros():
    return render_template("cadastrolivros.html")


@app.route('/perfil-usuario', methods=['POST'])
def perfil_log():
    nome = request.form ['name']
    sobrenome = request.form ['lastname']
    email = request.form ['email']
    senha = request.form ['password']
    confirma_senha = request.form ['passconfirmation']

    if (senha == confirma_senha):
        return render_template("perfil.html", nome = nome, sobrenome = sobrenome, email = email, senha = senha)
    else:
        erro = 'Errou a senha, trouxa!'
        return render_template('cadastro.html', erro = erro)


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