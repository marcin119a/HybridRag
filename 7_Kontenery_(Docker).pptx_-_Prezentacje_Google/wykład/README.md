

# Tworzenie obrazu
```
docker build \
  --build-arg OPENAI_API_KEY=sk-proj-... \
  -t gradio-agent-langchain .
  ```

# Tworzenie Kontenera
```
  docker run -p 7860:7860 -e OPENAI_API_KEY gradio-agent-langchain:latest
```