# Twilio.py
"""
Module for managing a Twilio client and handling WhatsApp conversations.
"""

import os
import time
import json
from twilio.rest import Client
from dotenv import load_dotenv
from rich.console import Console
from rich import progress

console = Console()


class Twilio:
    def __init__(self):
        """
        Initialize the Twilio client, set up the conversation service,
        and reset old messages.
        """
        console.print("Initializing Twilio connection ...", style="bold green")
        load_dotenv()
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        api_sid = os.getenv("TWILIO_API_KEY_SID")
        api_secret = os.getenv("TWILIO_API_KEY_SECRET")
        self.service_sid = os.getenv("TWILIO_CHAT_SERVICE_SID")
        self.client = Client(api_sid, api_secret, account_sid)
        self.service = self.client.conversations.v1.services(self.service_sid)

        self.address = f"whatsapp:{os.getenv('PHONE_NUMBER')}"
        self.ms_address = f"whatsapp:{os.getenv('TWILIO_PHONE_NUMBER')}"

        self.my_conversation = (
            self.get_my_conversation() or self.create_my_conversation()
        )
        
        self.reset_messages()

    def delete_all_conversations(self):
        """
        Delete all conversations in the Twilio service.
        """
        console.print("Deleting all conversations...", style="bold red")
        for conversation in progress.track(
            self.service.conversations.list(), description="Deleting conversations..."
        ):
            conversation.delete()

    def get_my_conversation(self):
        """
        Retrieve an existing conversation that includes the user's phone number.
        
        Returns:
            conversation: The conversation object if found, otherwise None.
        """
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
        """
        Create a new conversation with the user's phone number.
        
        Returns:
            conversation: The newly created conversation object.
        """
        conversation = self.service.conversations.create(
            friendly_name=f"Conversation with {self.address}"
        )
        conversation.participants.create(
            messaging_binding_address=self.address,
            messaging_binding_proxy_address=self.ms_address,
        )
        return conversation

    def wait_for_user_message(self):
        """
        Wait until the user sends a message to the conversation.
        
        Returns:
            str: The body of the user's message.
        """
        while True:
            messages = self.my_conversation.messages.list()
            if len(messages) > 0 and messages[-1].author == self.address:
                console.print("Got a message from the user", style="bold green")
                message_body = messages[-1].body
                try:
                    messages[-1].delete()
                except Exception as e:
                    console.print(f"Could not delete message: {str(e)}", style="bold yellow")
                return message_body
            console.print("Waiting for user message...", style="bold yellow")
            time.sleep(1)

    def reset_messages(self):
        """
        Reset the message history by deleting messages sent by the user.
        """
        messages = self.my_conversation.messages.list()
        for message in messages:
            if message.author == self.address:
                message.delete()

    def send_message(self, message):
        """
        Send a text message to the user.
        
        Args:
            message (str): The message to be sent.
        """
        console.print(f"Sending message to the user: {message}", style="bold blue")
        self.my_conversation.messages.create(body=message)
        
    def send_test_message(self):
        """
        Send a test message to the user.
        
        Args:
            message (str): The message to be sent.
        """
        console.print(f"Sending test message to the user!", style="bold blue")
        message = self.my_conversation.messages.create(
        # Note: these parameter names match the ones in the Content API documentation.
        content_sid="HXa71443fe717854911f3c858892a901fd",
        content_variables=json.dumps({
            "1": "template_id"
        })
        )
        print("Message SID:", message.sid)
        
    def send_quick_reply_message(self, template_id):
        """
        Send a test message to the user.
        
        Args:
            message (str): The message to be sent.
        """
        console.print(f"Sending test message to the user!", style="bold blue")
        message = self.my_conversation.messages.create(
        # Note: these parameter names match the ones in the Content API documentation.
        content_sid="HX61d6f00d36124d6259f741df5183f746",
        content_variables=json.dumps({
            "1": template_id
        })
        )
        print("Message SID:", message.sid)
    
        
        
    def send_media_message(self, message_body, url_for_media):
        """
        Send a media message to the user and block until the message is delivered.
        
        Args:
            message_body (str): The text accompanying the media.
            url_for_media (list or str): URL(s) of the media to send.
        """
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
    demo.send_quick_reply_message(156892)
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