import { Rect, Settings } from '../store/Atoms'
import { dataURItoBlob } from '../utils'

const API_ENDPOINT_FROM_ENV = process.env.REACT_APP_INPAINTING_URL?.trim()

export const API_ENDPOINT = API_ENDPOINT_FROM_ENV || 'http://localhost:8080'
export const IS_API_ENDPOINT_FALLBACK = !API_ENDPOINT_FROM_ENV

export interface ServerStatus {
  phase: string
  message: string
  progress: number | null
  updated_at: number
  model: string | null
}

export interface ModelCapability {
  display_name: string
  recommended_resolution: string
  vram_estimate: string
  speed: string
  quality: string
}

async function parseError(res: Response): Promise<string> {
  try {
    const data = await res.json()
    return data?.error?.message || `Server error (${res.status})`
  } catch {
    return `Server error (${res.status})`
  }
}

export default async function inpaint(
  imageFile: File,
  maskBase64: string,
  settings: Settings,
  cropperRect: Rect,
  prompt?: string,
  sizeLimit?: string,
  seed?: number
): Promise<{ blob: string; seed: string | null }> {
  // 1080, 2000, Original
  const fd = new FormData()
  fd.append('image', imageFile)
  const mask = dataURItoBlob(maskBase64)
  fd.append('mask', mask)

  const hdSettings = settings.hdSettings[settings.model]
  if (!hdSettings) {
    throw new Error(
      `HD settings not found for model "${settings.model}". Please reload the page or re-select your model in Settings.`
    )
  }
  fd.append('ldmSteps', settings.ldmSteps.toString())
  fd.append('ldmSampler', settings.ldmSampler.toString())
  fd.append('zitsWireframe', settings.zitsWireframe.toString())
  fd.append('hdStrategy', hdSettings.hdStrategy)
  fd.append('hdStrategyCropMargin', hdSettings.hdStrategyCropMargin.toString())
  fd.append(
    'hdStrategyCropTriggerSize',
    hdSettings.hdStrategyCropTriggerSize.toString()
  )
  fd.append(
    'hdStrategyResizeLimit',
    hdSettings.hdStrategyResizeLimit.toString()
  )

  fd.append('prompt', prompt === undefined ? '' : prompt)
  fd.append('cropperX', cropperRect.x.toString())
  fd.append('cropperY', cropperRect.y.toString())
  fd.append('cropperHeight', cropperRect.height.toString())
  fd.append('cropperWidth', cropperRect.width.toString())
  fd.append('useCropper', settings.showCropper ? 'true' : 'false')
  fd.append('sdMaskBlur', settings.sdMaskBlur.toString())
  fd.append('qualityPreset', settings.qualityPreset.toString())
  fd.append('sdStrength', settings.sdStrength.toString())
  fd.append('sdSteps', settings.sdSteps.toString())
  fd.append('sdGuidanceScale', settings.sdGuidanceScale.toString())
  fd.append('sdSampler', settings.sdSampler.toString())
  fd.append('sdSeed', seed ? seed.toString() : '-1')
  fd.append('enableTiling', settings.enableTiling ? 'true' : 'false')
  fd.append('tileSize', settings.tileSize.toString())
  fd.append('tileOverlap', settings.tileOverlap.toString())

  fd.append('cv2Radius', settings.cv2Radius.toString())
  fd.append('cv2Flag', settings.cv2Flag.toString())

  if (sizeLimit === undefined) {
    fd.append('sizeLimit', '1080')
  } else {
    fd.append('sizeLimit', sizeLimit)
  }

  try {
    const res = await fetch(`${API_ENDPOINT}/inpaint`, {
      method: 'POST',
      body: fd,
    })
    if (!res.ok) {
      throw new Error(await parseError(res))
    }
    const blob = await res.blob()
    const newSeed = res.headers.get('x-seed')
    return { blob: URL.createObjectURL(blob), seed: newSeed }
  } catch (error: unknown) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Something went wrong on server side.')
  }
}

export function switchModel(name: string): Promise<Response> {
  const fd = new FormData()
  fd.append('name', name)
  return fetch(`${API_ENDPOINT}/model`, {
    method: 'POST',
    body: fd,
  })
}

export function currentModel(): Promise<Response> {
  return fetch(`${API_ENDPOINT}/model`, {
    method: 'GET',
  })
}

export function modelDownloaded(name: string): Promise<Response> {
  return fetch(`${API_ENDPOINT}/model_downloaded/${name}`, {
    method: 'GET',
  })
}

export async function modelCapabilities(): Promise<Record<string, ModelCapability>> {
  const res = await fetch(`${API_ENDPOINT}/model_capabilities`, {
    method: 'GET',
  })
  if (!res.ok) {
    throw new Error(await parseError(res))
  }
  return res.json()
}

export async function serverStatus(): Promise<ServerStatus> {
  const res = await fetch(`${API_ENDPOINT}/server_status`, {
    method: 'GET',
  })
  if (!res.ok) {
    throw new Error(await parseError(res))
  }
  return res.json()
}
