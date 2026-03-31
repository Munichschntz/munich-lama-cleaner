import React, { useEffect } from 'react'
import { useRecoilState, useRecoilValue } from 'recoil'
import Editor from './Editor/Editor'
import ShortcutsModal from './Shortcuts/ShortcutsModal'
import SettingModal from './Settings/SettingsModal'
import Toast from './shared/Toast'
import { AIModel, isSDState, settingState, toastState } from '../store/Atoms'
import {
  currentModel,
  modelDownloaded,
  switchModel,
} from '../adapters/inpainting'
import SidePanel from './SidePanel/SidePanel'

interface WorkspaceProps {
  file: File
}

const Workspace = ({ file }: WorkspaceProps) => {
  const [settings, setSettingState] = useRecoilState(settingState)
  const [toastVal, setToastState] = useRecoilState(toastState)
  const isSD = useRecoilValue(isSDState)

  const parseResponseError = async (res: Response) => {
    try {
      const data = await res.json()
      return data?.error?.message || 'Server error'
    } catch {
      return 'Server error'
    }
  }

  const onSettingClose = async () => {
    let curModel: AIModel = settings.model
    try {
      const curModelRes = await currentModel()
      if (!curModelRes.ok) {
        throw new Error(await parseResponseError(curModelRes))
      }
      const curModelJson = await curModelRes.json()
      curModel = curModelJson.model as AIModel
      if (curModel === settings.model) {
        return
      }

      const downloadedRes = await modelDownloaded(settings.model)
      if (!downloadedRes.ok) {
        throw new Error(await parseResponseError(downloadedRes))
      }
      const downloadedJson = await downloadedRes.json()
      const downloaded = Boolean(downloadedJson.downloaded)

      const { model } = settings

      let loadingMessage = `Switching to ${model} model`
      let loadingDuration = 3000
      if (!downloaded) {
        loadingMessage = `Downloading ${model} model, this may take a while`
        loadingDuration = 9999999999
      }

      setToastState({
        open: true,
        desc: loadingMessage,
        state: 'loading',
        duration: loadingDuration,
      })

      const switchRes = await switchModel(model)
      if (!switchRes.ok) {
        throw new Error(await parseResponseError(switchRes))
      }

      setToastState({
        open: true,
        desc: `Switch to ${model} model success`,
        state: 'success',
        duration: 3000,
      })
    } catch (error: unknown) {
      setToastState({
        open: true,
        desc:
          error instanceof Error
            ? `Switch model failed: ${error.message}`
            : 'Switch model failed',
        state: 'error',
        duration: 3000,
      })
      setSettingState(old => {
        return { ...old, model: curModel }
      })
    }
  }

  useEffect(() => {
    currentModel()
      .then(res => res.json())
      .then(({ model }) => {
        setSettingState(old => {
          return { ...old, model: model as AIModel }
        })
      })
  }, [setSettingState])

  return (
    <>
      {isSD ? <SidePanel /> : <></>}
      <Editor file={file} />
      <SettingModal onClose={onSettingClose} />
      <ShortcutsModal />
      <Toast
        {...toastVal}
        onOpenChange={(open: boolean) => {
          setToastState(old => {
            return { ...old, open }
          })
        }}
      />
    </>
  )
}

export default Workspace
