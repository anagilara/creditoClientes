import os
import sqlite3
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "local-dev-key-change-before-deploy")
app.config["DATABASE"] = Path(
    os.environ.get("DATABASE", Path(__file__).with_name("clientes.db"))
)
CSRFProtect(app)


def connect_db():
    connection = sqlite3.connect(app.config["DATABASE"])
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with connect_db() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                empresa TEXT NOT NULL DEFAULT '',
                correo TEXT NOT NULL DEFAULT '',
                telefono TEXT NOT NULL DEFAULT '',
                notas TEXT NOT NULL DEFAULT '',
                creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


@app.get("/")
def index():
    search = request.args.get("q", "").strip()
    with connect_db() as connection:
        total = connection.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
        with_email = connection.execute(
            "SELECT COUNT(*) FROM clientes WHERE correo <> ''"
        ).fetchone()[0]
        companies = connection.execute(
            "SELECT COUNT(DISTINCT empresa) FROM clientes WHERE empresa <> ''"
        ).fetchone()[0]
        if search:
            pattern = f"%{search}%"
            clientes = connection.execute(
                """
                SELECT * FROM clientes
                WHERE nombre LIKE ? OR empresa LIKE ? OR correo LIKE ? OR telefono LIKE ?
                ORDER BY nombre COLLATE NOCASE
                """,
                (pattern, pattern, pattern, pattern),
            ).fetchall()
        else:
            clientes = connection.execute(
                "SELECT * FROM clientes ORDER BY nombre COLLATE NOCASE"
            ).fetchall()
    return render_template(
        "index.html",
        clientes=clientes,
        search=search,
        total=total,
        with_email=with_email,
        companies=companies,
    )


@app.post("/clientes/guardar")
def save_client():
    client_id = request.form.get("id", "").strip()
    nombre = request.form.get("nombre", "").strip()
    empresa = request.form.get("empresa", "").strip()
    correo = request.form.get("correo", "").strip()
    telefono = request.form.get("telefono", "").strip()
    notas = request.form.get("notas", "").strip()

    if not nombre:
        flash("El nombre es obligatorio.", "error")
        return redirect(url_for("index"))

    with connect_db() as connection:
        if client_id:
            connection.execute(
                """
                UPDATE clientes
                SET nombre = ?, empresa = ?, correo = ?, telefono = ?, notas = ?
                WHERE id = ?
                """,
                (nombre, empresa, correo, telefono, notas, client_id),
            )
            message = "Cliente actualizado."
        else:
            connection.execute(
                """
                INSERT INTO clientes (nombre, empresa, correo, telefono, notas)
                VALUES (?, ?, ?, ?, ?)
                """,
                (nombre, empresa, correo, telefono, notas),
            )
            message = "Cliente agregado."
    flash(message, "success")
    return redirect(url_for("index"))


@app.post("/clientes/<int:client_id>/eliminar")
def delete_client(client_id):
    with connect_db() as connection:
        connection.execute("DELETE FROM clientes WHERE id = ?", (client_id,))
    flash("Cliente eliminado.", "success")
    return redirect(url_for("index"))


init_db()


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")