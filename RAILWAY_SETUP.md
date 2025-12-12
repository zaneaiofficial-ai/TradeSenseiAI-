# Railway Deployment Steps

## Quick Setup

1. **Install Railway CLI** (optional but recommended):
   ```powershell
   npm i -g @railway/cli
   railway login
   ```

2. **Link Project via VS Code Extension**:
   - Install the Railway extension in VS Code
   - Command Palette → `Railway: Login`
   - `Railway: Link to Existing Project` or `Railway: Create New Project`
   - Select service folder: `TradeSenseiAI/src/python_backend`

3. **Set Environment Variables** in Railway Dashboard:
   - Go to your project → Variables tab
   - Add these variables:
     ```
     OPENAI_API_KEY=your-key-here
     ELEVENLABS_API_KEY=your-key-here
     SUPABASE_URL=https://your-project.supabase.co
     SUPABASE_KEY=your-anon-key
     SUPABASE_SECRET=your-service-role-key
     PORT=8000
     ```

4. **Deploy**:
   - Railway auto-deploys on push to main (via GitHub integration)
   - Or manually: `railway up` from `src/python_backend`

5. **Get Public URL**:
   - Railway dashboard → your service → Settings → Generate Domain
   - Copy the URL (e.g., `https://tradesensei-backend.up.railway.app`)

6. **Update Desktop App**:
   - Edit `src/csharp_ui/App.config`:
     ```xml
     <add key="ApiBaseUrl" value="https://your-railway-url" />
     ```
   - Rebuild: `dotnet publish -c Release -r win-x64 --self-contained`

## GitHub Actions Auto-Deploy

The workflow in `.github/workflows/railway-deploy.yml` will auto-deploy on pushes to `main` affecting `src/python_backend/**`.

**Required Secret**:
- GitHub repo → Settings → Secrets → Actions → New secret
- Name: `RAILWAY_TOKEN`
- Value: Generate at railway.app → Account → Tokens

## Verify Deployment

- Health check: `https://your-railway-url/`
- API docs: `https://your-railway-url/docs`
