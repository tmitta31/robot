def formatEntries(systemDef, promptsAndResponses):
    """
    The conversation ledger is formatted using openai specs. Whenever using a different model
    the conversation ledger may need to be changed for LLM specifcations

    PARAMS
        - systemDef is a list of strings and represents the system definition
        - promptsAndResponses are a list of strings that represent the prompts
            and responses
    RETURN
        returns a string that represents the conversation ledger. A string is the
            expected type for the llama prompt.
    """
    # Format sysdef. Join will concatenate the strings in a list
    formattedSysDef = f"<s>[INST] <<SYS>>\n{systemDef}\n<</SYS>>\n"
    
    # Format other entries
    formattedPromptsAndResponses = '\n'.join(promptsAndResponses)
    
    # Combine and return the formatted entries
    return formattedSysDef + formattedPromptsAndResponses

def separateEntries(data):
    """
    seperateEntries takes in a conversation ledger, and seperates the data
    into two camps.

    PARAMS 
        data is the list of dicts that represents the conversation ledger.
    RETURN
        -sysDef is a string that contains the system definition
        - promptsAndResponses is a list that contains prompts and responses
    """
    sysDef = ""
    promptsAndResponses = []

    for entry in data:
        role = entry.get('role')
        content = entry.get('content')

        # Gets the system definition
        if role == 'system':
            if sysDef == "":
                sysDef = content
            else: raise("there should only be 1 sysDef")
        else:  
            # This will include both 'user' and 'assistant' roles
            promptsAndResponses.append(content)

    return sysDef, promptsAndResponses

def reformat(conversation, queryParams):
    """
    reformat is responsbile for adding our conversation ledger to our
    llama query paramters in a llama format. 
        
    PARAMS
        - conversation is the conversation ledger. It is a list of dicts
            containing the system definition, prompts, and responses.
        - queryParams are additional query paramters such as token limit,
            and temperature.
    RETURN
        returns a dict which expresses the content to give to the LLM. 
    """
    system_entries, other_entries = separateEntries(conversation)
    information = formatEntries(system_entries, other_entries) + "[/INST]"

    # Construct the input for the LLM
    queryParams["inputs"] = information

    return queryParams
