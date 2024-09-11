from flask import Flask, request, render_template_string
import os
import csv
import shutil

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    num_rows = int(request.form.get('num_rows', 10))  # Standaard op 10
    directories = [request.form.get(f'directory_{i}', '') for i in range(num_rows)]
    target_directory = request.form.get('target_directory', 'C:/Users/ExampleUser/Documents')  # Voorbeeldpad

    uploaded_files = []
    if 'upload' in request.files:
        file = request.files['upload']
        if file and file.filename:
            file_path = f'uploads/{file.filename}'
            file.save(file_path)
            uploaded_files.append(file_path)
    
    confirmation_message = ""
    if request.method == 'POST':
        if 'delete_file' in request.form:
            file_to_delete = request.form.get('delete_file')
            if file_to_delete and os.path.isfile(file_to_delete):
                os.remove(file_to_delete)
        
        if 'save_all' in request.form:
            save_to_csv(directories, target_directory)
            confirmation_message = "Gegevens succesvol opgeslagen."
        
        if 'create_directories' in request.form:
            return create_directories()
    
    # Verkrijg alle bestanden in de upload directory
    uploaded_files = [os.path.join('uploads', f) for f in os.listdir('uploads') if os.path.isfile(os.path.join('uploads', f))]
    
    return render_template_string('''
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                margin: 0;
                padding: 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                overflow: hidden;
            }
            .container {
                background: #fff;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                padding: 20px;
                width: 100vw;
                max-width: 1200px;
                height: 100vh;
                overflow-y: auto;
            }
            h1 {
                font-size: 24px;
                color: #333;
                margin-bottom: 20px;
                text-align: center;
            }
            .form-group {
                margin-bottom: 15px;
            }
            .form-group label {
                display: block;
                font-weight: bold;
                margin-bottom: 5px;
            }
            .form-group input[type="number"],
            .form-group input[type="text"],
            .form-group input[type="file"] {
                width: calc(100% - 22px);
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            .form-group input[type="submit"] {
                background-color: #007bff;
                color: #fff;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }
            .form-group input[type="submit"]:hover {
                background-color: #0056b3;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            table, th, td {
                border: 1px solid #ddd;
            }
            th, td {
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            td input[type="text"] {
                width: 100%;
                padding: 8px;
                border: none;
                box-sizing: border-box;
            }
            .file-list {
                margin-top: 20px;
            }
            .file-list ul {
                list-style-type: none;
                padding: 0;
            }
            .file-list li {
                margin-bottom: 10px;
            }
            .confirmation {
                font-size: 18px;
                color: green;
                text-align: center;
            }
        </style>
        <div class="container">
            <h1>Folder Master</h1>
            <form method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="upload">Upload een bestand:</label>
                    <input type="file" id="upload" name="upload">
                    <input type="submit" value="Uploaden">
                </div>
            </form>
            {% if uploaded_files %}
                <div class="file-list">
                    <h2>Geüploade bestanden:</h2>
                    <ul>
                        {% for file in uploaded_files %}
                            <li>{{ file }} <form method="post" style="display:inline;"><input type="hidden" name="delete_file" value="{{ file }}"><input type="submit" value="Verwijderen"></form></li>
                        {% endfor %}
                    </ul>
                </div>
            {% endif %}
            <form method="post">
                <div class="form-group">
                    <label for="num_rows">Aantal mappen:</label>
                    <input type="number" id="num_rows" name="num_rows" value="{{ num_rows }}" min="1" onchange="this.form.submit()">
                </div>
                <table id="directory_table">
                    <thead>
                        <tr>
                            <th>Mapnamen</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for i in range(num_rows) %}
                            <tr>
                                <td>
                                    <input type="text" id="directory_{{ i }}" name="directory_{{ i }}" value="{{ directories[i] }}">
                                </td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
                <div class="form-group">
                    <label for="target_directory">Pad naar doeldirectory:</label>
                    <input type="text" id="target_directory" name="target_directory" value="{{ target_directory }}" placeholder="Bijvoorbeeld: C:/Users/ExampleUser/Documents">
                </div>
                <div class="form-group">
                    <input type="submit" name="save_all" value="Opslaan Alles">
                </div>
                <div class="form-group">
                    <input type="submit" name="create_directories" value="Maak Mappen Aan">
                </div>
            </form>
            {% if confirmation_message %}
                <p class="confirmation">{{ confirmation_message }}</p>
            {% endif %}
        </div>
    ''', uploaded_files=uploaded_files, num_rows=num_rows, directories=directories, target_directory=target_directory, confirmation_message=confirmation_message)

def save_to_csv(directories, target_directory):
    csv_file = 'data.csv'
    header = ['Mapnaam', 'Doeldirectory']
    
    if not os.path.isfile(csv_file):
        # Schrijf header als het bestand nog niet bestaat
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(header)
    
    # Schrijf gegevens naar CSV
    with open(csv_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for directory in directories:
            if directory:  # Alleen opnemen als mapnaam niet leeg is
                writer.writerow([directory, target_directory])

def create_directories():
    csv_file = 'data.csv'
    
    # Lees CSV-bestand
    directories = []
    target_directory = ""
    
    if os.path.isfile(csv_file):
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                if row:
                    directories.append(row[0])
                    target_directory = row[1]

    # Maak mappen aan en voeg bestanden toe
    if directories:
        for directory in directories:
            dir_path = os.path.join(target_directory, directory)
            os.makedirs(dir_path, exist_ok=True)
            
            # Voeg geüploade bestanden toe aan de nieuwe map
            for file_path in os.listdir('uploads'):
                file_full_path = os.path.join('uploads', file_path)
                if os.path.isfile(file_full_path):
                    # Kopieer het bestand naar de nieuwe map
                    new_file_path = os.path.join(dir_path, file_path)
                    shutil.copy(file_full_path, new_file_path)

    # Geef een bevestiging terug aan de gebruiker
    return render_template_string('''
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                margin: 0;
                padding: 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                overflow: hidden;
            }
            .container {
                background: #fff;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                padding: 20px;
                width: 100vw;
                max-width: 1200px;
                height: 100vh;
                overflow-y: auto;
            }
            h1 {
                font-size: 24px;
                color: #333;
                margin-bottom: 20px;
                text-align: center;
            }
            .confirmation {
                font-size: 18px;
                color: green;
                text-align: center;
            }
        </style>
        <div class="container">
            <h1>Folder Master</h1>
            <p class="confirmation">Mappen succesvol aangemaakt en bestanden toegevoegd.</p>
            <a href="/">Terug naar startpagina</a>
        </div>
    ''')

if __name__ == '__main__':
    app.run(debug=True)
