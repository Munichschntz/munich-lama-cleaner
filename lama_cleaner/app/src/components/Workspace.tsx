import React, { useCallback, useEffect } from 'react'
import { useRecoilState, useRecoilValue } from 'recoil'
import Editor from './Editor/Editor'
import ShortcutsModal from './Shortcuts/ShortcutsModal'
import SettingModal from './Settings/SettingsModal'
import Toast from './shared/Toast'
import { AIModel, isSDState, settingState, toastState } from '../store/Atoms'
import {
  currentModel,
  IS_API_ENDPOINT_FALLBACK,
  API_ENDPOINT,
  modelDownloaded,
  switchModel,
} from '../adapters/inpainting'
import SidePanel from './SidePanel/SidePanel'

const AI_MODELS = new Set(Object.values(AIModel))

interface WorkspaceProps {
  file: File
}

const isAIModel = (value: unknown): value is AIModel =>
  AI_MODELS.has(value as AIModel)

const SHORT_TOAST_DURATION = 3000
const LONG_TOAST_DURATION = 20000
const INDEFINITE_TOAST_DURATION = 9999999999

const parseResponseError = async (res: Response): Promise<string> => {
  try {
    const data = await res.json()
    return data?.error?.message || 'Server error'
  } catch {
    return 'Server error'
  }
}

const errorMessage = (error: unknown, fallback: string): string =>
  error instanceof Error ? `${fallback}: ${error.message}` : fallback

const getSwitchToastMeta = (
  model: AIModel,
  hasKnownDownloadState: boolean,
  downloaded: boolean
) => {
  if (!hasKnownDownloadState) {
    return {
      desc: `Preparing ${model} model, this may take a while`,
      duration: LONG_TOAST_DURATION,
    }
  }

  if (!downloaded) {
    return {
      desc: `Downloading ${model} model, this may take a while`,
      duration: INDEFINITE_TOAST_DURATION,
    }
  }

  return {
    desc: `Switching to ${model} model`,
    duration: SHORT_TOAST_DURATION,
  }
}

const Workspace = ({ file }: WorkspaceProps) => {
  const [settings, setSettingState] = useRecoilState(settingState)
  const [toastVal, setToastState] = useRecoilState(toastState)
  const isSD = useRecoilValue(isSDState)

  const showToast = useCallback(
    ({
      desc,
      state,
      duration,
    }: {
      desc: string
      state: 'default' | 'loading' | 'success' | 'error'
      duration: number
    }) => {
      setToastState({
        open: true,
        desc,
        state,
        duration,
      })
    },
    [setToastState]
  )

  const onSettingClose = async () => {
    let curModel: AIModel = settings.model
    try {
      const curModelRes = await currentModel()
      if (!curModelRes.ok) {
        throw new Error(await parseResponseError(curModelRes))
      }
      const curModelJson = await curModelRes.json()
      if (isAIModel(curModelJson.model)) {
        curModel = curModelJson.model
      }
      if (curModel === settings.model) {
        return
      }

      const downloadedRes = await modelDownloaded(settings.model)
      if (!downloadedRes.ok) {
        throw new Error(await parseResponseError(downloadedRes))
      }
      const downloadedJson = await downloadedRes.json()
      const hasKnownDownloadState = typeof downloadedJson.downloaded === 'boolean'
      const downloaded = hasKnownDownloadState && downloadedJson.downloaded

      const { model } = settings
      const loadingToast = getSwitchToastMeta(
        model,
        hasKnownDownloadState,
        downloaded
      )

      showToast({
        ...loadingToast,
        state: 'loading',
      })

      const switchRes = await switchModel(model)
      if (!switchRes.ok) {
        throw new Error(await parseResponseError(switchRes))
      }

      showToast({
        desc: `Switch to ${model} model success`,
        state: 'success',
        duration: SHORT_TOAST_DURATION,
      })
    } catch (error: unknown) {
      showToast({
        desc: errorMessage(error, 'Switch model failed'),
        state: 'error',
        duration: SHORT_TOAST_DURATION,
      })
      setSettingState(old => {
        return { ...old, model: curModel }
      })
    }
  }

  useEffect(() => {
    if (!IS_API_ENDPOINT_FALLBACK) {
      return
    }
    showToast({
      desc: `Using fallback API endpoint: ${API_ENDPOINT}`,
      state: 'default',
      duration: 3500,
    })
  }, [showToast])

  useEffect(() => {
    let disposed = false

    const syncCurrentModel = async () => {
      try {
        const res = await currentModel()
        if (!res.ok) {
          throw new Error(await parseResponseError(res))
        }
        const currentModelJson = await res.json()
        if (!disposed && isAIModel(currentModelJson.model)) {
          setSettingState(old => {
            return { ...old, model: currentModelJson.model }
          })
        }
      } catch (error: unknown) {
        if (disposed) {
          return
        }
        showToast({
          desc: errorMessage(error, 'Unable to read current model'),
          state: 'error',
          duration: SHORT_TOAST_DURATION,
        })
      }
    }

    syncCurrentModel()

    return () => {
      disposed = true
    }
  }, [setSettingState, showToast])

  return (
    <>
      {isSD ? <SidePanel /> : null}
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
