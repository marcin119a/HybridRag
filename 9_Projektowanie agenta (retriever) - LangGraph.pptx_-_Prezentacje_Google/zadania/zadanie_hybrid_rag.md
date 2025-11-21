# Zadanie: Budowa systemu Hybrid RAG dla wyszukiwania mieszkań

## Cel zadania

Zbuduj system Hybrid RAG (Retrieval-Augmented Generation) wykorzystujący LangGraph, który będzie inteligentnie decydował, kiedy używać wyszukiwania w bazie dokumentów, a kiedy odpowiadać bezpośrednio. System będzie działał na danych z ogłoszeń o mieszkaniach.

## Wymagania wstępne

- Znajomość Python
- Podstawowa znajomość LangChain i LangGraph
- Dostęp do API OpenAI (lub innego dostawcy LLM)
- Biblioteki: `langchain`, `langchain-openai`, `langgraph`, `pandas`, `tiktoken`

## Krok 1: Przygotowanie danych

1. Pobierz plik z danymi ogłoszeń:
   ```bash
   wget https://raw.githubusercontent.com/marcin119a/r_d/refs/heads/main/scraper/data/ogloszenia_lodz_detailed.csv
   ```

2. Wczytaj dane do pandas DataFrame i przygotuj strukturę:
   - Wybierz kolumny: `price_total_zl`, `full_address`, `photo_count`, `description_text`, `url`
   - Zmień nazwy kolumn na: `price`, `street_address`, `num_images`, `description`, `offer_url`
   - Dodaj kolumnę `currency` z wartością `'PLN'`
   - Uporządkuj kolumny w kolejności: `['price', 'currency', 'street_address', 'num_images', 'description', 'offer_url']`

## Krok 2: Tworzenie dokumentów

Przekształć każdy wiersz DataFrame na obiekt `Document` z LangChain:
- `page_content`: sformatowany tekst zawierający adres, cenę, liczbę zdjęć i opis
- `metadata`: słownik z kluczami: `offer_url`, `price`, `currency`, `street_address`, `num_images`

Format tekstu:
```
Adres: {street_address}
Cena: {price} {currency}
Liczba zdjęć: {num_images}

Opis: {description}
```

## Krok 3: Podział dokumentów na chunki

Użyj `RecursiveCharacterTextSplitter` z tiktoken encoder:
- `chunk_size=400`
- `chunk_overlap=100`

## Krok 4: Tworzenie wektorowej bazy danych

1. Utwórz `InMemoryVectorStore` z wykorzystaniem `OpenAIEmbeddings()`
2. Dodaj wszystkie podzielone dokumenty do vectorstore
3. Utwórz retriever z domyślnymi parametrami

## Krok 5: Narzędzie retrievera

Utwórz narzędzie retrievera używając `create_retriever_tool`:
- Nazwa narzędzia: `"search_listings"`
- Opis: `"Wyszukuj i zwracaj informacje o ogłoszeniach mieszkań (adres, cena, opis)."`

## Krok 6: Budowa grafu LangGraph

Zaimplementuj graf z następującymi węzłami i logiką:

### 6.1. Węzeł `generate_query_or_respond`
- Funkcja decyduje, czy użyć narzędzia `search_listings` (gdy potrzebny RAG) czy odpowiedzieć bezpośrednio (np. small talk)
- Użyj modelu `gpt-4o` z `temperature=0`
- Binduj narzędzie `retriever_tool` do modelu
- Zwracaj odpowiedź w formacie zgodnym z `MessagesState`

### 6.2. Węzeł `retrieve`
- Użyj wbudowanego `ToolNode` z narzędziem `retriever_tool`
- Wykonuje wyszukiwanie w bazie dokumentów

### 6.3. Węzeł `grade_documents`
- Funkcja ocenia, czy znalezione dokumenty są istotne względem pytania użytkownika
- Użyj modelu `gpt-4o` z `temperature=0` i structured output
- Zdefiniuj schemat Pydantic:
  ```python
  class GradeDocuments(BaseModel):
      binary_score: str = Field(
          description="Relevance score: 'yes' jeśli istotne, 'no' jeśli nie"
      )
  ```
- Prompt dla gradera:
  ```
  Jesteś graderem oceniającym, czy znalezione ogłoszenie jest istotne względem pytania użytkownika.
  Oto treść ogłoszenia:
  {context}
  
  Oto pytanie użytkownika:
  {question}
  
  Jeśli ogłoszenie pasuje do intencji pytania (lokalizacja, cena, cechy), odpowiedz 'yes'. 
  Jeśli nie pasuje – 'no'.
  ```
- Zwraca `"generate_answer"` jeśli `binary_score == "yes"`, w przeciwnym razie `"rewrite_question"`

### 6.4. Węzeł `rewrite_question`
- Poprawia pytanie użytkownika, aby było bardziej precyzyjne
- Prompt:
  ```
  Popraw pytanie użytkownika tak, aby było bardziej precyzyjne w kontekście rynku nieruchomości.
  Weź pod uwagę lokalizację, cenę, liczbę pokoi, cechy mieszkania.
  Oto pytanie:
  -------
  {question}
  -------
  Zwróć jedno, lepsze pytanie.
  ```
- Zwraca nowe pytanie jako `HumanMessage`, które trafia z powrotem do `generate_query_or_respond`

### 6.5. Węzeł `generate_answer`
- Generuje finalną odpowiedź na podstawie znalezionych dokumentów
- Prompt:
  ```
  Jesteś asystentem pomagającym analizować rynek mieszkań na podstawie ogłoszeń.
  Korzystaj z poniższego kontekstu (fragmenty ogłoszeń: adres, cena, opis), aby odpowiedzieć na pytanie.
  Jeśli nie wiesz – napisz, że na podstawie dostępnych ogłoszeń nie możesz odpowiedzieć.
  Maksymalnie 4 zdania. Odpowiadaj po polsku.
  
  Pytanie: {question}
  
  Kontekst z ogłoszeń:
  {context}
  ```

### 6.6. Struktura grafu

```
START → generate_query_or_respond
         ↓
    [conditional: tools_condition]
         ↓
    ┌────┴────┐
    │         │
  tools      END
    │
  retrieve
    │
[conditional: grade_documents]
    │
    ├──→ generate_answer → END
    │
    └──→ rewrite_question → generate_query_or_respond
```

## Krok 7: Testowanie systemu

Przetestuj system na następujących przykładach:

1. **Pytanie wymagające RAG:**
   ```
   "Znajdź mieszkania 2-pokojowe na Bautach do 900 tysięcy z balkonem."
   ```

2. **Small talk (bez RAG):**
   ```
   "Cześć, co robisz?"
   ```

3. **Pytanie wymagające przepisania:**
   ```
   "Mieszkania"
   ```


