# DiamondDust Trial Client Frontend

React/Vite source for the lightweight local trial client.

The frontend talks only to the local Python trial-client API. Domain
validation, provider execution, artifact persistence, and formal-vault safety
remain in Python.

## Development

Start the Python backend:

```bash
PYTHONPATH=src .venv/bin/python -m diamonddust trial-client
```

Then run the frontend dev server:

```bash
cd frontend/trial-client
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173/
```

## Built Frontend

Build:

```bash
npm run build
```

Serve the built files from the Python backend:

```bash
PYTHONPATH=src .venv/bin/python -m diamonddust trial-client \
  --frontend-dist frontend/trial-client/dist
```
