
# **ZADANIE: Budowa grafowej bazy nieruchomości i narzędzia wyszukującego oferty w Neo4j + LangChain**

## **Cel zadania**

Twoim zadaniem jest:

1. Uruchomić lokalnie Neo4j.
2. Załadować dane z pliku CSV do grafu Neo4j (offers → locations → buildings).
3. Wykonać pierwsze zapytanie Cypher.
4. Zintegrować Neo4j z LangChain.
5. Napisać narzędzie (`@tool`) wykonujące zapytania Cypher.
6. Zbudować agenta LLM, który umie korzystać z tego narzędzia.

---

# **CZĘŚĆ 1 — Przygotowanie środowiska Neo4j**

### 1. Uruchom bazę Neo4j

**Opcja – Docker** (rekomendowana)

```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/test123123 \
  neo4j:5
```

Sprawdź dostępność:
➡ [http://localhost:7474](http://localhost:7474)

---

# **CZĘŚĆ 2 — Wczytanie danych o nieruchomościach**

W Colab/Jupyter wklej poniższy kod (z pliku `wyklad.ipynb`):

```python
import pandas as pd

df = pd.read_csv('ogloszenia_warszawa_detailed.csv')
df['currency'] = 'PLN'
df = df.dropna()
```



---

# **CZĘŚĆ 3 — Zapis danych do Neo4j**

### 3.1 Zdefiniuj funkcję `load_offer`

Korzystasz z poniższego kodu:

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "test123123")
)
```

Funkcja zapisująca ofertę:

```python
def load_offer(tx, row):
    tx.run("""
    MERGE (o:Offer {url: $url})
    SET
        o.rooms = $rooms,
        o.area = $area,
        o.price_total = $price_total,
        ...
    MERGE (loc:Location {full_address: $full_address})
    MERGE (o)-[:LOCATED_AT]->(loc)
    MERGE (coord:Coordinates {lat: $lat, lon: $lon})
    MERGE (o)-[:HAS_COORDINATES]->(coord)
    MERGE (b:Building {building_type: $building_type})
    MERGE (o)-[:IN_BUILDING]->(b)
    """, ...)
```

### 3.2 Załaduj wszystkie rekordy

```python
with driver.session() as session:
    for i, row in df.iterrows():
        session.execute_write(load_offer, row)
```


---

# **CZĘŚĆ 4 — Pierwsze zapytanie Cypher**

Wykonaj zapytanie na najtańsze dwupokojowe mieszkania:

```python
query = """
MATCH (o:Offer)-[:LOCATED_AT]->(l:Location)
WHERE o.rooms = 2.0 AND l.city_district CONTAINS "Mokotów"
RETURN o.url, o.price_total AS price, o.area, l.full_address
ORDER BY price ASC
LIMIT 10;
"""
```

### Zadanie 4.1

Uruchom zapytanie i pokaż wynik.
Zmień filtr tak, aby wyszukać oferty w dzielnicy *Śródmieście*.



Utwórz narzędzie:

```python
from langchain.tools import tool

@tool
def search_offers(city_district: str = "Mokotów", rooms: float = 2.0, limit: int = 10):
    """
    Wyszukuje oferty w Neo4j po liczbie pokoi i dzielnicy.
    """
    query = f"""
    MATCH (o:Offer)-[:LOCATED_AT]->(l:Location)
    WHERE o.rooms = {rooms} AND l.city_district CONTAINS '{city_district}'
    RETURN 
        o.url AS url, 
        o.price_total AS price_total, 
        o.area AS area, 
        l.full_address AS address
    ORDER BY price_total ASC
    LIMIT {limit}
    """
    with driver.session() as session:
        results = session.run(query).data()
    return results
```

---


### 7.1 Utwórz agenta

```python
tools = [search_offers]

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

llm = ChatOpenAI(model="gpt-4o-mini")

agent = create_agent(
    model=llm,
    tools=tools
)
```

### 7.2 Zapytaj agenta

```python
response = agent.invoke({
    "messages": [
        {"role": "user", "content": "Znajdź 5 najtańszych ofert z 2 pokojami na Mokotowie."}
    ]
})
```

### Zadanie 7.3

Zadaj agentowi pytanie:
„Pokaż najtańsze mieszkanie na Ursynowie o powierzchni powyżej 50 m²”.

Czy agent potrafił przekształcić to w zapytanie Cypher?

