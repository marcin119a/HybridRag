## Rozszerzenie zadania:  LangSmith

Zakładamy, że masz już działający system Hybrid RAG (z zadania 9) z LangGraph z poprzednich kroków (ładowanie CSV → Document → vectorstore → retriever → graf).


### 9. Integracja z LangSmith (monitoring i debugging)

Skonfiguruj LangSmith, aby cały przepływ LangGraph (w tym narzędzia) był trace’owany.

1. Zainstaluj LangSmith (jeśli jeszcze nie):

```bash
pip install langsmith
```

2. Ustaw zmienne środowiskowe (np. w `.env` albo przed uruchomieniem aplikacji):

```bash
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
export LANGCHAIN_API_KEY="TWÓJ_LANGSMITH_API_KEY"
export LANGCHAIN_PROJECT="Hybrid-RAG-Mieszkania"
```

3. Upewnij się, że używasz modeli / narzędzi z ekosystemu LangChain (co już robisz) – po ustawieniu powyższych zmiennych:

* każdy run modelu (`ChatOpenAI` / `ChatOpenAI` z `langchain-openai`),
* każdy call narzędzia,
* wywołania węzłów LangGraph

będą widoczne w panelu LangSmith jako pojedynczy trace z historią kroków.

