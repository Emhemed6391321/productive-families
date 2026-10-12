set -e
cd "$(dirname "$0")"; mkdir -p dist
npx esbuild src/main.tsx --bundle --outfile=dist/app.js --define:process.env.NODE_ENV=\"production\" --loader:.ts=ts --log-level=warning
npx tailwindcss -i src/input.css -o dist/app.css --minify 2>&1 | tail -1
