from ..LLM.ernie import ErnieClass
import os

ernie_access_token = os.environ["ERNIE_TOKEN"]
llm = ErnieClass(access_token=ernie_access_token)

def get_prompt_extracted(customer_information, input_text, target_info):
    prompt = f'''
    你是一个对话访谈机器人，你需要通过对话挖掘用户的信息，以完成你的目标。
    你的目标是{target_info}。
    
    当前，你需要对<用户回复>进行分析，从中挖掘用户的信息，将这些信息补充到<用户信息>中，你也可以对<用户信息>中已有的信息进行修正。
    
    返回内容是一个字典
    {"{"}
        "整理后的用户信息":String
    {"}"}
    <用户信息>：{customer_information}，
    <用户回复>：{input_text}。
    '''
    return prompt

def get_prompt_question(customer_information, input_text, target_info):
    prompt = f'''
    你是一个对话访谈机器人，你需要通过对话挖掘用户的信息，以完成你的目标。
    你的目标是{target_info}。
    
    具体来说，你需要检查<用户信息>并考虑你是否从用户那里获取了足够的信息，从而支持你完成你的目标。如果信息并不充分，请继续询问。
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

def refresh_extracted_information(chat_history, customer_information, input_text, target_info):
    prompt = get_prompt_extracted(customer_information, input_text, target_info)
    input_msg = chat_history + [{"role": "user", "content": prompt}]
    json_dict = llm.get_llm_json_answer_with_msg(input_msg)
    new_customer_information = json_dict["整理后的用户信息"]
    return new_customer_information

def get_reply(chat_history, customer_information, input_text, target_info):
    prompt_question = get_prompt_question(customer_information, input_text, target_info)
    input_msg = chat_history + [{"role": "user", "content": prompt_question}]
    reply = llm.get_llm_json_answer_with_msg(input_msg)
    stop_flag = 1 if reply["结束判断"] == 1 else 0
    new_question = reply["新的问题"]
    return stop_flag, new_question

def fn_chatbot_input(stop_flag, current_info, input_text, chat_bot_infor, target_info):
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

    customer_information = refresh_extracted_information(chat_history, customer_information, input_text, target_info)

    stop_flag, new_question = get_reply(chat_history, customer_information, input_text, target_info)

    if stop_flag == 1:
        chat_bot_infor.append((input_text, "感谢您的回答，本次对话到此结束~"))
    else:
        chat_bot_infor.append((input_text, new_question))
    current_info = customer_information

    return stop_flag, current_info, "", chat_bot_infor