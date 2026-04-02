const fs = require('fs')
const path = require('path')

function hasLegacyOpenSSLFlag(nodeOptions) {
  if (!nodeOptions) {
    return false
  }
  return nodeOptions.includes('--openssl-legacy-provider')
}

function readApiEndpoint() {
  const appRoot = process.cwd()
  const envLocal = path.join(appRoot, '.env.local')
  const envFile = path.join(appRoot, '.env')

  const readFrom = filePath => {
    if (!fs.existsSync(filePath)) {
      return ''
    }
    const content = fs.readFileSync(filePath, 'utf8')
    const line = content
      .split(/\r?\n/)
      .find(entry => entry.startsWith('REACT_APP_INPAINTING_URL='))
    if (!line) {
      return ''
    }
    const value = line.substring('REACT_APP_INPAINTING_URL='.length)
    return value.replace(/^["']|["']$/g, '').trim()
  }

  return readFrom(envLocal) || readFrom(envFile)
}

function main() {
  const nodeVersion = process.versions.node
  const major = parseInt(nodeVersion.split('.')[0], 10)
  const nodeOptions = process.env.NODE_OPTIONS || ''
  const apiEndpoint = readApiEndpoint()

  console.log('[preflight] app path:', process.cwd())
  console.log('[preflight] node version:', nodeVersion)

  if (major >= 17 && !hasLegacyOpenSSLFlag(nodeOptions)) {
    console.warn(
      '[preflight] warning: Node >= 17 detected without --openssl-legacy-provider. Use `yarn build:win` on Windows.'
    )
  }

  if (!apiEndpoint) {
    console.warn(
      '[preflight] warning: REACT_APP_INPAINTING_URL is not set in .env.local/.env. App will use fallback http://localhost:8080.'
    )
  } else {
    console.log('[preflight] api endpoint:', apiEndpoint)
  }

  if (!fs.existsSync(path.join(process.cwd(), 'node_modules'))) {
    console.warn('[preflight] warning: node_modules not found. Run `yarn install`.')
  }

  console.log('[preflight] done')
}

main()
