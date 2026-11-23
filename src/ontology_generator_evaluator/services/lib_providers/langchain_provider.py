from langchain_text_splitters import RecursiveCharacterTextSplitter


class LangchainProvider:
    def main(self):
        pass

    def split_text(self, text):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=2500,
            chunk_overlap=300,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        return splitter.split_text(text)

    def create_embedding(self, text):
        pass
