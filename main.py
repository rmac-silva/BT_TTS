import subprocess
import threading
import os

script_path = os.path.abspath(__file__)[:-7] + "script.ps1"


class VoiceSynth():
    
    def __init__(self):
        self.speech_rate = "1.0"
        self.phoneme_variability = "0.8"
        self.noise_scale = "0.667"
        
        self.load_configs()
        
    def load_configs(self):
        settings = open("settings.cfg").readlines()
        
        print("\nLoading settings!\n")
        for s in settings:
            args = s.split("=")
            value = args[1].split("#")[0].strip()
            print(f"Setting {args[0]} with {value}\n")
            self.__setattr__(args[0].strip(),value)
            
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
        echo '{text}' | ./piper --model BT7274.onnx --output_file ../output/"{filename}".wav --length_scale {float(self.speech_rate)} --noise_w {float(self.phoneme_variability)} --noise_scale {float(self.noise_scale)}
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

            t = threading.Thread(target=self.generate_text,args=(line,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        
voiceModel = VoiceSynth()
voiceModel.run()