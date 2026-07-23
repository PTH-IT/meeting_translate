import { takeEvery, put, select } from 'redux-saga/effects'

function* getTranscriptionState() {
  const state = (yield select((s: any) => s)).meeting
  return {
    targetLanguages: state.targetLanguages,
    audioBuffer: state.audioBuffer,
    chunkCounter: state.chunkCounter,
    actualSampleRate: state.actualSampleRate,
    captureMode: state.captureMode
  }
}

export function* watchStartRecording() {
  yield takeEvery('meeting/startRecording', handleStartRecording)
}

export function* watchStopRecording() {
  yield takeEvery('meeting/stopRecording', handleStopRecording)
}

function* handleStartRecording() {
  try {
    yield takeAudioStream()
    yield put({ type: 'meeting/setRecording', payload: true })
    yield put({ type: 'ui/setActiveTab', payload: 'translation' })
  } catch (e: any) {
    yield put({ type: 'meeting/setLastError', payload: e.message })
  }
}

const takeAudioStream = () =>
  navigator.mediaDevices.getUserMedia({
    audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
  })

function* handleStopRecording() {
  yield put({ type: 'meeting/setRecording', payload: false })
  yield put({ type: 'meeting/clearDebugLog' })
}

export default function* audioFlow() {
  yield watchStartRecording()
  yield watchStopRecording()
}
