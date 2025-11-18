import pandas as pd
df1 = pd.read_csv('https://raw.githubusercontent.com/marcin119a/r_d/refs/heads/main/scraper/data/ogloszenia_lodz_cleaned.csv')
df1['city'] = 'Łódź'

df2 = pd.read_csv('https://raw.githubusercontent.com/marcin119a/r_d/refs/heads/main/scraper/data/ogloszenia_warszawa_cleaned.csv')
df2['city'] = 'Warszawa'

df = pd.concat([df1, df2])
df.head()

df = df[['locality', 'price_total_zl', 'area', 'rooms', 'city', 'url']]
print(df.info())

from langchain.tools import tool

@tool
def search_listings(city: str, max_price: int = 1_000_000):
  """
  Zwraca pierwsze 5 ogłoszeń z danego miasta poniżej max_price.
  """
  subset = df.query("city == @city and price_total_zl <= @max_price").sort_values(by='price_total_zl')
  return subset.head(5).to_dict(orient="records")

tools=[search_listings]

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse

basic_model = ChatOpenAI(model="gpt-4o-mini")
advanced_model = ChatOpenAI(model="gpt-4o")


@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
   """Choose model based on conversation complexity."""
   message_count = len(request.state["messages"])

   if message_count > 10:
       # Use an advanced model for longer conversations
       model = advanced_model
   else:
       model = basic_model

   request.model = model
   return handler(request)


def run_agent(query: str) -> str:
    agent = create_agent(
    model=basic_model,  # Default model
    tools=tools,
    middleware=[dynamic_model_selection]
    )
    result = agent.invoke(
        {"messages": [{"role": "user", "content": query}]},
        context={"user_role": "expert"}
    )
    return (result['messages'][-1].content)

import gradio as gr

with gr.Blocks() as demo:
    gr.Markdown("# Wyszukiwarka nieruchomości")
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="Zapytaj o nieruchomości w Warszawie lub Łodzi")
    clear = gr.Button("Wyczyść czat")

    def user(user_message, history):
        return "", history + [[user_message, None]]

    def bot(history):
        user_message = history[-1][0]
        response = run_agent(user_message)
        history[-1][1] = response
        return history

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)

demo.launch(server_name="0.0.0.0", server_port=7860)