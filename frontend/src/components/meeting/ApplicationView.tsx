import React, { useEffect, useRef } from 'react'
import { useAppDispatch, useAppSelector } from '../../store'
import {
  clearTranscript,
  addDebugLog,
  setLastError,
  setConnectionStatus
} from '../../store/meetingSlice'
import StatusBar from './StatusBar'
import RecordingControls from './RecordingControls'
import LanguageControls from './LanguageControls'
import TranscriptPanel from './TranscriptPanel'
import ControlButtons from './ControlButtons'

export default function ApplicationView() {
  const isRecording = useAppSelector((state) => state.meeting.isRecording)
  const connectionStatus = useAppSelector((state) => state.meeting.connectionStatus)
  const captureMode = useAppSelector((state) => state.meeting.captureMode)
  const targetLanguages = useAppSelector((state) => state.meeting.targetLanguages)
  const dispatch = useAppDispatch()
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  return (
    <>
      <StatusBar />
      <RecordingControls />
      <LanguageControls />
      <TranscriptPanel />
      <ControlButtons />
    </>
  )
}
