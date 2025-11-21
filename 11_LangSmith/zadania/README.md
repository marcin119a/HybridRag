## Rozszerzenie zadania: filtrowanie po liczbie zdjęć + LangSmith

Zakładamy, że masz już działający system Hybrid RAG (z zadania 9) z LangGraph z poprzednich kroków (ładowanie CSV → Document → vectorstore → retriever → graf).

### 8. Nowy retriever z filtrowaniem po metadanych

Dodaj drugi retriever, który filtruje ogłoszenia po liczbie zdjęć (`num_images` w metadata).

1. Zbuduj dodatkowy retriever na bazie istniejącego `vectorstore`:

```python
def build_image_filtered_retriever(vectorstore):
    def _filter_by_num_images(doc, liczba: int):
        return doc.metadata.get("num_images") == liczba

    base_retriever = vectorstore.as_retriever(search_kwargs={"k": 20})
    return base_retriever, _filter_by_num_images
```

2. Zrób z tego osobne narzędzie LangChain (np. jako klasyczny tool, nie prebuilt):

```python
from langchain.tools import tool

@tool("search_listings_with_images", return_direct=False)
def search_listings_with_images(query: str, liczba: int) -> str:
    """
    Wyszukuje ogłoszenia mieszkań pasujące do zapytania użytkownika,
    dodatkowo filtrując po liczbie zdjęć (num_images == liczba).
    Zwraca zwięzłe podsumowanie pasujących ofert.
    """
    docs = base_retriever.get_relevant_documents(query)
    filtered = [d for d in docs if d.metadata.get("num_images") == liczba]
    # Tu możesz np. zjoinować page_content lub zbudować krótkie podsumowanie
    return "\n\n---\n\n".join(d.page_content for d in filtered)
```

3. W grafie:

* dodaj ten tool do listy narzędzi podawanych do `ToolNode` / modelu (`[retriever_tool, image_retriever_tool]`),
* w logice `generate_query_or_respond` zadbaj, by model mógł wybrać właśnie `search_listings_with_images`, gdy użytkownik wspomina np. „pokaż ogłoszenia z co najmniej X zdjęciami” itp.

> Uwaga: dokładna implementacja filtra zależy od użytego vectorstore. Dopuszczalne jest też rozwiązanie: retriever bez filtra + ręczne filtrowanie `docs` w narzędziu (jak wyżej).

---

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

