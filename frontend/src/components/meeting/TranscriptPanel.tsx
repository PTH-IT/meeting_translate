import React from 'react'
import { useAppDispatch, useAppSelector } from '../../store'
import { clearTranscript } from '../../store/meetingSlice'

const languageNames: Record<string, string> = {
  vi: 'Vietnamese',
  en: 'English',
  ja: 'Japanese',
  zh: 'Chinese',
  ko: 'Korean'
}

export default function TranscriptPanel() {
  const transcript = useAppSelector((state) => state.meeting.transcript)
  const translations = useAppSelector((state) => state.meeting.translations)
  const targetLanguages = useAppSelector((state) => state.meeting.targetLanguages)
  const dispatch = useAppDispatch()

  return (
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
                  <p>{(translations as any)[seg.id || String(idx)]?.[lang] || seg.text}</p>
                </div>
              ))
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
