import re
from langchain.schema import BaseOutputParser


class MarkdownCodeblockParser(BaseOutputParser):
    def get_format_instructions(self) -> str:
        return """Respond your code as a single code block with all code in it. Make a code block as in markdown ```<>```"""

    def parse(self, response):
        # Regular expression to find code blocks, with or without language tags
        code_blocks = re.findall(r"```(?:[a-zA-Z0-9-]*\n)?(.*?)```", response, re.DOTALL)
        return code_blocks


if __name__ == '__main__':
    m = MarkdownCodeblockParser()
    print(m.parse("""```python
aaa
```
"""))
