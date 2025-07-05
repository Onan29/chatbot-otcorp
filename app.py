from flask import Flask, request, jsonify, render_template, session
from flask_session import Session
from dotenv import load_dotenv
import json
import requests
import os

# Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
print("API KEY cargada:", API_KEY)

app = Flask(__name__)

# Configuración de sesión
app.secret_key = os.getenv("SECRET_KEY")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./.flask_session/"
app.config["SESSION_PERMANENT"] = False
Session(app)

# Cargar reglas desde rules.json
with open("rules.json", "r", encoding="utf-8") as f:
    reglas = json.load(f)

# Cargar calendario académico y días libres
with open("calendario.json", "r", encoding="utf-8") as f:
    calendario = json.load(f)

with open("dias_libres.json", "r", encoding="utf-8") as f:
    dias_libres = json.load(f)

def consultar_ia(history):
    # Construir el system_prompt con reglas y calendario
    reglas_texto = ""
    for pregunta, respuesta in reglas.items():
        reglas_texto += f"- {pregunta} → {respuesta}\n"

    calendario_texto = ""
    for item in calendario:
        calendario_texto += (
            f"- {item['actividad']}:\n"
            f"    I semestre → {item['I_semestre']}\n"
            f"    II semestre → {item['II_semestre']}\n"
            f"    Verano → {item['Verano']}\n\n"
        )

    libres_texto = ""
    for nombre, fecha in dias_libres.items():
        libres_texto += f"- {nombre}: {fecha}\n"

    system_prompt = f"""Eres un asistente inteligente para estudiantes.

Tienes acceso al calendario académico oficial de la universidad:

{calendario_texto}
{libres_texto}

Si el usuario pregunta sobre fechas académicas, actividades universitarias o semestres, responde usando exclusivamente esta información.

Si el usuario pregunta sobre temas generales (como estaciones del año, cultura, ciencia, etc.), responde con tu conocimiento general, sin usar el calendario académico.

Sé claro, útil y no asumas que todo se refiere a la universidad.
"""

    payload_messages = [{"role": "system", "content": system_prompt}] + history

    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "mistralai/mistral-7b-instruct",
            "messages": payload_messages
        },
        timeout=10
    )

    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"Error en la API: {resp.status_code} - {resp.text}"

@app.route("/")
def index():
    session.pop("history", None)
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_text = request.json.get("message", "").strip()
    lower = user_text.lower()

    # Reglas simples exactas
    simple = reglas.get(lower)
    if simple:
        return jsonify({"response": simple})

    # Detección directa de semestres
    if "semestre" in lower:
        inicio = next(item for item in calendario if item["actividad"] == "Inicio de clases")
        if "prim" in lower or "i semestre" in lower:
            return jsonify({"response": inicio["I_semestre"]})
        if "segund" in lower or "ii semestre" in lower:
            return jsonify({"response": inicio["II_semestre"]})

    # Historial en sesión
    history = session.get("history", [])
    history.append({"role": "user", "content": user_text})

    ai_resp = consultar_ia(history)

    history.append({"role": "assistant", "content": ai_resp})
    session["history"] = history

    return jsonify({"response": ai_resp})

if __name__ == "__main__":
    app.run(debug=True)
