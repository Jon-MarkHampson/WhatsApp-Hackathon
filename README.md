<<<<<<< HEAD
# WhatsApp Meme Generator

A WhatsApp bot that generates AI-powered memes using Imgflip's API and sends them through Twilio's WhatsApp integration.

## Features
- Generates AI-powered memes using Imgflip's API
- Responds to WhatsApp messages with the command `/ai_meme`
- Uses OpenAI's model for meme generation
- Sends memes without watermarks

## Setup

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

3. Run the application:
```bash
python app.py
```

4. Set up your Twilio webhook:
   - Go to your Twilio console
   - Configure the WhatsApp webhook URL to point to your server's `/webhook` endpoint
   - Make sure your server is accessible via HTTPS (required for Twilio)

## Usage
Send the command `/ai_meme` to your WhatsApp number to receive a randomly generated AI meme.

## Note
- The Imgflip AI meme generation requires a Premium API subscription
- First 50 creations per month are included, then $0.02 per creation
- The service uses OpenAI's model for meme generation 
=======




```bash
pip install -r requirements.txt
```
>>>>>>> 086905fd81a296898f597b87941ae4bc6164d532
