from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema.language_model import BaseLanguageModel


class ControllerNameGenerationChain(LLMChain):
    """Chain to make a name based on the description"""

    @classmethod
    def from_llm(cls, llm: BaseLanguageModel, verbose: bool = True) -> LLMChain:
        """Get the response parser."""
        name_prompt = """
        %DESCRIPTION
        A controller for handling tasks
        
        %NAME
        task
        
        %DESCRIPTION
        {description}
        
        %NAME
        """
        prompt = PromptTemplate(
            template=name_prompt,
            input_variables=[
                "description",
            ],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)
