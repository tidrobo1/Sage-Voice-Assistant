import queue
import threading
from typing import Callable


class MuteableAudioInterface:
    """Custom audio interface with mute/unmute functionality."""

    INPUT_FRAMES_PER_BUFFER = 4000  # 250ms @ 16kHz
    OUTPUT_FRAMES_PER_BUFFER = 1000  # 62.5ms @ 16kHz

    def __init__(self):
        try:
            import pyaudio
        except ImportError:
            raise ImportError("To use MuteableAudioInterface you must install pyaudio.")
        self.pyaudio = pyaudio
        self.is_muted = True  # Start muted until user clicks mic

    def start(self, input_callback: Callable[[bytes], None]):
        self.input_callback = input_callback

        # Audio output is buffered so we can handle interruptions.
        self.output_queue: queue.Queue[bytes] = queue.Queue()
        self.should_stop = threading.Event()
        self.output_thread = threading.Thread(target=self._output_thread)

        self.p = self.pyaudio.PyAudio()
        self.in_stream = self.p.open(
            format=self.pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            stream_callback=self._in_callback,
            frames_per_buffer=self.INPUT_FRAMES_PER_BUFFER,
            start=True,
        )
        self.out_stream = self.p.open(
            format=self.pyaudio.paInt16,
            channels=1,
            rate=16000,
            output=True,
            frames_per_buffer=self.OUTPUT_FRAMES_PER_BUFFER,
            start=True,
        )

        self.output_thread.start()

    def stop(self):
        self.should_stop.set()
        self.output_thread.join()
        self.in_stream.stop_stream()
        self.in_stream.close()
        self.out_stream.close()
        self.p.terminate()

    def output(self, audio: bytes):
        self.output_queue.put(audio)

    def interrupt(self):
        try:
            while True:
                _ = self.output_queue.get(block=False)
        except queue.Empty:
            pass

    def mute(self):
        """Stop sending audio to the API (stream keeps running but data is ignored)."""
        self.is_muted = True

    def unmute(self):
        """Resume sending audio to the API."""
        self.is_muted = False

    def _output_thread(self):
        while not self.should_stop.is_set():
            try:
                audio = self.output_queue.get(timeout=0.25)
                self.out_stream.write(audio)
            except queue.Empty:
                pass

    def _in_callback(self, in_data, frame_count, time_info, status):
        # Only send audio data if not muted
        if self.input_callback and not self.is_muted:
            self.input_callback(in_data)
        return (None, self.pyaudio.paContinue)
