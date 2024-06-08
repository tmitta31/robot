import os

# this object handles querying the llama LLM within your local network
class OtherLlama():
    def __init__(self, testing = False):
        """
        PARAMS
            - testing is a bool that defaults to False and changes
                the time the llm has for inference
        """

        self.modelName = "LLaMA2"

        # Env var
        llamaApi = os.environ.get("LLAMA_ENDP")
        self.API_URL = llamaApi if llamaApi is not None else input("enter your LLAMA endpoint:\n")
        
        self.HEADERS = {
            "Content-Type": "application/json",
        }

        self.PARAMS = {
            "parameters": {
                "max_new_tokens": 1024
            }
        }

        self.timeLastCalled = 0
        self.waitingTime = 10

        if testing: 
            self.waitingTime = 20
        
    def parseJson(self, jsonData):
        """
        PARAMS
            jsonData is dict that expresses the llms output.
        RETURN
            returns either a string that is the llms response, or
                None
        """
        if isinstance(jsonData, dict):
            return jsonData.get('generated_text')
        else:
            print(f"Unexpected data: {jsonData}")
            return None