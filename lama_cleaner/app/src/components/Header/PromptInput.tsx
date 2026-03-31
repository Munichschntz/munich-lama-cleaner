import React, { FormEvent, useEffect, useRef } from 'react'
import { useClickAway } from 'react-use'
import { useRecoilState } from 'recoil'
import emitter, { EVENT_PROMPT } from '../../event'
import { appState, promptState } from '../../store/Atoms'
import { serverStatus } from '../../adapters/inpainting'
import Button from '../shared/Button'
import TextInput from '../shared/Input'

// TODO: show progress in input
const PromptInput = () => {
  const [app, setAppState] = useRecoilState(appState)
  const [prompt, setPrompt] = useRecoilState(promptState)
  const ref = useRef(null)

  useEffect(() => {
    if (!app.isInpainting) {
      return
    }

    const interval = window.setInterval(async () => {
      try {
        const status = await serverStatus()
        setAppState(old => ({
          ...old,
          inpaintingMessage: status.message,
          inpaintingProgress: status.progress,
        }))
      } catch {
        // Ignore status polling errors while a request is in flight.
      }
    }, 700)

    return () => {
      window.clearInterval(interval)
    }
  }, [app.isInpainting, setAppState])

  const handleOnInput = (evt: FormEvent<HTMLInputElement>) => {
    evt.preventDefault()
    evt.stopPropagation()
    const target = evt.target as HTMLInputElement
    setPrompt(target.value)
  }

  const handleRepaintClick = () => {
    if (prompt.length !== 0 && !app.isInpainting) {
      emitter.emit(EVENT_PROMPT)
    }
  }

  useClickAway<MouseEvent>(ref, () => {
    if (ref?.current) {
      const input = ref.current as HTMLInputElement
      input.blur()
    }
  })

  const onKeyUp = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleRepaintClick()
    }
  }

  const buttonText = app.isInpainting
    ? `${app.inpaintingMessage || 'Inpainting...'}${
        app.inpaintingProgress !== null ? ` ${app.inpaintingProgress}%` : ''
      }`
    : 'Dream'

  return (
    <div className="prompt-wrapper">
      <TextInput
        ref={ref}
        value={prompt}
        onInput={handleOnInput}
        onKeyUp={onKeyUp}
        placeholder="I want to repaint of..."
      />
      <Button
        border
        onClick={handleRepaintClick}
        disabled={prompt.length === 0 || app.isInpainting}
      >
        {buttonText}
      </Button>
    </div>
  )
}

export default PromptInput
