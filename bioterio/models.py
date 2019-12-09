from bioterio import db, login_manager
from datetime import datetime
from dateutil.relativedelta import relativedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
# By inheriting the UserMixin we get access to a lot of built-in attributes
# which we will be able to call in our views!
# is_authenticated()
# is_active()
# is_anonymous()
# get_id()


# The user_loader decorator allows flask-login to load the current user
# and grab their id.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    # Create a table in the db
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, email, password):
        self.email = email
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # https://stackoverflow.com/questions/23432478/flask-generate-password-hash-not-constant-output
        return check_password_hash(self.password_hash, password)


class Cruza(db.Model):
    __tablename__ = 'cruza'
    __table_args__ = {'extend_existing': True}

    db.Model.metadata.reflect(db.engine)
    id = db.Column(db.Integer, primary_key=True)
    caja = db.Column(db.String(20), nullable=False)
    cepa = db.Column(db.String(20), nullable=False)
    fecha_cruza = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    machos = db.Column(db.Integer, default=0)
    hembras = db.Column(db.Integer, default=0)
    camadas = db.relationship('Camada', backref='cruza', lazy=True)
    macho = db.relationship('Macho', backref='cruza', lazy=True)
    hembra = db.relationship('Hembra', backref='cruza', lazy=True)

    def __repr__(self):
        return '<Cruza %r>' % self.id


class Camada(db.Model):
    __tablename__ = 'camada'
    __table_args__ = {'extend_existing': True}

    db.Model.metadata.reflect(db.engine)
    id = db.Column(db.Integer, primary_key=True)
    fecha_nacimiento = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_destete = db.Column(db.DateTime, default=datetime.today() + relativedelta(days=+28), nullable=False)
    machos = db.Column(db.Integer, default=0, nullable=False)
    hembras = db.Column(db.Integer, default=0, nullable=False)
    macho_is_created = db.Column(db.Boolean, default=False, nullable=False)
    hembra_is_created = db.Column(db.Boolean, default=False, nullable=False)
    cruza_id = db.Column(db.Integer, db.ForeignKey('cruza.id'), nullable=False)

    def __repr__(self):
        return '<Camada %r>' % self.id


class Macho(db.Model):
    __tablename__ = 'macho'
    __table_args__ = {'extend_existing': True}

    db.Model.metadata.reflect(db.engine)
    id = db.Column(db.Integer, primary_key=True)
    caja = db.Column(db.String(20), nullable=False)
    cepa = db.Column(db.String(20), nullable=False)
    fecha_nacimiento = db.Column(db.DateTime, default=datetime.today() + relativedelta(days=-28), nullable=False)
    fecha_destete = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    cantidad = db.Column(db.Integer, default=0, nullable=False)
    padres = db.Column(db.String(20), nullable=False)
    cruza_id = db.Column(db.Integer, db.ForeignKey('cruza.id'), nullable=False)
    observacion = db.relationship('Observacion', backref='macho', lazy=True)

    def __repr__(self):
        return '<Macho %r>' % self.id


class Hembra(db.Model):
    __tablename__ = 'hembra'
    __table_args__ = {'extend_existing': True}

    db.Model.metadata.reflect(db.engine)
    id = db.Column(db.Integer, primary_key=True)
    caja = db.Column(db.String(20), nullable=False)
    cepa = db.Column(db.String(20), nullable=False)
    fecha_nacimiento = db.Column(db.DateTime, default=datetime.today() + relativedelta(days=-28), nullable=False)
    fecha_destete = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    cantidad = db.Column(db.Integer, default=0, nullable=False)
    padres = db.Column(db.String(20), nullable=False)
    cruza_id = db.Column(db.Integer, db.ForeignKey('cruza.id'), nullable=False)
    observacion = db.relationship('Observacion', backref='hembra', lazy=True)

    def __repr__(self):
        return '<Hembra %r>' % self.id


class Observacion(db.Model):
    __tablename__ = 'observacion'
    __table_args__ = {'extend_existing': True}

    db.Model.metadata.reflect(db.engine)
    id = db.Column(db.Integer, primary_key=True)
    observacion = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    macho_id = db.Column(db.Integer, db.ForeignKey('macho.id'))
    hembra_id = db.Column(db.Integer, db.ForeignKey('hembra.id'))

    def __repr__(self):
        return '<Observacion %r>' % self.id
