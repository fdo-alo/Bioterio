from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bioterio.db'
db = SQLAlchemy(app)
cepa_list = ['C57B6/J','CD45.1','RAG1+/-']


#############################################TABLAS###############################################################
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
        return '<Cruza %r>' %self.id
    
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
        return '<Camada %r>' %self.id
    
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
        return '<Macho %r>' %self.id
    
    
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
        return '<Hembra %r>' %self.id
    
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
        return '<Observacion %r>' %self.id
    
#############################PAGINAS#############################################################################   
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
        
        if verificar_caja(caja, cepa) and existe_caja(caja) == False:            
            try:
                db.session.add(new_cruza)
                db.session.commit()
                return redirect('/')
            except:
                return redirect("/user-error/")
        else:
            return render_template("error.html", error="El nombre de la caja no coincide con el tipo de la cepa o la caja ya existe.")
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
            return redirect('/camada/{}'.format(id))
        except:
            return redirect("/user-error/")
    else:        
        return render_template("camada.html", cruza=cruza)

@app.route("/macho/<int:id>", methods=['POST', 'GET'])    
def macho(id):
    camada = Camada.query.get_or_404(id)    
    cruza = Cruza.query.get_or_404(camada.cruza_id)
            
    if request.method == 'POST' and camada.macho_is_created == False:
        caja = request.form['caja'].upper()
        try:
            fecha_destete = datetime.strptime(request.form['fecha_destete'], "%Y-%m-%d")
        except:
            return redirect("/user-error/")
        if caja and camada.fecha_destete:
            padres = cruza.caja
            macho = Macho(caja=caja, fecha_nacimiento=camada.fecha_nacimiento,fecha_destete=fecha_destete, cantidad=camada.machos, cepa=cruza.cepa, cruza=cruza, padres=padres)      
            
            if verificar_caja(caja, cruza.cepa) and existe_caja(caja) == False:                
                try:                         
                    db.session.add(macho)
                    db.session.commit()
                    camada.macho_is_created = True
                    db.session.commit()
                    return redirect('/camada/{}'.format(id))
                except Exception as e:
                    return str(e)
            else:
                return render_template("error.html", error="El nombre de la caja no coincide con el tipo de la cepa o la caja ya existe.")
        else:
            return redirect("/user-error/")
    else:
        caja = siguiente_caja(cruza.cepa)
        return render_template("macho.html", cruza=cruza, camada=camada, caja=caja)
        
@app.route("/hembra/<int:id>", methods=['POST', 'GET'])    
def hembra(id):
    camada = Camada.query.get_or_404(id)    
    cruza = Cruza.query.get_or_404(camada.cruza_id)
    
    if request.method == 'POST' and camada.hembra_is_created == False:        
        caja = request.form['caja'].upper()
        try:
            fecha_destete = datetime.strptime(request.form['fecha_destete'], "%Y-%m-%d")
        except:
            return redirect("/user-error/")
        if caja and camada.fecha_destete:
            padres = cruza.caja
            hembra = Hembra(caja=caja, fecha_nacimiento=camada.fecha_nacimiento,fecha_destete=fecha_destete, cantidad=camada.hembras, cepa=cruza.cepa, cruza=cruza, padres=padres)
                    
            try:            
                db.session.add(hembra)
                db.session.commit()
                camada.hembra_is_created = True
                db.session.commit()            
                return redirect('/camada/{}'.format(id))
            except Exception as e:
                return str(e)
        else:
            return redirect("/user-error/")
    else:
        caja = siguiente_caja(cruza.cepa)
        return render_template("hembra.html", cruza=cruza, camada=camada, caja=caja)
    
    
@app.route("/macho-hembra/", methods=['GET'])    
def macho_hembra_get():    
    machos = Macho.query.order_by(Macho.cepa).all()
    hembras = Hembra.query.order_by(Hembra.cepa).all()
    return render_template("macho-hembra.html", machos=machos, hembras=hembras)

@app.route("/observacion-macho/<int:id>", methods=['POST', 'GET'])
def observacion_macho(id):
    macho = Macho.query.get_or_404(id)
    if request.method == 'POST':        
        observacion =  request.form['observacion']            
         
        new_observacion = Observacion(observacion=observacion, macho=macho)
                
        try:
            db.session.add(new_observacion)
            db.session.commit()
            return redirect('/macho-hembra/')
        except:
            return redirect("/user-error/")
    else:        
        return render_template("observacion-macho.html", macho=macho)
    
@app.route("/observacion-hembra/<int:id>", methods=['POST', 'GET'])
def observacion_hembra(id):
    hembra = Hembra.query.get_or_404(id)
    if request.method == 'POST':        
        observacion =  request.form['observacion']            
         
        new_observacion = Observacion(observacion=observacion, hembra=hembra)
                
        try:
            db.session.add(new_observacion)
            db.session.commit()
            return redirect('/macho-hembra/')
        except:
            return redirect("/user-error/")
    else:        
        return render_template("observacion-hembra.html", hembra=hembra)
    
@app.route('/delete/<int:id>')
def delete(id):
    cruza_to_delete = Cruza.query.get_or_404(id)     
    
    try:
        db.session.delete(cruza_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return redirect("/user-error/")
    
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
            return redirect("/user-error/")
        
    else:        
        return render_template('update.html', cruza=cruza, cepa_list=cepa_list)
    
@app.route('/user-error/', methods=['GET'])
def user_error():
    return render_template('user-error.html')    
    
@app.route("/destete/", methods=['GET'])
def destete():
        camadas = Camada.query.order_by(Camada.fecha_destete.desc()).all()
        return render_template("destete.html", camadas=camadas)
    
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
            return redirect("/user-error/")
         
    else:        
        return render_template('update-camada.html', camada=camada)
    
def verificar_caja(caja, cepa):
    if cepa == cepa_list[0]:        
        return "A" == str(caja[:1])
    if cepa == cepa_list[1]:
        return "B" == str(caja[:1])
    if cepa == cepa_list[2]:
        return "C" == str(caja[:1])

    return False

def regresar_letra_cepa(cepa):
    if cepa == cepa_list[0]:        
        return "A"
    if cepa == cepa_list[1]:
        return "B"
    if cepa == cepa_list[2]:
        return "C"    

def siguiente_caja(cepa):    
    lista = []
    machos = Macho.query.order_by(Macho.cepa).all()
    hembras = Hembra.query.order_by(Hembra.cepa).all()
    cruzas = Cruza.query.order_by(Cruza.fecha_cruza.desc()).all()
    
    letra = regresar_letra_cepa(cepa)
   
    for macho in machos:   
        if letra == macho.caja[:1]:
            lista.append(macho.caja) 
        
    for hembra in hembras:
        if letra == hembra.caja[:1]:
            lista.append(hembra.caja) 
        
    for cruza in cruzas:
        if letra == cruza.caja[:1]:
            lista.append(cruza.caja)
            
    values = sorted([int(x[1:]) for x in lista])
    print(values)
    
    numero = 0
    
    if len(values) == 0:
        numero = 1
    elif len(values) == 1:
        numero = values[-1] + 1
    else:        
        for i in range(len(values)-1):
            if values[i] + 1 != values[i+1]:
                numero = values[i] + 1
                break
            elif i == len(values) - 2:
                numero = values[-1] + 1
            
    return letra + str(numero)

def existe_caja(caja):
    lista = []
    machos = Macho.query.order_by(Macho.cepa).all()
    hembras = Hembra.query.order_by(Hembra.cepa).all()
    cruzas = Cruza.query.order_by(Cruza.fecha_cruza.desc()).all()
    for macho in machos:   
        if caja == macho.caja:
            lista.append(macho.caja) 
        
    for hembra in hembras:
        if caja == hembra.caja:
            lista.append(hembra.caja) 
        
    for cruza in cruzas:
        if caja == cruza.caja:
            lista.append(cruza.caja)
            
    return len(lista) > 0
    
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)