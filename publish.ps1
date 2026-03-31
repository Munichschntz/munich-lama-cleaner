$ErrorActionPreference = "Stop"

Push-Location "./lama_cleaner/app"
yarn run build
Pop-Location

if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}

python setup.py sdist bdist_wheel
twine upload dist/*
