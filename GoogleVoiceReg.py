from google.cloud import speech_v1
from google.cloud import speech_v1p1beta1
from google.cloud.speech_v1 import enums
import io
import argparse
import os


def sample_recognize(local_file_path):
    """
    Transcribe a short audio file using synchronous speech recognition

    Args:
      local_file_path Path to local audio file, e.g. /path/audio.wav
    """

    client = speech_v1.SpeechClient()

    # local_file_path = 'resources/brooklyn_bridge.raw'

    # The language of the supplied audio
    language_code = "en-US"

    # Sample rate in Hertz of the audio data sent
    sample_rate_hertz = 44100
    # audio_channel_count=2
    # enableSeparateRecognitionPerChannel = True

    # Encoding of audio data sent. This sample sets this explicitly.
    # This field is optional for FLAC and WAV audio formats.
    encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16
    config = {
        "language_code": language_code,
        "sample_rate_hertz": sample_rate_hertz,
        "encoding": encoding,
    }
    with io.open(local_file_path, "rb") as f:
        content = f.read()
    audio = {"content": content}

    response = client.recognize(config, audio)
    for result in response.results:
        # First alternative is the most probable result
        alternative = result.alternatives[0]
        print(u"Transcript: {}".format(alternative.transcript))


def sample_long_running_recognize(local_file_path):
    """
    Print confidence level for individual words in a transcription of a short audio
    file
    Separating different speakers in an audio file recording

    Args:
      local_file_path Path to local audio file, e.g. /path/audio.wav
    """

    client = speech_v1p1beta1.SpeechClient()

    # local_file_path = 'resources/commercial_mono.wav'

    # If enabled, each word in the first alternative of each result will be
    # tagged with a speaker tag to identify the speaker.
    enable_speaker_diarization = True

    # Optional. Specifies the estimated number of speakers in the conversation.
    diarization_speaker_count = 2
    sample_rate_hertz = 44100

    # The language of the supplied audio
    language_code = "en-US"
    config = {
        # "enable_speaker_diarization": enable_speaker_diarization,
        # "diarization_speaker_count": diarization_speaker_count,
        "language_code": language_code,
        # "sample_rate_hertz": sample_rate_hertz,
    }
    with io.open(local_file_path, "rb") as f:
        content = f.read()
    audio = {"content": content}

    operation = client.long_running_recognize(config, audio)

    print(u"Waiting for operation to complete...")
    response = operation.result()
    print("The number of responses is "+str(len(response.results)))

    for result in response.results:
        count = 0
        # First alternative has words tagged with speakers
        alternative = result.alternatives[0]
        print("The number of words is "+str(len(alternative.words)))
        print(u"Transcript: {}".format(alternative.transcript))
        # Print the speaker_tag of each word
        for word in alternative.words:
            print(u"Word - {}: {}".format(count,word.word))
            # print(u"Speaker tag: {}".format(word.speaker_tag))
            count =count + 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, default="morning.wav", help="File you want to transcript")
    args = parser.parse_args()

    filepath = args.file
    # sample_recognize(filepath)

    direc = "/home/p2baghae/Downloads/Studies/S7"
    for root, dirs, files in os.walk(direc):
        for file in files:
            if file.endswith(".m4a"):
                filename = os.path.join(root, file)
                # print(filename)
                if file != "audio_only_1.m4a": # include only files which contain at least 1 pedestrian
                    if file != "audio_only.m4a": # include only files which contain at least 1 pedestrian
                        if not "Gamma" in filename:
                            if not "Parastoo" in filename:
                                print(filename)
                                print("-------------------------------------------------------------------------------------------")
                                sample_long_running_recognize(filename)