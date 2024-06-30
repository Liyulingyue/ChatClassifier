import os
import Agently

ernie_token = os.environ['ERNIE_TOKEN']
agent_factory = (
    Agently.AgentFactory()
        .set_settings("current_model", "ERNIE")
        .set_settings("model.ERNIE.auth", { "aistudio": ernie_token })
        .set_settings("model.ERNIE.options", { "model": "ernie-4.0" }) # 缺Token可以使用免费模型，例如ernie-speed
)

## 创建工作流对象并初始化agent
workflow = Agently.Workflow()

agent = agent_factory.create_agent()
agent\
    .set_agent_prompt("role", "一个访谈式对话机器人，你需要基于{info.choices}和用户进行对话访谈，并总结用户信息，最终判断用户属于{info.choices}的哪一类")\
    .set_agent_prompt("instruct", [
        "1. 在提问时，你应当尽可能旁敲侧击，避免直接性的让用户回答和{info.choices}有关的信息。从而使得你可以通过总结的方式尽可能客观地获取用户的信息。",
        "2. 在提问时，你需要结合已知的信息（{input.user_info}, {input.chat_history}），避免向用户提出重复的问题。"
        "3. 在总结时，你需要参考已知的信息（{input.user_info}, {input.chat_history}），本轮问答信息（{input.question}和{input.answer}），进行分析，挖掘用户信息，给出你对用户的评价/总结，评价/总结内容应当尽可能详细。"
        "4. 在总结时，如果有必要，你可以推翻已有的总结/评价信息。"
    ])

debug_mode = True # 调试模式，False时不输出调试信息
def debug_print(function_name ,value): # 调试输出函数
    if debug_mode:
        print(f"[DEBUG MODE - {function_name}]: ", value)


## 定义工作块
## 初始化模块，在这个模块涉及到对属性的初始化
@workflow.chunk()
def openning(inputs, storage):
    debug_print("openning", "start")
    # 初始化
    init_choices = inputs["default"]["choices"]
    agent.set_agent_prompt("info", {"choices": init_choices})  # 初始化选择，请注意，info的配置与上面role，instruct对应
    chat_round = inputs["default"]["least_talk_round"]
    storage.set("chat_round", chat_round + 1)  # 为了避免存0问题，这里+1
    role = inputs["default"]["role"]
    if role != "":
        debug_print("openning", "change the role")
        agent.set_user_prompt("role", role)
    # 初始化其他信息
    storage.set("user_info", "")
    storage.set("question", "")
    storage.set("answer", "")
    chat_history = [{"role": "user", "content": "hi"}, ]
    storage.set("chat_history", chat_history)

    result = agent \
        .input("请你作为主持人，生成一段开场白") \
        .output("一段开场白，引导用户进行对话，最好是抛出一个问题给用户") \
        .start()

    debug_print("openning", result)
    storage.set("question", result)
    return


## 获取用户回复
@workflow.chunk()
def chat(inputs, storage):
    debug_print("chat", "start")
    question = storage.get("question")
    print("主持人：", question)
    answer = input("您的回复：")
    storage.set("answer", answer)
    # 更新聊天记录
    chat_history = storage.get("chat_history")
    chat_history.append({"role": "assistant", "content": question})
    chat_history.append({"role": "user", "content": answer})
    storage.set("chat_history", chat_history)

    # 更新对话次数
    chat_round = storage.get("chat_round")
    if chat_round > 1:
        chat_round = chat_round - 1
    else:
        chat_round = 1
    storage.set("chat_round", chat_round)

    return


## 抽象用户信息
@workflow.chunk()
def abstract_info(inputs, storage):
    debug_print("abstract_info", "start")
    # 获取输入信息
    question = storage.get("question")
    answer = storage.get("answer")
    user_info = storage.get("user_info")
    chat_history = storage.get("chat_history")

    result = agent \
        .input({"answer": answer, "question": question, "user_info": user_info, "chat_history": chat_history}) \
        .output({
        "user_info": (str, "总结得到的用户信息"),
    }) \
        .start()
    debug_print("abstract_info", result)
    storage.set("user_info", result["user_info"])

    return result


## 判断信息是否充足
@workflow.chunk()
def judge_sufficiency(inputs, storage):
    debug_print("judge_sufficiency", "start")
    # 获取输入信息
    user_info = storage.get("user_info")

    chat_round = storage.get("chat_round")
    if 1 >= chat_round:  # 对话次数足够
        result = agent \
            .input({"user_info": user_info}) \
            .output({
            "sufficiency": (int, "当前总结得到的用户信息{input.user_info}是否足以进行判断类别，充分为1，不充分为0"),
        }) \
            .start()
        debug_print("judge_sufficiency", result)
    else:  # 对话次数不足，直接为0
        result = {"sufficiency": 0}

    return result


## 生成新的问题
@workflow.chunk()
def question(inputs, storage):
    debug_print("question", "start")
    # 获取输入信息
    user_info = storage.get("user_info")
    chat_history = storage.get("chat_history")

    result = agent \
        .input({"user_info": user_info, "chat_history": chat_history}) \
        .output({
        "question": (str, "新的追问问题"),
    }) \
        .start()
    debug_print("question", result)
    storage.set("question", result["question"])

    return


## 判断类型
@workflow.chunk()
def get_type(inputs, storage):
    debug_print("get_type", "start")
    user_info = storage.get("user_info")

    result = agent \
        .input({"user_info": user_info}) \
        .output({
        "user_type": (str, "用户类型"),
        "reason": (str, "用户属于此类型的原因"),
    }) \
        .start()

    print("主持人：您的类型是", result["user_type"])
    print("主持人：您属于此类型的原因是", result["reason"])
    return result


## 连接工作块
(
    workflow
    .connect_to("openning")
    .connect_to("chat")
    .connect_to("abstract_info")
    .connect_to("judge_sufficiency")
    .if_condition(lambda value, storage: value["sufficiency"] == 1)
    .connect_to("get_type")
    .connect_to("end")
    .else_condition()
    .connect_to("question")
    .connect_to("chat")
)