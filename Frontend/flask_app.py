from flask import Flask, render_template 
app = Flask('__name__') 

@app.route('/') 
def home(): 
    return render_template("index.html"); 

@app.route('/feed')
def feed():
    return render_template("feed.html");

@app.route('/cadastro')
def cadastro():
    return render_template("cadastro.html");

@app.route('/dom-quixote')
def item1():
    return render_template("item1.html");

@app.route('/login')
def login():
    return render_template("login.html");

@app.route('/pequeno-principe')
def item2():
    return render_template("item2.html");

@app.route('/perfil')
def perfil():
    return render_template("perfil.html");
