# TradeSensei AI - Public Deployment Guide

## 🚀 Making TradeSensei AI Publicly Available

Follow these steps to deploy TradeSensei AI for public use.

### 1. Host the Backend on Railway

1. **Create Railway Account**: Go to [railway.app](https://railway.app) and sign up.
2. **Connect Repository**: Link your GitHub repo containing `src/python_backend`.
3. **Deploy**: Railway auto-detects the `Dockerfile` and deploys the FastAPI app.
4. **Set Environment Variables** in Railway dashboard:
   ```
   OPENAI_API_KEY=your-openai-key
   ELEVENLABS_API_KEY=your-elevenlabs-key
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_SECRET=your-service-role-key
   ```
5. **Get Public URL**: e.g., `https://tradesensei-backend.up.railway.app`

### 2. Update Desktop App Configuration

1. **Edit App.config** in `src/csharp_ui/`:
   ```xml
   <configuration>
     <appSettings>
       <add key="ApiBaseUrl" value="https://your-railway-url" />
       <add key="OpenAiApiKey" value="" />
       <add key="ElevenLabsApiKey" value="" />
     </appSettings>
   </configuration>
   ```
   - Leave API keys empty for user-provided keys.

2. **Build the App**:
   - Open `TradeSensei.UI.csproj` in Visual Studio.
   - Go to **Build > Publish**.
   - Choose **Folder** publish method.
   - Select **Self-contained** and **win-x64**.
   - Publish to a folder (e.g., `publish/`).

3. **Create Installer** (Optional):
   - Use [Inno Setup](https://jrsoftware.org/isinfo.php) to create an MSI installer.
   - Bundle the published files and create a setup wizard.

### 3. Handle API Keys for Public Users

- **User-Provided Keys**: Users enter their own OpenAI/ElevenLabs keys in app settings.
- **Centralized Keys**: Use your keys for free tier, implement subscriptions for premium.
- **Hybrid**: Free with limits, paid for unlimited.

### 4. Create Download Website

1. **Use GitHub Pages**:
   - Create `docs/index.html` in your repo.
   - Enable Pages in repo settings.

2. **Sample Landing Page**:
   ```html
   <!DOCTYPE html>
   <html>
   <head>
       <title>TradeSensei AI - AI Trading Mentor</title>
   </head>
   <body>
       <h1>TradeSensei AI</h1>
       <p>Real-time AI trading mentor with voice chat, webcam analysis, and overlay tools.</p>
       <a href="https://github.com/your-repo/releases/download/v1.0/TradeSenseiAI-Setup.exe">Download for Windows</a>
   </body>
   </html>
   ```

3. **Upload Installer**:
   - Go to GitHub Releases.
   - Upload the EXE/MSI file.
   - Update download link in the page.

### 5. Security and Compliance

- **HTTPS**: Railway provides SSL automatically.
- **Rate Limiting**: Add to FastAPI for abuse prevention.
- **Data Privacy**: Supabase handles GDPR-compliant storage.
- **Updates**: Implement auto-updater with Squirrel.Windows.

### 6. Testing and Launch

- **Test End-to-End**: Install on a fresh Windows machine, connect to hosted backend.
- **Monitor**: Check Railway logs for errors.
- **Marketing**: Share on trading forums, Reddit r/algotrading, social media.

## 📋 Checklist

- [ ] Railway account created
- [ ] Backend deployed
- [ ] WPF config updated
- [ ] App published
- [ ] Installer created
- [ ] Download website live
- [ ] API keys handled
- [ ] Security measures in place
- [ ] Tested on fresh machine

TradeSensei AI is now ready for public distribution! 🎉