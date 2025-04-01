# meme_bot.py
from rich.console import Console
from Twilio import Twilio
from imgflip import AutoMeme, AIMeme

class MemeBot:
    def __init__(self):
        self.console = Console()
        # Initialize Twilio and Imgflip instances
        self.twilio = Twilio()
        self.automeme = AutoMeme()
        self.ai_meme = AIMeme()

    def process_message(self, message: str):
        # Determine the command and its arguments
        user_message_instruction = message.lower().split(" ")[0]
        prompt = message[len(user_message_instruction):].strip()
        
        if user_message_instruction == "help":
            self.handle_help()
        elif user_message_instruction in ("meme", "ai_meme"):
            self.handle_meme(user_message_instruction, prompt)
        else:
            # Fallback for unknown commands
            self.twilio.send_message(
                "Sorry, I didn't understand that command. Please use 'meme', 'ai_meme', or 'help'."
            )

    def handle_help(self):
        help_text = (
            "Help Menu:\n"
            "- Send 'meme <caption>' to generate a meme.\n"
            "- Send 'ai_meme <prompt>' to generate an AI meme.\n"
            "- Send '.' to exit."
        )
        self.twilio.send_message(help_text)
        self.console.print("Replied with help menu", style="bold green")

    def handle_meme(self, instruction: str, prompt: str):
        if instruction == "meme":
            response = self.automeme.send_caption_to_imgflip(caption=prompt)
        elif instruction == "ai_meme":
            response = self.ai_meme.send_ai_meme_to_imgflip(prompt=prompt)
        else:
            response = None

        if response:
            if response.get("success"):
                meme_url = response["data"]["url"]
                self.console.print(f"Meme generated: {meme_url}", style="bold blue")
                self.twilio.send_media_message(
                    "Here's your generated meme.", url_for_media=meme_url
                )
            else:
                error_message = response.get("error_message", "Unknown error")
                self.console.print(f"Failed to generate meme: {error_message}", style="bold red")
                self.twilio.send_message(f"Failed to generate meme: {error_message}")

    def run(self):
        self.console.print("MemeBot is running. Awaiting user messages...", style="bold green")
        while True:
            message = self.twilio.wait_for_user_message()
            if message == ".":
                self.console.print("Ending conversation as user sent '.'", style="bold red")
                break
            self.console.print(f"Received message: '{message}'", style="bold green")
            self.process_message(message)
