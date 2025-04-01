# meme_bot.py
from rich.console import Console
from Twilio import Twilio
from imgflip import AutoMeme, AIMeme, GetMeme, GetMemes, MemeSearch, CaptionImage
import random
import time

class MemeBot:
    def __init__(self):
        self.console = Console()
        # Initialize Twilio and Imgflip instances
        self.twilio = Twilio()
        self.automeme = AutoMeme()
        self.ai_meme = AIMeme()
        self.get_meme = GetMeme()
        self.get_memes = GetMemes()
        self.search_memes = MemeSearch()
        self.caption_image = CaptionImage()
        self.console.print("Meme Machine initialized.", style="bold green")

    def process_message(self, message: str):
        # Determine the command and its arguments
        user_message_instruction = message.lower().split(" ")[0]
        prompt = message[len(user_message_instruction):].strip()
        
        if user_message_instruction == "help":
            self.handle_help()
        elif user_message_instruction in ("meme", "generate"):
            self.handle_meme(user_message_instruction, prompt)
        elif user_message_instruction == "search":
            self.handle_search(prompt)
        elif user_message_instruction == "top":
            self.handle_top_templates()
        elif user_message_instruction == "random":
            self.handle_random_templates()
        elif user_message_instruction == "caption":
            self.handle_caption(prompt)
        else:
            # Fallback for unknown commands
            self.twilio.send_message(
                "Sorry, I didn't understand that command. Please type 'help' to see the possible commands."
            )

    def handle_help(self):
        help_text = (
            "Help Menu:\n"
            "- Send 'meme <caption>' to generate a meme.\n"
            "- Send 'generate <prompt>' to generate an AI meme.\n"
            "- Send 'search <keyword>' to search for memes.\n"
            "- Send 'top' to see the top 20 meme templates\n"
            "- Send 'random' to see 20 random templates.\n"
            "- Send 'caption' <template_id> <text_input_1> <text_input_2> to add a caption to an existing meme.\n"
            # "- Send '.' to exit."
        )
        self.twilio.send_message(help_text)
        self.console.print("Replied with help menu", style="bold green")

    def handle_meme(self, instruction: str, prompt: str):
        if instruction == "meme":
            response = self.automeme.send_caption_to_imgflip(caption=prompt)
        elif instruction == "generate":
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
                self.twilio.send_message(
                    f"Failed to generate meme: {error_message}.\n"
                    "Try 'templates' or 'random' to see available templates.\n"
                    "Type 'help' for further instructions."
                )
    def handle_search(self, prompt: str):
        try:
            # Search for memes based on the prompt
            self.console.print(f"Searching for memes with keyword: {prompt}", style="bold yellow")
            self.twilio.send_message(f"Searching for memes with keyword: {prompt}")
            response = self.search_memes.search(query=prompt)
            if response:
                if response.get("success"):
                    self.console.print("Meme search completed successfully", style="bold blue")
                    memes = response["data"]["memes"]
                    if memes:
                        for meme in memes:
                            meme_id = meme["id"]
                            meme_name = meme["name"]
                            meme_url = meme["url"]
                            box_count = meme["box_count"]
                            self.twilio.send_media_message(
                                f"Template: {meme_name} (ID: {meme_id}) Text Box Count {box_count}", url_for_media=meme_url
                            )
                    else:
                        self.console.print("No memes found for the given keyword.", style="bold red")
                        self.twilio.send_message("No memes found for the given keyword.")
                else:
                    error_message = response.get("error_message", "Unknown error occurred during search.")
                    self.console.print(f"Error: {error_message}", style="bold red")
                    self.twilio.send_message(f"Error during meme search: {error_message}")
            else:
                self.console.print("Error: No response received during search.", style="bold red")
                self.twilio.send_message("Error: No response received during meme search.")
        except Exception as e:
            self.console.print(f"An exception occurred: {str(e)}", style="bold red")
            self.twilio.send_message("An error occurred while searching for memes. Please try again later.")
        self.console.print("Replied with search results", style="bold green")
        
    def handle_top_templates(self, limit: int = 20):
        try:
            # Fetch top 20 meme templates from Imgflip
            self.console.print("Fetching top 20 meme templates...", style="bold yellow")
            self.twilio.send_message("Fetching top 20 meme templates...")
            response = self.get_memes.get_memes()
            
            if response:
                if response.get("success"):
                    self.console.print("Meme templates retrieved successfully", style="bold blue")
                    memes = response["data"]["memes"]
                    for meme in memes[:limit]:
                        meme_id = meme["id"]
                        meme_name = meme["name"]
                        meme_url = meme["url"]
                        box_count = meme["box_count"]
                        self.twilio.send_media_message(
                            f"Template: {meme_name} (ID: {meme_id}) Text Box Count {box_count}", url_for_media=meme_url
                        )
                else:
                    error_message = response.get("error_message", "Unknown error occurred when fetching memes.")
                    self.console.print(f"Error: {error_message}", style="bold red")
                    self.twilio.send_message(f"Error fetching meme templates: {error_message}")
            else:
                self.console.print("Error: No response received while fetching memes.", style="bold red")
                self.twilio.send_message("Error: No response received while fetching meme templates.")
        except Exception as e:
            self.console.print(f"An exception occurred: {str(e)}", style="bold red")
            self.twilio.send_message("An error occurred while fetching meme templates. Please try again later.")
        self.console.print("Replied with top 20 meme templates", style="bold green")
        
    def handle_random_templates(self, limit: int = 20):
        try:
            # Fetch 20 random meme templates from Imgflip
            self.console.print("Fetching 20 random meme templates...", style="bold yellow")
            self.twilio.send_message("Fetching 20 random meme templates...")
            response = self.get_memes.get_memes()
            
            if response:
                if response.get("success"):
                    self.console.print("Meme templates retrieved successfully", style="bold blue")
                    memes = response["data"]["memes"]
                    random_memes = random.sample(memes, k=min(limit, len(memes)))
                    for meme in random_memes:
                        meme_id = meme["id"]
                        meme_name = meme["name"]
                        meme_url = meme["url"]
                        box_count = meme["box_count"]
                        self.twilio.send_media_message(
                            f"Template: {meme_name} (ID: {meme_id}) Text Box Count {box_count}", url_for_media=meme_url
                        )
                else:
                    error_message = response.get("error_message", "Unknown error occurred when fetching memes.")
                    self.console.print(f"Error: {error_message}", style="bold red")
                    self.twilio.send_message(f"Error fetching meme templates: {error_message}")
            else:
                self.console.print("Error: No response received while fetching memes.", style="bold red")
                self.twilio.send_message("Error fetching meme templates. Please try again later.")
        except Exception as e:
            self.console.print(f"An exception occurred: {str(e)}", style="bold red")
            self.twilio.send_message("An error occurred while fetching meme templates. Please try again later.")
        self.console.print("Replied with 20 random meme templates", style="bold green")
        
    def handle_caption(self, template_id: str):
        response = self.get_meme.get(template_id=template_id)
        # Extract the template ID and text inputs from the message
        
        if response:
            self.console.print(response)
            if response.get("success"):
                number_of_text_boxes = response["data"]["meme"]["box_count"]
                self.console.print(f"Template ID: {template_id} has {number_of_text_boxes} text boxes.", style="bold blue")
                self.twilio.send_message(f"Template ID: {template_id} has {number_of_text_boxes} text boxes.")
                time.sleep(2)
                # Prompt the user for captions
                captions = []
                for i in range(number_of_text_boxes):
                    self.twilio.send_message(f"Please provide caption {i + 1} (or send '.' to cancel):")
                    self.console.print(f"Waiting for caption {i + 1}...", style="bold yellow")
                    # Wait for user input
                    caption = self.twilio.wait_for_user_message()
                    if caption == ".":
                        self.console.print("Ending conversation as user sent '.'", style="bold red")
                        return
                    captions.append(caption)
                # Generate the meme with the provided captions
                response = self.caption_image.caption(
                    template_id=template_id, text0=captions[0], text1=captions[1] if number_of_text_boxes > 1 else ""
                )
                meme_url = response["data"]["url"]
                self.console.print(f"Meme generated with captions: {meme_url}", style="bold blue")
                self.twilio.send_media_message(
                    "Here's your meme with captions.", url_for_media=meme_url
                )
            else:
                error_message = response.get("error_message", "Unknown error occurred while fetching template.")
                self.console.print(f"Error: {error_message}", style="bold red")
                self.twilio.send_message(f"Error fetching meme template: {error_message}")
        else:
            self.console.print("Error: No response received while fetching template.", style="bold red")
            self.twilio.send_message("Error: No response received while fetching meme template.")
        
        
        

    def run(self):
        self.console.print("MemeBot is running. Awaiting user messages...", style="bold green")
        while True:
            message = self.twilio.wait_for_user_message()
            if message == ".":
                self.console.print("Ending conversation as user sent '.'", style="bold red")
                break
            self.console.print(f"Received message: '{message}'", style="bold green")
            self.process_message(message)
