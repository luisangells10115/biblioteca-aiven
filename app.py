import os
import mysql.connector
from flask import Flask, render_template_string

app = Flask(__name__)

def conectar():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database="biblioteca2",
        ssl_disabled=False
    )

@app.route("/")
def inicio():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("SHOW TABLES")
    tablas = [fila[0] for fila in cursor.fetchall()]

    cursor.close()
    conexion.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Biblioteca</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                background: #f4f6f8;
            }

            h1 {
                color: #1f4e79;
            }

            .tabla {
                background: white;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
            }

            a {
                text-decoration: none;
                color: #1f4e79;
                font-weight: bold;
            }
        </style>
    </head>

    <body>

        <h1>Base de datos Biblioteca</h1>

        <p>Base de datos MySQL alojada en Aiven.</p>

        <h2>Tablas disponibles</h2>

        {% for tabla in tablas %}
            <div class="tabla">
                <a href="/tabla/{{ tabla }}">{{ tabla }}</a>
            </div>
        {% endfor %}

    </body>
    </html>
    """, tablas=tablas)


@app.route("/tabla/<nombre>")
def ver_tabla(nombre):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("SHOW TABLES")
    tablas_permitidas = [fila[0] for fila in cursor.fetchall()]

    if nombre not in tablas_permitidas:
        cursor.close()
        conexion.close()
        return "Tabla no encontrada", 404

    cursor.execute(f"SELECT * FROM `{nombre}`")

    columnas = [columna[0] for columna in cursor.description]
    datos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="es">

    <head>
        <meta charset="UTF-8">
        <title>{{ nombre }}</title>

        <style>

            body {
                font-family: Arial, sans-serif;
                margin: 30px;
                background: #f4f6f8;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                background: white;
            }

            th, td {
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
            }

            th {
                background: #1f4e79;
                color: white;
            }

            a {
                color: #1f4e79;
            }

        </style>

    </head>

    <body>

        <h1>Tabla: {{ nombre }}</h1>

        <p><a href="/">← Regresar a las tablas</a></p>

        <table>

            <tr>
                {% for columna in columnas %}
                    <th>{{ columna }}</th>
                {% endfor %}
            </tr>

            {% for fila in datos %}
                <tr>
                    {% for dato in fila %}
                        <td>{{ dato }}</td>
                    {% endfor %}
                </tr>
            {% endfor %}

        </table>

    </body>
    </html>
    """, nombre=nombre, columnas=columnas, datos=datos)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
