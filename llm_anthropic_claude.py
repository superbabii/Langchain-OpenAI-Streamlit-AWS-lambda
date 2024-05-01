from langchain.llms.bedrock import Bedrock
from langchain.chat_models import ChatOpenAI
import config

# Constants
OPENAI_KEY = config.OPENAI_API_KEY

# If you want to use Bedrock, use this code instead of ChatOpenAI
# anthropic_claude_llm = Bedrock(credentials_profile_name="default",
#                               model_id="anthropic.claude-v2",
#                               model_kwargs={"max_tokens_to_sample": 9096,
#                                             "temperature": 0.3,
#                                             "top_k": 250,
#                                             "top_p": 0.5,
#                                             "stop_sequences": ["\n\nHuman"],
#                                             }
#                               )


anthropic_claude_llm = ChatOpenAI(openai_api_key=OPENAI_KEY, model_name="gpt-4", temperature=0.0)