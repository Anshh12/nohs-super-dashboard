# Streamlit Community Cloud Deployment

The deployment entrypoint is `app.py`. It runs the verified `super_dashboard_production_v _dc_8_09_2026.py` dashboard.

## Deploy

1. Open https://share.streamlit.io/ and sign in with the GitHub account that can access the private repository.
2. Select **New app**.
3. Repository: `Anshh12/nohs-super-dashboard`.
4. Branch: `main`.
5. Main file path: `app.py`.
6. Select **Deploy**.

The app may take a few minutes to install dependencies and start.

## Required repository files

- `app.py`: Streamlit Cloud entrypoint.
- `super_dashboard_production_v _dc_8_09_2026.py`: dashboard implementation.
- `requirements_super_dashboard.txt`: Python dependencies.

If Streamlit Cloud asks for the dependency filename, use `requirements_super_dashboard.txt` or rename it to `requirements.txt` before deployment. The current project keeps the original dependency filename for compatibility with the existing workspace.

## Update the deployed app

After code changes:

```powershell
git add .
git commit -m "Update NOHS dashboard"
git push origin main
```

Streamlit Cloud will redeploy the `main` branch automatically.
