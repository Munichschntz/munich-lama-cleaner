import React, { useCallback } from 'react'
import { useRecoilState } from 'recoil'
import * as PopoverPrimitive from '@radix-ui/react-popover'
import { useToggle } from 'react-use'
import { SDSampler, settingState } from '../../store/Atoms'
import NumberInputSetting from '../Settings/NumberInputSetting'
import SettingBlock from '../Settings/SettingBlock'
import Selector from '../shared/Selector'
import { Switch, SwitchThumb } from '../shared/Switch'

const INPUT_WIDTH = 30

// TODO: 添加收起来的按钮
const SidePanel = () => {
  const [open, toggleOpen] = useToggle(true)
  const [setting, setSettingState] = useRecoilState(settingState)

  const updateSetting = useCallback(
    (patch: Partial<typeof setting>) => {
      setSettingState(old => {
        return { ...old, ...patch }
      })
    },
    [setSettingState, setting]
  )

  const intOrZero = (value: string): number => {
    return value.length === 0 ? 0 : parseInt(value, 10)
  }

  const floatOrZero = (value: string): number => {
    return value.length === 0 ? 0 : parseFloat(value)
  }

  return (
    <div className="side-panel">
      <PopoverPrimitive.Root open={open}>
        <PopoverPrimitive.Trigger
          className="btn-primary side-panel-trigger"
          onClick={() => toggleOpen()}
        >
          Stable Diffusion
        </PopoverPrimitive.Trigger>
        <PopoverPrimitive.Portal>
          <PopoverPrimitive.Content className="side-panel-content">
            <SettingBlock
              title="Show Cropper"
              input={
                <Switch
                  checked={setting.showCropper}
                  onCheckedChange={value => {
                    updateSetting({ showCropper: value })
                  }}
                >
                  <SwitchThumb />
                </Switch>
              }
            />
            {/* 
            <NumberInputSetting
              title="Num Samples"
              width={INPUT_WIDTH}
              value={`${setting.sdNumSamples}`}
              desc=""
              onValue={value => {
                const val = value.length === 0 ? 0 : parseInt(value, 10)
                setSettingState(old => {
                  return { ...old, sdNumSamples: val }
                })
              }}
            /> */}

            <NumberInputSetting
              title="Steps"
              width={INPUT_WIDTH}
              value={`${setting.sdSteps}`}
              desc="Large steps result in better result, but more time-consuming"
              onValue={value => {
                updateSetting({ sdSteps: intOrZero(value) })
              }}
            />

            <NumberInputSetting
              title="Strength"
              width={INPUT_WIDTH}
              allowFloat
              value={`${setting.sdStrength}`}
              desc="How strongly the model transforms the masked area (0-1). Lower values preserve more of the original image."
              onValue={value => {
                updateSetting({ sdStrength: floatOrZero(value) })
              }}
            />

            <NumberInputSetting
              title="Guidance Scale"
              width={INPUT_WIDTH}
              allowFloat
              value={`${setting.sdGuidanceScale}`}
              desc="How closely the output follows the text prompt. Higher values give more prompt-aligned results but reduce variety."
              onValue={value => {
                updateSetting({ sdGuidanceScale: floatOrZero(value) })
              }}
            />

            <NumberInputSetting
              title="Mask Blur"
              width={INPUT_WIDTH}
              value={`${setting.sdMaskBlur}`}
              desc="Gaussian blur radius applied to mask edges before inpainting. Creates smoother transitions between inpainted and original areas."
              onValue={value => {
                updateSetting({ sdMaskBlur: intOrZero(value) })
              }}
            />

            <SettingBlock
              className="sub-setting-block"
              title="Sampler"
              input={
                <Selector
                  width={80}
                  value={setting.sdSampler as string}
                  options={Object.values(SDSampler)}
                  onChange={val => {
                    const sampler = val as SDSampler
                    updateSetting({ sdSampler: sampler })
                  }}
                />
              }
            />

            <SettingBlock
              title="Seed"
              input={
                <div
                  style={{
                    display: 'flex',
                    gap: 0,
                    justifyContent: 'center',
                    alignItems: 'center',
                  }}
                >
                  {/* 每次会从服务器返回更新该值 */}
                  <NumberInputSetting
                    title=""
                    width={80}
                    value={`${setting.sdSeed}`}
                    desc=""
                    disable={!setting.sdSeedFixed}
                    onValue={value => {
                      updateSetting({ sdSeed: intOrZero(value) })
                    }}
                  />
                  <Switch
                    checked={setting.sdSeedFixed}
                    onCheckedChange={value => {
                      updateSetting({ sdSeedFixed: value })
                    }}
                    style={{ marginLeft: '8px' }}
                  >
                    <SwitchThumb />
                  </Switch>
                </div>
              }
            />
          </PopoverPrimitive.Content>
        </PopoverPrimitive.Portal>
      </PopoverPrimitive.Root>
    </div>
  )
}

export default SidePanel
