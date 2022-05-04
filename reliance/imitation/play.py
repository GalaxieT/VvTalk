from pyaudio import PyAudio
import wave
from audiotsm2 import phasevocoder
from audiotsm2.io.wav import WavReader, WavWriter
import threading as trd


class Player:
    def __init__(self, fn='speech.wav'):
        self.fileName = fn
        self.alteredName = 'resources/temp_altered.wav'
        self.speed_rate = 0.5
        self.play_flag = False
        self.natural_end = False

    def _play(self):
        self.natural_end = True
        chunk = 1024
        wf = wave.open(self.alteredName, 'rb')
        p = PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        data = wf.readframes(chunk)
        while len(data) > 0 and self.play_flag:
            stream.write(data)
            data = wf.readframes(chunk)
        self.play_flag = False
        stream.stop_stream()
        stream.close()
        p.terminate()

    def start(self):
        trd.Thread(target=self._play).start()
        self.play_flag = True

    def stop(self):
        self.play_flag = False
        self.natural_end = False

    def set_speed(self, speed=1.0):
        self.speed_rate = speed
        with WavReader(self.fileName) as reader:
            with WavWriter(self.alteredName, reader.channels, reader.samplerate) as writer:
                phasevocoder(reader.channels, speed=self.speed_rate).run(reader, writer)



if __name__ == "__main__":
    p = Player()
    p.set_speed(0.5)
    p.start()
