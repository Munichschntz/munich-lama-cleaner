import { ArrowLeftIcon, UploadIcon } from '@heroicons/react/outline'
import React, { useState } from 'react'
import { useRecoilState, useRecoilValue } from 'recoil'
import { AIModel, fileState, isSDState, settingState } from '../../store/Atoms'
import Button from '../shared/Button'
import Shortcuts from '../Shortcuts/Shortcuts'
import useResolution from '../../hooks/useResolution'
import { ThemeChanger } from './ThemeChanger'
import SettingIcon from '../Settings/SettingIcon'
import PromptInput from './PromptInput'

const MODEL_DISPLAY_NAME: { [key in AIModel]: string } = {
  [AIModel.LAMA]: 'LaMa',
  [AIModel.LDM]: 'LDM',
  [AIModel.ZITS]: 'ZITS',
  [AIModel.MAT]: 'MAT',
  [AIModel.FCF]: 'FcF',
  [AIModel.SD14]: 'SD 1.4',
  [AIModel.CV2]: 'CV2',
}

const Header = () => {
  const [file, setFile] = useRecoilState(fileState)
  const [settings, setSettingState] = useRecoilState(settingState)
  const resolution = useResolution()
  const [uploadElemId] = useState(`file-upload-${Math.random().toString()}`)
  const isSD = useRecoilValue(isSDState)

  const renderHeader = () => {
    return (
      <header>
        <div style={{ visibility: file ? 'visible' : 'hidden' }}>
          <label htmlFor={uploadElemId}>
            <Button icon={<UploadIcon />} style={{ border: 0 }}>
              <input
                style={{ display: 'none' }}
                id={uploadElemId}
                name={uploadElemId}
                type="file"
                onChange={ev => {
                  const newFile = ev.currentTarget.files?.[0]
                  if (newFile) {
                    setFile(newFile)
                  }
                }}
                accept="image/png, image/jpeg"
              />
              {resolution === 'desktop' ? 'Upload New' : undefined}
            </Button>
          </label>
        </div>

        {isSD && file ? <PromptInput /> : <></>}

        <div className="header-icons-wrapper">
          {file && (
            <div
              className="model-chip"
              title="Current model. Click to open settings."
              role="button"
              tabIndex={0}
              onClick={() => {
                setSettingState({ ...settings, show: true })
              }}
              onKeyDown={ev => {
                if (ev.key === 'Enter' || ev.key === ' ') {
                  setSettingState({ ...settings, show: true })
                }
              }}
            >
              Model: {MODEL_DISPLAY_NAME[settings.model] || settings.model}
            </div>
          )}
          <ThemeChanger />
          {file && (
            <div className="header-icons">
              <Shortcuts />
              <SettingIcon />
            </div>
          )}
        </div>
      </header>
    )
  }
  return renderHeader()
}

export default Header
