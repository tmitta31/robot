To run groq llm
1. Run ``node server.js`` in CLEAR_worker_server 
2. In file CLEAR_llm_handler/LLM_handler/platforms/GPT/ChatGpt.py in line 39 enter groq api key
3. Run ``python main.py --address <address>`` in CLEAR_llm_handler with address as http://localhost:9999
4. The terminal will prompt you to ask questions to groq api's llama3 model