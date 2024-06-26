from llm_components.prompt_templates import QATemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

class QAContext():
    @staticmethod
    def rag_query(query: str, context: str):
        prompt = QATemplate().create_template()
        model = ChatOpenAI(temperature=0)
        chain = prompt | model | StrOutputParser()
        return chain.invoke({"user_query":query,  "context": context})