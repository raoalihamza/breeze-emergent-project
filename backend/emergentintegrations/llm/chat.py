class UserMessage:
    def __init__(self, text="", filenames=None):
        self.text = text
        self.filenames = filenames or []

class LlmChat:
    def __init__(self, api_key="", session_id="", system=""):
        self.api_key = api_key
        self.session_id = session_id
        self.system = system
    
    async def chat(self, message):
        return "Atlas AI is currently unavailable in local development."