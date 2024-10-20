import asyncio
# This example uses the sounddevice library to get an audio stream from the
# microphone. It's not a dependency of the project but can be installed with
# `python -m pip install amazon-transcribe aiofile`
# `pip install sounddevice`.
import sounddevice
import os


from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

import os

os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
os.environ['AWS_SECRET_ACCESS_KEY'] = 'Yap24BM6wB5dvy1diDK+vdo8tO3Y61YGKCFjI3UD'
os.environ['AWS_SESSION_TOKEN'] = 'IQoJb3JpZ2luX2VjEAMaCXVzLWVhc3QtMSJGMEQCIEr8MvWGKZs5UnuhpbYMMeIt+STOmQYs0zQPHurWt9ZIAiBohsIt0+NfW+siBJSwdChsv7j8h6c2cNW/9+TcvOpYOCqZAghsEAAaDDQ5MTAzMzA2OTM0NiIM66Dp8oPWixyCubqTKvYBE8+Y37feWNyLCZLp7KHZfBFGNBmdkLn9qEOSxNHaSHLl3f07U3Gz4Qumf4qzJQrQRdtS5WhGQIsl8Yj7ctWa0E32vN2J1NA8Ja9Fvh247o555EIXWq5QeKzVOS+uafexuUi0a85lxEi+mhl4DGYQNJnS4LE6CPdUsAhWanM3+jutVmgUapvlMR8F2VuOgQG7kM2QJeu+xlpI++9wZjHuKEQvr/RluSWX7CAjoIKJkQLiYN7W85Qqd8N0DXgkO74o9+uQ5ZdzDsf/TtJtR7pTOot2lL6mWxE2QwyyXVlaL935PEFqszqyJi1g7NHb8GsqgfKyg/AUMKnf0bgGOp4Bj8oqp4SoNyHyrgw87j1jLimpbTSNcNV5eaO8M+Naf4LXzuj7t8zZDjHG6DQcfsWAZjesnOlCNR5Q/4trcGqUjjQoiuLSljPTPN16tUMGOl8xEjW8WSK0007aYjshGmcMJpwBFp3Gv6WyrG4S+M2hsKrnUr5jkViVC7gZldhXzUmongjkLHj4z120PZ5wcGoq8zlgRhva+ELlota7jpY='  # Only if using temporary credentials

class MyEventHandler(TranscriptResultStreamHandler):
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        # This handler can be implemented to handle transcriptions as needed.
        # Here's an example to get started.
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                if not result.is_partial:
                    print(f"{alt.transcript}")


async def mic_stream():
    # This function wraps the raw input stream from the microphone forwarding
    # the blocks to an asyncio.Queue.
    loop = asyncio.get_event_loop()
    input_queue = asyncio.Queue()

    def callback(indata, frame_count, time_info, status):
        loop.call_soon_threadsafe(input_queue.put_nowait, (bytes(indata), status))

    # Be sure to use the correct parameters for the audio stream that matches
    # the audio formats described for the source language you'll be using:
    # https://docs.aws.amazon.com/transcribe/latest/dg/streaming.html
    stream = sounddevice.RawInputStream(
        channels=1,
        samplerate=16000,
        callback=callback,
        blocksize=1024 * 2,
        dtype="int16",
    )
    # Initiate the audio stream and asynchronously yield the audio chunks
    # as they become available.
    with stream:
        while True:
            indata, status = await input_queue.get()
            yield indata, status


async def write_chunks(stream):
    # This connects the raw audio chunks generator coming from the microphone
    # and passes them along to the transcription stream.
    async for chunk, status in mic_stream():
        await stream.input_stream.send_audio_event(audio_chunk=chunk)
    await stream.input_stream.end_stream()


async def basic_transcribe():
    # Setup up our client with our chosen AWS region
    client = TranscribeStreamingClient(region="us-west-2")

    # Start transcription to generate our async stream
    stream = await client.start_stream_transcription(
        language_code="en-US",
        media_sample_rate_hz=16000,
        media_encoding="pcm"
    )

    # Instantiate our handler and start processing events
    handler = MyEventHandler(stream.output_stream)
    await asyncio.gather(write_chunks(stream), handler.handle_events())


asyncio.run(basic_transcribe())