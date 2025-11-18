import gradio as gr 


app = gr.Interface(
    fn=lambda name: f"Witaj, {name}!",
    inputs=gr.Textbox(label="Podaj swoje imię"),
    outputs=gr.Textbox(label="Powitanie"),
    title="Prosty przykład Gradio",
    description="Aplikacja witająca użytkownika po imieniu."
)

app.launch(server_name="0.0.0.0", server_port=7860)