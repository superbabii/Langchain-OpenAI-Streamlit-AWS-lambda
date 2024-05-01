"""
ValueError: ZeroShotAgent does not support multi-input tool

pip install chromadb==0.3.29
"""
from langchain import hub
from langchain.agents import AgentType, initialize_agent, load_tools, tool, \
    create_structured_chat_agent, AgentExecutor
from custom_message_retrieval_tool import CustomMessageRetrievalTool
from custom_search_results import CustomSearchResults
from llm_anthropic_claude import anthropic_claude_llm

initialize_agent._validate_tools = lambda *_, **__: ...


# Constants
PERSIST_DIRECTORY = 'docs/chroma/'
TEXT_PATH = "docs/guide/text_feature"

NOVEL_PROMPT = """
Your Role: You are a software test engineer creating useful feedback and writing user stories to better document features for Forte based on a user's work context.

Have a self dialogue between a Manager and a Software Test Engineer where the Manager asks the 
Software Test Engineer to describe how he contributes when he is at his best.

Have the dialogue for 5 iterations and come up with a final concise answer that describes the user's request.
Iteration1:
Manger:
Software Engineer: 

Iteration2:
Manger:
Software Engineer: 

... 
till 5-6 iterations

Use plain software engineering terminology with technical details. You should summarize in a sentence with 60 or fewer words (recommended).
How to write a growth idea

Growth ideas are forward-looking actions an employee can take to develop and grow. They may be stretch activities, expanded project areas, new skills to develop, or a subject to learn. Growth ideas are not areas of weakness.

You'll also select 1-3 Leadership Principles the person should focus on for growth. The LPs you select can help support the super powers you described.

When you write growth ideas, focus on specific situations, behaviors, and impact. To interrupt unconscious bias, avoid focusing on their personality or style

Response format: Provide details in 60 words or less for Forte feedback.

Research Question: {research_question}
------------------------------------------------------------------------------------------------------------------------
"""

# LLM Chatbot and tools integration
class LLMChatbot:
    def __init__(self):
        self.llm = anthropic_claude_llm

    def run_agent(self, prompt, chat_history=None):
        try:
            tools = [CustomSearchResults(), CustomMessageRetrievalTool()]
            prompt_hub = hub.pull("hwchase17/structured-chat-agent")
            agent_chain = create_structured_chat_agent(
                tools=tools,
                llm=self.llm,
                prompt=prompt_hub)
            agent_executor = AgentExecutor(agent=agent_chain, tools=tools, verbose=True,
                                           handle_parsing_errors=True)
            # Prepare the input with chat history if available
            input_data = {"input": prompt}
            output = agent_executor.invoke(input_data)
            # print("Agent output: ", output)
            return output
        except Exception as e:
            print("Agent error, trying again:", e)
            # Try again once
            try:
                tools = [CustomSearchResults(),
                         CustomMessageRetrievalTool()]
                prompt_hub = hub.pull("hwchase17/structured-chat-agent")
                agent_chain = create_structured_chat_agent(
                    tools=tools,
                    llm=self.llm,
                    prompt=prompt_hub)
                agent_executor = AgentExecutor(agent=agent_chain, tools=tools, verbose=True,
                                               handle_parsing_errors=True)
                # Prepare the input with chat history if available
                input_data = {"input": prompt}
                output = agent_executor.invoke(input_data)
                return output
            except Exception as e:
                print("Agent error: ", e)
                return str(e)
