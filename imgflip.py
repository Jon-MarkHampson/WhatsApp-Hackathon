import os
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ImgflipAPI(ABC):
    """Base class for Imgflip API operations"""
    BASE_URL = "https://api.imgflip.com"
    
    def __init__(self, username: str = None, password: str = None, base_folder: str = "memes"):
        # Get credentials from environment variables if not provided
        self.username = username or os.getenv("IMGFLIP_USERNAME")
        self.password = password or os.getenv("IMGFLIP_PASSWORD")
        
        if not self.username or not self.password:
            raise ValueError("Imgflip credentials not found. Please set IMGFLIP_USERNAME and IMGFLIP_PASSWORD in .env file")
        
        self.base_folder = base_folder
        self._create_folder_structure()
        
        # Initialize or load metadata file
        self.metadata_file = os.path.join(self.base_folder, "meme_metadata.json")
        self.metadata = self._load_metadata()
    
    def _create_folder_structure(self):
        """Create the folder structure for different types of memes"""
        # Create base folder if it doesn't exist
        if not os.path.exists(self.base_folder):
            os.makedirs(self.base_folder)
            
        # Create type-specific folders
        self.folders = {
            "ai": os.path.join(self.base_folder, "ai_memes"),
            "auto": os.path.join(self.base_folder, "auto_memes"),
            "caption": os.path.join(self.base_folder, "captioned_memes"),
            "gif": os.path.join(self.base_folder, "gif_memes")
        }
        
        for folder in self.folders.values():
            if not os.path.exists(folder):
                os.makedirs(folder)
    
    def _load_metadata(self) -> Dict:
        """Load or create metadata JSON file"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"memes": []}
    
    def _save_metadata(self, meme_type: str, query: str, response_data: Dict[str, Any], local_path: str):
        """Save meme metadata to JSON file"""
        timestamp = datetime.now().isoformat()
        
        meme_info = {
            "timestamp": timestamp,
            "type": meme_type,
            "query": query,
            "imgflip_url": response_data["data"]["url"],
            "page_url": response_data["data"].get("page_url"),
            "local_path": local_path,
            "template_id": response_data["data"].get("template_id"),
            "texts": response_data["data"].get("texts", [])
        }
        
        self.metadata["memes"].append(meme_info)
        
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a POST request to the Imgflip API"""
        url = f"{self.BASE_URL}/{endpoint}"
        data.update({
            "username": self.username,
            "password": self.password
        })
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json()
    
    def save_meme(self, response_data: Dict[str, Any], meme_type: str, query: str, prefix: str = "") -> str:
        """Save the meme image to type-specific folder and update metadata"""
        if not response_data.get("success"):
            raise Exception(f"API request failed: {response_data.get('error_message')}")
            
        meme_url = response_data["data"]["url"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Determine file extension from URL
        extension = "jpg" if meme_url.endswith(".jpg") else "gif"
        filename = f"{prefix}_{timestamp}.{extension}"
        
        # Get the appropriate folder for this meme type
        folder = self.folders.get(meme_type, self.base_folder)
        filepath = os.path.join(folder, filename)
        
        # Download and save the image
        img_response = requests.get(meme_url)
        img_response.raise_for_status()
        
        with open(filepath, "wb") as f:
            f.write(img_response.content)
        
        # Save metadata
        self._save_metadata(meme_type, query, response_data, filepath)
            
        return filepath

class AIMeme(ImgflipAPI):
    """Class for generating AI-powered memes"""
    def generate(self, prefix_text: str, model: str = "openai", template_id: Optional[int] = None) -> Dict[str, Any]:
        data = {
            "model": model,
            "prefix_text": prefix_text,
            "no_watermark": True
        }
        if template_id:
            data["template_id"] = template_id
            
        response = self._make_request("ai_meme", data)
        query = f"{prefix_text[:30]}"
        filepath = self.save_meme(response, "ai", query, f"ai_meme_{prefix_text[:30]}")
        print(f"Meme saved to: {filepath}")
        return response

class AutoMeme(ImgflipAPI):
    """Class for automatically generating memes from text"""
    def generate(self, text: str) -> Dict[str, Any]:
        data = {
            "text": text,
            "no_watermark": True
        }
        
        response = self._make_request("automeme", data)
        query = f"{text[:30]}"
        filepath = self.save_meme(response, "auto", query, f"automeme_{text[:30]}")
        print(f"Meme saved to: {filepath}")
        return response

class MemeSearch(ImgflipAPI):
    """Class for searching meme templates"""
    def search(self, query: str, include_nsfw: bool = False) -> Dict[str, Any]:
        data = {
            "query": query,
            "include_nsfw": 1 if include_nsfw else 0
        }
        
        return self._make_request("search_memes", data)

class GetMeme(ImgflipAPI):
    """Class for getting a specific meme template"""
    def get(self, template_id: int) -> Dict[str, Any]:
        data = {
            "template_id": template_id
        }
        
        return self._make_request("get_meme", data)

class CaptionImage(ImgflipAPI):
    """Class for captioning static images"""
    def caption(self, template_id: int, text0: str, text1: str = "", font: str = "impact") -> Dict[str, Any]:
        data = {
            "template_id": template_id,
            "text0": text0,
            "text1": text1,
            "font": font,
            "no_watermark": True
        }
        
        response = self._make_request("caption_image", data)
        query = f"{text0} | {text1}"
        filepath = self.save_meme(response, "caption", query, f"caption_{template_id}")
        print(f"Meme saved to: {filepath}")
        return response

class CaptionGif(ImgflipAPI):
    """Class for captioning animated GIFs"""
    def caption(self, template_id: int, boxes: list) -> Dict[str, Any]:
        data = {
            "template_id": template_id,
            "boxes": json.dumps(boxes),
            "no_watermark": True
        }
        
        response = self._make_request("caption_gif", data)
        query = " | ".join(box["text"] for box in boxes)
        filepath = self.save_meme(response, "gif", query, f"gif_{template_id}")
        print(f"Meme saved to: {filepath}")
        return response

def main():
    try:
        print("\nWelcome to Imgflip API Client!")
        print("Available options:")
        print("1. Generate AI Meme")
        print("2. Generate Auto Meme")
        print("3. Search Meme Templates")
        print("4. Get Specific Meme")
        print("5. Caption Image")
        print("6. Caption GIF")
        
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == "1":
            context = input("Enter context for the meme (e.g., 'trump greenland'): ")
            ai_meme = AIMeme()
            result = ai_meme.generate(context)
            print("\nMeme generated successfully!")
            print(f"URL: {result['data']['url']}")
            
        elif choice == "2":
            text = input("Enter text for the meme: ")
            auto_meme = AutoMeme()
            result = auto_meme.generate(text)
            print("\nMeme generated successfully!")
            print(f"URL: {result['data']['url']}")
            
        elif choice == "3":
            query = input("Enter search query: ")
            search = MemeSearch()
            result = search.search(query)
            print("\nSearch results:")
            for meme in result['data']['memes'][:5]:  # Show top 5 results
                print(f"- {meme['name']} (ID: {meme['id']})")
                
        elif choice == "4":
            template_id = int(input("Enter template ID: "))
            get_meme = GetMeme()
            result = get_meme.get(template_id)
            print("\nMeme details:")
            print(f"Name: {result['data']['meme']['name']}")
            print(f"URL: {result['data']['meme']['url']}")
            
        elif choice == "5":
            template_id = int(input("Enter template ID: "))
            text0 = input("Enter top text: ")
            text1 = input("Enter bottom text: ")
            caption = CaptionImage()
            result = caption.caption(template_id, text0, text1)
            print("\nMeme captioned successfully!")
            print(f"URL: {result['data']['url']}")
            
        elif choice == "6":
            template_id = int(input("Enter template ID: "))
            boxes = []
            num_boxes = int(input("Enter number of text boxes: "))
            for i in range(num_boxes):
                text = input(f"Enter text for box {i+1}: ")
                boxes.append({"text": text})
            caption = CaptionGif()
            result = caption.caption(template_id, boxes)
            print("\nGIF captioned successfully!")
            print(f"URL: {result['data']['url']}")
            
        else:
            print("Invalid choice!")
            
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
