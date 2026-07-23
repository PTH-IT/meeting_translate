import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'

interface Meeting {
  id: string
  name: string
  platform: string
  status: 'available' | 'detected' | 'running'
}

const initialMeetings: Meeting[] = [
  { id: 'zoom', name: 'Zoom', platform: 'zoom', status: 'available' },
  { id: 'teams', name: 'Microsoft Teams', platform: 'teams', status: 'available' },
  { id: 'meet', name: 'Google Meet', platform: 'google_meet', status: 'available' },
  { id: 'system', name: 'System Audio', platform: 'system_audio', status: 'available' },
  { id: 'microphone', name: 'Microphone', platform: 'system_audio', status: 'available' },
  { id: 'upload', name: 'Upload File', platform: 'upload', status: 'available' }
]

interface TranscriptSegment {
  id: string
  speaker: string
  text: string
  timestamp: number
}

interface MultiLangTranslations {
  [lang: string]: string
}

interface MeetingState {
  meetings: Meeting[]
  selectedMeetingId: string | null
  isRecording: boolean
  connectionStatus: 'disconnected' | 'connecting' | 'connected'
  captureMode: 'mic' | 'system'
  targetLanguages: string[]
  transcript: TranscriptSegment[]
  translations: Record<string, MultiLangTranslations>
  debugLog: string[]
  lastError: string | null
  activeTab: 'meeting_sources' | 'translation' | 'text_translation'
  textInput: string
  textSourceLang: string
  textTargetLang: string
  translatedText: string
  textLoading: boolean
  textError: string | null
}

const initialState: MeetingState = {
  meetings: initialMeetings,
  selectedMeetingId: null,
  isRecording: false,
  connectionStatus: 'disconnected',
  captureMode: 'mic',
  targetLanguages: ['vi'],
  transcript: [],
  translations: {},
  debugLog: [],
  lastError: null,
  activeTab: 'translation',
  textInput: '',
  textSourceLang: 'auto',
  textTargetLang: 'vi',
  translatedText: '',
  textLoading: false,
  textError: null
}

const meetingSlice = createSlice({
  name: 'meeting',
  initialState,
  reducers: {
    setMeetings: (state, action: PayloadAction<Meeting[]>) => {
      state.meetings = action.payload
    },
    selectMeeting: (state, action: PayloadAction<string | null>) => {
      state.selectedMeetingId = action.payload
    },
    startRecording: (state) => {
      state.isRecording = true
    },
    stopRecording: (state) => {
      state.isRecording = false
    },
    setRecording: (state, action: PayloadAction<boolean>) => {
      state.isRecording = action.payload
    },
    setConnectionStatus: (state, action: PayloadAction<'disconnected' | 'connecting' | 'connected'>) => {
      state.connectionStatus = action.payload
    },
    setCaptureMode: (state, action: PayloadAction<'mic' | 'system'>) => {
      state.captureMode = action.payload
    },
    setTargetLanguages: (state, action: PayloadAction<string[]>) => {
      state.targetLanguages = action.payload
    },
    toggleLanguage: (state, action: PayloadAction<string>) => {
      const lang = action.payload
      if (state.targetLanguages.includes(lang)) {
        state.targetLanguages = state.targetLanguages.filter((l) => l !== lang)
      } else {
        state.targetLanguages = [...state.targetLanguages, lang]
      }
    },
    setActiveTab: (state, action: PayloadAction<'meeting_sources' | 'translation' | 'text_translation'>) => {
      state.activeTab = action.payload
    },
    setTextInput: (state, action: PayloadAction<string>) => {
      state.textInput = action.payload
    },
    setTextSource: (state, action: PayloadAction<string>) => {
      state.textSourceLang = action.payload
    },
    setTextTarget: (state, action: PayloadAction<string>) => {
      state.textTargetLang = action.payload
    },
    setTranslatedText: (state, action: PayloadAction<string>) => {
      state.translatedText = action.payload
    },
    setTextLoading: (state, action: PayloadAction<boolean>) => {
      state.textLoading = action.payload
    },
    setTextError: (state, action: PayloadAction<string | null>) => {
      state.textError = action.payload
    },
    clearTextTranslation: (state) => {
      state.translatedText = ''
      state.textError = null
    },
    addTranscriptSegments: (state, action: PayloadAction<TranscriptSegment[]>) => {
      state.transcript.push(...action.payload)
    },
    setTranslations: (state, action: PayloadAction<Record<string, MultiLangTranslations>>) => {
      state.translations = { ...state.translations, ...action.payload }
    },
    addDebugLog: (state, action: PayloadAction<string>) => {
      state.debugLog.push(action.payload)
      if (state.debugLog.length > 100) {
        state.debugLog = state.debugLog.slice(-50)
      }
    },
    setLastError: (state, action: PayloadAction<string | null>) => {
      state.lastError = action.payload
    },
    clearTranscript: (state) => {
      state.transcript = []
      state.translations = {}
    }
  }
})

export const {
  setMeetings,
  selectMeeting,
  startRecording,
  stopRecording,
  setRecording,
  setConnectionStatus,
  setCaptureMode,
  setTargetLanguages,
  toggleLanguage,
  addTranscriptSegments,
  setTranslations,
  addDebugLog,
  setLastError,
  clearTranscript,
  setActiveTab,
  setTextInput,
  setTextSource,
  setTextTarget,
  setTranslatedText,
  setTextLoading,
  setTextError,
  clearTextTranslation
} = meetingSlice.actions

export const translateText = createAsyncThunk(
  'meeting/translateText',
  async (
    { text, targetLang, sourceLang }: { text: string; targetLang: string; sourceLang?: string },
    { dispatch, rejectWithValue }
  ) => {
    dispatch(setTextLoading(true))
    dispatch(setTextError(null))
    try {
      const baseUrl = window.location.origin.replace(/^http/, 'http')
      const resp = await fetch('/api/translate-text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, target_lang: targetLang, source_lang: sourceLang })
      })
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ error: 'Unknown error' }))
        return rejectWithValue(err.error || 'Translation failed')
      }
      const data = await resp.json()
      dispatch(setTranslatedText(data.translated_text || ''))
      return data
    } catch (e: any) {
      const message = e.message || 'Network error'
      dispatch(setTextError(message))
      return rejectWithValue(message)
    } finally {
      dispatch(setTextLoading(false))
    }
  }
)

export default meetingSlice.reducer
