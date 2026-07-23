import React from 'react'
import { useAppDispatch, useAppSelector } from '../../store'
import { translateText, setTextSource, setTextTarget, setTextInput, clearTextTranslation } from '../../store/meetingSlice'

const languages = [
  { code: 'vi', name: 'Tiếng Việt' },
  { code: 'en', name: 'English' },
  { code: 'ja', name: 'Japanese' },
  { code: 'zh', name: 'Chinese' },
  { code: 'ko', name: 'Korean' }
]

export default function TextTranslationView() {
  const sourceLang = useAppSelector((state) => state.meeting.textSourceLang)
  const targetLang = useAppSelector((state) => state.meeting.textTargetLang)
  const inputText = useAppSelector((state) => state.meeting.textInput)
  const translatedText = useAppSelector((state) => state.meeting.translatedText)
  const textLoading = useAppSelector((state) => state.meeting.textLoading)
  const textError = useAppSelector((state) => state.meeting.textError)
  const dispatch = useAppDispatch()

  const handleTranslate = async () => {
    if (!inputText.trim()) return
    await dispatch(translateText({ text: inputText, targetLang, sourceLang }))
  }

  return (
    <div className="text-translation">
      <div className="language-controls">
        <label>
          Ngôn ngữ nguồn:
          <select value={sourceLang} onChange={(e) => dispatch(setTextSource(e.target.value))}>
            <option value="auto">Tự động</option>
            {languages.map(lang => (
              <option key={lang.code} value={lang.code}>{lang.name}</option>
            ))}
          </select>
        </label>
        <label>
          Ngôn ngữ đích:
          <select value={targetLang} onChange={(e) => dispatch(setTextTarget(e.target.value))}>
            {languages.map(lang => (
              <option key={lang.code} value={lang.code}>{lang.name}</option>
            ))}
          </select>
        </label>
      </div>

      <div className="translation-panels">
        <div className="panel">
          <h3>Văn bản gốc</h3>
          <textarea
            className="transcript"
            placeholder="Nhập văn bản cần dịch..."
            value={inputText}
            onChange={(e) => dispatch(setTextInput(e.target.value))}
          />
        </div>
        <div className="panel">
          <h3>Bản dịch</h3>
          <div className="transcript">
            {textError && <div className="status error">{textError}</div>}
            {!textError && translatedText ? (
              <div className="segment">
                <p>{translatedText}</p>
              </div>
            ) : (
              <div className="no-data">Kết quả dịch sẽ hiển thị ở đây</div>
            )}
          </div>
        </div>
      </div>

      <div className="controls-bottom">
        <button onClick={handleTranslate} disabled={textLoading || !inputText.trim()}>
          {textLoading ? 'Đang dịch...' : 'Dịch'}
        </button>
        <button onClick={() => dispatch(clearTextTranslation())}>Xóa</button>
      </div>
    </div>
  )
}
