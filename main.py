from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import os
from faker import Faker
import uuid

app = Flask(__name__)
fake = Faker()

# Directory for temporary files
TEMP_DIR = "temp"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/download-template', methods=['GET'])
def download_template():
    # Create an empty DataFrame with the expected structure
    columns = ["Nome", "Cognome", "Email", "Telefono"]
    df = pd.DataFrame(columns=columns)
    template_path = os.path.join(TEMP_DIR, "template.xlsx")
    df.to_excel(template_path, index=False)

    return send_file(template_path,
                     as_attachment=True,
                     download_name="template.xlsx")


@app.route('/generate-data', methods=['GET'])
def generate_data():
    # Genera 10 record casuali
    data = [{
        "Nome": fake.first_name(),
        "Cognome": fake.last_name(),
        "Email": fake.email(),
        "Telefono": fake.phone_number()
    } for _ in range(10)]

    # Crea un DataFrame con i dati
    df = pd.DataFrame(data)

    # Salva il file Excel in un percorso temporaneo
    file_name = f"generated_data_{uuid.uuid4().hex}.xlsx"
    file_path = os.path.join(TEMP_DIR, file_name)
    df.to_excel(file_path, index=False)

    # Restituisce il file Excel come allegato
    return send_file(file_path,
                     as_attachment=True,
                     download_name="generated_data.xlsx")


from werkzeug.utils import secure_filename

import secrets
import string


def generate_random_string(length=10):
    """Genera una stringa alfanumerica casuale."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


@app.route('/anonymize-data', methods=['POST'])
def anonymize_data():
    if 'file' not in request.files:
        return jsonify({"error": "Nessun file caricato."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nome del file non valido."}), 400

    # Salva il file caricato in una posizione temporanea
    filename = secure_filename(file.filename)
    file_path = os.path.join(TEMP_DIR, filename)
    file.save(file_path)

    try:
        # Leggi il file Excel
        df = pd.read_excel(file_path)

        # Anonimizza i dati
        for column in df.columns:
            df[column] = [generate_random_string() for _ in range(len(df))]

        # Salva il file anonimizzato
        anonymized_file_name = f"anonymized_{uuid.uuid4().hex}.xlsx"
        anonymized_file_path = os.path.join(TEMP_DIR, anonymized_file_name)
        df.to_excel(anonymized_file_path, index=False)

        # Ritorna il file anonimizzato come risposta scaricabile
        return send_file(anonymized_file_path,
                         as_attachment=True,
                         download_name="anonymized_data.xlsx")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
