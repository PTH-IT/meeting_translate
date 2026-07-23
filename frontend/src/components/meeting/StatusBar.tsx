import React from 'react'
import { useAppDispatch, useAppSelector } from '../../store'
import { addDebugLog, setLastError } from '../../store/meetingSlice'

export default function StatusBar() {
  const transcript = useAppSelector((state) => state.meeting.transcript)
  const isRecording = useAppSelector((state) => state.meeting.isRecording)
  const connectionStatus = useAppSelector((state) => state.meeting.connectionStatus)
  const lastError = useAppSelector((state) => state.meeting.lastError)
  const dispatch = useAppDispatch()

  return (
    <div className="status-bar">
      <span className={`status ${connectionStatus}`}>Connection: {connectionStatus}</span>
      <span className={`status ${isRecording ? 'recording' : 'idle'}`}>
        Status: {isRecording ? 'Recording' : 'Ready'}
      </span>
      {lastError && <span className="status error">{lastError}</span>}
    </div>
  )
}
