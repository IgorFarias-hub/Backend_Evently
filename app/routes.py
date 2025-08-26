from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from app.models import Guest
from app.forms import GuestForm

# Página inicial (formulário)
@app.route("/", methods=["GET", "POST"])
def index():
    form = GuestForm()
    if form.validate_on_submit():
        nome = form.nome.data.strip()
        email = form.email.data.strip()

        # Verifica duplicado
        if Guest.query.filter_by(email=email).first():
            flash("Este e-mail já está cadastrado!", "danger")
            return redirect(url_for("index"))

        guest = Guest(nome=nome, email=email)
        db.session.add(guest)
        db.session.commit()
        flash("Convidado cadastrado com sucesso!", "success")
        return redirect(url_for("index"))
    return render_template("index.html", title="Lista de Convidados", form=form)

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

@app.route("/api/convidados/<int:id>", methods=["GET", "PUT", "DELETE"])
def api_convidado(id):
    guest = Guest.query.get_or_404(id)

    if request.method == "GET":
        return jsonify(guest.to_dict())

    if request.method == "PUT":
        data = request.get_json()
        if "nome" in data:
            guest.nome = data["nome"]
        if "email" in data:
            if "@" not in data["email"]:
                return jsonify({"erro": "E-mail inválido"}), 400
            guest.email = data["email"]
        db.session.commit()
        return jsonify(guest.to_dict())

    if request.method == "DELETE":
        db.session.delete(guest)
        db.session.commit()
        return jsonify({"msg": "Convidado removido"}), 200

@app.route("/api/convidados/<int:id>/confirmar", methods=["PUT"])
def api_confirmar(id):
    guest = Guest.query.get_or_404(id)
    guest.confirmado = True
    db.session.commit()
    return jsonify(guest.to_dict())
