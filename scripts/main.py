from dotenv import load_dotenv
load_dotenv()  # loads HUGGINGFACE_HUB_TOKEN from .env if present

from gui import App

if __name__ == "__main__":
    App().mainloop()
