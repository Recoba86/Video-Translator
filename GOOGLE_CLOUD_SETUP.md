# 🔑 Google Cloud API Setup Guide

## What You Need

This project uses **Google Cloud APIs** for:
- 🎤 **Speech-to-Text API** - Transcribing video audio
- 🔄 **Translation API** - Translating to Persian/Farsi

---

## Step-by-Step Setup

### 1. Create Google Cloud Account

1. Go to: https://console.cloud.google.com
2. Sign in with your Google account
3. Accept terms of service

### 2. Create a New Project

1. Click the project dropdown (top left)
2. Click "New Project"
3. Name it: `video-subtitler` (or any name)
4. Click "Create"
5. **Wait for project creation** (takes 10-20 seconds)
6. Select your new project from the dropdown

### 3. Enable Billing

⚠️ **IMPORTANT**: These APIs require billing to be enabled

1. Go to: https://console.cloud.google.com/billing
2. Click "Link a Billing Account"
3. Create a new billing account or select existing
4. Add payment method (credit/debit card)

**Don't worry about costs!** Both APIs have generous free tiers:
- Speech-to-Text: **60 minutes FREE per month**
- Translation: **500,000 characters FREE per month**

Example: A 10-minute video typically costs **$0.04-0.10** beyond free tier.

### 4. Enable Required APIs

#### Option A: Via Console (Easy)

**Enable Speech-to-Text API:**
1. Go to: https://console.cloud.google.com/apis/library/speech.googleapis.com
2. Click "Enable"
3. Wait for confirmation

**Enable Translation API:**
1. Go to: https://console.cloud.google.com/apis/library/translate.googleapis.com
2. Click "Enable"
3. Wait for confirmation

#### Option B: Via Command Line

```bash
# Install gcloud CLI first: https://cloud.google.com/sdk/docs/install

# Enable both APIs
gcloud services enable speech.googleapis.com
gcloud services enable translate.googleapis.com
```

### 5. Create Service Account

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click "Create Service Account"
3. **Service account name**: `video-subtitler`
4. Click "Create and Continue"

5. **Grant Roles** - Add these two roles:
   - Click "Select a role"
   - Search and add: `Cloud Speech Client`
   - Click "Add Another Role"
   - Search and add: `Cloud Translation API User`
   
6. Click "Continue"
7. Click "Done"

### 6. Create and Download Key

1. Click on your newly created service account
2. Go to "Keys" tab
3. Click "Add Key" → "Create New Key"
4. Select **JSON** format
5. Click "Create"
6. **A JSON file will download automatically** - this is your credentials file!

### 7. Configure Your Project

1. **Rename** the downloaded file to `google-credentials.json`
2. **Move** it to your project root:
   ```bash
   mv ~/Downloads/video-subtitler-*.json /Users/amin/Documents/Witamin-Game/Video-Translator/Video-Translator/google-credentials.json
   ```

3. **Update `.env` file**:
   ```bash
   # Open .env and verify this line:
   GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json
   ```

### 8. Verify Setup

Run the installation test:
```bash
python test_installation.py
```

Should show:
```
✅ Google Cloud Credentials File
✅ Google Cloud Credentials - Valid JSON format
```

---

## 🎯 Quick Setup Commands

```bash
# 1. Download your JSON key from Google Cloud Console
# 2. Move and rename it:
mv ~/Downloads/your-project-*.json ./google-credentials.json

# 3. Verify the file exists:
ls -lh google-credentials.json

# 4. Test the setup:
python test_installation.py
```

---

## 💰 Cost Estimation

### Free Tier (Monthly)
- Speech-to-Text: 60 minutes
- Translation: 500,000 characters

### Beyond Free Tier
- Speech-to-Text: ~$0.024 per minute ($1.44 per hour)
- Translation: ~$20 per million characters

### Example Costs
| Video Length | Approximate Cost |
|--------------|------------------|
| 1 minute     | FREE (within quota) |
| 5 minutes    | FREE (within quota) |
| 60 minutes   | FREE (at quota limit) |
| 120 minutes  | ~$1.44 |
| 300 minutes  | ~$3.60 |

**Pro Tip**: Use short test videos first to stay within free tier!

---

## 🔒 Security Best Practices

### ✅ DO:
- Keep `google-credentials.json` private
- Add it to `.gitignore` (already done)
- Use service accounts (not personal accounts)
- Restrict API keys to specific IPs in production
- Enable monitoring and alerts

### ❌ DON'T:
- Commit credentials to git
- Share credentials publicly
- Use the same credentials for multiple projects
- Leave credentials on public servers

---

## 🐛 Troubleshooting

### "Billing not enabled"
→ Enable billing at: https://console.cloud.google.com/billing

### "API not enabled"
→ Enable APIs at:
- https://console.cloud.google.com/apis/library/speech.googleapis.com
- https://console.cloud.google.com/apis/library/translate.googleapis.com

### "Invalid credentials"
→ Re-download JSON key from service account page

### "Permission denied"
→ Ensure service account has both required roles:
  - Cloud Speech Client
  - Cloud Translation API User

### "Quota exceeded"
→ Check usage at: https://console.cloud.google.com/apis/dashboard
→ Either wait for quota reset or upgrade billing

---

## 📊 Monitor Your Usage

Track your API usage:
1. Go to: https://console.cloud.google.com/apis/dashboard
2. Select your project
3. View metrics for:
   - Speech-to-Text API
   - Translation API

Set up billing alerts:
1. Go to: https://console.cloud.google.com/billing/budgets
2. Create budget alert (e.g., alert at $5)
3. Get email notifications

---

## 🆘 Need Help?

- **Google Cloud Documentation**: https://cloud.google.com/docs
- **Speech-to-Text Docs**: https://cloud.google.com/speech-to-text/docs
- **Translation Docs**: https://cloud.google.com/translate/docs
- **Pricing Calculator**: https://cloud.google.com/products/calculator

---

## ✅ Setup Checklist

- [ ] Google Cloud account created
- [ ] Project created
- [ ] Billing enabled
- [ ] Speech-to-Text API enabled
- [ ] Translation API enabled
- [ ] Service account created with correct roles
- [ ] JSON credentials downloaded
- [ ] File renamed to `google-credentials.json`
- [ ] File moved to project root
- [ ] `.env` file updated
- [ ] Test passed (`python test_installation.py`)

---

**Once all steps are complete, you're ready to run the application!**

```bash
./start.sh
```

**Happy subtitling! 🎬**
