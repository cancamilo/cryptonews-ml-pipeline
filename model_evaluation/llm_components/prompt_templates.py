from abc import ABC, abstractmethod
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.prompts import PromptTemplate, BasePromptTemplate, ChatPromptTemplate


class BaseTemplate(ABC, BaseModel):
    @abstractmethod
    def create_template(self) -> BasePromptTemplate:
        pass

class QueryMetadata(BaseModel):
    """Information to extract from the user query. 
    Dates should be transformed to yyyy-mm-dd and be relative to the given current date"""

    currency: str = Field(description="The cryptocurrency mentioned in the query.")
    date: str = Field(description="date from the text in the format yyyy-mm-dd")

class QueryExpansionTemplate(BaseTemplate):
    prompt: str = """You are an AI language model assistant. Your task is to generate {n_expansions}
    different versions of the given user question to retrieve relevant documents from a vector
    database. By generating multiple perspectives on the user question, your goal is to help
    the user overcome some of the limitations of the distance-based similarity search.
    Provide these alternative questions seperated by '{separator}'.
    Original question: {question}"""

    @property
    def separator(self) -> str:
        return "#next-question#"

    def create_template(self, n_expansions: int) -> BasePromptTemplate:
        return PromptTemplate(
            template=self.prompt,
            input_variables=["question"],
            partial_variables={
                "separator": self.separator,
                "n_expansions": n_expansions,
            },
        )
    
class QueryMetaTemplate(BaseTemplate):

    def create_template(self) -> BasePromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", "Today´s date is {current_date}."),
            ("human", "{user_query}"),
        ])

class RerankingTemplate(BaseTemplate):
    prompt: str = """You are an AI language model assistant. Your task is to rerank passages related to a query
    based on their relevance. 
    The most relevant passages should be put at the beginning. 
    You should only pick at max {keep_top_k} passages.
    The provided and reranked documents are separated by '{separator}'.
    
    The following are passages related to this query: {question}.
    
    Passages: 
    {passages}
    """

    def create_template(self, keep_top_k: int) -> PromptTemplate:
        return PromptTemplate(
            template=self.prompt,
            input_variables=["question", "passages"],
            partial_variables={"keep_top_k": keep_top_k, "separator": self.separator},
        )

    @property
    def separator(self) -> str:
        return "\n#next-document#\n"

class QATemplate(BaseTemplate):

    prompt: str = """You are an AI language model assistant whose job is to provide answers to cryptocurrency investors
    in order to make informed decisions based on news. If the user query is a question, provide answers based on the given context only if it is relevant.
    If the user query is not a question, just give a summary of the relevant content in the context related to the query. 
    USER_QUERY:
    ```{user_query}```
    CONTEXT:
    {context}"""

    def create_template(self) -> BasePromptTemplate:
        return PromptTemplate(
            template=self.prompt,
            input_variables=["user_query", "context"]
        )
    
class InferenceTemplate(BaseTemplate):
    simple_prompt: str = """You are an AI language model assistant. Your task is to generate a cohesive and concise response to the user question.
    Question: {question}
    """

    rag_prompt: str = """ You are a specialist in cryptocurrency content writing. Your task is to create articles based on a user query given a specific context 
    with additional information consisting of the user's previous writings and his knowledge.
    
    Here is a list of steps that you need to follow in order to solve this task:
    Step 1: You need to analyze the user provided query : {question}
    Step 2: You need to analyze the provided context and how the information in it relates to the user question: {context}
    Step 3: Generate the content keeping in mind that it needs to be as cohesive and concise as possible related to the subject presented in the query and similar to the users writing style and knowledge presented in the context.
    """

    def create_template(self, enable_rag: bool = True) -> PromptTemplate:
        if enable_rag is True:
            return PromptTemplate(
                template=self.rag_prompt, input_variables=["question", "context"]
            )

        return PromptTemplate(template=self.simple_prompt, input_variables=["question"])
    
class LLMEvaluationTemplate(BaseTemplate):
    prompt: str = """
        You are an AI assistant and your task is to evaluate the output generated by another LLM.
        You need to follow these steps:
        Step 1: Analyze the user query: {query}
        Step 2: Analyze the response: {output}
        Step 3: Evaluate the generated response based on the following criteria and provide a score from 1 to 5 along with a brief justification for each criterion:

        Evaluation:
        Relevance - [score]
        [1 sentence justification why relevance = score]
        Coherence - [score]
        [1 sentence justification why coherence = score]
        Conciseness - [score]
        [1 sentence justification why conciseness = score]
"""

    def create_template(self) -> PromptTemplate:
        return PromptTemplate(template=self.prompt, input_variables=["query", "output"])