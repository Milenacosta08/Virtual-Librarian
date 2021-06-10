from flask import current_app as app, render_template, request, redirect, url_for, session
from PVL.entidades import Usuario, Livros, Postagem, Genero, categorizados, ForumLivro, Resposta, Amigo
from PVL import db, login_manager
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import desc
import os
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(user_id)

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/feed')
@login_required
def feed():

    posts = {}
    postagens = Postagem.query.order_by(desc(Postagem.id)).all()

    for post in postagens:
        pessoa = Usuario.query.get(post.usuario_id)
        posts[post] = {'nome': pessoa.nome, 'sobrenome': pessoa.sobrenome, 'conteudo': post.conteudo, 'data': post.data, 'idpostagem': post.id, 'curtidas': post.curtidas, 'imagem': pessoa.imagem, 'idusuario': pessoa.id}


    return render_template('feed.html', postagem = posts)


@app.route('/feed-post', methods=['POST'])
@login_required
def feed_post():
    comentario = request.form['comentario']
    usu = Usuario.query.filter_by(email=session['user_email']).first()

    postagem = Postagem()
    postagem.conteudo = comentario
    postagem.usuario_id = usu.id

    file = request.files['imagemsel']

    if file is not None:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            imgs = os.listdir(app.config['UPLOAD_FOLDER'])
            filename = f'{len(imgs)+1:08}.{filename.rsplit(".", 1)[1].lower()}'

            file.save(app.config['UPLOAD_FOLDER']+'/'+filename)
            postagem.imagem = filename

    if postagem.conteudo is not None:
        db.session.add(postagem)
        db.session.commit()

    return redirect('/feed')

@app.route('/curtir/<idpostagem>')
@login_required
def curtir(idpostagem):

    postagem = Postagem.query.filter_by(id = idpostagem).first()

    postagem.curtidas += 1
    db.session.commit()

    return redirect('/feed')

@app.route('/descurtir/<idpostagem>')
@login_required
def descurtir(idpostagem):

    postagem = Postagem.query.filter_by(id = idpostagem).first()

    postagem.curtidas -= 1
    db.session.commit()

    return redirect('/feed')

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

    if (Usuario.query.filter_by(email=email).first() is None):
        if (senha == confirma_senha):
            novo = Usuario()
            novo.nome = nome
            novo.sobrenome = sobrenome
            novo.nome_completo = '{} {}'.format(nome, sobrenome)
            novo.email = email
            novo.senha = senha
            session['user_email'] = email

            db.session.add(novo)
            db.session.commit()

            login_user(novo)
            session['user_id'] = novo.id

            return render_template("perfil.html")
        else:
            erro = 'Senha no campo de confirmação escrita incorretamente!'

            return render_template('cadastro.html', erro = erro)
    else:
        erro = 'Email já cadastrado!'

        return render_template('cadastro.html', erro = erro)


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/feed-usuario', methods=['POST'])
def feed_log():
    email = request.form ['email']
    password = request.form['senha']

    usu = Usuario.query.filter_by(email=email).first()

    if (usu is None):
        erro = 'Usuário não encontrado'

        return render_template('login.html', erro = erro)
    else:
        if (usu.senha == password):
            login_user(usu)
            session['user_id'] = usu.id
            session['user_email'] = email
            return redirect('/feed')
        else:
            erro = 'Senha incorreta'
            return render_template('login.html', erro = erro)



@app.route('/perfil')
@login_required
def perfil():
    post = Postagem.query.filter_by(usuario_id=session['user_id']).order_by(desc(Postagem.id)).all()

    return render_template("perfil.html", postagens = post)


@app.route('/perfil/<id_usuario>')
@login_required
def perfil_usu(id_usuario):
    amigo = Amigo.query.filter(Amigo.id_usuario == current_user.id).filter(Amigo.id_amigo == id_usuario).all()
    existe = 1

    if amigo == []:
        existe = 0


    usu = Usuario.query.filter_by(id=id_usuario).first()
    post = Postagem.query.filter_by(usuario_id=id_usuario).order_by(desc(Postagem.id)).all()

    return render_template("perfil.html", usuario = usu, postagens=post, existe = existe)


@app.route('/delete')
@login_required
def deletarUsuario():
    user = Usuario.query.get(current_user.id)

    for postagem in user.postagens:
        db.session.delete(postagem)
        db.session.commit()

    for livro in user.livros:
        livro.generos.clear()
        db.session.commit()

        db.session.delete(livro)
        db.session.commit()


    for amigo in user.amigos:
        db.session.delete(amigo)
        db.session.commit()



    db.session.delete(user)
    db.session.commit()

    return redirect('/login')


@app.route('/adicionar/<idamigo>')
@login_required
def amigo(idamigo):
    amigo = Amigo.query.filter(Amigo.id_amigo == idamigo).filter(Amigo.id_usuario == current_user.id).all()

    if current_user.id != idamigo:
        if amigo == []:
            novo = Amigo()
            novo.id_usuario = current_user.id
            novo.id_amigo = idamigo
            db.session.add(novo)
            db.session.commit()

    return redirect(f"/perfil/{idamigo}")

@app.route('/remover/<idamigo>')
@login_required
def removeramigo(idamigo):
    amigo = Amigo.query.filter(Amigo.id_amigo == idamigo).filter(Amigo.id_usuario == current_user.id).all()

    db.session.delete(amigo)
    db.session.commit()

    return redirect(f"/perfil{idamigo}")


@app.route('/estante')
@login_required
def estante():
    livros = Livros.query.filter_by(usuario_id = current_user.id).all()

    exemplar = {}
    livro_id = {}

    for livro in livros:
        #if(livro.usuario_id==session['user_id']):
        exemplar[livro] = {'titulo': livro.titulo, 'autor': livro.autor, 'genero': livro.generos, 'idlivro': livro.id, 'capa':livro.imagem}
        livro_id[livro] = livro.id

    usu = Usuario.query.get(current_user.id)

    if usu.id != session['user_id']:
        id_user = usu.id

        return render_template("estante.html", livros = exemplar, livroid = livro_id, usuario = id_user)
    else:
        return render_template("estante.html", livros = exemplar, livroid = livro_id)


@app.route('/delete/<id>')
@login_required
def deletarLivro(id):
    user = Usuario.query.get(current_user.id)
    livro = Livros.query.get(id)

    if livro.usuario_id == current_user.id:
        livro.generos.clear()
        db.session.commit()

        db.session.delete(livro)
        db.session.commit()

    return redirect(f'/estante')


@app.route('/livro-cadastrado', methods=['POST'])
@login_required
def livro_cadastrado():
    titulo = request.form["titulo"]
    autor = request.form["autor"]
    genero = request.form.getlist('genero')
    resumo = request.form["resumo"]
    status = request.form["status"]
    preco = request.form["preco"]

    usu = Usuario.query.get(current_user.id)

    livro = Livros()
    livro.titulo = titulo
    livro.autor = autor
    livro.resumo = resumo
    livro.usuario_id = usu.id
    livro.status = status
    livro.preco = preco

    # percorre a lista "genero" que contém os gêneros selecionados pelo usuário
    for g in genero:
        genero1 = db.session.query(Genero).filter(Genero.nome == g).first()

        if genero1 is None:
            genero1 = Genero()
            genero1.nome = g
            db.session.add(genero1)
            db.session.commit()

        livro.generos.append(genero1)


    file = request.files['imagemsel']

    if file is not None:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            imgs = os.listdir(app.config['UPLOAD_FOLDER'])
            filename = f'{len(imgs)+1:08}.{filename.rsplit(".", 1)[1].lower()}'

            file.save(app.config['UPLOAD_FOLDER']+'/'+filename)
            livro.imagem = filename


        db.session.add(livro)
        db.session.commit()

    return redirect(f'/estante')

#return render_template("estante.html", livros = livros[:8], titulo = titulo)

@app.route('/livros/<id_livro>')
@login_required
def paglivros(id_livro):
    livro = Livros.query.filter_by(id=id_livro).first()
    usuario = Usuario.query.filter_by(id=current_user.id).first()
    forum = ForumLivro.query.filter_by(id_livro = id_livro).order_by(desc(ForumLivro.id)).all()
    respostas = Resposta.query.filter_by(id_livro = id_livro).order_by(desc(Resposta.data)).all()
    posts = {}
    respostass = {}

    for resposta in respostas:
        usu = Usuario.query.get(resposta.id_usuario)
        respostass[resposta] = {'texto' : resposta.texto, 'idforum' : resposta.id_forum, 'usuario' : usu, 'data' : resposta.data}


    for comentario in forum:
        pessoa = Usuario.query.get(comentario.usuario_id)
        posts[comentario] = {'nome': pessoa.nome, 'sobrenome': pessoa.sobrenome, 'conteudo': comentario.texto, 'id': comentario.id, 'data': comentario.data, 'idlivro': comentario.id_livro, 'imagem': pessoa.imagem, 'idusuario': pessoa.id}


    return render_template('item1.html', livro = livro, usuario = usuario, posts = posts, respostas = respostass)

@app.route('/forum/cadastro/<id_li>', methods=['POST'])
@login_required
def Forum(id_li):
    comentario = request.form['comentario']
    livro = Livros.query.filter_by(usuario_id = current_user.id).first()

    if comentario != '':
        novo = ForumLivro()
        novo.usuario_id = current_user.id
        novo.id_livro = id_li
        novo.texto = comentario

        db.session.add(novo)
        db.session.commit()

    return redirect(f'/livros/{id_li}')

@app.route('/delete/forum/<idcomentario>/<idliv>', methods=['POST'])
@login_required
def deletarforum(idcomentario, idliv):

    respostas = Resposta.query.filter(Resposta.id_forum == idcomentario).all()

    for resposta in respostas:
        db.session.delete(resposta)
        db.session.commit()

    ForumLivro.query.filter_by(id = idcomentario).delete()

    db.session.commit()

    return redirect(f'/livros/{idliv}')



@app.route('/forum/cadastro/resposta/<id_livro>/<usu_post>', methods=['POST'])
@login_required
def resposta(id_livro, usu_post):
    resposta = request.form['resposta']

    if resposta != '':
        novo = Resposta()
        novo.id_usuario = current_user.id
        novo.id_livro = id_livro
        novo.id_forum = usu_post
        novo.texto = resposta

        db.session.add(novo)
        db.session.commit()

    return redirect(f'/livros/{id_livro}')


@app.route('/buscas')
@login_required
def buscas():
    existe = 0
    busca = request.args.get('pesquisass')
    nomes = Usuario.query.filter_by(nome = busca).all()
    sobrenomes = Usuario.query.filter_by(sobrenome = busca).all()
    livros = Livros.query.filter_by(titulo = busca).all()
    nomecomp = Usuario.query.filter_by(nome_completo = busca).all()

    if nomes or sobrenomes or livros or nomecomp:
        existe = 1

    return render_template('buscas.html', busca = busca, nomes = nomes, sobrenomes = sobrenomes, livros = livros, nomecomp = nomecomp, existe = existe)


@app.route('/amigos')
@login_required
def amigos():
    amigos = Amigo.query.filter(Amigo.id_usuario == current_user.id).all()
    amigoss = []

    for amigo in amigos:
        if amigo != []:
            usu = Usuario.query.get(amigo.id_amigo)
            amigoss.append({'usuario' : usu})

    return render_template('amigos.html', amigos = amigoss)

@app.route("/logout/")
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('home'))

@app.route('/atualiza', methods=['POST'])
@login_required
def atualiza():
    novo_nome = request.form['nome_novo']
    novo_sobrenome = request.form['sobrenome_novo']
    novo_email = request.form['email_novo']
    nova_senha = request.form['senha_nova']
    senha_inserida = request.form['senha_atual']

    quem = Usuario.query.get(current_user.id)

    if(quem.senha==senha_inserida):

        if(novo_nome!=""):
            quem.nome = novo_nome
            db.session.add(quem)
            db.session.commit()

        if(novo_sobrenome!=""):
            quem.sobrenome = novo_sobrenome
            db.session.add(quem)
            db.session.commit()

        if(novo_email!=""):
            quem.email = novo_email
            db.session.add(quem)
            db.session.commit()

        if(nova_senha!=""):
            quem.senha = nova_senha
            db.session.add(quem)
            db.session.commit()
        return redirect ('/perfil')

    else:
        erro = 'Alterações não concluídas pois a senha inserida é inválida!'
        return render_template('perfil.html', erro=erro)

@app.route('/atualizardg', methods=['POST'])
@login_required
def atualizardg():
    biografia = request.form['biografia']
    file = request.files['imagemsel']

    usuario = Usuario.query.get(current_user.id)
    if biografia != '':
        usuario.biografia = biografia

    if file is not None:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            imgs = os.listdir(app.config['UPLOAD_FOLDER'])
            filename = f'{len(imgs)+1:08}.{filename.rsplit(".", 1)[1].lower()}'

            file.save(app.config['UPLOAD_FOLDER']+'/'+filename)
            usuario.imagem = filename

    else:
        usuario.imagem = 'padrao'

    db.session.commit()

    return redirect ('/perfil')




