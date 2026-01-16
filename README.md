# Sage - Voice Virtual Assistant

A voice-powered AI assistant built with ElevenLabs Conversational AI and Flask.

## Features

- Real-time voice conversation with AI
- Clean web interface with animated microphone button
- Live chat transcript display
- Push-to-talk functionality

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/sage-voice-assistant.git
cd sage-voice-assistant
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
brew install portaudio  # macOS only
pip install elevenlabs "elevenlabs[pyaudio]" python-dotenv flask flask-socketio
```

### 4. Set up ElevenLabs
1. Create an account at [ElevenLabs](https://elevenlabs.io)
2. Go to Conversational AI → Agents → Create a new agent
3. Get your Agent ID and API Key

### 5. Create a `.env` file
```
AGENT_ID=your_agent_id_here
API_KEY=your_api_key_here
```

### 6. Run the app
```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Usage

1. Click the microphone button to start talking to Sage
2. Speak naturally - Sage will respond with voice
3. Click the microphone again to end the conversation

## Tech Stack

- **Backend**: Python, Flask, Flask-SocketIO
- **Frontend**: HTML, CSS, JavaScript
- **Voice AI**: ElevenLabs Conversational AI
- **Real-time Communication**: WebSockets
