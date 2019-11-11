from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bioterio.db'
db = SQLAlchemy(app)
cepa_list = ['C57B6/J','CD45.1','RAG1+/-']

class Cruza(db.Model):
    __tablename__ = 'cruza'
    __table_args__ = {'extend_existing': True}  
    
    db.Model.metadata.reflect(db.engine)
    id = db.Column(db.Integer, primary_key=True)
    caja = db.Column(db.String(20), nullable=False)
    cepa = db.Column(db.String(20), nullable=False)
    fecha_cruza = db.Column(db.DateTime, default=datetime.utcnow)    
    machos = db.Column(db.Integer, default=0)
    hembras = db.Column(db.Integer, default=0)
    camadas = db.relationship('Camada', backref='cruza', lazy=True)
    
    def __repr__(self):
        return '<Task %r>' %self.id
    
class Camada(db.Model):
    __tablename__ = 'camada'
    __table_args__ = {'extend_existing': True}    
    
    db.Model.metadata.reflect(db.engine)
    id = db.Column(db.Integer, primary_key=True)
    fecha_nacimiento = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_destete = db.Column(db.DateTime, default=datetime.today() + relativedelta(days=+28))
    machos = db.Column(db.Integer, default=0)
    hembras = db.Column(db.Integer, default=0)
    is_created = db.Column(db.Boolean, default=False)
    cruza_id = db.Column(db.Integer, db.ForeignKey('cruza.id'), nullable=False)
    
    
@app.route("/", methods=['POST', 'GET'])
def index():
    db.create_all()
    if request.method == 'POST':
        caja = request.form['caja'].upper()        
        cepa = request.form['cepa']        
        fecha_cruza = datetime.strptime(request.form['fecha_cruza'], "%Y-%m-%d")        
        machos = int(request.form['machos'])        
        hembras = int(request.form['hembras'])        
        new_cruza = Cruza(caja=caja, cepa=cepa, fecha_cruza=fecha_cruza, machos=machos, hembras=hembras)
        
        
        try:
            db.session.add(new_cruza)
            db.session.commit()
            return redirect('/')
        except:
            return "Hubo un error agregando la cruza a la base de datos"
    else:
        cruzas = Cruza.query.order_by(Cruza.fecha_cruza.desc()).all()
        return render_template("index.html", cruzas=cruzas, cepa_list=cepa_list)
    
@app.route("/camada/<int:id>", methods=['POST', 'GET'])
def camada(id):
    cruza = Cruza.query.get_or_404(id)
    if request.method == 'POST':
        fecha_nacimiento = datetime.strptime(request.form['fecha_cruza'], "%Y-%m-%d")      
        fecha_destete = fecha_nacimiento + relativedelta(days=+28)       
        machos = int(request.form['machos'])        
        hembras = int(request.form['hembras'])        
        new_camada = Camada(fecha_nacimiento=fecha_nacimiento,fecha_destete=fecha_destete,machos=machos,hembras=hembras, cruza=cruza)
                
        try:
            db.session.add(new_camada)
            db.session.commit()
            return redirect('/')
        except:
            return "Hubo un error agregando la cruza a la base de datos"
    else:        
        return render_template("camada.html", cruza=cruza)

    
@app.route('/delete/<int:id>')
def delete(id):
    cruza_to_delete = Cruza.query.get_or_404(id)   
     
    
    try:
        db.session.delete(cruza_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There was a problem deleting the task"
    
@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):    
    cruza = Cruza.query.get_or_404(id)
    
    if request.method == 'POST':
        cruza.caja = request.form['caja'].upper()        
        cruza.cepa = request.form['cepa']        
        cruza.fecha_cruza = datetime.strptime(request.form['fecha_cruza'], "%Y-%m-%d")        
        cruza.machos = int(request.form['machos'])        
        cruza.hembras = int(request.form['hembras'])        
        
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "Hubo un error "
        
    else:        
        return render_template('update.html', cruza=cruza, cepa_list=cepa_list)
    
@app.route('/update-camada/<int:id>', methods=['POST', 'GET'])
def update_camada(id):    
    camada = Camada.query.get_or_404(id)
     
    if request.method == 'POST':
        camada.fecha_nacimiento = datetime.strptime(request.form['fecha_cruza'], "%Y-%m-%d")      
        camada.fecha_destete = datetime.strptime(request.form['fecha_destete'], "%Y-%m-%d")       
        camada.machos = int(request.form['machos'])        
        camada.hembras = int(request.form['hembras'])        
         
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "Hubo un error "
         
    else:        
        return render_template('update-camada.html', camada=camada)
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)