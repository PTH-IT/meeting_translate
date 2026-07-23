import React, { useState, useEffect } from 'react'
import { Provider } from 'react-redux'
import { store } from './store'
import MeetingSources from './components/MeetingSources'
import TranslationView from './components/meeting/TranslationView'
import TextTranslationView from './components/meeting/TextTranslationView'
import './App.css'

function AppInner() {
  const [activeTab, setActiveTab] = useState<'meeting_sources' | 'translation' | 'text_translation'>('translation')

  return (
    <div className={`app${activeTab === 'translation' ? ' is-live' : ''}`}>
      <header>
        <h1>Real-time Meeting Translator</h1>
        <div className="tabs">
          <button
            className={activeTab === 'meeting_sources' ? 'active' : ''}
            onClick={() => setActiveTab('meeting_sources')}
          >
            Nguồn cuộc họp
          </button>
          <button
            className={activeTab === 'translation' ? 'active' : ''}
            onClick={() => setActiveTab('translation')}
          >
            Dịch
          </button>
          <button
            className={activeTab === 'text_translation' ? 'active' : ''}
            onClick={() => setActiveTab('text_translation')}
          >
            Dịch văn bản
          </button>
        </div>
      </header>

      <main>
        {activeTab === 'meeting_sources' && <MeetingSources />}
        {activeTab === 'translation' && <TranslationView />}
        {activeTab === 'text_translation' && <TextTranslationView />}
      </main>
    </div>
  )
}

export default function App() {
  return (
    <Provider store={store}>
      <AppInner />
    </Provider>
  )
}
