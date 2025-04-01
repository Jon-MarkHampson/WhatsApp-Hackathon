import os
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import json
from dotenv import load_dotenv
from rich.console import Console

console = Console()

load_dotenv()

class ImgflipAPI(ABC):
    """
    Base class for Imgflip API operations.

    This class handles the basic utilities like folder creation, metadata management,
    and performing API requests.
    """
    BASE_URL = "https://api.imgflip.com"
    
    def __init__(self, username: str = None, password: str = None, base_folder: str = "memes"):
        """
        Initialize the API client.

        Credentials can be passed directly or loaded from environment variables.
        The folder structure and metadata file are set up upon initialization.

        Args:
            username (str, optional): Imgflip username. Defaults to os.getenv("IMGFLIP_USERNAME").
            password (str, optional): Imgflip password. Defaults to os.getenv("IMGFLIP_PASSWORD").
            base_folder (str, optional): Folder to store meme metadata. Defaults to "memes".
        
        Raises:
            ValueError: If credentials are not found.
        """
        self.username = username or os.getenv("IMGFLIP_USERNAME")
        self.password = password or os.getenv("IMGFLIP_PASSWORD")
        
        if not self.username or not self.password:
            raise ValueError("Imgflip credentials not found. Please set IMGFLIP_USERNAME and IMGFLIP_PASSWORD in .env file")
        
        self.base_folder = base_folder
        self._create_folder_structure()
        
        self.metadata_file = os.path.join(self.base_folder, "meme_metadata.json")
        self.metadata = self._load_metadata()
    
    def _create_folder_structure(self):
        """
        Create the folder structure for storing metadata.
        
        This method ensures that the base folder exists.
        """
        if not os.path.exists(self.base_folder):
            os.makedirs(self.base_folder)
    
    def _load_metadata(self) -> Dict:
        """
        Load the metadata from the JSON file or create a new structure if the file doesn't exist.

        Returns:
            Dict: Metadata containing a list of memes.
        """
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not read {self.metadata_file}. Creating new metadata file.")
                return {"memes": []}
        return {"memes": []}
    
    def _save_metadata(self, meme_type: str, query: str, response_data: Dict[str, Any], local_path: str):
        """
        Save meme metadata to a JSON file.

        This method updates the metadata JSON file with new meme information.

        Args:
            meme_type (str): The type of meme (e.g., 'ai', 'auto', etc.).
            query (str): The search query or description used.
            response_data (Dict[str, Any]): API response data.
            local_path (str): Local storage path (currently unused).
        """
        try:
            timestamp = datetime.now().isoformat()
            
            meme_info = {
                "timestamp": timestamp,
                "type": meme_type,
                "query": query,
                "imgflip_url": response_data["data"]["url"],
                "page_url": response_data["data"].get("page_url"),
                "template_id": response_data["data"].get("template_id"),
                "texts": response_data["data"].get("texts", [])
            }
            
            self.metadata["memes"].append(meme_info)
            
            os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            
            print(f"\nMetadata saved to: {self.metadata_file}")
            
        except Exception as e:
            print(f"\nWarning: Could not save metadata: {str(e)}")
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a POST request to the Imgflip API.

        This method appends the user credentials to the request data.

        Args:
            endpoint (str): API endpoint (e.g., "caption_image").
            data (Dict[str, Any]): Payload data for the request.

        Returns:
            Dict[str, Any]: The JSON response from the API.

        Raises:
            HTTPError: If the API response indicates an error.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        data.update({
            "username": self.username,
            "password": self.password
        })
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json()
    
    def save_meme(self, response_data: Dict[str, Any], meme_type: str, query: str, prefix: str = "") -> str:
        """
        Save the meme metadata to the JSON file.

        Validates the API response and delegates saving metadata.
        
        Args:
            response_data (Dict[str, Any]): API response dictionary.
            meme_type (str): Type of the meme.
            query (str): Query or textarea used for generating meme.
            prefix (str, optional): Any prefix to use (currently not used for file storage). Defaults to "".

        Returns:
            str: URL of the generated meme.

        Raises:
            ValueError: If the API response indicates failure.
        """
        if not response_data.get("success"):
            raise ValueError(f"API request failed: {response_data.get('error_message')}")
            
        self._save_metadata(meme_type, query, response_data, None)
            
        return response_data["data"]["url"]

class AIMeme(ImgflipAPI):
    """
    Class for generating AI-powered memes.
    
    Extends the basic ImgflipAPI to include AI meme specific functionality.
    """
    
    def generate(self, prefix_text: str, model: str = "openai", template_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate an AI-powered meme.

        Args:
            prefix_text (str): The initial text prompt for the AI meme.
            model (str, optional): The AI model to use. Defaults to "openai".
            template_id (Optional[int], optional): Optional template ID to use. Defaults to None.

        Returns:
            Dict[str, Any]: API response data for the generated meme.
        """
        data = {
            "model": model,
            "prefix_text": prefix_text,
            "no_watermark": True
        }
        if template_id:
            data["template_id"] = template_id
            
        response = self._make_request("ai_meme", data)
        query = f"{prefix_text[:30]}"
        url = self.save_meme(response, "ai", query, f"ai_meme_{prefix_text[:30]}")
        return response
    
    def send_ai_meme_to_imgflip(self, prompt, model="openai"):
        """
        Send an AI meme prompt to Imgflip through a dedicated endpoint.

        Args:
            prompt (str): The meme prompt.
            model (str, optional): AI model to use. Defaults to "openai".

        Returns:
            Dict[str, Any]: API response data.
        """
        console.print(f"Sending AI meme prompt: {prompt}", style="bold blue")
        response = requests.post(
            os.getenv("IMGFLIP_AI_ENDPOINT"),
            data={
                "username": os.getenv("IMGFLIP_USERNAME"),
                "password": os.getenv("IMGFLIP_PASSWORD"),
                "model": model,
                "prefix_text": prompt,
                "no_watermark": ""
            },
        )
        response_data = response.json()
        if response_data["success"]:
            self.save_meme(response_data, "ai", prompt)
        return response_data

class AutoMeme(ImgflipAPI):
    """
    Class for automatically generating memes from text.

    Provides functionality to generate auto memes and interact with Imgflip's API.
    """
    
    def generate(self, text: str) -> Dict[str, Any]:
        """
        Generate an automatic meme from provided text.

        Args:
            text (str): The text for the meme.

        Returns:
            Dict[str, Any]: API response data for the generated meme.
        """
        data = {
            "text": text,
            "no_watermark": True
        }
        
        response = self._make_request("automeme", data)
        query = f"{text[:30]}"
        url = self.save_meme(response, "auto", query, f"automeme_{text[:30]}")
        return response
    
    def send_caption_to_imgflip(self, caption):
        """
        Send a caption to Imgflip to generate a meme.

        Args:
            caption (str): Caption text to send for meme generation.

        Returns:
            Dict[str, Any]: API response from Imgflip.
        """
        console.print(f"Sending caption to imgflip: {caption}", style="bold blue")
        response = requests.post(
            os.getenv("IMGFLIP_AUTOMEME_ENDPOINT"),
            data={
                "username": os.getenv("IMGFLIP_USERNAME"),
                "password": os.getenv("IMGFLIP_PASSWORD"),
                "text": caption,
                "no_watermark": True
            },
        )
        response_data = response.json()
        if response_data["success"]:
            self.save_meme(response_data, "auto", caption)
        return response_data

class MemeSearch(ImgflipAPI):
    """
    Class for searching meme templates.
    
    Allows queries to search for specific meme templates.
    """
    
    def search(self, query: str, include_nsfw: bool = False) -> Dict[str, Any]:
        """
        Search for meme templates by query.

        Args:
            query (str): The search query.
            include_nsfw (bool, optional): Whether to include NSFW results. Defaults to False.

        Returns:
            Dict[str, Any]: API response containing search results.
        """
        data = {
            "query": query,
            "include_nsfw": 1 if include_nsfw else 0
        }
        
        return self._make_request("search_memes", data)

class GetMeme(ImgflipAPI):
    """
    Class for retrieving a specific meme template.
    
    Retrieves details of a meme template by its ID.
    """
    
    def get(self, template_id: int) -> Dict[str, Any]:
        """
        Get a specific meme template by template ID.

        Args:
            template_id (int): The ID of the meme template.

        Returns:
            Dict[str, Any]: API response data containing the meme template.
        """
        data = {
            "template_id": template_id
        }
        
        return self._make_request("get_meme", data)
    
class GetMemes(ImgflipAPI):
    """
    Class for retrieving all meme templates.
    
    Provides functionality to get a complete list of meme templates.
    """
    
    def get_memes(self):
        """
        Retrieve all meme templates available on Imgflip.

        Returns:
            Dict[str, Any]: API response data with the list of memes.
        """
        url = f"{self.BASE_URL}/get_memes"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

class CaptionImage(ImgflipAPI):
    """
    Class for captioning static images.
    
    Uses Imgflip's caption_image endpoint to generate memes with captions.
    """
    
    def caption(self, template_id: int, text0: str, text1: str = "", font: str = "impact") -> Dict[str, Any]:
        """
        Caption a static image using a template.

        Args:
            template_id (int): ID of the meme template.
            text0 (str): Primary caption text.
            text1 (str, optional): Secondary caption text. Defaults to "".
            font (str, optional): Font style for the text. Defaults to "impact".

        Returns:
            Dict[str, Any]: API response data with the captioned image.
        """
        data = {
            "template_id": template_id,
            "text0": text0,
            "text1": text1,
            "font": font,
            "no_watermark": True
        }
        
        response = self._make_request("caption_image", data)
        return response

class CaptionGif(ImgflipAPI):
    """
    Class for captioning animated GIFs.
    
    Uses Imgflip's caption_gif endpoint to embed text into GIFs.
    """
    
    def caption(self, template_id: int, boxes: list) -> Dict[str, Any]:
        """
        Caption an animated GIF with multiple text boxes.

        Args:
            template_id (int): ID of the GIF template.
            boxes (list): A list of dictionaries for each text box (each with a 'text' key).

        Returns:
            Dict[str, Any]: API response data with the captioned GIF.
        """
        data = {
            "template_id": template_id,
            "boxes": json.dumps(boxes),
            "no_watermark": True
        }
        
        response = self._make_request("caption_gif", data)
        query = " | ".join(box["text"] for box in boxes)
        url = self.save_meme(response, "gif", query, f"gif_{template_id}")
        return response

def main():
    """
    Main function that provides a command-line interface for accessing Imgflip API operations.
    
    The user can generate memes, search for meme templates, caption images or GIFs,
    and exit the application.
    """
    while True:
        try:
            print("\nWelcome to Imgflip API Client!")
            print("Available options:")
            print("1. Generate AI Meme")
            print("2. Generate Auto Meme")
            print("3. Search Meme Templates")
            print("4. Get Specific Meme")
            print("5. Caption Image")
            print("6. Caption GIF")
            print("7. Exit")
            
            choice = input("\nEnter your choice (1-7): ")
            
            if choice == "7":
                print("Goodbye!")
                break
                
            if choice == "1":
                while True:
                    try:
                        context = input("Enter context for the meme (e.g., 'trump greenland'): ")
                        ai_meme = AIMeme()
                        result = ai_meme.generate(context)
                        print("\nMeme generated successfully!")
                        print(f"URL: {result['data']['url']}")
                        break
                    except ValueError as e:
                        print(f"\nError: {str(e)}")
                        retry = input("Would you like to try again? (y/n): ")
                        if retry.lower() != 'y':
                            break
                
            elif choice == "2":
                while True:
                    try:
                        text = input("Enter text for the meme: ")
                        auto_meme = AutoMeme()
                        result = auto_meme.generate(text)
                        print("\nMeme generated successfully!")
                        print(f"URL: {result['data']['url']}")
                        break
                    except ValueError as e:
                        print(f"\nError: {str(e)}")
                        retry = input("Would you like to try again? (y/n): ")
                        if retry.lower() != 'y':
                            break
                
            elif choice == "3":
                query = input("Enter search query: ")
                search = MemeSearch()
                result = search.search(query)
                print("\nSearch results:")
                for meme in result['data']['memes'][:5]:
                    print(f"- {meme['name']} (ID: {meme['id']})")
                
            elif choice == "4":
                template_id = input("Enter template ID: ")
                get_meme = GetMeme()
                result = get_meme.get(int(template_id))
                print(f"\nMeme name: {result['data']['meme']['name']}")
                
            elif choice == "5":
                while True:
                    try:
                        template_id = int(input("Enter template ID: "))
                        text0 = input("Enter first text: ")
                        text1 = input("Enter second text (optional): ")
                        caption = CaptionImage()
                        result = caption.caption(template_id, text0, text1)
                        print("\nMeme generated successfully!")
                        print(f"URL: {result['data']['url']}")
                        break
                    except ValueError as e:
                        print(f"\nError: {str(e)}")
                        retry = input("Would you like to try again? (y/n): ")
                        if retry.lower() != 'y':
                            break
                
            elif choice == "6":
                while True:
                    try:
                        template_id = int(input("Enter template ID: "))
                        num_boxes = int(input("Enter number of text boxes: "))
                        boxes = []
                        for i in range(num_boxes):
                            text = input(f"Enter text for box {i+1}: ")
                            boxes.append({"text": text})
                        
                        caption_gif = CaptionGif()
                        result = caption_gif.caption(template_id, boxes)
                        print("\nMeme generated successfully!")
                        print(f"URL: {result['data']['url']}")
                        break
                    except ValueError as e:
                        print(f"\nError: {str(e)}")
                        retry = input("Would you like to try again? (y/n): ")
                        if retry.lower() != 'y':
                            break
            
        except Exception as e:
            print(f"\nAn unexpected error occurred: {str(e)}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
