from langchain_text_splitters import RecursiveCharacterTextSplitter


class LangchainProvider:
    def split_text(self, text: str) -> list[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=2500,
            chunk_overlap=300,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        return splitter.split_text(text)
