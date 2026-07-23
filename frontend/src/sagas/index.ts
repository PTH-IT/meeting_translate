import { all, fork } from 'redux-saga/effects'
import audioFlow from './audioFlow'

export default function* rootSaga() {
  yield all([fork(audioFlow)])
}
