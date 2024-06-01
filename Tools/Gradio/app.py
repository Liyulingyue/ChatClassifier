import gradio as gr
from .gradio_fn import *

with gr.Blocks() as app:
    gr.Markdown("""
        # Chat Classifier
    """)
    target_info = gr.Textbox(label="Target info", value="通过和用户对话，总结用户的特质。这些特质将用于判断用户属于哈利波特中的哪个学院。")
    with gr.Row():
        choices_describe = gr.TextArea(label="选择描述",
                                       value="""
                                       格兰芬多 (Gryffindor)：以勇敢、骁勇、豪爽和直爽著称。格兰芬多的学生通常表现出明显的勇敢和英雄主义倾向。
                                       斯莱特林 (Slytherin)：斯莱特林学院看重野心、狡猾、足智多谋和血统纯正。该学院的学生往往精明且有领导才能，但也可能倾向于狡诈和自私。
                                       赫奇帕奇 (Hufflepuff)：这个学院重视努力、耐心、忠诚和公平竞争。赫奇帕奇的学生通常是勤奋和忠诚的，他们珍视正直和努力的品质。
                                       拉文克劳 (Ravenclaw)：拉文克劳学院强调智慧、聪明、好奇心和创造力。该学院的学生倾向于拥有敏锐的头脑和对知识的渴望。""",
                                       scale=5)
        make_choice = gr.Checkbox(label="支持选择")
    chatbot = gr.Chatbot(value=[], label="Chatbot")
    with gr.Row():
        user_input = gr.Textbox(label="Enter your message", scale=5)
        btn_send = gr.Button(value="Send")
    stop_flag = gr.Number(label="Stop flag", value=0)
    current_info = gr.TextArea(label="Current info")


    btn_send.click(
        fn=fn_chatbot_input,
        inputs=[stop_flag, current_info, user_input, chatbot, target_info, choices_describe, make_choice],
        outputs=[stop_flag, current_info, user_input, chatbot],
    )
