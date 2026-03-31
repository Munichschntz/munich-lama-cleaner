import React from 'react'
import { useSetRecoilState } from 'recoil'
import { batchFilesState, batchIndexState, fileState } from '../../store/Atoms'
import FileSelect from '../FileSelect/FileSelect'

const LandingPage = () => {
  const setFile = useSetRecoilState(fileState)
  const setBatchFiles = useSetRecoilState(batchFilesState)
  const setBatchIndex = useSetRecoilState(batchIndexState)

  return (
    <div className="landing-page">
      <h1>
        Image inpainting powered by 🦙
        <a href="https://github.com/saic-mdal/lama">LaMa</a>
      </h1>
      <div className="landing-file-selector">
        <FileSelect
          onSelection={async (f, files) => {
            setBatchFiles(files)
            setBatchIndex(0)
            setFile(f)
          }}
        />
      </div>
    </div>
  )
}

export default LandingPage
