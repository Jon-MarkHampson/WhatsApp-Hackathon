from imgflip import AIMeme, AutoMeme, MemeSearch, GetMeme, CaptionImage, CaptionGif
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Example 1: Generate an AI Meme
    print("\nGenerating AI Meme...")
    ai_meme = AIMeme(base_folder="custom_memes")  # Optional: specify custom base folder
    result = ai_meme.generate("house keeping")
    print(f"AI Meme URL: {result['data']['url']}")
    
    # Example 2: Generate an Auto Meme
    print("\nGenerating Auto Meme...")
    auto_meme = AutoMeme()  # Uses default "memes" folder
    result = auto_meme.generate("When you finally clean your room but can't find anything")
    print(f"Auto Meme URL: {result['data']['url']}")
    
    # Example 3: Search for meme templates
    print("\nSearching for memes...")
    search = MemeSearch()
    result = search.search("cleaning")
    print("Found memes:")
    for meme in result['data']['memes'][:3]:  # Show top 3 results
        print(f"- {meme['name']} (ID: {meme['id']})")
    
    # Example 4: Get a specific meme template
    print("\nGetting specific meme...")
    get_meme = GetMeme()
    result = get_meme.get(61579)  # "One Does Not Simply" meme
    print(f"Meme name: {result['data']['meme']['name']}")
    
    # Example 5: Caption an image
    print("\nCaptioning image...")
    caption = CaptionImage()
    result = caption.caption(
        61579,  # "One Does Not Simply" meme
        "One does not simply",
        "Clean the entire house in one day"
    )
    print(f"Captioned image URL: {result['data']['url']}")
    
    # Example 6: Caption a GIF
    print("\nCaptioning GIF...")
    caption_gif = CaptionGif()
    boxes = [
        {"text": "When you start cleaning"},
        {"text": "And find things you thought were lost forever"}
    ]
    result = caption_gif.caption(89370399, boxes)  # Example GIF template
    print(f"Captioned GIF URL: {result['data']['url']}")

if __name__ == "__main__":
    main() 