import gradio as gr
from .gradio_fn import *

with gr.Blocks() as app:
    gr.Markdown("""
        # Chat Classifier
    """)
    chatbot = gr.Chatbot(value=[], label="Chatbot")
    with gr.Row():
        user_input = gr.Textbox(label="Enter your message", scale=5)
        btn_send = gr.Button(value="Send")
    stop_flag = gr.Number(label="Stop flag", value=0)
    current_info = gr.TextArea(label="Current info")


    btn_send.click(
        fn=fn_chatbot_input,
        inputs=[stop_flag, current_info, user_input, chatbot],
        outputs=[stop_flag, current_info, user_input, chatbot],
    )
