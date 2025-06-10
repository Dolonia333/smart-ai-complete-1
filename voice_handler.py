import speech_recognition as sr
import pyttsx3
import threading
import time
from typing import Optional, Callable

class VoiceHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.listening = False
        self.setup_tts()
        self.calibrate_microphone()
    
    def setup_tts(self):
        """Configure text-to-speech settings"""
        voices = self.tts_engine.getProperty('voices')
        if voices:
            # Use first available voice
            self.tts_engine.setProperty('voice', voices[0].id)
        self.tts_engine.setProperty('rate', 180)  # Speed
        self.tts_engine.setProperty('volume', 0.9)  # Volume
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            print("Calibrating microphone for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Microphone calibrated.")
        except Exception as e:
            print(f"Microphone calibration failed: {e}")
    
    def speak(self, text: str):
        """Convert text to speech"""
        try:
            print(f"Speaking: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"TTS error: {e}")
    
    def listen_once(self, timeout: int = 5) -> Optional[str]:
        """Listen for a single voice command"""
        try:
            print("Listening...")
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            print("Processing speech...")
            text = self.recognizer.recognize_google(audio)
            print(f"Heard: {text}")
            return text
            
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return None
        except sr.WaitTimeoutError:
            print("Listening timeout")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def listen_continuously(self, callback: Callable[[str], None], wake_word: str = "assistant"):
        """Listen continuously for wake word and commands"""
        print(f"Listening continuously for wake word: '{wake_word}'")
        self.listening = True
        
        while self.listening:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
                text = self.recognizer.recognize_google(audio).lower()
                print(f"Heard: {text}")
                
                if wake_word.lower() in text:
                    self.speak("Yes, how can I help you?")
                    command = self.listen_once(timeout=10)
                    if command:
                        callback(command)
                
            except (sr.UnknownValueError, sr.WaitTimeoutError):
                continue
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
                time.sleep(1)
            except Exception as e:
                print(f"Unexpected error in continuous listening: {e}")
                time.sleep(1)
    
    def start_listening_background(self, callback: Callable[[str], None], wake_word: str = "assistant"):
        """Start continuous listening in background thread"""
        thread = threading.Thread(target=self.listen_continuously, args=(callback, wake_word))
        thread.daemon = True
        thread.start()
        return thread
    
    def stop_listening(self):
        """Stop continuous listening"""
        self.listening = False
        print("Voice listening stopped.")
    
    def test_voice_system(self):
        """Test voice input and output"""
        self.speak("Voice system test. Please say something.")
        result = self.listen_once()
        if result:
            self.speak(f"I heard you say: {result}")
            return True
        else:
            self.speak("Voice test failed.")
            return False
