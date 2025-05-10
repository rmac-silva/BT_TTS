import subprocess
import time
import os
import shutil
import threading
from git import Repo

script_path = os.path.abspath(__file__)[:-7]

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
        self.num_threads = "4"
        
        self.transcript = "voicelines.csv"
        
        self.voice_model = "BT7274"
        
        self.load_model()
        self.copy_model_to_piper()
        self.load_configs()

        self.check_config()
        
        
        #Saves the Thread | Index combo
        self.ACTIVE_THREADS = {}
        
        #Busy files
        self.BUSY_FILES = []
    
        
    def load_model(self):
       
        if(os.path.isdir(MODEL_FOLDER)):
           print("Model exists!") 
        else:
            print("Downloading model...")
            os.mkdir(MODEL_FOLDER, exist_ok = True)
            Repo.clone_from(self.model_github, MODEL_FOLDER)
            print("Model")
            
        
        
    def check_config(self):
        """Checks if the script is in running condition, checking various conditions. If any fails, an error is thrown.
        """
        print("\nChecking script state...\n")
        
        #Check if output folder exists
        if(not os.path.isdir("output")):
            print("Output folder was missing, creating...")
            os.mkdir("output")
            print("Folder created!")
            
        #Check if model .onnx exists
        if(not os.path.isfile(f"{PIPER_FOLDER}/{self.voice_model}.onnx")):
            print(f"{self.voice_model}.onnx file is missing in piper! Please launch main.py again or drag it manually to the piper folder.")
        if(not os.path.isfile(f"{PIPER_FOLDER}/{self.voice_model}.onnx.json")):
            print(f"{self.voice_model}.onnx.JSON file is missing in piper! Please launch main.py again or drag it manually to the piper folder.")
            
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
        """Loads the settings from settings.cfg, uses setAttr on the main class.
        """
        
        settings = open("settings.cfg").readlines()
        
        print("\nLoading settings!\n")
        for s in settings:
            if(s.strip() == "" or s is None):
                continue
            else:
                args = s.split("=")
                value = args[1].split("#")[0].strip()
                print(f"Setting {args[0]} with {value}")
                self.__setattr__(args[0].strip(),value)
        print("\nSettings loaded!\n")
            
    def run_script(self, index):
        """Runs the voice generation, creating powershell scripts to call piper."""
        
        try:
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", f"{script_path}script{index}.ps1"], check=True,stdout = subprocess.DEVNULL)#
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while running the script: {e}")

    def generate_text(self, text : str, filename : str, thread_index : int) :
        text = text.strip()
        
        #Script name is script1.ps1 for thread 1, script2.ps1 for thread 2 etc...
        script_name = f"script{thread_index}.ps1"
        
        #Create the powershell script, or open it if it already exists
        if(os.path.isfile(script_name)):
            script = open(script_name,'w')
        else:
            script = open(script_name,'x')
        
        new_script = f"""
        cd "./piper"
        echo "{text}" | ./piper --model {self.voice_model}.onnx --output_file ../output/"{"" if(filename == text) else filename.strip() + "_"}{text[:-1]}".wav --length_scale {float(self.speech_rate)} --noise_w {float(self.phoneme_variability)} --noise_scale {float(self.noise_scale)}
        """
        #Write the script to the file
        script.write(new_script)
        script.close()
        #Run it
        self.run_script(thread_index)
        
        print(f"\nVoice line {text} generated as {filename}.wav in output folder!")
        self.BUSY_FILES[thread_index] = False
        
    
    def get_transcript(self):
        try:
            file = open(f"transcripts/{self.transcript}",'r')
            return file
        except FileNotFoundError:
            print(f"Error! Transcript file not found under transcripts/{self.transcript}")
        
    def get_next_available_file(self):
        for i in range(0,len(self.BUSY_FILES)):
            if self.BUSY_FILES[i] == False:
                return i

        return -1
        
    def run(self):
        lines = []
        
        file = self.get_transcript()
        
        lines.extend(file.readlines())
        
        
        
        if(self.use_threading):
            for i in range (0,int(self.num_threads)):
                self.BUSY_FILES.append(False)
        
        #Vars
        text_column = 1
        line_index = 0
        
        #States
        valid_line = True
        processed_line = True
        
        
        while line_index < len(lines):
            processed_line = True
            valid_line = True
            
            #Read line
            line = lines[line_index].strip()
            
            #Check for comments
            if(line[0] == "!" and line[1] == "#"):
                valid_line = False
            
            #Check for DEFs
            if(line[0:3] == "DEF"):
                text_column = int(line.split(":")[1].split("#")[0].strip())
                valid_line = False
            
            # It's a valid text line
            if(valid_line):
                args = line.split("|")
                print(f"\nGenerating line: {line}")

                #Sets the filename variable, if there are multiple columns uses the first
                if(text_column == 1):
                    text = args[0]
                    filename = args[0]
                else:
                    text = args[text_column-1]
                    filename = args[0]
                
                if(self.use_threading == "True"):
                    
                    file_index = self.get_next_available_file() # Gets a free file
                    
                    if(file_index != -1):
                        self.BUSY_FILES[file_index] = True #Mark the file as busy
                        
                        t = threading.Thread(target=self.generate_text,args=(text,filename,file_index))
                        t.start()
                        
                    else:
                        time.sleep(1)
                        processed_line = False
                else: #Non-paralel, generates each text one at a time
                    self.generate_text(text,filename,1)
            
            if(processed_line):
                line_index += 1

        
voiceModel = VoiceSynth()
voiceModel.run()

