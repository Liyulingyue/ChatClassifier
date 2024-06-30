import gradio as gr

class StorageHelper(object):
    def __init__(self):
        self.value = {}

    def set(self, key: str, value):
        self.value[key] = value

    def get(self, key: str, default):
        if key in self.value:
            return self.value[key]
        else:
            return default

with gr.Blocks() as app:
    gr.Markdown("""# Chat Classifier""")
    chatbot = gr.Chatbot()
    input_text = gr.Textbox(label="Input Text")
    with gr.Row():
        btn_send = gr.Button("Send")
        btn_clear = gr.Button("Clear")