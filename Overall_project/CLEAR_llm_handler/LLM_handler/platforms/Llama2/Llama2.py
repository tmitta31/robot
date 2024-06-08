import requests, time, os, asyncio, inspect, json
from LLM_handler.platforms.Llama2.support import reformat
from LLM_handler.platforms.Llama2.HuggingFaceLlama import HuggingFaceLlama
from LLM_handler.platforms.Llama2.OtherLlama import OtherLlama

# Parrent class for the huggingface llama api, and also the lincoln api
class Llama2():
    # The new method dynamically creates our Llama2 class.
    # The way we are going about this is very strange, but was just me trying to use new.
    # Instead of using a factory approach that would return either the LL llama,
    # or hf llama, we instead get all the attributes and methods of one these classes,
    # and add them to this class during run-time.
    def __new__(cls, testing = False, base = None):
        """
        PARAMS
            - cls is the Llama2 class
            - testing is not used in this method. Instead, initiated child object is.
            - base represents the child object being used <OtherLlama, HuggingFaceLlama>
        
        RETURN
            A newly created version of the Llama2 class which has new imported attributes and
            methods.
        """
        baseClass = HuggingFaceLlama if (base is not None and "hugging" in base.lower()) \
                      else OtherLlama
        
        # gets and sets all functions defined in baseClass.
        # You may be asking, "hey why are we not using a standard factory approach?".
        # The answer is yes, you are correct, this is strange but intended for my education
        for name, obj in inspect.getmembers(baseClass):
            if inspect.isfunction(obj):
                setattr(cls, name, obj)

        return super().__new__(cls)
    
    # The amount of times the LLM will be queried till giving up 
    ATTEMPT_TOLERANCE = 3

    # This exists to uphold a standard between llm classes.
    def specifyModel(self, message):
        pass

    def getResponse(self, messages, timesTried = 0):
        """
        getResponse is a recursive function responsible for querying the LLM.
        If a query fails, it will attempt to query the llm again, until it has made
        three attempts. 

        PARAMS
            - messages is the conversation ledger, sent as a list of dicts, we are
                sending to the LLM. It is formatted using the specifications of the
                OpenAI models. It is reformatted 
            - timesTried is an int that tracks how many times we have tried querying the LLM.
                getResponse is recursive, and will call itself if failing to get a response from
                model. After @ATTEMPT_TOLERANCE attempts the function will stop tring
        RETURN
            A string expressing the LLMs response, or a string that says ERROR if the query failed
        """

        # We are using a coroutine to prevent stalling. It is common for an error to occur when
        # communicating with the LLM. When these occur, the program run sits untill a response is returned.
        # But our coroutine allows us to implement a timeout, a way to circumvent problematic long response times.
        async def _getResponse(messages = messages, timesTried = timesTried):
            if self.timeLastCalled + self.waitingTime > time.time() :
                await asyncio.sleep((self.timeLastCalled + self.waitingTime) - time.time())

            if timesTried >= Llama2.ATTEMPT_TOLERANCE : 
                print("bummers")
                return "ERROR"
            
            try:
                self.timeLastCalled = time.time()
                llmInput = reformat(messages, self.PARAMS)
                response = await self.queryApi(llmInput, self.waitingTime)

                if response is None:
                    return await _getResponse(messages, timesTried = timesTried+1)
                
                return response
        
            except Exception as e :
                print("Exception in getResponse ", e)
                await asyncio.sleep(2)
                return await _getResponse(messages, timesTried=timesTried+1)
            
        return asyncio.run(_getResponse())

    # Used to send out our conversation ledger and get a response in an asynchronous way
    async def queryApi(self, messages):
        """
        PARAMS
            messages is the conversation ledger, sent as a list of dicts, we are
                sending to the LLM. It is formatted using the specifications of the
                llama models. 
        RETURN
            either a string given by the LLM, or None
        """
        try:
            response = await asyncio.wait_for(self.deliverQueryDirect(messages), 
                                              timeout=self.waitingTime * 2)
            return response

        except asyncio.TimeoutError:
            print("The API call has timed out.")
            return None

        except Exception as e:
            print("Exception with GPT: {}".format(str(e)))
            return None

    # Helper method to run the synchronous method queryGptDirect asynchronously
    async def deliverQueryDirect(self, messages):
        """
        PARAMS
            messages is the conversation ledger, sent as a list of dicts, we are
                sending to the LLM. It is formatted using the specifications of the
                llama models.
        RETURN
            either a string given by the LLM, or None
        """
        loop = asyncio.get_running_loop()

        def callingHuggingFace(messages):
            response = requests.post(self.API_URL, json=messages, headers=self.HEADERS)

            return self.parseJson(response.json())
        
        return await loop.run_in_executor(None, callingHuggingFace, messages)
