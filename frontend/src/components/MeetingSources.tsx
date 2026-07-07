import React, { useState } from 'react'
import './MeetingSources.css'

interface MeetingSource {
  id: string
  name: string
  platform: string
  status: 'available' | 'detected' | 'running'
}

const platformInitial: Record<string, string> = {
  zoom: 'Z',
  teams: 'T',
  google_meet: 'G',
  system_audio: 'S',
  upload: 'U'
}

export default function MeetingSources() {
  const [sources, setSources] = useState<MeetingSource[]>([
    { id: 'zoom', name: 'Zoom', platform: 'zoom', status: 'available' },
    { id: 'teams', name: 'Microsoft Teams', platform: 'teams', status: 'available' },
    { id: 'meet', name: 'Google Meet', platform: 'google_meet', status: 'available' },
    { id: 'system', name: 'System Audio', platform: 'system_audio', status: 'available' },
    { id: 'microphone', name: 'Microphone', platform: 'system_audio', status: 'available' },
    { id: 'upload', name: 'Upload File', platform: 'upload', status: 'available' }
  ])

  const [selectedSource, setSelectedSource] = useState<string | null>(null)

  const detectMeetings = () => {
    // Simulate detection - in production would check running applications
    setSources(prev => prev.map(s => ({
      ...s,
      status: Math.random() > 0.5 ? 'detected' : 'available'
    })))
  }

  const selectSource = (sourceId: string) => {
    setSelectedSource(sourceId)
    // User must press "Start Translation" to begin
  }

  return (
    <div className="sources-container">
      <div className="sources-topbar">
        <div className="sources-heading">
          <h2>Meeting Sources</h2>
          <p className="warning">Translation starts only after pressing "Start Translation"</p>
        </div>
        <button onClick={detectMeetings} className="detect-btn">
          Detect Available Sources
        </button>
      </div>

      <div className="sources-scroll">
        <div className="sources-grid">
          {sources.map(source => (
            <div
              key={source.id}
              className={`source-card ${source.status} ${selectedSource === source.id ? 'selected' : ''}`}
              onClick={() => selectSource(source.id)}
            >
              <div className="source-icon">{platformInitial[source.platform] || '?'}</div>
              <div className="source-info">
                <h3>{source.name}</h3>
                <span className={`status-badge ${source.status}`}>
                  {source.status === 'detected' ? 'Detected' : source.status === 'running' ? 'Running' : 'Available'}
                </span>
              </div>
              {selectedSource === source.id && <div className="source-check">✓</div>}
            </div>
          ))}
        </div>
      </div>

      {selectedSource && (
        <div className="action-section">
          <button className="start-btn">Start Translation</button>
        </div>
      )}
    </div>
  )
}