import React from 'react'
import { useAppDispatch, useAppSelector } from '../../store'
import { selectMeeting, setCaptureMode } from '../../store/meetingSlice'

export default function CaptureControls() {
  const captureMode = useAppSelector((state) => state.meeting.captureMode)
  const isRecording = useAppSelector((state) => state.meeting.isRecording)
  const dispatch = useAppDispatch()

  return (
    <div className="capture-controls">
      <span>Audio source:</span>
      <label>
        <input
          type="radio"
          name="captureMode"
          checked={captureMode === 'mic'}
          onChange={() => dispatch(setCaptureMode('mic'))}
          disabled={isRecording}
        />
        Microphone
      </label>
      <label>
        <input
          type="radio"
          name="captureMode"
          checked={captureMode === 'system'}
          onChange={() => dispatch(setCaptureMode('system'))}
          disabled={isRecording}
        />
        System / Tab audio
      </label>
    </div>
  )
}
