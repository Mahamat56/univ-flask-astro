from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"


app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_cle_secrete_super_securisee'
# Remplacez "motdepasse" par le mot de passe root que vous avez défini
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://astro_user:password123@localhost/astro_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODÈLES DE DONNÉES ---

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class AppareilPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marque = db.Column(db.String(100), nullable=False)
    modele = db.Column(db.String(100), nullable=False)
    date_sortie = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False) # 1 à 5
    categorie = db.Column(db.String(50), nullable=False) # Amateur, Amateur sérieux, Professionnel

class Telescope(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marque = db.Column(db.String(100), nullable=False)
    modele = db.Column(db.String(100), nullable=False)
    date_sortie = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False) # 1 à 5
    categorie = db.Column(db.String(50), nullable=False) # Enfants, Automatisés, Complets

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES D'AUTHENTIFICATION ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Hachage du mot de passe
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        new_user = User(username=username, password_hash=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Inscription réussie, connectez-vous !')
            return redirect(url_for('login'))
        except:
            flash('Ce nom d\'utilisateur existe déjà.')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        # Vérification du hash
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Identifiants incorrects.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- ROUTES DU SITE (Nécessitent d'être connecté) ---

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/appareils-photo')
@login_required
def appareils_photo():
    appareils = AppareilPhoto.query.all()
    # Groupement par catégories
    amateur = [a for a in appareils if a.categorie == 'Amateur']
    serieux = [a for a in appareils if a.categorie == 'Amateur sérieux']
    pro = [a for a in appareils if a.categorie == 'Professionnel']
    return render_template('appareils.html', amateur=amateur, serieux=serieux, pro=pro)

@app.route('/telescopes')
@login_required
def telescopes():
    telescopes_db = Telescope.query.all()
    enfants = [t for t in telescopes_db if t.categorie == 'Téléscopes pour enfants']
    auto = [t for t in telescopes_db if t.categorie == 'Automatisés']
    complets = [t for t in telescopes_db if t.categorie == 'Téléscopes complets']
    return render_template('telescopes.html', enfants=enfants, auto=auto, complets=complets)

@app.route('/photographies')
@login_required
def photographies():
    # Ici on liste de fausses données en dur pour l'exemple, à adapter selon vos besoins
    photos = [
        {"titre": "Nébuleuse d'Orion", "auteur": "AstroFan99"},
        {"titre": "Galaxie d'Andromède", "auteur": "StarGazer"}
    ]
    return render_template('photographies.html', photos=photos)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Crée les tables si elles n'existent pas
    app.run(debug=True, port=5000)

