import React, { useState, useRef, useEffect } from 'react'
import MeetingSources from './components/MeetingSources'
import './App.css'


interface TranscriptSegment {
  speaker: string
  text: string
  timestamp: number
}

interface MultiLangTranslations {
  [lang: string]: string
}

function App() {
  const [isRecording, setIsRecording] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected')
  const [targetLanguages, setTargetLanguages] = useState<string[]>(['vi'])
  const [transcript, setTranscript] = useState<TranscriptSegment[]>([])
  const [translations, setTranslations] = useState<Record<number, MultiLangTranslations>>({})
  const [activeTab, setActiveTab] = useState<'sources' | 'translation'>('translation')
  const [debugLog, setDebugLog] = useState<string[]>([])

  const websocketRef = useRef<WebSocket | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const processorRef = useRef<ScriptProcessorNode | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const audioBufferRef = useRef<Float32Array>(new Float32Array(0))
  const sendIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const chunkIdRef = useRef(0)
  const seenSegmentRef = useRef<Set<string>>(new Set())

  const languageNames: Record<string, string> = {
    vi: 'Vietnamese',
    en: 'English',
    ja: 'Japanese',
    zh: 'Chinese',
    ko: 'Korean'
  }

const sampleRate = 16000

// send ~5s chunks for better Whisper transcription quality
const bufferSeconds = 5
const bufferSize = sampleRate * bufferSeconds

  const encodeAudio = (audioData: Float32Array): string => {
    const buffer = new ArrayBuffer(audioData.length * 4)
    const view = new DataView(buffer)
    for (let i = 0; i < audioData.length; i++) {
      view.setFloat32(i * 4, audioData[i], true)
    }
    const bytes = new Uint8Array(buffer)
    let binary = ''
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i])
    }
    return btoa(binary)
  }

  const log = (msg: string) => {
    console.log(msg)
    setDebugLog(prev => [...prev.slice(-10), `[${new Date().toLocaleTimeString()}] ${msg}`])
  }

  const toggleLanguage = (lang: string) => {
    setTargetLanguages(prev =>
      prev.includes(lang)
        ? prev.filter(l => l !== lang)
        : [...prev, lang]
    )
  }

  useEffect(() => {
    return () => {
      if (websocketRef.current) {
        websocketRef.current.close()
      }
      if (processorRef.current) {
        processorRef.current.disconnect()
      }
      if (audioContextRef.current) {
        audioContextRef.current.close()
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  const connectMultiLangWebSocket = () => {
    setConnectionStatus('connecting')
    const wsUrl = 'ws://localhost:8000/api/ws/multi-lang'
    console.log('Connecting WebSocket to:', wsUrl)
    websocketRef.current = new WebSocket(wsUrl)

    websocketRef.current.onopen = () => {
      console.log('WebSocket connected')
      setConnectionStatus('connected')
    }

    websocketRef.current.onerror = (error) => {
      console.error('WebSocket error:', error)
      setConnectionStatus('disconnected')
    }

    websocketRef.current.onclose = () => {
      setConnectionStatus('disconnected')
    }

    websocketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log('Received data:', data)

      if (data.error) {
        console.error('Server error:', data.error)
        return
      }

      const segments = data.segments || []
      const transData = data.translations || {}

      setTranscript(prev => {
        const newSegs = [...prev]
        segments.forEach((seg: any) => {
          if (seg.text) {
            const segKey = `${seg.speaker || 'Unknown'}:${seg.text.toLowerCase().trim()}`
            if (seenSegmentRef.current.has(segKey)) {
              return
            }
            seenSegmentRef.current.add(segKey)
            if (seenSegmentRef.current.size > 500) {
              const arr = Array.from(seenSegmentRef.current)
              seenSegmentRef.current = new Set(arr.slice(-250))
            }
            newSegs.push({
              id: seg.id || `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
              speaker: seg.speaker || 'Unknown',
              text: seg.text,
              timestamp: Date.now()
            })
          }
        })
        return newSegs
      })

      setTranslations(prev => {
        const merged = { ...prev }
        Object.entries(data.translations || {}).forEach(([key, value]) => {
          merged[key] = value as any
        })
        return merged
      })
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { sampleRate: sampleRate, channelCount: 1 }
      })
      streamRef.current = stream
      audioBufferRef.current = new Float32Array(0)

      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: sampleRate
      })

      const source = audioContextRef.current.createMediaStreamSource(stream)
      processorRef.current = audioContextRef.current.createScriptProcessor(4096, 1, 1)

      processorRef.current.onaudioprocess = (e) => {
        const audioData = e.inputBuffer.getChannelData(0)
        if (audioData.length > 0) {
          const newBuffer = new Float32Array(audioBufferRef.current.length + audioData.length)
          newBuffer.set(audioBufferRef.current)
          newBuffer.set(audioData, audioBufferRef.current.length)
          audioBufferRef.current = newBuffer
        }
      }

      source.connect(processorRef.current)
      processorRef.current.connect(audioContextRef.current.destination)

      connectMultiLangWebSocket()

      sendIntervalRef.current = setInterval(() => {
        if (websocketRef.current?.readyState === WebSocket.OPEN && audioBufferRef.current.length > bufferSize) {
          const bufferCopy = audioBufferRef.current.slice(0, bufferSize)
          audioBufferRef.current = audioBufferRef.current.slice(bufferSize)
          const base64Audio = encodeAudio(bufferCopy)
          const chunkId = ++chunkIdRef.current
          websocketRef.current?.send(JSON.stringify({
            audio: base64Audio,
            target_langs: targetLanguages,
            sample_rate: sampleRate,
            chunk_id: chunkId
          }))
        }
      }, bufferSeconds * 1000)

      setActiveTab('translation')
      setIsRecording(true)
    } catch (err) {
      console.error('Recording error:', err)
    }
  }

  const stopRecording = () => {
    if (processorRef.current) {
      processorRef.current.disconnect()
      processorRef.current = null
    }
    if (audioContextRef.current) {
      audioContextRef.current.close()
      audioContextRef.current = null
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    if (sendIntervalRef.current) {
      clearInterval(sendIntervalRef.current)
      sendIntervalRef.current = null
    }
    if (audioBufferRef.current.length > 0 && websocketRef.current?.readyState === WebSocket.OPEN) {
      const base64Audio = encodeAudio(audioBufferRef.current)
      const chunkId = ++chunkIdRef.current
      websocketRef.current?.send(JSON.stringify({
        audio: base64Audio,
        target_langs: targetLanguages,
        sample_rate: sampleRate,
        chunk_id: chunkId
      }))
      audioBufferRef.current = new Float32Array(0)
    }
    setIsRecording(false)
    if (websocketRef.current) {
      websocketRef.current.close()
    }
  }

  const clearTranscript = () => {
    setTranscript([])
    setTranslations({})
    seenSegmentRef.current = new Set()
  }

  return (
    <div className={`app${isRecording ? ' is-live' : ''}`}>
      <header>
        <h1>Real-time Meeting Translator</h1>
        <div className="tabs">
          <button
            className={activeTab === 'sources' ? 'active' : ''}
            onClick={() => setActiveTab('sources')}
          >
            Meeting Sources
          </button>
          <button
            className={activeTab === 'translation' ? 'active' : ''}
            onClick={() => setActiveTab('translation')}
          >
            Translation
          </button>
        </div>
      </header>

      <main>
        {activeTab === 'sources' && <MeetingSources />}

        {activeTab === 'translation' && (
          <>
            <div className="status-bar">
              <span className={`status ${connectionStatus}`}>Connection: {connectionStatus}</span>
              <span className={`status ${isRecording ? 'recording' : 'idle'}`}>
                Status: {isRecording ? 'Recording' : 'Ready'}
              </span>
            </div>

            <div className="language-controls">
{Object.entries(languageNames).map(([code, name]: [string, string]) => (
                <label key={code}>
                  <input
                    type="checkbox"
                    checked={targetLanguages.includes(code)}
                    onChange={() => toggleLanguage(code)}
                  />
                  {name}
                </label>
              ))}
            </div>

            <div className="translation-panels">
              {targetLanguages.map(lang => (
                <div key={lang} className="panel">
                  <h3>{languageNames[lang]}</h3>
                  <div className="transcript">
                    {transcript.length === 0 ? (
                      <div className="no-data">Nothing said yet. Start translation and speak into your microphone.</div>
                    ) : (
                      transcript.map((seg, idx) => (
                        <div key={seg.id || idx} className="segment">
                          <strong>{seg.speaker}</strong>
                          <p>{(translations as Record<string, MultiLangTranslations>)[seg.id || String(idx)]?.[lang] || seg.text}</p>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="controls-bottom">
              <button onClick={isRecording ? stopRecording : startRecording}>
                {isRecording ? 'Stop' : 'Start'} Translation
              </button>
              <button onClick={clearTranscript}>Clear</button>
            </div>
          </>
        )}
      </main>
    </div>
  )
}

export default App