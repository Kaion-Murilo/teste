from flask import Flask, render_template, request, redirect, jsonify, session
import requests
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload
from typing import Optional

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'trevale'  # Defina sua chave secreta aqui
db = SQLAlchemy(app)
# Chave de API do TMDb
api_key = 'da2823190e0c7601e2b252f2775028fb'
idioma = 'pt-BR'
TMDb_nota = ""
TMDb_num = ""


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(50), unique=True, nullable=False)
  password = db.Column(db.String(100), nullable=False)
  comments = db.relationship('Comment', backref='user', lazy=True)


class Comment(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  movie = db.Column(db.String(100), nullable=False)
  comment = db.Column(db.Text, nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class filmeDB(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  site_nota = db.Column(db.Float)
  site_num_avali = db.Column(db.Integer)
  nome_filme = db.Column(db.String(150), unique=True)


@app.route("/avali", methods=["POST"])
def avali():
  if 'username' in session:
    username = session['username']
    rating = int(request.form['rating'])
    nome_filme = session.get('nome_filme')

    filme_existente = filmeDB.query.filter_by(nome_filme=nome_filme).first()

    if filme_existente:
      filme_existente.site_nota += rating
      filme_existente.site_num_avali += 1

    else:
      novo_filme = filmeDB(nome_filme=nome_filme,
                           site_nota=rating,
                           site_num_avali=1)
      db.session.add(novo_filme)
    filme = filmeDB.query.filter_by(nome_filme=nome_filme).first()

    if filme:
      resultado1 = float(filme.site_nota)
      session['no_banco_nota'] = resultado1
      testando2 = int(filme.site_num_avali)
      session['no_banco_num_avali'] = testando2
      session['final_quant'] = testando2
      resultado2 = float(session.get('nota')) * float(
        session.get('quant_nota'))
      testando = (session.get('no_banco_nota') + resultado2) / (
        float(filme.site_num_avali) + float(session.get('quant_nota')))
      session['final_value'] = testando

    db.session.commit()
    return redirect(f"/leiamais/{str(session.get('nome_filme'))}")

  else:
    return render_template("login.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
  if 'username' in session:
    username = session['username']
    return popo()
  if request.method == 'POST':
    print(request.form)
    username = request.form['input_nome']
    password = request.form['input_senha']

    with app.app_context():
      user = User.query.filter_by(username=username).first()

      if user and check_password_hash(user.password, password):
        session['username'] = username
        return redirect('/catalogo')
      else:
        error = 'Usuário ou senha inválidos.'
        return render_template('login.html', error=error)

  return render_template('login.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
  if request.method == 'POST':
    username = request.form['input_nome']
    password = request.form['input_senha']

    with app.app_context():
      if User.query.filter_by(username=username).first():
        error = 'Nome de usuário já existente.'
        return render_template('registro.html', error=error)

      hashed_password = generate_password_hash(password)
      new_user = User(username=username, password=hashed_password)
      db.session.add(new_user)
      db.session.commit()

    return redirect('/login')

  return render_template('registro.html')


@app.route('/crud', methods=['GET', 'POST'])
def crud():
  if 'username' not in session:  # Verificar se o usuário está autenticado
    return "Você não está logado, seu merdinha"

  user_to_update = None

  if request.method == 'POST':
    action = request.form['action']

    if action == 'add':
      username = request.form['username']
      password = request.form['password']

      with app.app_context():
        if User.query.filter_by(username=username).first():
          error = 'Nome de usuário já existente.'
          return render_template('crud.html', error=error)

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

      return redirect('/crud')

    elif action == 'delete':
      user_id = request.form['user_id']

      with app.app_context():
        user = User.query.get(user_id)

        if user:
          db.session.delete(user)
          db.session.commit()

      return redirect('/crud')

    elif action == 'update':
      user_id = request.form['user_id']
      new_username = request.form['username']
      new_password = request.form['password']
      new_comentario = request.form['comentario']

      with app.app_context():
        user_to_update = User.query.get(user_id)

        if user_to_update:
          user_to_update.username = new_username
          user_to_update.password = generate_password_hash(new_password)

          if user_to_update.comentarios:
            user_to_update.comentarios.append(new_comentario)
          else:
            user_to_update.comentarios = [new_comentario]

          db.session.commit()

      return redirect('/crud')

  with app.app_context():
    users = User.query.all()

  return render_template('crud.html',
                         users=users,
                         user_to_update=user_to_update)


@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
  if 'username' not in session:  # Verificar se o usuário está autenticado
    return jsonify({'error': 'Acesso não autorizado.'}), 401

  search_query = request.args.get(
    'q')  # Obter o valor do parâmetro de consulta 'q'

  with app.app_context():
    if search_query:
      # Se um termo de busca foi fornecido, filtrar os usuários com base no nome de usuário
      users = User.query.filter(User.username.ilike(f'%{search_query}%')).all()
    else:
      # Caso contrário, obter todos os usuários
      users = User.query.all()

    usuarios = []
    for user in users:
      usuario = {
        'id': user.id,
        'username': user.username,
        'password': user.password
      }
      usuarios.append(usuario)

    return jsonify(usuarios)


@app.route('/catalogo')
def popo(cinemas_proximos=None):
  # Fazendo a solicitação à API do TMDb
  url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language={idioma}'
  response = requests.get(url)
  data = response.json()

  # Obtendo os filmes mais populares
  filmes_populares = data['results']
  filmes = []

  url = f'https://api.themoviedb.org/3/movie/top_rated?api_key={api_key}&language=pt-BR'
  response = requests.get(url)
  data = response.json()

  movies = data['results']

  for movie in movies:
    filme = {
      'id': movie['id'],
      'title': movie['title'],
      'poster_path': movie['poster_path']
    }

    filmes.append(filme)
  # Renderizando o template HTML com os dados dos filmes
  print(cinemas_proximos)
  return render_template('catalogo.html',
                         filmes=filmes_populares,
                         filmesav=filmes,
                         cinemas=cinemas_proximos)


@app.route("/")
def home():
  return render_template("telaprincipal.html")


@app.route('/cinemas_proximos')
def cinemas():
  latitude = -5.81116
  longitude = -35.2063
  # latitude = request.args.get('latitude')
  # longitude = request.args.get('longitude')
  # Configuração da chave de API do Yelp Fusion
  api_key = 'qkmjt6x-ZIXrixQqc_CwuLDjApx6-48wbzRBo_3gVo3KcvGOxT05VB8QkGQex9EMG8J0zYHzeL0uiBZI_FkaT4D-EYSFpOuvDCEOn4KKRk0Z3V6COG_0OC-ggduAZHYx'

  # Parâmetros da solicitação à API do Yelp Fusion
  params = {
    'latitude': latitude,
    'longitude': longitude,
    'categories': 'movietheaters',
    'radius': 5000,  # Raio de busca em metros
    'limit': 3  # Número máximo de cinemas a serem retornados
  }

  # URL da API do Yelp Fusion
  url = 'https://api.yelp.com/v3/businesses/search'

  # Cabeçalho da solicitação com a chave de API
  headers = {'Authorization': f'Bearer {api_key}'}

  # Faz a solicitação GET à API do Yelp Fusion
  response = requests.get(url, params=params, headers=headers)
  data = response.json()

  # Extrai informações relevantes dos cinemas retornados
  cinemas_proximos = []
  if 'businesses' in data:
    for cinema in data['businesses']:
      cinemas_proximos.append({
        'nome':
        cinema['name'],
        'endereco':
        ', '.join(cinema['location']['display_address'])
      })
    if cinemas_proximos == None:
      return popo(cinemas_proximos=None)
  return popo(cinemas_proximos)


@app.route('/buscar', methods=['GET', 'POST'])
def buscar_filme():
  print(request.form['titulo'])
  nome_filme = request.form['titulo']
  if nome_filme != "":
    return redirect(f"/leiamais/{nome_filme}")
  else:
    return render_template("error.html")


@app.route('/leiamais/<string:nome_filme>', methods=['GET', 'POST'])
def leiamais(nome_filme):
  # Solicitando detalhes do filme à API do TMDb
  url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={nome_filme}&language={idioma}'
  response = requests.get(url)
  data = response.json()

  if 'results' in data and len(data['results']) > 0:
    filme_existente = filmeDB.query.filter_by(nome_filme=nome_filme).first()

    if filme_existente:
      print("filme existe")

    else:
      novo_filme = filmeDB(nome_filme=nome_filme,
                           site_nota=0,
                           site_num_avali=0)
      db.session.add(novo_filme)
    filme = filmeDB.query.filter_by(nome_filme=nome_filme).first()
    try:
      resultado1 = float(filme.site_nota)
      session['no_banco_nota'] = resultado1
      testando2 = int(filme.site_num_avali)
      session['no_banco_num_avali'] = testando2
      session['final_quant'] = testando2
      resultado2 = float(session.get('nota')) * float(session.get('quant_nota'))
      testando = (session.get('no_banco_nota') + resultado2) / (
        float(filme.site_num_avali) + float(session.get('quant_nota')))
      session['final_value'] = testando
      filme = data['results'][0]
      movie_id = filme['id']
      titulo = filme['title']
      session['nome_filme'] = titulo
      movie_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language={idioma}'
      movie_response = requests.get(movie_url)
      data = movie_response.json()
      session['nota'] = data['vote_average']
      rating = data['vote_average']
      session['quant_nota'] = data['vote_count']
      num_ratings = data['vote_count']
      av_meu = session.get('final_value')
      av_meu = f'{av_meu:.2f}'
      quant_meu = session.get('final_quant')
    except:
        resultado1 = 0
        session['no_banco_nota'] = resultado1
        testando2 = 0
        session['no_banco_num_avali'] = testando2
        session['final_quant'] = testando2
        resultado2 = 0
        testando = 0
        session['final_value'] = testando
        filme = data['results'][0]
        movie_id = filme['id']
        titulo = filme['title']
        session['nome_filme'] = titulo
        movie_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language={idioma}'
        movie_response = requests.get(movie_url)
        data = movie_response.json()
        session['nota'] = data['vote_average']
        rating = data['vote_average']
        session['quant_nota'] = data['vote_count']
        num_ratings = data['vote_count']
        av_meu = session.get('final_value')
        quant_meu = session.get('final_quant')
    try:
      quant_total = quant_meu + num_ratings
    except:
      quant_total = 0
    try:
      cal1 = float(session['no_banco_nota'])
      cal2 = int(session['no_banco_num_avali'])
      quant_banco_avali = session['no_banco_num_avali']
    except KeyError:
      cal1 = 0
      cal2 = 0
      quant_banco_avali = 0
    try:
      quant_banco_nota = cal1 / cal2
    except ZeroDivisionError:
      quant_banco_nota = 0

      # Solicitando detalhes do elenco à API do TMDb

    title = filme['title']
    poster_path = filme['poster_path'] if filme['poster_path'] else None
    release_date = filme['release_date']
    vote_average = filme['vote_average']
    overview = filme['overview']

    poster_url = f'https://image.tmdb.org/t/p/w500{poster_path}' if poster_path else None
    
    if request.method == 'POST':
      username = session['username']
      if 'form1_submit' in request.form:
        comentario_texto = request.form['input_comentario']
        username = session['username']

        with app.app_context():
          # Obter o usuário atual
          user = User.query.filter_by(username=username).first()

          # Criar um novo objeto Comment associado ao usuário e filme
          comentario = Comment(comment=comentario_texto,
                               user_id=user.id,
                               movie=nome_filme)

          db.session.add(comentario)
          db.session.commit()

    # Carregar os comentários do filme atual
    with app.app_context():
      comentarios = Comment.query.filter_by(movie=nome_filme).options(
        joinedload(Comment.user)).all()
      filme1 = filmeDB.query.filter_by(
        nome_filme=session['nome_filme']).first()
  # Faça o que desejar com a lista de comentários e seus respectivos usuários
    for comentario in comentarios:
      username = comentario.user_id
    if nome_filme != "" and nome_filme != None and nome_filme != "None" and nome_filme != "null" and nome_filme != "Null": 
      return render_template('filmesjulia.html',
                            title=title,
                            poster_url=poster_url,
                            release_date=release_date,
                            vote_average=vote_average,
                            overview=overview,
                            rating=rating,
                            num_ratings=num_ratings,
                            av_meu=av_meu,
                            quant_meu=quant_meu,
                            comentarios=comentarios,
                            filme=filme1,
                            quant_total=quant_total,
                            quant_banco_nota=quant_banco_nota,
                            quant_banco_avali=quant_banco_avali)
    else:
      return render_template("error.html")  
  else:
    return render_template("error.html")


@app.route('/cadastrar_comentario', methods=['POST'])
def cadastrar_comentario():
  if 'username' not in session:
    return render_template("login.html")

  user_id = session['username']
  movie = request.form['movie']
  comment = request.form['comment']

  with app.app_context():
    new_comment = Comment(movie=movie, comment=comment, user_id=user_id)
    db.session.add(new_comment)
    db.session.commit()

  return redirect(f"/leiamais/{str(session.get('nome_filme'))}")


@app.route('/comentarios/<string:nome_filme>')
def mostrar_comentarios(nome_filme):
  with app.app_context():
    comentarios = Comment.query.filter_by(movie=nome_filme).all()
  return render_template('comentarios.html', comentarios=comentarios)


if __name__ == '__main__':
  with app.app_context():
    db.create_all()
  app.run(host='0.0.0.0', port=81, debug=True)
