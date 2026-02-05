"""Voice recorder component for browser-based audio capture."""

import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, Any


def render_voice_recorder() -> Optional[bytes]:
    """
    Render a voice recorder component.

    Returns:
        Recorded audio data as bytes, or None if no recording
    """
    # Check if recording is in progress
    if 'recording' not in st.session_state:
        st.session_state.recording = False
    if 'audio_data' not in st.session_state:
        st.session_state.audio_data = None

    # Voice recorder HTML/JS component
    recorder_html = """
    <div id="voice-recorder" class="voice-recorder">
        <div style="text-align: center; margin-bottom: 1rem;">
            <h4>🎤 Voice Recorder</h4>
            <p>Click to start recording your voice for stress analysis</p>
        </div>

        <div style="text-align: center;">
            <button id="record-btn" class="record-btn">
                <span id="record-icon">🎤</span>
            </button>
            <div id="status" style="margin-top: 1rem; font-weight: bold;">Ready to record</div>
            <div id="timer" style="margin-top: 0.5rem; color: #666;">00:00</div>
        </div>

        <div id="visualizer" style="margin-top: 1rem; height: 60px; background: #f0f0f0; border-radius: 8px; display: none;"></div>

        <script>
            let mediaRecorder = null;
            let audioChunks = [];
            let isRecording = false;
            let startTime = null;
            let timerInterval = null;
            let stream = null;

            const recordBtn = document.getElementById('record-btn');
            const recordIcon = document.getElementById('record-icon');
            const statusDiv = document.getElementById('status');
            const timerDiv = document.getElementById('timer');
            const visualizer = document.getElementById('visualizer');

            // Check for browser support
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                statusDiv.textContent = 'Voice recording not supported in this browser';
                statusDiv.style.color = 'red';
                recordBtn.disabled = true;
                return;
            }

            recordBtn.addEventListener('click', async () => {
                if (!isRecording) {
                    await startRecording();
                } else {
                    stopRecording();
                }
            });

            async function startRecording() {
                try {
                    stream = await navigator.mediaDevices.getUserMedia({
                        audio: {
                            echoCancellation: true,
                            noiseSuppression: true,
                            autoGainControl: true,
                            sampleRate: 44100
                        }
                    });

                    mediaRecorder = new MediaRecorder(stream, {
                        mimeType: 'audio/webm;codecs=opus'
                    });

                    audioChunks = [];
                    isRecording = true;

                    mediaRecorder.ondataavailable = (event) => {
                        if (event.data.size > 0) {
                            audioChunks.push(event.data);
                        }
                    };

                    mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

                        // Convert to base64 for Streamlit
                        const reader = new FileReader();
                        reader.onload = () => {
                            const base64Data = reader.result.split(',')[1];

                            // Send to Streamlit via session state
                            window.parent.postMessage({
                                type: 'streamlit:setSessionState',
                                key: 'audio_data',
                                value: base64Data
                            }, '*');

                            window.parent.postMessage({
                                type: 'streamlit:setSessionState',
                                key: 'recording',
                                value: false
                            }, '*');
                        };
                        reader.readAsDataURL(audioBlob);

                        cleanup();
                    };

                    mediaRecorder.start(1000); // Collect data every second
                    startTime = Date.now();

                    // Update UI
                    recordBtn.classList.add('recording');
                    recordIcon.textContent = '⏹️';
                    statusDiv.textContent = 'Recording...';
                    statusDiv.style.color = '#EF5350';
                    visualizer.style.display = 'block';

                    // Start timer
                    timerInterval = setInterval(updateTimer, 1000);

                    // Start visualizer
                    startVisualizer();

                } catch (error) {
                    console.error('Recording failed:', error);
                    statusDiv.textContent = 'Recording failed: ' + error.message;
                    statusDiv.style.color = 'red';
                }
            }

            function stopRecording() {
                if (mediaRecorder && isRecording) {
                    mediaRecorder.stop();
                    isRecording = false;

                    // Update UI
                    recordBtn.classList.remove('recording');
                    recordIcon.textContent = '🎤';
                    statusDiv.textContent = 'Processing...';
                    statusDiv.style.color = '#FFA726';
                    clearInterval(timerInterval);
                }
            }

            function updateTimer() {
                if (startTime) {
                    const elapsed = Math.floor((Date.now() - startTime) / 1000);
                    const minutes = Math.floor(elapsed / 60).toString().padStart(2, '0');
                    const seconds = (elapsed % 60).toString().padStart(2, '0');
                    timerDiv.textContent = `${minutes}:${seconds}`;
                }
            }

            function startVisualizer() {
                if (!stream) return;

                const canvas = document.createElement('canvas');
                canvas.width = visualizer.offsetWidth;
                canvas.height = visualizer.offsetHeight;
                visualizer.innerHTML = '';
                visualizer.appendChild(canvas);

                const canvasCtx = canvas.getContext('2d');
                const analyser = new AnalyserNode(stream.context, {
                    fftSize: 256,
                    smoothingTimeConstant: 0.8
                });

                const source = new MediaStreamAudioSourceNode(stream, { mediaStream: stream });
                source.connect(analyser);

                const bufferLength = analyser.frequencyBinCount;
                const dataArray = new Uint8Array(bufferLength);

                function draw() {
                    if (!isRecording) return;

                    analyser.getByteFrequencyData(dataArray);

                    canvasCtx.fillStyle = 'rgb(240, 240, 240)';
                    canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

                    const barWidth = (canvas.width / bufferLength) * 2.5;
                    let barHeight;
                    let x = 0;

                    for (let i = 0; i < bufferLength; i++) {
                        barHeight = (dataArray[i] / 255) * canvas.height;

                        const gradient = canvasCtx.createLinearGradient(0, canvas.height - barHeight, 0, canvas.height);
                        gradient.addColorStop(0, '#00897B');
                        gradient.addColorStop(1, '#80CBC4');

                        canvasCtx.fillStyle = gradient;
                        canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);

                        x += barWidth + 1;
                    }

                    requestAnimationFrame(draw);
                }

                draw();
            }

            function cleanup() {
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                    stream = null;
                }
                clearInterval(timerInterval);
                visualizer.style.display = 'none';
            }

            // Handle page unload
            window.addEventListener('beforeunload', cleanup);
        </script>
    </div>
    """

    # Render the component
    components.html(recorder_html, height=300)

    # Handle recorded audio
    if st.session_state.get('audio_data'):
        audio_base64 = st.session_state.audio_data

        # Convert base64 to bytes
        import base64
        audio_bytes = base64.b64decode(audio_base64)

        # Clear the session state
        st.session_state.audio_data = None
        st.session_state.recording = False

        return audio_bytes

    return None
