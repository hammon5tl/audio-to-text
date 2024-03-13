import speech_recognition as sr
from pydub import AudioSegment
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import os

class App:
    def __init__(self):
        self.root = Tk()
        self.root.title("Audio To Text")
        self.root.minsize(575, 350)

        self.buttons_frame = Frame(self.root)
        self.buttons_frame.grid(row=0, column=0, padx=7, pady=10, sticky=W+E)

        self.add_button = Button(self.buttons_frame, text="Add New Audio File", command=lambda : self.add_audio_file())
        self.add_button.grid(row=0, column=0, padx=3)
        self.convert_button = Button(self.buttons_frame, text="Convert To Text", command=lambda : self.convert_audio_to_text(self.file_list.get(ANCHOR)))
        self.convert_button.config(state=DISABLED)
        self.convert_button.grid(row=0, column=1, padx=3)
        self.save_button = Button(self.buttons_frame, text="Save Text", command=lambda : self.save_text_file(self.text_area.get(1.0, END)))
        self.save_button.config(state=DISABLED)
        self.save_button.grid(row=0, column=2, padx=3)

        self.areas_frame = Frame(self.root)
        self.areas_frame.grid(row=1, column=0, padx=10, pady=16, sticky=E+W+N+S)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.areas_frame.rowconfigure(0, weight=1)
        self.areas_frame.columnconfigure(0, weight=1)
        self.areas_frame.columnconfigure(1, weight=1)

        self.file_list = Listbox(self.areas_frame)
        self.file_list.grid(row=0, column=0, padx=3, sticky=N+S+E+W)

        self.text_area = Text(self.areas_frame)
        self.text_area.config(font=("consolas", 12), state=DISABLED, wrap=WORD)
        self.text_area.grid(row=0, column=1, padx=3, sticky=N+S+E+W)

        self.map_file_to_text = {}

        self.file_list.bind("<<ListboxSelect>>", lambda e: self.listbox_bind_trigger())
        self.text_area.bind("<<Modified>>", lambda e: self.text_area_bind_trigger())
        
        
    def listbox_bind_trigger(self):
        if self.file_list.get(ANCHOR):
            self.convert_button.config(state=NORMAL)
            if self.map_file_to_text[self.file_list.get(ANCHOR)]:
                self.update_text_area(self.map_file_to_text[self.file_list.get(ANCHOR)])
            else:
                self.update_text_area("")
        else:
            self.convert_button.config(state=DISABLED)
            self.update_text_area("")
    
    def text_area_bind_trigger(self):
        if len(self.text_area.get(1.0,END)) > 0:
            self.save_button.config(state=NORMAL)
        else:
            self.save_button.config(state=DISABLED)
        
    def convert_audio_to_text(self, audio_file):
        self.root.grab_set()
        recognizer = sr.Recognizer()
        deleteConvertedFile = False
        og_name = audio_file

        if not audio_file.endswith('.wav'):
            output_file = audio_file + '.wav'
            try:
                self.convert_to_wav(audio_file, output_file)
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while converting the file: {e}")
                self.root.grab_release()
                return
            audio_file = output_file
            deleteConvertedFile = True
        
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio, language='it-IT')
            if text:
                self.map_file_to_text[og_name] = text
                self.update_text_area(text)
        except sr.UnknownValueError:
            messagebox.showwarning("Warning", "Google Speech Recognition could not understand the audio")
        except sr.RequestError as e:
            messagebox.showerror("Error", f"Could not request results from Google Speech Recognition service; {e}")
        
        if deleteConvertedFile:
            os.remove(audio_file)
        self.root.grab_release()

    def update_text_area(self, text):
        self.text_area.configure(state=NORMAL)
        self.text_area.delete(1.0, END)
        self.text_area.insert(END, text)
        self.text_area.configure(state=DISABLED)
    
    def convert_to_wav(self, input_file, output_file):
        audio = AudioSegment.from_file(input_file)
        audio.export(output_file, format='wav')

    def add_audio_file(self):
        self.root.grab_set()
        audio_file = filedialog.askopenfilename(filetypes=[
            ("Audio Files", "*.wav"),
            ("Audio Files", "*.mp3"),
            ("Audio Files", "*.ogg"),
            ("Audio Files", "*.flac"),
            ("Audio Files", "*.wma"),
            ("Audio Files", "*.m4a"),
            ("Audio Files", "*.aiff"),
            ("Audio Files", "*.aif"),
            ("Audio Files", "*.aac"),
            ],
            title="Select an audio file")
        if audio_file:
            self.file_list.insert(END, audio_file)
            self.map_file_to_text[audio_file] = ""
        self.root.grab_release()
    
    def save_text_file(self, body):
        self.root.grab_set()
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")], title="Save the text file")

        if file_path:
            with open(file_path, "w") as file:
                file.write(body)
        
        self.root.grab_release()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()