from ..LLM.ernie import ErnieClass
import os

ernie_access_token = os.environ["ERNIE_TOKEN"]
llm = ErnieClass(access_token=ernie_access_token)

def get_prompt_extracted(customer_information, input_text):
    prompt = f'''
    你是一个相亲信息记录机器人，你需要对<用户回复>进行分析，从中挖掘用户的信息，以及你对用户的评价（例如情绪、性格特点等），
    将这些信息补充到<用户信息>中，你也可以对<用户信息>中已有的信息进行修正。
    返回内容是一个字典
    {"{"}
        "整理后的用户信息":String
    {"}"}
    <用户信息>：{customer_information}，
    <用户回复>：{input_text}。
    '''
    return prompt

def get_prompt_question(customer_information, input_text):
    prompt = f'''
    在每个人进行相亲之前，都需要先录入自己的信息，但是自己对自己的评价可能较为主观。
    因此，通过对话、一问一答的方式，除了能够获取这个人的个人信息之外，还能够挖掘这个人的能够更好地采集到这个人的性格特征。
    你作为一个相亲信息记录机器人，需要通过对话的方式收集用户信息，对于一些事实性的信息，例如姓名、年龄，可以从用户对话中抽取，或者直接询问。
    但对于一些具有抽象特征的信息，例如脾气、心态、性格等，需要从对话中，根据言谈特征自行总结。

    具体来说，你需要检查<用户信息>并考虑你是否从用户那里获取了足够的信息，从而支持你根据这份资料向其他人介绍这位相亲对象。如果信息并不充分，请继续询问。
    如果信息充分，则结束询问，输出中<结束判断>为1，否则为0，请检查对话历史，保证对话的连贯性，用户的最近一次回复在<用户回复>中，而非对话历史中。

    返回内容是一个字典
    {"{"}
        "结束判断":int,
        "新的问题":String
    {"}"}

    <用户信息>：{customer_information}，
    <用户回复>：{input_text}。
    '''
    return prompt

def refresh_extracted_information(chat_history, customer_information, input_text):
    prompt = get_prompt_extracted(customer_information, input_text)
    input_msg = chat_history + [{"role": "user", "content": prompt}]
    json_dict = llm.get_llm_json_answer_with_msg(input_msg)
    new_customer_information = json_dict["整理后的用户信息"]
    return new_customer_information

def get_reply(chat_history, customer_information, input_text):
    prompt_question = get_prompt_question(customer_information, input_text)
    input_msg = chat_history + [{"role": "user", "content": prompt_question}]
    reply = llm.get_llm_json_answer_with_msg(input_msg)
    stop_flag = 1 if reply["结束判断"] == 1 else 0
    new_question = reply["新的问题"]
    return stop_flag, new_question

def fn_chatbot_input(stop_flag, current_info, input_text, chat_bot_infor):
    """
    根据用户输入和当前信息，与聊天机器人进行交互，并更新用户信息。

    Args:
        stop_flag (int): 停止标志，用于控制交互过程是否结束。
        current_info (str): 当前用户信息。
        input_text (str): 用户输入文本。
        chat_bot_infor (List[Tuple[str, str]]): 聊天机器人与用户的历史交互记录。

    Returns:
        Tuple[int, str, str, List[Tuple[str, str]]]: 返回一个元组，包含以下内容：
        - 停止标志 (int)：指示交互过程是否结束。
        - 更新后的用户信息 (str)。
        - 空字符串 (str)：占位符，实际使用中可以移除或替换为其他内容。
        - 更新后的聊天机器人与用户的历史交互记录 (List[Tuple[str, str]])。

    """

    customer_information = current_info
    chat_history = []
    for chat_item in chat_bot_infor:
        chat_history.extend([{"role": "user", "content": chat_item[0]}, {"role": "assistant", "content": chat_item[1]}])

    customer_information = refresh_extracted_information(chat_history, customer_information, input_text)

    stop_flag, new_question = get_reply(chat_history, customer_information, input_text)

    if stop_flag == 1:
        chat_bot_infor.append((input_text, "感谢您的回答，本次对话到此结束~"))
    else:
        chat_bot_infor.append((input_text, new_question))

    return stop_flag, current_info, "", chat_bot_infor