## 📝 Zadanie: Dodanie nowego miasta do scrapera (Łódź)

Twoim zadaniem jest rozszerzenie istniejącego systemu scrapowania o **nowe miasto – Łódź**.

### 1. Utwórz nowy **Job** w Kubernetes

* Skopiuj istniejący plik `job-warszawa.yaml` lub `job-wroclaw.yaml`.
* Zmień nazwę Job na `scraper-lodz`.
* Ustaw zmienną środowiskową `CITY` na `"lodz"`.

---

### 2. Dodaj do **CronJob**, aby scrapowanie uruchamiało się codziennie o 2:00 dla Łodzi.


### 3. Wdróż zmiany w klastrze. 

---

### 4. Sprawdź działanie

* Wylistuj joby:

  ```bash
  kubectl get jobs -n scraper
  ```
* Podejrzyj logi:

  ```bash
  kubectl logs -n scraper -l city=lodz
  ```

---
