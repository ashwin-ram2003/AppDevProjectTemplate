# Deployment (TD-08 / OPS-01 / R2-3)

The app deploys as **one service on one public URL**. The Flask process
serves both the JSON API and the compiled React client, so there is no
second frontend host, no CORS configuration, and one link to hand the
instructor.

## How the pieces fit

`Dockerfile` builds in two stages. Stage one uses Node to compile the React
client to static files. Stage two is a Python image that installs the
backend, copies in only the compiled output, and runs it under gunicorn.
Node is gone from the shipped image.

That two-stage shape is what lets a Python host run a React frontend. It
also keeps the image portable, so nothing below is locked to one provider.

At runtime the host sets `PORT`, gunicorn binds it, and `CLIENT_DIST`
points Flask at the compiled client.

## First deploy on Render

Render's free tier needs no credit card.

1. Push this branch to `main`.
2. In Render, choose **New > Blueprint** and point it at the repository.
   It reads `render.yaml` and proposes one web service.
   (If the blueprint gives trouble, **New > Web Service**, pick the repo,
   choose **Docker**, and leave the rest at the defaults. Same result.)
3. When prompted for `MONGODB_URI`, paste the Atlas connection string.
   It is marked `sync: false` in `render.yaml`, so it is stored as a
   secret and never committed.
4. In Atlas, under **Network Access**, allow `0.0.0.0/0`. Render's free
   tier has no fixed outbound IP to allow-list instead.
5. Wait for the first build, then open the service URL.

Verify with `/healthz`, which answers without touching the database:

```
{"status":"ok","clientBuilt":true}
```

`clientBuilt: false` means the image shipped without the compiled client
and the page will 503.

## Environment variables

| Name | Required | Purpose |
|---|---|---|
| `MONGODB_URI` | yes | Atlas connection string. No default exists anywhere in the code. |
| `MONGODB_DB` | no | Database name. Defaults to `HaaSResourceManager`. |
| `PORT` | no | Set by the host. Defaults to 8000 in the image. |
| `CLIENT_DIST` | no | Path to the compiled client. Set inside the image. |

Copy `.env.example` to `server/.env` for local work. `.env` is gitignored.

## Before the connection string exists

The app deploys and serves the UI without `MONGODB_URI`. Any API call then
returns a clear `503 database_not_configured` with the fix in the message,
rather than an HTML stack trace. Set the variable in the host and the same
build starts working, with no redeploy needed beyond the restart.

## The free-tier catch

A free Render service sleeps after about 15 minutes of no traffic, and the
next request waits roughly 50 seconds while it wakes. A TA opening a cold
URL may well assume the app is broken.

Two ways to handle it, and they combine:

- Open the URL a minute before any demo or grading window.
- Point a free uptime pinger (UptimeRobot and similar) at `/healthz` every
  14 minutes. One always-on service fits inside the 750 free hours a month.

## Running the production build locally

```bash
cd client && npm ci && npm run build
cd ../server && pip install -r requirements.txt
gunicorn --bind 127.0.0.1:8000 app:app
```

Open `http://127.0.0.1:8000`. This is the same path the image takes, so it
is worth checking here before blaming the host.

`npm run dev` is still the loop for frontend work: Vite serves the client
and proxies `/api` to Flask on port 5050.

## Moving to another host

The image is standard, so the same `Dockerfile` runs on Fly.io, Railway,
Cloud Run, or anything else that takes a container. Only `render.yaml` is
provider-specific. Set the same environment variables and deploy.
