import { configureStore } from '@reduxjs/toolkit'
import { useDispatch, useSelector } from 'react-redux'
import meetingReducer from './meetingSlice'
import createSagaMiddleware from 'redux-saga'
import rootSaga from '../sagas/index'

const sagaMiddleware = createSagaMiddleware()

export const store = configureStore({
  reducer: {
    meeting: meetingReducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({ thunk: true }).concat(sagaMiddleware)
})

sagaMiddleware.run(rootSaga)

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch

export const useAppDispatch = () => useDispatch<AppDispatch>()

export const useAppSelector = <T>(
  selector: (state: RootState) => T
): T => {
  const typedSelector = selector as (state: RootState) => T
  return useSelector(typedSelector)
}

export default store
