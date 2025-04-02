# meme_bot.py
from rich.console import Console
from Twilio import Twilio
from imgflip import AutoMeme, AIMeme, GetMeme, GetMemes, MemeSearch, CaptionImage
import random
import time
import json
import itertools

class MemeBot:
    """
    A bot to generate and send memes via Twilio and Imgflip APIs.

    Attributes:
        console (Console): For logging messages with rich formatting.
        twilio (Twilio): Instance to handle messaging via Twilio.
        automeme (AutoMeme): Instance for auto meme generation.
        ai_meme (AIMeme): Instance for AI meme generation.
        get_meme (GetMeme): Instance to get a meme template.
        get_memes (GetMemes): Instance to get multiple meme templates.
        search_memes (MemeSearch): Instance to search meme templates.
        caption_image (CaptionImage): Instance to caption an image.
    """
    def __init__(self):
        """
        Initialize the MemeBot with required components and instances.
        """
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
        self.surprise_meme_path = "iconic_meme_prompts.json"

    def process_message(self, message: str):
        """
        Process an incoming message, determine the command, and handle it.

        Args:
            message (str): The incoming message text.
        """
        # Determine the command and its arguments
        user_message_instruction = message.lower().split(" ")[0]
        prompt = message[len(user_message_instruction):].strip()
        
        if user_message_instruction == "help":
            self.handle_help()
        elif user_message_instruction in ("meme", "generate"):
            self.handle_meme(user_message_instruction, prompt)
        elif user_message_instruction == "surprise":
            self.handle_suprise()
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
        """
        Send the help menu message listing all available commands.
        """
        help_text = (
            "Welcome to Meme Machine! Ready to make magic? Just send me one of the below commands to get started. Let’s meme! 😎🎉\n"
            "\n- generate [text]  🤖 Generate an AI-powered meme based on your text\n"
            "- meme [text]    🎲 Let Imgflip choose the perfect template for your text\n"
            "- surprise      🎁 Get a random meme from our curated collection\n"
            "- search [query]   🔍 Search for meme templates by keyword\n"
            "- top        ✨ View the 20 most popular meme templates\n"
            "- random       🔄 View 20 random meme templates\n"
            "- caption [id]    📝 Add your text to a specific meme template\n"
            "- help        ❓ Show all available commands\n"
        )
        self.twilio.send_message(help_text)
        self.console.print("Replied with help menu", style="bold green")

    def handle_meme(self, instruction: str, prompt: str):
        """
        Generate a meme based on the provided caption or AI prompt.

        Args:
            instruction (str): Either 'meme' for auto meme or 'generate' for AI meme.
            prompt (str): The caption or prompt for meme generation.
        """
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
                    "Try 'top' or 'random' to see some available meme templates.\n"
                    "Type 'help' for further instructions."
                )


    def handle_suprise(self):
        """
        Generate a random meme and send it to the user.
        """
        try:
            self.console.print("Generating a random meme...", style="bold yellow")
            self.twilio.send_message("Generating a random meme...")

            # Load prompts
            with open(self.surprise_meme_path, "r") as handle:
                prompts = json.load(handle)

            # Flatten all captions into a single list
            all_captions = list(itertools.chain.from_iterable(prompts.values()))

            # Choose one at random
            suprise_caption = random.choice(all_captions)

            self.console.print(f"Random caption selected: {suprise_caption}", style="bold yellow")
            self.twilio.send_message(f"Random caption selected: {suprise_caption}")

            # Send to Imgflip
            self.console.print("Sending caption to Imgflip...", style="bold yellow")
            response = self.automeme.send_caption_to_imgflip(caption=suprise_caption)

            if response:
                if response.get("success"):
                    meme_url = response["data"]["url"]
                    self.console.print(f"Random meme generated: {meme_url}", style="bold blue")
                    self.twilio.send_media_message("Here's your surprise meme.", url_for_media=meme_url)
                else:
                    error_message = response.get("error_message", "Unknown error occurred.")
                    self.console.print(f"Error: {error_message}", style="bold red")
                    self.twilio.send_message(f"Error generating surprise meme: {error_message}")
            else:
                self.console.print("Error: No response received.", style="bold red")
                self.twilio.send_message("Error: No response received while generating surprise meme.")
        except Exception as e:
            self.console.print(f"An exception occurred: {str(e)}", style="bold red")
            self.twilio.send_message("An error occurred while generating surprise meme. Please try again later.")

            
            
    def handle_search(self, prompt: str):
        """
        Search for meme templates based on a keyword and send the results.

        Args:
            prompt (str): The keyword to search memes.
        """
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
                                f"Template: {meme_name}\n"
                                f"ID: {meme_id}\n"
                                f"Text Box Count: {box_count}", url_for_media=meme_url
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
        """
        Fetch and send the top meme templates.

        Args:
            limit (int, optional): The maximum number of templates to send. Defaults to 20.
        """
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
                            f"Template: {meme_name}\n"
                            f"ID: {meme_id}\n"
                            f"Text Box Count: {box_count}", url_for_media=meme_url
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
        """
        Fetch and send random meme templates.

        Args:
            limit (int, optional): Number of random templates to send. Defaults to 20.
        """
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
                            f"Template: {meme_name}\n"
                            f"ID: {meme_id}\n"
                            f"Text Box Count: {box_count}", url_for_media=meme_url
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
        """
        Handle captioning a meme template by prompting the user for each caption.

        Args:
            template_id (str): The ID of the meme template to caption.
        """
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
        """
        Start the main loop to continuously process incoming user messages.
        """
        self.console.print("Meme Machine is running. Awaiting user messages...", style="bold green")
        while True:
            message = self.twilio.wait_for_user_message()
            if message == ".":
                self.console.print("Ending conversation as user sent '.'", style="bold red")
                break
            self.console.print(f"Received message: '{message}'", style="bold green")
            self.process_message(message)
