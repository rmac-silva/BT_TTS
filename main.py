import subprocess
import threading
import os
import shutil
from git import Repo

script_path = os.path.abspath(__file__)[:-7] + "script.ps1"

PIPER_FOLDER = "./piper/"
MODEL_FOLDER = "Models/"
REPO_FOLDER = "Titanfall2/"
VOICE_MODEL = MODEL_FOLDER + REPO_FOLDER

class VoiceSynth():
    
    def __init__(self):
        self.speech_rate = "1.0"
        self.phoneme_variability = "0.8"
        self.noise_scale = "0.667"
        self.use_threading = "True"
        self.voice_model = "BT7274"
        
        self.load_model()
        self.load_configs()
    
    def load_model(self):
       
        if(os.path.isdir(MODEL_FOLDER)):
           print("Model exists!") 
        else:
            print("Downloading model...")
            os.mkdir(MODEL_FOLDER)
            Repo.clone_from(self.model_url, MODEL_FOLDER)
            print("Model")
            
        self.copy_model_to_piper()
            
    def copy_model_to_piper(self):
        path_to_model = f"{VOICE_MODEL}{self.voice_model}/{self.voice_model}.onnx"
        path_to_model_json = path_to_model+".json"
        
        if(not os.path.isfile(f"{PIPER_FOLDER}/{self.voice_model}.onnx")):
            print("Moved model to piper")
            shutil.copyfile(path_to_model,f"{PIPER_FOLDER}/{self.voice_model}.onnx")
        
        if(not os.path.isfile(f"{PIPER_FOLDER}/{self.voice_model}.onnx.json")):
            print("Moved model config to piper")
            shutil.copyfile(path_to_model_json,f"{PIPER_FOLDER}/{self.voice_model}.onnx.json")
    
    def load_configs(self):
        settings = open("settings.cfg").readlines()
        
        print("\nLoading settings!\n")
        for s in settings:
            args = s.split("=")
            value = args[1].split("#")[0].strip()
            print(f"Setting {args[0]} with {value}")
            self.__setattr__(args[0].strip(),value)
        print("\nSettings loaded!\n")
            
    def run_script(self):
        try:
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path], check=True)
            print("Audio file generated successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while running the script: {e}")

    def generate_text(self, text : str) :
        text = text.strip()
        filename = ""
        if(text[-1] == "."):
            # print("Last character is dot")
            filename = text[:-1]
        else:
            filename = text
        
        new_script = f"""
        cd "./piper"
        echo '{text}' | ./piper --model {self.voice_model}.onnx --output_file ../output/"{filename}".wav --length_scale {float(self.speech_rate)} --noise_w {float(self.phoneme_variability)} --noise_scale {float(self.noise_scale)}
        """
        
        open(script_path,mode='w').write(new_script)
        self.run_script()
        
    def run(self):
        lines = []
        file = open("voicelines.txt",'r')
        
        first_line = file.readline()
        if(first_line[0] != "#"):
            lines.append(first_line)
        
        lines.extend(file.readlines())
        
        threads = []
        
        for line in lines:
            args = line.split("|")
            print(f"\nGenerating line: {args[0]}")

            if(self.use_threading == "True"):
                t = threading.Thread(target=self.generate_text,args=(line,))
                t.start()
                threads.append(t)
            else:
                self.generate_text(line)
        
        if(self.use_threading == "True"):
            for t in threads:
                t.join()
        
voiceModel = VoiceSynth()
voiceModel.run()

