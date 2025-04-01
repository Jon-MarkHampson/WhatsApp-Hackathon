# main.py
import os
import time
# import requests
from rich.console import Console
from twilio.rest import Client
from dotenv import load_dotenv
from Twilio import Twilio

console = Console()

# # Initialize Flask app
# app = Flask(__name__)

# Load environment variables from .env file
# load_dotenv()



def main():
    twilio = Twilio()

    while True:
        user_message = twilio.wait_for_user_message()
        if user_message == ".":
            console.print(
                "Ending conversation, since got '.' from user", style="bold red" # Give instructions for use here
            )
            break
        elif user_message == "help":
            twilio.send_message(
                "Hey there, got your request for 'help'. Here is the help menu" # ADD help menu here
            )
            console.print(
                "Got a message from the user: 'help', and replied with help menu",
                style="bold green",
            )
        twilio.send_message(
            f"Hey there, got your message: {user_message}, send '.' to end the conversation. Length of your last message: {len(user_message)}"
        )
        console.print(
            f"Got a message from the user: '{user_message}', and replied",
            style="bold green",
        )
        # Check if the user message is a command
        user_message_instruction = user_message.lower().split(" ")[0]
        if user_message_instruction in ["meme", "Meme", "meme!", "Meme!", "MEME", "MEME!"]:
            # Send a caption to imgflip
            caption = user_message[len(user_message_instruction):].strip()
            imgflip_response = twilio.send_caption_to_imgflip(caption=caption)
            print(f"imgflip response: {imgflip_response}")
            if imgflip_response["success"]:
                console.print(f"imgflip response: {imgflip_response['data']['url']}", style="bold blue")
                # twilio.send_message(
                #     f"Here's your ai generated meme: {imgflip_response['data']['url']}"
                # )
                twilio.send_media_message(
                    f"Here's your ai generated meme.",
                    url_for_media=imgflip_response["data"]["url"]
                )
            else:
                console.print(f"Failed to generate imgflip meme: {imgflip_response.get('error_message', 'Unknown error')}", style="bold red")
                twilio.send_message(
                    f"Failed to generate meme: {imgflip_response.get('error_message', 'Unknown error')}"
                )
        
        elif user_message_instruction == "ai_meme":
            # Send an AI meme prompt to imgflip
            ai_prompt = user_message[len(user_message_instruction):].strip()
            ai_meme_response = twilio.send_ai_meme_to_imgflip(prompt=ai_prompt)
            if ai_meme_response["success"]:
                console.print(f"imgflip response: {ai_meme_response['data']['url']}", style="bold blue")
                # twilio.send_message(
                #     f"Here's your ai generated meme: {ai_meme_response['data']['url']}"
                # )
                twilio.send_media_message(
                    f"Here's your ai generated meme.",
                    url_for_media=ai_meme_response["data"]["url"]
                )
            else:
                console.print(f"Failed to generate AI meme: {ai_meme_response['error_message']}", style="bold red")
                twilio.send_message(
                    f"Failed to generate ai meme: {imgflip_response.get('error_message', 'Unknown error')}"
                )
        
    
    
    
    
if __name__ == "__main__":
    main()
