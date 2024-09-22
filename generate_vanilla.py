import yaml
import subprocess
import os
import PIL

changed_files_path = 'changed_files.txt'

print("Generating vanilla files!")
print(f"Processing changed files from: {changed_files_path}")
      
with open(changed_files_path, 'r') as file:
    lines = file.readlines()

for line in lines:
    filename = 'sodium/'+line.split('\t')[1].strip()

    if filename.endswith('.obj'):
        meta_filename = filename.replace('.obj', '.objmeta')

        if os.path.exists(meta_filename):
            try:
                with open(meta_filename, 'r') as meta_file:
                    meta_data = yaml.safe_load(meta_file)

                texture = meta_data.get('texture', None)
                output_model = meta_data.get('output_model', None)
                output_texture = meta_data.get('output_texture', None)
                offset = meta_data.get('offset','0.0 0.0 0.0').split()
                options = meta_data.get('options', [])
                visibility = meta_data.get('visibility', 7)

            except FileNotFoundError:
                print(f"Meta file not found for {filename} ({meta_filename})")
            except yaml.YAMLError as exc:
                print(f"Error parsing YAML file {meta_filename}: {exc}")
        else:
            options = []
            visibility = 7
            offset = ['0.0', '0.0', '0.0']
            texture = None
            output_model = None
            output_texture = None
            
        print(f"Offset: {offset[0]} {offset[1]} {offset[2]}")
            
        if not texture:
            print("Get texture from .mtl file: ",filename.replace('.obj', '.mtl'))
            with open(filename.replace('.obj','.mtl'), 'r') as file:
                for line in file:
                    print(line)
                    if line.startswith('map_Kd'):
                        texture = line.split()[1].strip()
                        break  
        if texture:
            texture = "sodium/assets/" + texture.replace(":", "/textures/")+".png"

        if not output_model:
            output_model = filename.replace('.obj', '.json').replace('sodium/','vanilla/')
            print("Use default output model: ",output_model)
        else:
            output_model = "vanilla/assets/" + output_model.replace(":", "/models/")+".json"

        if not output_texture:
            output_texture = texture.replace('sodium/', 'vanilla/')
            print("Use default output texture: ",output_texture)
        else:
            output_texture = "vanilla/assets/" + output_texture.replace(":", "/textures/")+".png"

        if texture and output_model and output_texture:

            output_model_dir = os.path.dirname(output_model)
            output_texture_dir = os.path.dirname(output_texture)

            if output_model_dir:
                os.makedirs(output_model_dir, exist_ok=True)
            if output_texture_dir:
                os.makedirs(output_texture_dir, exist_ok=True)

            runList = ['python3', 'objmc/objmc.py', '--objs', filename, '--texs', texture, '--offset', offset[0], offset[1], offset[2],  '--out', output_model, output_texture, '--visibility', str(visibility)]
            if 'noshadow' in options:
                runList.append('--noshadow')
            if 'flipuv' in options:
                runList.append('--flipuv')
            
            print(f"Running process script with {runList}")

            try:
                result = subprocess.run(runList, check=True,
                    stdout=subprocess.PIPE,   # Umleitung der normalen Ausgabe
                    stderr=subprocess.PIPE)    # Umleitung der Fehlerausgabe
            except subprocess.CalledProcessError as e:
                print(f"Error running process script: {e}")
                print("Script output (stdout):", e.stdout.decode('utf-8') if e.stdout else "No stdout")
                print("Script error output (stderr):", e.stderr.decode('utf-8') if e.stderr else "No stderr")
        else:
            print(f"Missing one of the required parameters for {filename}")
