import json, re
from connect import get_llm
from marks_of_truth import Marks
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = get_llm("deepseek_r1")

prompt_template = """

"""

prompt = ChatPromptTemplate.from_template(prompt_template)
output_parser = StrOutputParser()


def web_search(text: str):

    return {
        "mark": Marks.CORRECT,
        "reason": "reason",
        "accuracy": 100,
    }
