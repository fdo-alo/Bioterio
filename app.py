from flask import render_template, request, redirect, url_for, flash, abort
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from bioterio import app, db
from bioterio.models import Cruza, Camada, Macho, Hembra, Observacion, User
from bioterio.forms import RegistrationForm, LoginForm
from flask_login import login_user, login_required, logout_user

cepa_list = ['C57B6/J', 'CD45.1', 'RAG1+/-']


@app.route('/')
def index():
    return render_template("index.html")


@app.route("/cruza", methods=['POST', 'GET'])
@login_required
def cruza():
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
                return redirect(url_for('cruza'))
            except:
                return redirect(url_for('user_error'))
        else:
            return render_template("error.html",
                                   error="El nombre de la caja no coincide con el tipo de la cepa o la caja ya existe.")
    else:
        cruzas = Cruza.query.order_by(Cruza.fecha_cruza.desc()).all()
        return render_template("cruza.html", cruzas=cruzas, cepa_list=cepa_list)


@app.route("/camada/<int:id>", methods=['POST', 'GET'])
@login_required
def camada(id):
    cruza = Cruza.query.get_or_404(id)
    if request.method == 'POST':
        fecha_nacimiento = datetime.strptime(request.form['fecha_cruza'], "%Y-%m-%d")
        fecha_destete = fecha_nacimiento + relativedelta(days=+28)
        machos = int(request.form['machos'])
        hembras = int(request.form['hembras'])
        new_camada = Camada(fecha_nacimiento=fecha_nacimiento, fecha_destete=fecha_destete, machos=machos,
                            hembras=hembras, cruza=cruza)

        try:
            db.session.add(new_camada)
            db.session.commit()
            return redirect(url_for('destete'))
        except:
            return redirect(url_for("user_error"))
    else:
        return render_template("camada.html", cruza=cruza)


@app.route("/macho/<int:id>", methods=['POST', 'GET'])
@login_required
def macho(id):
    camada = Camada.query.get_or_404(id)
    cruza = Cruza.query.get_or_404(camada.cruza_id)

    if request.method == 'POST' and camada.macho_is_created == False:
        caja = request.form['caja'].upper()
        try:
            fecha_destete = datetime.strptime(request.form['fecha_destete'], "%Y-%m-%d")
        except:
            return redirect(url_for("user_error"))
        if caja and camada.fecha_destete:
            padres = cruza.caja

            if verificar_caja(caja, cruza.cepa) and existe_caja(caja) == False:
                macho = Macho(caja=caja, fecha_nacimiento=camada.fecha_nacimiento, fecha_destete=fecha_destete,
                              cantidad=camada.machos, cepa=cruza.cepa, cruza=cruza, padres=padres)
                try:
                    db.session.add(macho)
                    db.session.commit()
                    camada.macho_is_created = True
                    db.session.commit()
                    return redirect(url_for('destete'))
                except Exception as e:
                    return str(e)
            else:
                return render_template("error.html",
                                       error="El nombre de la caja no coincide con el tipo de la cepa o la caja ya existe.")
        else:
            return redirect(url_for('user_error'))
    else:
        caja = siguiente_caja(cruza.cepa)
        return render_template("macho.html", cruza=cruza, camada=camada, caja=caja)


@app.route("/hembra/<int:id>", methods=['POST', 'GET'])
@login_required
def hembra(id):
    camada = Camada.query.get_or_404(id)
    cruza = Cruza.query.get_or_404(camada.cruza_id)

    if request.method == 'POST' and camada.hembra_is_created == False:
        caja = request.form['caja'].upper()
        try:
            fecha_destete = datetime.strptime(request.form['fecha_destete'], "%Y-%m-%d")
        except:
            return redirect(url_for('user_error'))
        if caja and camada.fecha_destete:
            padres = cruza.caja

            if verificar_caja(caja, cruza.cepa) and existe_caja(caja) == False:
                hembra = Hembra(caja=caja, fecha_nacimiento=camada.fecha_nacimiento, fecha_destete=fecha_destete,
                                cantidad=camada.hembras, cepa=cruza.cepa, cruza=cruza, padres=padres)
                try:
                    db.session.add(hembra)
                    db.session.commit()
                    camada.hembra_is_created = True
                    db.session.commit()
                    return redirect(url_for('destete'))
                except Exception as e:
                    return str(e)
            else:
                return render_template("error.html",
                                       error="El nombre de la caja no coincide con el tipo de la cepa o la caja ya existe.")
        else:
            return redirect(url_for('user_error'))
    else:
        caja = siguiente_caja(cruza.cepa)
        return render_template("hembra.html", cruza=cruza, camada=camada, caja=caja)


def calculate_age(born):
    today = date.today()
    diferencia = today - born

    return str(round(diferencia.days // 7, 0)) + " semanas y " + str((round(diferencia.days % 7, 0))) + " días"


@app.route("/macho-hembra/", methods=['GET'])
@login_required
def macho_hembra_get():
    machos_a = Macho.query.filter(Macho.caja.contains('A')).order_by(Macho.fecha_destete).all()
    hembras_a = Hembra.query.filter(Hembra.caja.contains('A')).order_by(Hembra.fecha_destete).all()
    machos_b = Macho.query.filter(Macho.caja.contains('B')).order_by(Macho.fecha_destete).all()
    hembras_b = Hembra.query.filter(Hembra.caja.contains('B')).order_by(Hembra.fecha_destete).all()
    machos_c = Macho.query.filter(Macho.caja.contains('C')).order_by(Macho.fecha_destete).all()
    hembras_c = Hembra.query.filter(Hembra.caja.contains('C')).order_by(Hembra.fecha_destete).all()

    total_macho_a = sum([x.cantidad for x in machos_a])
    total_macho_b = sum([x.cantidad for x in machos_b])
    total_macho_c = sum([x.cantidad for x in machos_c])

    total_hembra_a = sum([x.cantidad for x in hembras_a])
    total_hembra_b = sum([x.cantidad for x in hembras_b])
    total_hembra_c = sum([x.cantidad for x in hembras_c])

    calculate = calculate_age

    return render_template("macho-hembra.html", machos_a=machos_a, total_macho_a=total_macho_a,
                           hembras_a=hembras_a, total_hembra_a=total_hembra_a,
                           machos_b=machos_b, total_macho_b=total_macho_b,
                           hembras_b=hembras_b, total_hembra_b=total_hembra_b,
                           machos_c=machos_c, total_macho_c=total_macho_c,
                           hembras_c=hembras_c, total_hembra_c=total_hembra_c,
                           calculateage=calculate)


@app.route("/observacion-macho/<int:id>", methods=['POST', 'GET'])
@login_required
def observacion_macho(id):
    macho = Macho.query.get_or_404(id)
    if request.method == 'POST':
        observacion = request.form['observacion']

        new_observacion = Observacion(observacion=observacion, macho=macho)

        try:
            db.session.add(new_observacion)
            db.session.commit()
            return redirect('/observacion-macho/{}'.format(id))
        except:
            return redirect(url_for('user_error'))
    else:
        return render_template("observacion-macho.html", macho=macho)


@app.route("/observacion-hembra/<int:id>", methods=['POST', 'GET'])
@login_required
def observacion_hembra(id):
    hembra = Hembra.query.get_or_404(id)
    if request.method == 'POST':
        observacion = request.form['observacion']

        new_observacion = Observacion(observacion=observacion, hembra=hembra)

        try:
            db.session.add(new_observacion)
            db.session.commit()
            return redirect('/observacion-hembra/{}'.format(id))
        except:
            return redirect(url_for('user_error'))
    else:
        return render_template("observacion-hembra.html", hembra=hembra)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    cruza_to_delete = Cruza.query.get_or_404(id)

    try:
        db.session.delete(cruza_to_delete)
        db.session.commit()
        return redirect(url_for('index'))
    except:
        return redirect(url_for('user_error'))


@app.route('/delete-macho/<int:id>')
@login_required
def delete_macho(id):
    macho_to_delete = Macho.query.get_or_404(id)
    try:
        db.session.delete(macho_to_delete)
        db.session.commit()
        return redirect(url_for('macho_hembra_get'))
    except:
        return redirect(url_for('user_error'))


@app.route('/delete-hembra/<int:id>')
@login_required
def delete_hembra(id):
    hembra_to_delete = Hembra.query.get_or_404(id)

    try:
        db.session.delete(hembra_to_delete)
        db.session.commit()
        return redirect(url_for('macho_hembra_get'))
    except:
        return redirect(url_for('user_error'))


@app.route('/update/<int:id>', methods=['POST', 'GET'])
@login_required
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
            return redirect(url_for('cruza'))
        except:
            return redirect(url_for('user_error'))

    else:
        return render_template('update.html', cruza=cruza, cepa_list=cepa_list)


@app.route('/user-error', methods=['GET'])
@login_required
def user_error():
    return render_template('user-error.html')


def find_cruza(query):
    cruza = Cruza.query.filter_by(id=query).first()
    return cruza.cepa


@app.route("/destete", methods=['GET'])
@login_required
def destete():
    camadas = Camada.query.order_by(Camada.fecha_destete.desc()).all()
    cepa = find_cruza
    return render_template("destete.html", camadas=camadas, cepa=cepa)


@app.route('/update-camada/<int:id>', methods=['POST', 'GET'])
@login_required
def update_camada(id):
    camada = Camada.query.get_or_404(id)

    if request.method == 'POST':
        camada.fecha_nacimiento = datetime.strptime(request.form['fecha_cruza'], "%Y-%m-%d")
        camada.fecha_destete = datetime.strptime(request.form['fecha_destete'], "%Y-%m-%d")
        camada.machos = int(request.form['machos'])
        camada.hembras = int(request.form['hembras'])

        try:
            db.session.commit()
            return redirect(url_for('cruza'))
        except:
            return redirect(url_for('user_error'))

    else:
        return render_template('update-camada.html', camada=camada)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Saliste de forma correcta!')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()

        # Check that the user was supplied and the password is right
        # The verify_password method comes from the User object
        # https://stackoverflow.com/questions/2209755/python-operation-vs-is-not

        if user.check_password(form.password.data) and user is not None:
            # Log in the user

            login_user(user)
            flash('Logged in successfully.')

            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next == None or not next[0] == '/':
                next = url_for('index')

            return redirect(next)
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering! Now you can login!')
        return redirect(url_for('login'))

    return render_template('register.html', form=form, empty_list=len(User.query.order_by(User.id).all()) == 0)


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
        for i in range(len(values) - 1):
            if values[i] + 1 != values[i + 1]:
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
