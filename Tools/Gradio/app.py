import gradio as gr
from .gradio_fn import *

with gr.Blocks() as app:
    gr.Markdown("""
        # Chat Classifier
    """)
    target_info = gr.Textbox(label="Target info", value="从用户的对话中抽取一份用户的介绍文本，用于提供给相亲对象。")
    chatbot = gr.Chatbot(value=[], label="Chatbot")
    with gr.Row():
        user_input = gr.Textbox(label="Enter your message", scale=5)
        btn_send = gr.Button(value="Send")
    stop_flag = gr.Number(label="Stop flag", value=0)
    current_info = gr.TextArea(label="Current info")


    btn_send.click(
        fn=fn_chatbot_input,
        inputs=[stop_flag, current_info, user_input, chatbot, target_info],
        outputs=[stop_flag, current_info, user_input, chatbot],
    )
