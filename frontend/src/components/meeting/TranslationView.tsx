import React from 'react'
import StatusBar from './StatusBar'
import CaptureControls from './CaptureControls'
import LanguageControls from './LanguageControls'
import TranscriptPanel from './TranscriptPanel'
import ControlButtons from './ControlButtons'

export default function TranslationView() {
  return (
    <>
      <StatusBar />
      <CaptureControls />
      <LanguageControls />
      <TranscriptPanel />
      <ControlButtons />
    </>
  )
}
