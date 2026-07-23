import React from 'react'
import { useAppDispatch, useAppSelector } from '../../store'
import { clearTranscript } from '../../store/meetingSlice'
import useRecordingEngine from '../../hooks/useRecordingEngine'

export default function ControlButtons() {
  const isRecording = useAppSelector((state) => state.meeting.isRecording)
  const dispatch = useAppDispatch()
  const { start, stop } = useRecordingEngine()

  return (
    <div className="controls-bottom">
      <button onClick={isRecording ? stop : start}>
        {isRecording ? 'Stop' : 'Start'} Translation
      </button>
      <button onClick={() => dispatch(clearTranscript())}>Clear</button>
    </div>
  )
}