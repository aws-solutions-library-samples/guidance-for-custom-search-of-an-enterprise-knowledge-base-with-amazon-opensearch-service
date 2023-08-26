from langchain.prompts.prompt import PromptTemplate


CHINESE_PROMPT_TEMPLATE = """基于以下已知信息，简洁和专业的来回答用户的问题，并告知是依据哪些信息来进行回答的。
   如果无法从中得到答案，请说 "根据已知信息无法回答该问题" 或 "没有提供足够的相关信息"，不允许在答案中添加编造成分，答案请使用中文。
    
            问题: {question}
            =========
            {context}
            =========
            答案:"""
            
CHINESE_TC_PROMPT_TEMPLATE = """基于以下已知信息，簡潔和專業的來回答用戶的問題，並告知是依據哪些信息來進行回答的。
   如果無法從中得到答案，請說 "根據已知信息無法回答該問題" 或 "沒有提供足夠的相關信息"，不允許在答案中添加編造成分，答案請使用中文。
    
            問題: {question}
            =========
            {context}
            =========
            答案:"""           
            

ENGLISH_PROMPT_TEMPLATE = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
{context}

Question: {question}
Answer:"""  


SUMMARIZE_PROMPT_TEMPLATE = """请根据顾客和咨询师的通话记录，写一段顾客提出问题的摘要，突出显示与汽车故障相关的要点, 摘要不需要有咨询师的相关内容:
{text}

摘要是:"""

COMBINE_SUMMARIZE_PROMPT_TEMPLATE = """给出多段从长通话记录中提取出来的摘要信息，总结成一段无语义重复的用户问题摘要，突出顾客提出的问题:
{text}

摘要是:"""
 

CHINESE_CHAT_PROMPT_TEMPLATE = """你是一个助手，请根据以下对话历史记录，回答人类输入的问题，生成答案文本。
    =========        
    {history}
    =========
    人类输入: {human_input}
    回答:""" 


ENGLISH_CHAT_PROMPT_TEMPLATE = """You are an assistant, Refer to the following conversation history to answer questions from users.
       
            {history}
          
            user's question: {human_input}
            Answer:""" 



en_condense_qusetion_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
EN_CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(en_condense_qusetion_template)

cn_condense_question_template = """给定以下对话和后续问题，将后续问题重新表述为独立问题。

聊天历史记录:
{chat_history}
后续输入: {question}
独立问题:"""
CN_CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(cn_condense_question_template)

tc_condense_question_template = """給定以下對話和後續問題，將後續問題重新表述爲獨立問題。

聊天曆史記錄:
{chat_history}
後續輸入: {question}
獨立問題:"""
TC_CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(tc_condense_question_template)


EN_CONDENSE_PROMPT_LLAMA2 = "Given the following conversation and a follow up question, rephrase the last user question to be a standalone question."


EN_CHAT_PROMPT_LLAMA2 = "You are an assistant, Refer to the following conversation history to answer questions from users."