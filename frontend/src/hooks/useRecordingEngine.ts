import { useCallback, useRef, useEffect } from 'react'
import { useAppDispatch, useAppSelector } from '../store'
import {
  setConnectionStatus,
  setLastError,
  addDebugLog,
  addTranscriptSegments,
  setTranslations,
  startRecording,
  stopRecording
} from '../store/meetingSlice'

const sampleRate = 16000
const bufferSeconds = 5

function encodeAudio(audioData: Float32Array): string {
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

export default function useRecordingEngine() {
  const captureMode = useAppSelector((state) => state.meeting.captureMode)
  const targetLanguages = useAppSelector((state) => state.meeting.targetLanguages)
  const dispatch = useAppDispatch()

  const websocketRef = useRef<WebSocket | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const processorRef = useRef<ScriptProcessorNode | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const audioBufferRef = useRef<Float32Array>(new Float32Array(0))
  const sendIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const chunkIdRef = useRef(0)
  const seenSegmentRef = useRef<Set<string>>(new Set())
  const actualSampleRateRef = useRef<number>(sampleRate)

  useEffect(() => {
    return () => {
      if (websocketRef.current) websocketRef.current.close()
      if (processorRef.current) processorRef.current.disconnect()
      if (audioContextRef.current) audioContextRef.current.close()
      if (streamRef.current) streamRef.current.getTracks().forEach(track => track.stop())
    }
  }, [])

  const connectWebSocket = useCallback(() => {
    dispatch(setConnectionStatus('connecting'))
    dispatch(setLastError(null))
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const wsUrl = `${protocol}://${window.location.host}/api/ws/multi-lang`
    dispatch(addDebugLog('Connecting to ' + wsUrl))
    websocketRef.current = new WebSocket(wsUrl)

    websocketRef.current.onopen = () => {
      dispatch(addDebugLog('WebSocket connected'))
      dispatch(setConnectionStatus('connected'))
    }

    websocketRef.current.onerror = () => {
      dispatch(setConnectionStatus('disconnected'))
    }

    websocketRef.current.onclose = () => {
      dispatch(setConnectionStatus('disconnected'))
    }

    websocketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.error) {
        dispatch(setLastError('Server error: ' + data.error))
        return
      }

      const transcript = (data.segments || [])
        .filter((seg: any) => seg.text)
        .map((seg: any) => {
          const segKey = `${seg.speaker || 'Unknown'}:${seg.text.toLowerCase().trim()}`
          if (seenSegmentRef.current.has(segKey)) return null
          seenSegmentRef.current.add(segKey)
          if (seenSegmentRef.current.size > 500) {
            const arr = Array.from(seenSegmentRef.current)
            seenSegmentRef.current = new Set(arr.slice(-250))
          }
          return {
            id: seg.id || `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
            speaker: seg.speaker || 'Unknown',
            text: seg.text,
            timestamp: Date.now()
          }
        })
        .filter(Boolean)

      if (transcript.length) {
        dispatch(addTranscriptSegments(transcript))
        dispatch(setTranslations(data.translations || {}))
      }
    }
  }, [dispatch])

  const start = useCallback(async () => {
    try {
      let stream: MediaStream
      if (captureMode === 'system') {
        stream = await (navigator.mediaDevices as any).getDisplayMedia({
          video: true,
          audio: {
            echoCancellation: false,
            noiseSuppression: false,
            autoGainControl: false,
            sampleRate,
            channelCount: 1
          }
        })
        stream.getVideoTracks().forEach(track => track.stop())
        if (!stream.getAudioTracks().length) {
          throw new Error('No audio track captured. Make sure to tick "Share tab audio".')
        }
      } else {
        stream = await navigator.mediaDevices.getUserMedia({
          audio: { sampleRate, channelCount: 1 }
        })
      }

      streamRef.current = stream
      stream.getAudioTracks().forEach(track => {
        track.addEventListener('ended', () => {
          stop()
        })
      })

      audioBufferRef.current = new Float32Array(0)
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate })
      actualSampleRateRef.current = audioContextRef.current.sampleRate

      const source = audioContextRef.current.createMediaStreamSource(stream)
      processorRef.current = audioContextRef.current.createScriptProcessor(4096, 1, 1)

      processorRef.current.onaudioprocess = (e) => {
        const data = e.inputBuffer.getChannelData(0)
        if (data.length > 0) {
          const next = new Float32Array(audioBufferRef.current.length + data.length)
          next.set(audioBufferRef.current)
          next.set(data, audioBufferRef.current.length)
          audioBufferRef.current = next
        }
      }

      source.connect(processorRef.current)
      processorRef.current.connect(audioContextRef.current.destination)

      connectWebSocket()

      sendIntervalRef.current = setInterval(() => {
        if (websocketRef.current?.readyState === WebSocket.OPEN && audioBufferRef.current.length >= sampleRate * bufferSeconds) {
          const chunk = audioBufferRef.current.slice(0, sampleRate * bufferSeconds)
          audioBufferRef.current = audioBufferRef.current.slice(sampleRate * bufferSeconds)
          const base64 = encodeAudio(chunk)
          const chunkId = ++chunkIdRef.current
          websocketRef.current.send(JSON.stringify({
            audio: base64,
            target_langs: targetLanguages,
            sample_rate: actualSampleRateRef.current,
            chunk_id: chunkId
          }))
        }
      }, bufferSeconds * 1000)

      dispatch(startRecording())
    } catch (err: any) {
      const message = err.message || String(err)
      dispatch(setLastError(message))
      dispatch(addDebugLog('Recording error: ' + message))
    }
  }, [captureMode, targetLanguages, dispatch, connectWebSocket])

  const stop = useCallback(() => {
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
      const base64 = encodeAudio(audioBufferRef.current)
      const chunkId = ++chunkIdRef.current
      websocketRef.current.send(JSON.stringify({
        audio: base64,
        target_langs: targetLanguages,
        sample_rate: actualSampleRateRef.current,
        chunk_id: chunkId
      }))
      audioBufferRef.current = new Float32Array(0)
    }
    websocketRef.current?.close()
    dispatch(stopRecording())
    dispatch(addDebugLog('Recording stopped'))
  }, [targetLanguages, dispatch])

  return { start, stop }
}
