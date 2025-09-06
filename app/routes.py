from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from app.models import Guest
from app.forms import GuestForm

# Página inicial 

@app.route("/")
def home():
    return render_template("home.html", title="Início")

# Cadastro de convidados
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    form = GuestForm()
    if form.validate_on_submit():
        nome = form.nome.data.strip()
        email = form.email.data.strip()

        # Verifica duplicado
        if Guest.query.filter_by(email=email).first():
            flash("Este e-mail já está cadastrado!", "danger")
            return redirect(url_for("cadastro"))

        guest = Guest(nome=nome, email=email)
        db.session.add(guest)
        db.session.commit()
        flash("Convidado cadastrado com sucesso!", "success")
        return redirect(url_for("cadastro"))
    return render_template("cadastro.html", title="Cadastro de Convidados", form=form)

# Listagem de convidados
@app.route("/convidados")
def convidados():
    convidados = Guest.query.all()
    return render_template("convidados.html", title="Todos os Convidados", convidados=convidados)

# Quantidade de convidados
@app.route("/quantidade")
def quantidade():
    total = Guest.query.count()
    return render_template("quantidade.html", title="Quantidade", total=total)

# Confirmados
@app.route("/confirmados")
def confirmados():
    confirmados = Guest.query.filter_by(confirmado=True).all()
    return render_template("confirmados.html", title="Confirmados", convidados=confirmados)

# --- API REST ---
@app.route("/api/convidados", methods=["GET", "POST"])
def api_convidados():
    if request.method == "POST":
        data = request.get_json()
        if not data.get("nome") or not data.get("email"):
            return jsonify({"erro": "Nome e e-mail são obrigatórios"}), 400
        if "@" not in data["email"]:
            return jsonify({"erro": "E-mail inválido"}), 400

        guest = Guest(nome=data["nome"], email=data["email"])
        db.session.add(guest)
        db.session.commit()
        return jsonify(guest.to_dict()), 201

    convidados = Guest.query.all()
    return jsonify([g.to_dict() for g in convidados])


@app.route("/confirmar", methods=["GET", "POST"])
def confirmar():
    form = GuestForm()
    if form.validate_on_submit():
        email = form.email.data.strip()

        guest = Guest.query.filter_by(email=email).first()
        if not guest:
            flash("E-mail não encontrado na lista de convidados!", "danger")
            return redirect(url_for("confirmar"))

        if guest.confirmado:
            flash("Este convidado já confirmou presença!", "info")
        else:
            guest.confirmado = True
            db.session.commit()
            flash("Presença confirmada com sucesso!", "success")

        return redirect(url_for("convidados"))

    return render_template("confirmar.html", title="Confirmar Presença", form=form)

@app.route("/confirmar/<int:id>", methods=["POST"])
def confirmar_id(id):
    guest = Guest.query.get_or_404(id)

    if guest.confirmado:
        flash("Este convidado já confirmou presença!", "info")
    else:
        guest.confirmado = True
        db.session.commit()
        flash(f"Presença de {guest.nome} confirmada com sucesso!", "success")

    return redirect(url_for("convidados"))

# Editar convidado
@app.route("/convidados/<int:id>/editar", methods=["GET", "POST"])
def editar_convidado(id):
    guest = Guest.query.get_or_404(id)
    form = GuestForm(obj=guest)

    if form.validate_on_submit():
        guest.nome = form.nome.data.strip()
        guest.email = form.email.data.strip()
        db.session.commit()
        flash("Convidado atualizado com sucesso!", "success")
        return redirect(url_for("convidados"))

    return render_template("cadastro.html", title="Editar Convidado", form=form)


# Deletar convidado
@app.route("/convidados/<int:id>/deletar", methods=["POST"])
def deletar_convidado(id):
    guest = Guest.query.get_or_404(id)
    db.session.delete(guest)
    db.session.commit()
    flash("Convidado removido com sucesso!", "success")
    return redirect(url_for("convidados"))