import yaml
import subprocess
import os

# Datei mit den geänderten Dateien
changed_files_path = 'changed_files.txt'

print("Generating vanilla files!")
print(f"Processing changed files from: {changed_files_path}")
      
# Öffnen der Datei 'changed_files.txt' und Einlesen der Zeilen
with open(changed_files_path, 'r') as file:
    lines = file.readlines()

# Schleife über alle Zeilen
for line in lines:
    # Der Dateiname steht nach dem Tabulator, also den zweiten Teil der Zeile nehmen
    filename = 'sodium/'+line.split('\t')[1].strip()

    # Prüfen, ob die Datei eine .obj-Datei ist
    if filename.endswith('.obj'):
        # Pfad der .objmeta-Datei (im selben Verzeichnis)
        meta_filename = filename.replace('.obj', '.objmeta')

        try:
            # Öffnen und Laden der .objmeta-Datei mit PyYAML
            with open(meta_filename, 'r') as meta_file:
                meta_data = yaml.safe_load(meta_file)

            # Extrahieren der Werte für die Schlüssel 'texture', 'output_model' und 'output_texture'
            texture = meta_data.get('texture', None)
            output_model = meta_data.get('output_model', None)
            output_texture = meta_data.get('output_texture', None)
			
            # Anpassung des Wertes für 'output_model'
            if texture:
                texture = "sodium/assets/" + texture.replace(":", "/textures/")+".png"
            if output_model:
                output_model = "vanilla/assets/" + output_model.replace(":", "/models/")+".json"
            if output_texture:
                output_texture = "vanilla/assets/" + output_texture.replace(":", "/textures/")+".png"

            # Prüfen, ob alle benötigten Variablen vorhanden sind
            if texture and output_model and output_texture:
  
                output_model_dir = os.path.dirname(output_model)
                output_texture_dir = os.path.dirname(output_texture)

                if output_model_dir:
                    os.makedirs(output_model_dir, exist_ok=True)
                if output_texture_dir:
                    os.makedirs(output_texture_dir, exist_ok=True)

               # Aufrufen des Python-Skripts 'process' mit den Parametern
                print(f"Running process script with {filename}, {texture}, {output_model}, {output_texture}")

                try:
                    result = subprocess.run(
                        ['python3', 'objmc.py', '--objs', filename, '--texs', texture, '--out', output_model, output_texture],
                        check=True,
                        stdout=subprocess.PIPE,   # Umleitung der normalen Ausgabe
                        stderr=subprocess.PIPE)    # Umleitung der Fehlerausgabe
                except subprocess.CalledProcessError as e:
                    print(f"Error running process script: {e}")
                    print("Script output (stdout):", e.stdout.decode('utf-8') if e.stdout else "No stdout")
                    print("Script error output (stderr):", e.stderr.decode('utf-8') if e.stderr else "No stderr")
            else:
                print(f"Missing one of the required parameters for {filename}")

            # Ausgabe der Ergebnisse (optional)
            print(f"Processing {filename}:")
            print(f"  Texture: {texture}")
            print(f"  Output Model: {output_model}")
            print(f"  Output Texture: {output_texture}")
            print()  # Leerzeile zur besseren Lesbarkeit

        except FileNotFoundError:
            print(f"Meta file not found for {filename} ({meta_filename})")
        except yaml.YAMLError as exc:
            print(f"Error parsing YAML file {meta_filename}: {exc}")
