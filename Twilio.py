# Twilio.py
import os
import time
import requests
from twilio.rest import Client
from dotenv import load_dotenv
# from flask import Flask, request, jsonify
from rich.console import Console
from rich import progress

console = Console()



class Twilio:
    def __init__(self):
        console.print("Initializing Twilio connection ...", style="bold green")
        # Init Twilio client
        load_dotenv()
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        api_sid = os.getenv("TWILIO_API_KEY_SID")
        api_secret = os.getenv("TWILIO_API_KEY_SECRET")
        self.service_sid = os.getenv("TWILIO_CHAT_SERVICE_SID")
        self.client = Client(api_sid, api_secret, account_sid)
        self.service = self.client.conversations.v1.services(self.service_sid)

        # Init WhatsApp addresses
        self.address = f"whatsapp:{os.getenv('PHONE_NUMBER')}"
        self.ms_address = f"whatsapp:{os.getenv('TWILIO_PHONE_NUMBER')}"

        # Reference to the conversation where the own phone number is a participant, or create a new one if none exists
        self.my_conversation = (
            self.get_my_conversation() or self.create_my_conversation()
        )
        
        # Reset messages to avoid processing old messages
        self.reset_messages()

    def delete_all_conversations(self):
        # Get a fresh start within the service
        console.print("Deleting all conversations...", style="bold red")
        for conversation in progress.track(
            self.service.conversations.list(), description="Deleting conversations..."
        ):
            conversation.delete()

    def get_my_conversation(self):
        # Go over existing conversations within the service, find the one where
        # the own phone number is a participant. There can only be one or none.
        for conversation in progress.track(
            self.service.conversations.list(), description="Getting my conversation..."
        ):
            participants = conversation.participants.list()
            for participant in participants:
                if (
                    participant.messaging_binding
                    and participant.messaging_binding["address"] == self.address
                ):
                    return conversation
        return None

    def create_my_conversation(self):
        # Create conversation (note: assumes there is no existing conversation where the own phone number is a participant)
        conversation = self.service.conversations.create(
            friendly_name=f"Conversation with {self.address}"
        )
        conversation.participants.create(
            messaging_binding_address=self.address,
            messaging_binding_proxy_address=self.ms_address,
        )
        return conversation

    def wait_for_user_message(self):
        """Wait until user sends a message"""
        while True:
            messages = self.my_conversation.messages.list()
            if len(messages) > 0 and messages[-1].author == self.address:
                console.print(f"Got a message from the user", style="bold green")
                message_body = messages[-1].body
                try:
                    # Delete the message after reading it
                    messages[-1].delete()
                except Exception as e:
                    console.print(f"Could not delete message: {str(e)}", style="bold yellow")
                return message_body
            console.print(f"Waiting for user message...", style="bold yellow")
            time.sleep(1)

    def reset_messages(self):
        """Reset the message history to avoid processing old messages"""
        messages = self.my_conversation.messages.list()
        for message in messages:
            if message.author == self.address:
                message.delete()

    def send_message(self, message):
        # Send a message to the user
        console.print(f"Sending message to the user: {message}", style="bold blue")
        self.my_conversation.messages.create(body=message)
        
    def send_media_message(self, message_body, url_for_media):
        console.print(f"Sending message to the user: {message_body}", style="bold blue")
        message = self.client.messages.create(
            from_=self.ms_address,
            to=self.address,
            body=message_body,
            media_url=url_for_media
        )
        print("Message SID:", message.sid)

            


if __name__ == "__main__":
    demo = Twilio()
    while True:
        user_message = demo.wait_for_user_message()
        if user_message == ".":
            console.print(
                "Ending conversation, since got '.' from user", style="bold red"
            )
            break
        demo.send_message(
            f"Hey there, got your message: {user_message}, send '.' to end the conversation. Length of your last message: {len(user_message)}"
        )
        console.print(
            f"Got a message from the user: '{user_message}', and replied",
            style="bold green",
        )
        