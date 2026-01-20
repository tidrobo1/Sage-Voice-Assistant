import os
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from muteable_audio import MuteableAudioInterface

load_dotenv()

AGENT_ID = os.getenv("AGENT_ID")
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sage-voice-assistant'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global conversation and audio interface
conversation = None
audio_interface = None

def on_agent_response(response):
    """Called when Sage speaks - send to browser"""
    socketio.emit('sage_message', {'text': response})
    socketio.emit('sage_speaking', {'speaking': True})

def on_agent_response_correction(original, corrected):
    """Called when Sage is interrupted"""
    socketio.emit('sage_message', {'text': corrected, 'interrupted': True})

def on_user_transcript(transcript):
    """Called when user speaks - send to browser"""
    socketio.emit('user_message', {'text': transcript})

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """When browser connects, just acknowledge - don't start listening yet"""
    emit('status', {'message': 'Ready to connect to Sage'})

@socketio.on('start_conversation')
def handle_start_conversation():
    """When user clicks mic, start the conversation session (but muted)"""
    global conversation, audio_interface

    if conversation is None:
        client = ElevenLabs(api_key=API_KEY)
        audio_interface = MuteableAudioInterface()

        conversation = Conversation(
            client,
            AGENT_ID,
            requires_auth=True,
            audio_interface=audio_interface,
            callback_agent_response=on_agent_response,
            callback_agent_response_correction=on_agent_response_correction,
            callback_user_transcript=on_user_transcript,
        )

        conversation.start_session()
        emit('status', {'message': 'Connected to Sage'})

@socketio.on('unmute')
def handle_unmute():
    """When user clicks mic to start talking"""
    global audio_interface
    if audio_interface:
        audio_interface.unmute()
        emit('status', {'message': 'Listening...'})

@socketio.on('mute')
def handle_mute():
    """When user clicks mic to stop talking"""
    global audio_interface
    if audio_interface:
        audio_interface.mute()
        emit('status', {'message': 'Muted'})

@socketio.on('end_conversation')
def handle_end_conversation():
    """When user ends the conversation completely"""
    global conversation, audio_interface
    if conversation:
        try:
            conversation.end_session()
            conversation.wait_for_session_end()
        except Exception as e:
            print(f"Error ending session: {e}")
        conversation = None
        audio_interface = None
        emit('status', {'message': 'Disconnected from Sage'})

@socketio.on('disconnect')
def handle_disconnect():
    """When browser disconnects, end the conversation"""
    global conversation, audio_interface
    if conversation:
        try:
            conversation.end_session()
            conversation.wait_for_session_end()
        except Exception as e:
            print(f"Error ending session on disconnect: {e}")
        conversation = None
        audio_interface = None

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
