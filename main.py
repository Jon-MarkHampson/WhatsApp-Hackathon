# main.py
from meme_bot import MemeBot

def main():
    """Main entry point for the MemeBot application.

    This function creates an instance of MemeBot and calls its run method to start the application.
    """
    bot = MemeBot()
    bot.run()

if __name__ == "__main__":
    main()
