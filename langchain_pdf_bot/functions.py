from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS, Chroma
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.chains import SimpleSequentialChain
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
import openai
import os

# Import API Key
from apikey import API_KEY
os.environ["OPENAI_API_KEY"] = API_KEY

"""
query function
"""


def qa(folder_path, chain_type, query, k=4, model=OpenAI(temperature=0), show_pages=False):
    """
    Read-in and split the documents
    """
    all_pages = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.pdf'):
            file_path = os.path.join(folder_path, file_name)
            file = PyPDFLoader(file_path)
            file = file.load()
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=10, chunk_overlap=10)
            pages = text_splitter.split_documents(file)
            all_pages.extend(pages)

    if show_pages:
        print(len(all_pages))
        for page in all_pages:
            print(page)

    """
    Vectorstores
    """
    embeddings = OpenAIEmbeddings()

    db = FAISS.from_documents(all_pages, embeddings)
    # FAISS vectorstores can also be merged and saved to disk

    """
    Retriever
    """
    # Amount of returned documents k
    retriever = db.as_retriever(
        search_type="similarity", search_kwargs={"k": k})
    # Not needed if Retrieval Chain is used
    # docs = retriever.get_relevant_documents("what did he say about ketanji brown jackson")
    # -> get relevant documents from the retriever, but not really needed here

    docs = db.similarity_search(query, k=k)
    print(len(docs))

    """
    Chains
    """


    chain = RetrievalQA.from_chain_type(
        llm=OpenAI(temperature=0),
        chain_type="stuff",
        retriever=retriever,
        verbose=True,
        return_source_documents=True
    )

    print(chain.combine_documents_chain.llm_chain.prompt.template)

    result = chain({"query": query})

    print(chain.combine_documents_chain.llm_chain.prompt)

    # chain = load_qa_with_sources_chain(
    #     OpenAI(temperature=0), chain_type="stuff", verbose=True)
    # result = chain({"input_documents": docs, "question": query},
    #                return_only_outputs=True)

    return result


def qa2(file, query, chain_type, k):
    # load document
    loader = PyPDFLoader(file)
    documents = loader.load()
    # split the documents into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    # select which embeddings we want to use
    embeddings = OpenAIEmbeddings()
    # create the vectorestore to use as the index
    db = Chroma.from_documents(texts, embeddings)
    # expose this index in a retriever interface
    retriever = db.as_retriever(
        search_type="similarity", search_kwargs={"k": k})
    # create a chain to answer questions
    qa = RetrievalQA.from_chain_type(
        llm=OpenAI(), chain_type=chain_type, retriever=retriever, return_source_documents=True)
    result = qa({"query": query})
    print(result['result'])
    return result


folder_path = r'C:\Users\cesar\OneDrive\Desktop\test2'
folder_path2 = r"C:\Users\cesar\OneDrive\Desktop\test2\1-s2.0-S2666222120300083-main.pdf"
chain_type = "stuff"
query = "What is an LSTM model?"
k = 1

print(qa(folder_path=folder_path, chain_type=chain_type, query=query, k=1, show_pages=False))
