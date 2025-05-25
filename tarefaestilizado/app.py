from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Usuario, Tarefa

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tarefas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'corinthians'

db.init_app(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario and usuario.checar_senha(senha):
            session['usuario_id'] = usuario.id
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    return redirect(url_for('login'))

def login_necessario(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_necessario
def index():
    usuario = Usuario.query.get(session['usuario_id'])
    tarefas = Tarefa.query.filter_by(usuario_id=usuario.id).all()
    return render_template('index.html', tarefas=tarefas, usuario=usuario)

@app.route('/tarefa/adicionar', methods=['POST'])
@login_necessario
def adicionar_tarefa():
    titulo = request.form['titulo']
    descricao = request.form['descricao']
    usuario = Usuario.query.get(session['usuario_id'])
    tarefa = Tarefa(titulo=titulo, descricao=descricao, usuario_id=usuario.id)
    db.session.add(tarefa)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/tarefa/editar/<int:id>', methods=['GET', 'POST'])
@login_necessario
def editar_tarefa(id):
    tarefa = Tarefa.query.get_or_404(id)
    if request.method == 'POST':
        tarefa.titulo = request.form['titulo']
        tarefa.descricao = request.form['descricao']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('editar.html', tarefa=tarefa)

@app.route('/tarefa/deletar/<int:id>', methods=['POST'])
@login_necessario
def deletar_tarefa(id):
    tarefa = Tarefa.query.get_or_404(id)
    db.session.delete(tarefa)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['senha']
        confirmar = request.form['confirmar']

        if senha != confirmar:
            flash('As senhas não coincidem.')
            return render_template('cadastro.html')

        if Usuario.query.filter_by(username=username).first():
            flash('Nome de usuário já existe.')
            return render_template('cadastro.html')

        novo_usuario = Usuario(username=username)
        novo_usuario.set_senha(senha)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Usuário cadastrado com sucesso. Faça login.')
        return redirect(url_for('login'))

    return render_template('cadastro.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Usuario.query.filter_by(username='admin').first():
            u = Usuario(username='admin')
            u.set_senha('1234')
            db.session.add(u)
            db.session.commit()
    app.run(debug=True)