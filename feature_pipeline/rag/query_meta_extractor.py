from langchain_openai import ChatOpenAI
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.utils.function_calling import convert_to_openai_function
from llm_components.prompt_templates import QueryMetaTemplate, QueryMetadata
from settings import settings
from datetime import datetime

class QueryMetaExtractor:

    @staticmethod
    def generate_response(query: str) -> str:

        openai_functions = [convert_to_openai_function(QueryMetadata)]
        prompt = QueryMetaTemplate().create_template()
        model = ChatOpenAI(temperature=0)
        parser = JsonOutputFunctionsParser()
        chain = prompt | model.bind(functions=openai_functions) | parser

        current_date = datetime.now().strftime(format="%Y-%m-%d")
        return chain.invoke({"current_date":current_date,  "user_query": query})
