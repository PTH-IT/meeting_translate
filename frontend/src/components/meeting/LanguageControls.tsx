import React from 'react'
import { useAppDispatch, useAppSelector } from '../../store'
import { toggleLanguage } from '../../store/meetingSlice'

const languageNames: Record<string, string> = {
  vi: 'Vietnamese',
  en: 'English',
  ja: 'Japanese',
  zh: 'Chinese',
  ko: 'Korean'
}

export default function LanguageControls() {
  const targetLanguages = useAppSelector((state) => state.meeting.targetLanguages)
  const isRecording = useAppSelector((state) => state.meeting.isRecording)
  const dispatch = useAppDispatch()

  return (
    <div className="language-controls">
      {Object.entries(languageNames).map(([code, name]) => (
        <label key={code}>
          <input
            type="checkbox"
            checked={targetLanguages.includes(code)}
            onChange={() => dispatch(toggleLanguage(code))}
            disabled={isRecording}
          />
          {name}
        </label>
      ))}
    </div>
  )
}
