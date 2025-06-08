#!pip install python-dotenv black isort langchain langchain-openai langgraph grandalf langchain-core==0.3.60

from dotenv import load_dotenv
load_dotenv()
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a viral twitter influencer grading a tweet. Generate critique and recommendations for the user's tweet."
            "Always provide detailed recommendations, including requests for length, virality, style, etc.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

generation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a twitter techie influencer assistant tasked with writing excellent twitter posts."
            " Generate the best twitter post possible for the user's request."
            " If the user provides critique, respond with a revised version of your previous attempts.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

#import os
#from google.colab import userdata
#os.environ["OPENAI_API_KEY"] = userdata.get('OPENAI_API_KEY')

llm = ChatOpenAI()
generate_chain = generation_prompt | llm
reflect_chain = reflection_prompt | llm


from typing import List, Sequence



from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, MessageGraph



REFLECT = "reflect"
GENERATE = "generate"


def generation_node(state: Sequence[BaseMessage]):
    return generate_chain.invoke({"messages": state})


def reflection_node(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    res = reflect_chain.invoke({"messages": messages})
    return [HumanMessage(content=res.content)]


#def reflection_agent(query):
#    inputs = HumanMessage(content=query)
#    response = graph.invoke(inputs)
#    revised_tweets = [msg.content for msg in response if isinstance(msg, AIMessage)]
#    return revised_tweets

builder = MessageGraph()
builder.add_node(GENERATE, generation_node)
builder.add_node(REFLECT, reflection_node)
builder.set_entry_point(GENERATE)


def should_continue(state: List[BaseMessage]):
    if len(state) > 2:
        return END
    return REFLECT


builder.add_conditional_edges(GENERATE, should_continue)
builder.add_edge(REFLECT, GENERATE)

graph = builder.compile()
# print(graph.get_graph().draw_mermaid())
# graph.get_graph().print_ascii()
query="""Make this tweet better:"
                                    @LangChainAI
            — newly Tool Calling feature is seriously underrated.

            After a long wait, it's  here- making the implementation of agents across different models with function calling - super easy.

            Made a video covering their newest blog post

                                  """
def reflection_agent(query):
    inputs = HumanMessage(content=query)
    response = graph.invoke(inputs)
    return response[-1].content

ans=reflection_agent(query)
print(ans)