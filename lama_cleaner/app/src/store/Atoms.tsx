import { atom, AtomEffect, DefaultValue, selector } from 'recoil'
import _ from 'lodash'
import { HDStrategy, LDMSampler } from '../components/Settings/HDSettingBlock'
import { ToastState } from '../components/shared/Toast'

export enum AIModel {
  LAMA = 'lama',
  LDM = 'ldm',
  ZITS = 'zits',
  MAT = 'mat',
  FCF = 'fcf',
  SD14 = 'sd1.4',
  CV2 = 'cv2',
}

export const fileState = atom<File | undefined>({
  key: 'fileState',
  default: undefined,
})

export interface Rect {
  x: number
  y: number
  width: number
  height: number
}

interface AppState {
  disableShortCuts: boolean
  isInpainting: boolean
  inpaintingMessage: string
  inpaintingProgress: number | null
}

export const appState = atom<AppState>({
  key: 'appState',
  default: {
    disableShortCuts: false,
    isInpainting: false,
    inpaintingMessage: '',
    inpaintingProgress: null,
  },
})

export const promptState = atom<string>({
  key: 'promptState',
  default: '',
})

/** @deprecated Use promptState instead */
export const propmtState = promptState

export const isInpaintingState = selector<boolean>({
  key: 'isInpainting',
  get: ({ get }) => {
    const app = get(appState)
    return app.isInpainting
  },
  set: ({ get, set }, newValue: boolean | DefaultValue) => {
    if (newValue instanceof DefaultValue) {
      return
    }
    const app = get(appState)
    if (newValue) {
      set(appState, {
        ...app,
        isInpainting: true,
        inpaintingMessage: 'Inpainting...',
      })
      return
    }
    set(appState, {
      ...app,
      isInpainting: false,
      inpaintingMessage: '',
      inpaintingProgress: null,
    })
  },
})

export const cropperState = atom<Rect>({
  key: 'cropperState',
  default: {
    x: 0,
    y: 0,
    width: 512,
    height: 512,
  },
})

export const cropperX = selector<number>({
  key: 'cropperX',
  get: ({ get }) => get(cropperState).x,
  set: ({ get, set }, newValue: number | DefaultValue) => {
    if (newValue instanceof DefaultValue) {
      return
    }
    const rect = get(cropperState)
    set(cropperState, { ...rect, x: newValue })
  },
})

export const cropperY = selector<number>({
  key: 'cropperY',
  get: ({ get }) => get(cropperState).y,
  set: ({ get, set }, newValue: number | DefaultValue) => {
    if (newValue instanceof DefaultValue) {
      return
    }
    const rect = get(cropperState)
    set(cropperState, { ...rect, y: newValue })
  },
})

export const cropperHeight = selector<number>({
  key: 'cropperHeight',
  get: ({ get }) => get(cropperState).height,
  set: ({ get, set }, newValue: number | DefaultValue) => {
    if (newValue instanceof DefaultValue) {
      return
    }
    const rect = get(cropperState)
    set(cropperState, { ...rect, height: newValue })
  },
})

export const cropperWidth = selector<number>({
  key: 'cropperWidth',
  get: ({ get }) => get(cropperState).width,
  set: ({ get, set }, newValue: number | DefaultValue) => {
    if (newValue instanceof DefaultValue) {
      return
    }
    const rect = get(cropperState)
    set(cropperState, { ...rect, width: newValue })
  },
})

interface ToastAtomState {
  open: boolean
  desc: string
  state: ToastState
  duration: number
}

export const toastState = atom<ToastAtomState>({
  key: 'toastState',
  default: {
    open: false,
    desc: '',
    state: 'default',
    duration: 3000,
  },
})

export const shortcutsState = atom<boolean>({
  key: 'shortcutsState',
  default: false,
})

export interface HDSettings {
  hdStrategy: HDStrategy
  hdStrategyResizeLimit: number
  hdStrategyCropTriggerSize: number
  hdStrategyCropMargin: number
  enabled: boolean
}

type ModelsHDSettings = { [key in AIModel]: HDSettings }

export enum CV2Flag {
  INPAINT_NS = 'INPAINT_NS',
  INPAINT_TELEA = 'INPAINT_TELEA',
}

export interface Settings {
  show: boolean
  showCropper: boolean
  downloadMask: boolean
  graduallyInpainting: boolean
  runInpaintingManually: boolean
  model: AIModel
  hdSettings: ModelsHDSettings

  // For LDM
  ldmSteps: number
  ldmSampler: LDMSampler

  // For ZITS
  zitsWireframe: boolean

  // For SD
  qualityPreset: QualityPreset
  sdMaskBlur: number
  sdMode: SDMode
  sdStrength: number
  sdSteps: number
  sdGuidanceScale: number
  sdSampler: SDSampler
  sdSeed: number
  sdSeedFixed: boolean // true: use sdSeed, false: random generate seed on backend
  sdNumSamples: number

  // For OpenCV2
  cv2Radius: number
  cv2Flag: CV2Flag

  // tiled inference
  enableTiling: boolean
  tileSize: number
  tileOverlap: number
}

const defaultHDSettings: ModelsHDSettings = {
  [AIModel.LAMA]: {
    hdStrategy: HDStrategy.RESIZE,
    hdStrategyResizeLimit: 2048,
    hdStrategyCropTriggerSize: 2048,
    hdStrategyCropMargin: 128,
    enabled: true,
  },
  [AIModel.LDM]: {
    hdStrategy: HDStrategy.CROP,
    hdStrategyResizeLimit: 1080,
    hdStrategyCropTriggerSize: 1080,
    hdStrategyCropMargin: 128,
    enabled: true,
  },
  [AIModel.ZITS]: {
    hdStrategy: HDStrategy.CROP,
    hdStrategyResizeLimit: 1024,
    hdStrategyCropTriggerSize: 1024,
    hdStrategyCropMargin: 128,
    enabled: true,
  },
  [AIModel.MAT]: {
    hdStrategy: HDStrategy.CROP,
    hdStrategyResizeLimit: 1024,
    hdStrategyCropTriggerSize: 512,
    hdStrategyCropMargin: 128,
    enabled: true,
  },
  [AIModel.FCF]: {
    hdStrategy: HDStrategy.CROP,
    hdStrategyResizeLimit: 512,
    hdStrategyCropTriggerSize: 512,
    hdStrategyCropMargin: 128,
    enabled: false,
  },
  [AIModel.SD14]: {
    hdStrategy: HDStrategy.ORIGINAL,
    hdStrategyResizeLimit: 768,
    hdStrategyCropTriggerSize: 512,
    hdStrategyCropMargin: 128,
    enabled: true,
  },
  [AIModel.CV2]: {
    hdStrategy: HDStrategy.RESIZE,
    hdStrategyResizeLimit: 1080,
    hdStrategyCropTriggerSize: 512,
    hdStrategyCropMargin: 128,
    enabled: true,
  },
}

export enum SDSampler {
  ddim = 'ddim',
  pndm = 'pndm',
}

export enum SDMode {
  text2img = 'text2img',
  img2img = 'img2img',
  inpainting = 'inpainting',
}

export enum QualityPreset {
  fast = 'fast',
  balanced = 'balanced',
  best = 'best',
}

export const settingStateDefault: Settings = {
  show: false,
  showCropper: false,
  downloadMask: false,
  graduallyInpainting: true,
  runInpaintingManually: false,
  model: AIModel.LAMA,
  hdSettings: defaultHDSettings,

  ldmSteps: 25,
  ldmSampler: LDMSampler.plms,

  zitsWireframe: true,

  // SD
  qualityPreset: QualityPreset.balanced,
  sdMaskBlur: 5,
  sdMode: SDMode.inpainting,
  sdStrength: 0.75,
  sdSteps: 50,
  sdGuidanceScale: 7.5,
  sdSampler: SDSampler.ddim,
  sdSeed: 42,
  sdSeedFixed: true,
  sdNumSamples: 1,

  // CV2
  cv2Radius: 5,
  cv2Flag: CV2Flag.INPAINT_NS,

  // tiled inference
  enableTiling: false,
  tileSize: 1024,
  tileOverlap: 64,
}

const localStorageEffect =
  (key: string) =>
  ({ setSelf, onSet }: AtomEffect<Settings>) => {
    const savedValue = localStorage.getItem(key)
    if (savedValue != null) {
      const storageSettings = JSON.parse(savedValue)
      storageSettings.show = false

      if (
        storageSettings.showCroper !== undefined &&
        storageSettings.showCropper === undefined
      ) {
        storageSettings.showCropper = storageSettings.showCroper
      }
      if (storageSettings.hdSettings) {
        type LegacyModelSettings = {
          hdStrategyCropTrigerSize?: number
          hdStrategyCropTriggerSize?: number
          [key: string]: unknown
        }
        const hdSettings = storageSettings.hdSettings as Record<
          string,
          LegacyModelSettings
        >
        storageSettings.hdSettings = Object.fromEntries(
          Object.entries(hdSettings).map(([modelName, modelSettings]) => {
            if (
              modelSettings?.hdStrategyCropTrigerSize !== undefined &&
              modelSettings.hdStrategyCropTriggerSize === undefined
            ) {
              return [
                modelName,
                {
                  ...modelSettings,
                  hdStrategyCropTriggerSize: modelSettings.hdStrategyCropTrigerSize,
                },
              ]
            }
            return [modelName, modelSettings]
          })
        )
      }

      const restored = _.merge(
        _.cloneDeep(settingStateDefault),
        storageSettings
      )
      // Guard: if the restored model key isn't present in hdSettings (e.g. stale
      // or outdated localStorage from a previous app version), reset to the default
      // model so that hdSettings lookup never returns undefined.
      if (!(restored.model in restored.hdSettings)) {
        restored.model = settingStateDefault.model
      }
      setSelf(restored)
    }

    onSet((newValue: Settings, _oldValue: Settings, isReset: boolean) =>
      isReset
        ? localStorage.removeItem(key)
        : localStorage.setItem(key, JSON.stringify(newValue))
    )
  }

const ROOT_STATE_KEY = 'settingsState3'
// Each atom can reference an array of these atom effect functions which are called in priority order when the atom is initialized
// https://recoiljs.org/docs/guides/atom-effects/#local-storage-persistence
export const settingState = atom<Settings>({
  key: ROOT_STATE_KEY,
  default: settingStateDefault,
  effects: [localStorageEffect(ROOT_STATE_KEY)],
})

export const seedState = selector<number>({
  key: 'seed',
  get: ({ get }) => {
    const settings = get(settingState)
    return settings.sdSeed
  },
  set: ({ get, set }, newValue: number | DefaultValue) => {
    if (newValue instanceof DefaultValue) {
      return
    }
    const settings = get(settingState)
    set(settingState, { ...settings, sdSeed: newValue })
  },
})

export const hdSettingsState = selector<HDSettings>({
  key: 'hdSettings',
  get: ({ get }) => {
    const settings = get(settingState)
    return settings.hdSettings[settings.model]
  },
  set: ({ get, set }, newValue: Partial<HDSettings> | DefaultValue) => {
    if (newValue instanceof DefaultValue) {
      return
    }
    const settings = get(settingState)
    const hdSettings = settings.hdSettings[settings.model]
    const newHDSettings = { ...hdSettings, ...newValue }

    set(settingState, {
      ...settings,
      hdSettings: { ...settings.hdSettings, [settings.model]: newHDSettings },
    })
  },
})

export const isSDState = selector({
  key: 'isSD',
  get: ({ get }) => {
    const settings = get(settingState)
    return settings.model === AIModel.SD14
  },
})

export const runManuallyState = selector({
  key: 'runManuallyState',
  get: ({ get }) => {
    const settings = get(settingState)
    const isSD = get(isSDState)
    return settings.runInpaintingManually || isSD
  },
})
