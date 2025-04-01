# 🤖 WhatsApp Meme Generator

Turn your WhatsApp into a meme factory! This bot uses Imgflip's powerful API to generate and send memes directly through WhatsApp. Whether you want AI-generated memes, caption your favorites, or create custom GIFs - we've got you covered! 🎨

<img width="1115" alt="Screenshot 2025-04-01 at 05 01 04" src="https://github.com/user-attachments/assets/1d6ff114-5673-4711-9178-e66e71e10228" />
meme-machine-web.vercel.app

## ✨ Features
- 🧠 AI-powered meme generation using Imgflip's API
- 📱 Direct WhatsApp integration via Twilio
- 🎯 No watermarks on generated memes
- 📊 Automatic metadata tracking of all your creations

## 🎮 WhatsApp Commands

Send these commands to your WhatsApp bot:

```
/ai_meme [text]     🤖 Generate an AI-powered meme based on your text
/auto [text]        🎲 Let Imgflip choose the perfect template for your text
/caption [id] [text]📝 Add your text to a specific meme template
/gif [id] [text]    ✨ Create an animated meme with your text
/search [query]     🔍 Search for meme templates
/help              ❓ Show all available commands
```

[Screenshots coming soon!]

## 🎨 What Imgflip Offers

Our integration leverages these awesome Imgflip features:

### 1. AI Meme Generation 🤖
- Uses OpenAI's model to understand your text
- Automatically selects the perfect template
- Generates clever captions that match your intent

### 2. Auto Meme Creation 🎲
- Analyzes your text to find the best matching template
- Automatically positions text for optimal impact
- Works great for quick, spontaneous memes

### 3. Custom Captioning 📝
- Access to 100+ popular meme templates
- Full control over text placement
- Support for custom fonts and styling

### 4. GIF Memes ✨
- Animate your memes with multiple text frames
- Perfect for reaction GIFs
- Supports popular animated templates

## 📊 Metadata Storage

All generated memes are tracked in `memes/meme_metadata.json`:

```json
{
  "memes": [
    {
      "timestamp": "2024-03-21T15:30:45",  // Creation timestamp
      "type": "ai",                        // Meme type (ai, auto, caption, gif)
      "query": "funny cat",                // Original query/text
      "imgflip_url": "https://i.imgflip.com/xxx.jpg",  // Direct image URL
      "page_url": "https://imgflip.com/i/xxx",         // Web page URL
      "template_id": 123456,               // Template ID (if used)
      "texts": ["Text 1", "Text 2"]        // Generated/used texts
    }
  ]
}
```

## 🚀 Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_API_KEY_SID=your_api_key_sid
TWILIO_API_KEY_SECRET=your_api_key_secret
TWILIO_CHAT_SERVICE_SID=your_chat_service_sid
TWILIO_PHONE_NUMBER=your_phone_number
IMGFLIP_USERNAME=your_imgflip_username
IMGFLIP_PASSWORD=your_imgflip_password
```

3. Start the application:
```bash
# Flask
python app.py

# Twilio and imgflip
python main.py
```

4. Set up Twilio webhook:
   - Go to your Twilio console
   - Configure the WhatsApp webhook URL to point to your server's `/webhook` endpoint
   - Ensure your server is accessible via HTTPS (required by Twilio)

## 📝 Usage Tips
- Start with `/help` to see all available commands
- For AI memes, be descriptive in your text prompt
- Use `/search` to find specific meme templates
- All memes are stored on Imgflip's servers and accessible via URLs in the metadata
- Browse your meme history in the metadata JSON file

## ⚠️ Notes
- Imgflip AI meme generation requires a Premium API subscription
- First 50 creations per month are included
- For best results, keep text prompts clear and concise
- Some templates work better with shorter text

## 📸 Examples
[Screenshots coming soon!]
