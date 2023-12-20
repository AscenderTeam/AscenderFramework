from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema.language_model import BaseLanguageModel


class ControllerFileGenerationChain(LLMChain):
    """Chain to make a file based on the description"""

    @classmethod
    def from_llm(cls, llm: BaseLanguageModel, verbose: bool = True) -> LLMChain:
        """Get the response parser."""
        file_prompt = """
        Please help me with my python controller called `{controller_name}`:
        ===previous files for context
        {previous_files_created}
        ===
        
        
        I need now you to modify the single codeblock below to achieve this:
        {description}
        
        ===you are modifying this file:
        {formatted_blank}
        ===
        
        %OUTPUT_FORMAT
        {format_instructions}
        """
        prompt = PromptTemplate(
            template=file_prompt,
            input_variables=[
                "format_instructions",
                "controller_name",
                "description_prompt",
                "previous_files_created",
                "path",
            ],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)
