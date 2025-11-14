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


def verify(statement, content):
    mark = Marks.CORRECT  # Marks.CORRECT | Marks.INCORRECT | Marks.UNVERIFIABLE
    reason = "Exact reason for mark with proof (web urls might be multiple)"
    accuracy = 98  # Depending all content provided, accuracy for given statement

    return {
        "mark": mark,
        "reason": reason,
        "accuracy": accuracy,
    }
