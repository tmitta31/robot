import os

# This is used when querying the llama LLM via the Hugging Face API
class HuggingFaceLlama():
    def __init__(self, testing):
        self.modelName = "LLaMA2"
        hfEnv = os.environ.get("HF_API_KEY")
        HUGGING_FACE_KEY = hfEnv if hfEnv is not None else input("enter your HuggingFace Token:\n")

        self.API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf"
        self.HEADERS = {
            "Authorization": f"Bearer {HUGGING_FACE_KEY}",
            "Content-Type": "application/json",
        }
        self.PARAMS = {
            "parameters": {
                "max_length": 16384,
                "temperature": 1,
                "top_k": 2000
            }, 
            "options": {
                "use_cache": False,
                "wait_for_model": True
            }
        }
        self.timeLastCalled = 0
        self.waitingTime = 3

        if testing: 
            self.waitingTime = 60
 
    def parseJson(self, jsonData):
        """
        PARAMS
            jsonData is dict that expresses the llms output.
        RETURN
            returns either a string that is the llms response, or
                None
        """
        if isinstance(jsonData, list):
            jsonData = jsonData[0]

        if isinstance(jsonData, dict) and 'generated_text' in jsonData:
            inst_index = jsonData['generated_text'].find('[/INST]')
            
            if inst_index != -1:
                return jsonData['generated_text'][inst_index + len('[/INST] '):].strip()
        else:
            print(f"Unexpected data: {jsonData}")
            return None