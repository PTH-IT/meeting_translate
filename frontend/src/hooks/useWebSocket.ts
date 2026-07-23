import { useAppSelector, useAppDispatch } from '../store'
import { setRecording, setConnectionStatus, setLastError, addDebugLog } from '../store/meetingSlice'

export type UseWebSocketReturn = {
  connect: () => void
  disconnect: () => void
  connectionStatus: string
}

export function useWebSocket(): UseWebSocketReturn {
  const connectionStatus = useAppSelector((state) => state.meeting.connectionStatus)
  const isRecording = useAppSelector((state) => state.meeting.isRecording)
  const targetLanguages = useAppSelector((state) => state.meeting.targetLanguages)
  const dispatch = useAppDispatch()

  return {
    connect: () => {
      dispatch(setConnectionStatus('connecting'))
      dispatch(setLastError(null))
      dispatch(addDebugLog('Connect called'))
    },
    disconnect: () => {
      dispatch(setConnectionStatus('disconnected'))
    },
    connectionStatus
  }
}
