from discord import DiscordException
import wave
import logging
import os
import threading
import time
import subprocess
import sys
import struct
import io
from pydub import AudioSegment
import wave
from ..core import try_exc
_log = logging.getLogger(__name__)

__all__ = (
    "Filters",
    "Sink",
    "AudioData",
    "RawData",
)

class SinkException(DiscordException):
    pass

if sys.platform != "win32":
    CREATE_NO_WINDOW = 0
else:
    CREATE_NO_WINDOW = 0x08000000

default_filters = {
    "time": 0,
    "users": [],
    "max_size": 0,
}


class Filters:
    """Filters for sink
    .. versionadded:: 2.0

    Parameters
    ----------
    interface: :meth:`Filters.interface`

    """

    def __init__(self, **kwargs):
        self.filtered_users = kwargs.get("users", default_filters["users"])
        self.seconds = kwargs.get("time", default_filters["time"])
        self.max_size = kwargs.get("max_size", default_filters["max_size"])
        self.finished = False

    @staticmethod
    def interface(func):  # Contains all filters
        def _filter(self, data, user):
            if not self.filtered_users or user in self.filtered_users:
                return func(self, data, user)

        return _filter

    def init(self):
        if self.seconds != 0:
            thread = threading.Thread(target=self.wait_and_stop)
            thread.start()

    def wait_and_stop(self):
        time.sleep(self.seconds)
        if self.finished:
            return
        self.vc.stop_listening()


class RawData:
    """Handles raw data from Discord so that it can be decrypted and decoded to be used.

    .. versionadded:: 2.0
    """

    def __init__(self, data, client):
        self.data = bytearray(data)
        self.client = client

        self.header = data[:12]
        self.data = self.data[12:]

        unpacker = struct.Struct(">xxHII")
        self.sequence, self.timestamp, self.ssrc = unpacker.unpack_from(self.header)
        self.decrypted_data = getattr(self.client, "_decrypt_" + self.client.mode)(
            self.header, self.data
        )
        self.decoded_data = None

        self.user_id = None


class AudioData:
    """Handles data that's been completely decrypted and decoded and is ready to be saved to file.

    .. versionadded:: 2.0
    Raises
    ------
    ClientException
        The AudioData is already finished writing,
        The AudioData is still writing
    """

    def __init__(self, file):
        self.file_name = None
        if isinstance(file, io.BytesIO):
            self.file = file
        else:
            self.file = open(file, "ab")
            self.dir_path = os.path.split(file)[0]
            self.file_name = self.file.name

        self.finished = False

        self.recording = None

    def write(self, data):
        if self.finished:
            raise SinkException("The AudioData is already finished writing.")
        try:
            self.file.write(data)
        except ValueError:
            pass

    def cleanup(self):
        if self.finished:
            raise SinkException("The AudioData is already finished writing.")
        self.finished = True
        if not isinstance(self.file, io.BytesIO):
            self.file.close()
            # self.file_name = os.path.join(self.dir_path, self.file_name)


    def on_format(self, encoding):
        if not self.finished:
            raise SinkException("The AudioData is still writing.")
        # name = os.path.split(self.file)[1]
        # name = name.split(".")[0] + f".{encoding}"
        self.file_name = f'{self.file_name[:self.file_name.rfind(".")]}.{encoding}'


class Sink(Filters):
    """A Sink "stores" all the audio data.
    .. versionadded:: 2.0
    Parameters
    ----------
    encoding: :class:`string`
        The encoding to use. Valid types include wav, mp3, and pcm (even though it's not an actual encoding).
    output_path: :class:`string`
        A path to where the audio files should be output.

    Raises
    ------
    ClientException
        An invalid encoding type was specified.
        Audio may only be formatted after recording is finished.
    """

    valid_encodings = [
        "wav",
        "mp3",
        "pcm",
    ]

    def __init__(self, *, encoding="wav", output_path="", hide_input=True, hide_output=False, save_as_bytes=False, filters=None):
        if filters is None:
            filters = default_filters
        self.filters = filters
        Filters.__init__(self, **self.filters)

        encoding = encoding.lower()

        if encoding not in self.valid_encodings:
            raise SinkException("An invalid encoding type was specified.")

        self.encoding = encoding
        self.file_path = output_path
        self.vc = None
        self.audio_data = {}

        self._save_as_bytes = save_as_bytes
        self.hide_output = hide_output
        self.hide_input = hide_input

    def init(self, vc):  # called under listen
        self.vc = vc
        super().init()

    @Filters.interface
    def write(self, data, user):
        if user not in self.audio_data:
            ssrc = self.vc.get_ssrc(user)
            file = io.BytesIO() if self._save_as_bytes else os.path.join(self.file_path, f"{ssrc}.pcm")
            self.audio_data.update({user: AudioData(file)})

        file = self.audio_data[user]
        file.write(data)

    def cleanup(self):
        self.finished = True
        for file in self.audio_data.values():
            file.cleanup()
            self.format_audio(file)

    def format_audio(self, audio):
        out_path = ''
        if self.vc.recording:
            raise SinkException(
                "Audio may only be formatted after recording is finished."
            )
        if self.encoding == "pcm":
            return
        if self.encoding == "mp3":
            out_path = audio.file_name[:audio.file_name.rfind(".")] + ".mp3"
            args = [
                "ffmpeg",
                "-f",
                "s16le",
                "-ar",
                "48000",
                "-ac",
                "2",
                "-i",
                audio.file_name,
                out_path,
            ]
            process = None
            if os.path.exists(out_path):
                os.remove(
                    out_path
                )  # process will get stuck asking whether or not to overwrite, if file already exists.
            try:
                process = subprocess.Popen(args, creationflags=CREATE_NO_WINDOW)
            except FileNotFoundError:
                raise SinkException("ffmpeg was not found.") from None
            except subprocess.SubprocessError as exc:
                raise SinkException(
                    "Popen failed: {0.__class__.__name__}: {0}".format(exc)
                ) from exc
            process.wait()
        elif self.encoding == "wav":
            with open(audio.file, "rb") as pcm:
                data = pcm.read()

            out_path = audio.file_name[:audio.file_name.rfind(".")] + ".wav"
            with wave.open(out_path, "wb") as f:
                f.setnchannels(self.vc.decoder.CHANNELS)
                f.setsampwidth(self.vc.decoder.SAMPLE_SIZE // self.vc.decoder.CHANNELS)
                f.setframerate(self.vc.decoder.SAMPLING_RATE)
                f.writeframes(data)

        with open(out_path, "rb") as out:
            audio.recording = out.read()

        if self.hide_output:
            try_exc(os.remove, out_path)
        if self.hide_input:
            try_exc(os.remove, audio.file_name)
        audio.on_format(self.encoding)

class VirtualSink(Filters):
    """A Sink "stores" all the audio data.
    .. versionadded:: 2.0
    Parameters
    ----------
    encoding: :class:`string`
        The encoding to use. Valid types include wav, mp3, and pcm (even though it's not an actual encoding).
    output_path: :class:`string`
        A path to where the audio files should be output.

    Raises
    ------
    ClientException
        An invalid encoding type was specified.
        Audio may only be formatted after recording is finished.
    """

    valid_encodings = [
        "pcm",
        "wav",
        "mp3"
    ]

    def __init__(self, *, encoding="wav", conv_file='out/rec', hide_output=True, filters=None):
        if filters is None:
            filters = default_filters
        self.filters = filters
        Filters.__init__(self, **self.filters)

        encoding = encoding.lower()

        if encoding not in self.valid_encodings:
            raise SinkException("An invalid encoding type was specified.")

        self.encoding = encoding
        self.vc = None
        self.audio_data = {}
        self.conv_file = conv_file
        self.hide_output = hide_output

    def init(self, vc):  # called under listen
        self.vc = vc
        super().init()

    @Filters.interface
    def write(self, data, user):
        if user not in self.audio_data:
            file = io.BytesIO()
            self.audio_data.update({user: file})

        self.audio_data[user].write(data)

    def cleanup(self):
        self.finished = True
        for v in list(self.audio_data.values()):
            v.seek(0, 0)
            if self.encoding != 'pcm':
                with open(self.conv_file + '.pcm', 'wb') as f:
                    f.write(v.read())
                self.format_audio()

    def format_audio(self, in_path=None, out_path=None):
        in_path = in_path if in_path else self.conv_file
        if not in_path.endswith('.pcm'):
            in_path += '.pcm'
        out_path = out_path if out_path else f"{self.conv_file}.{self.encoding}"
        if self.vc.recording:
            raise SinkException(
                "Audio may only be formatted after recording is finished."
            )
        if self.encoding == "pcm":
            return
        if self.encoding == "mp3":
            args = [
                "ffmpeg",
                "-f",
                "s16le",
                "-ar",
                "48000",
                "-ac",
                "2",
                "-i",
                in_path,
                out_path,
            ]
            process = None
            if os.path.exists(out_path):
                os.remove(
                    out_path
                )  # process will get stuck asking whether or not to overwrite, if file already exists.
            try:
                process = subprocess.Popen(args, creationflags=CREATE_NO_WINDOW)
            except FileNotFoundError:
                raise SinkException("ffmpeg was not found.") from None
            except subprocess.SubprocessError as exc:
                raise SinkException(
                    "Popen failed: {0.__class__.__name__}: {0}".format(exc)
                ) from exc
            process.wait()
        elif self.encoding == "wav":
            with open(in_path, "rb") as pcm:
                data = pcm.read()
                pcm.close()

            with wave.open(out_path, "wb") as f:
                f.setnchannels(self.vc.decoder.CHANNELS)
                f.setsampwidth(self.vc.decoder.SAMPLE_SIZE // self.vc.decoder.CHANNELS)
                f.setframerate(self.vc.decoder.SAMPLING_RATE)
                f.writeframes(data)

        os.remove(in_path)
        r = open(out_path, 'rb').read()
        if self.hide_output:
            os.remove(out_path)
        return r