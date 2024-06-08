# CLEAR_llm_chat

CLEAR llm chat is responsible for handling a given large language model (LLM) tasked with the decision-making processes of the CLEAR project. This service connects to the worker server to receive prompts. These prompts will then be appended to a conversation ledger, which is given to the LLM. The LLM’s response will then be relayed to the worker server and appended to the conversation ledger. Additionally, it preserves and catalogs the conversations.
 
Run CLEAR_llm_chat on a Windows or Unix system in a Python 3.8 interpreter accompanied by the packages expressed in setup/requirements.txt. To run the service, use
 
``python main.py --address <address> --platform <offNetwork||onNetwork>``

-----

DISTRIBUTION STATEMENT A. Approved for public release. Distribution is unlimited.
 
This material is based upon work supported by the Under Secretary of Defense for Research and Engineering under Air Force Contract No. FA8702-15-D-0001. Any opinions, findings, conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the Under Secretary of Defense for Research and Engineering.

© 2023 Massachusetts Institute of Technology.

Subject to FAR52.227-11 Patent Rights - Ownership by the contractor (May 2014)

The software/firmware is provided to you on an As-Is basis

SPDX-License-Identifier: MIT
