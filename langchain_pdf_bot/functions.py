"""
Imports
"""
# Document loaders
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.document_loaders import UnstructuredMarkdownLoader
# Splitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import CharacterTextSplitter
# Embeddings and models
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.vectorstores import FAISS, Chroma
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryMemory
# Chains
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains import RetrievalQA
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.chains import SimpleSequentialChain
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import RetrievalQAWithSourcesChain
# Utils
import os
from termcolor import colored

# Import API Key
from apikey import API_KEY
os.environ["OPENAI_API_KEY"] = API_KEY

"""
query function
"""


def qa(folder_path, chain_type, chunk_size, query, k, own_knowledge = False, show_pages=False):

    
    """
    Read-in and split the documents
    """
    all_pages = []

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        if file_name.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_name.endswith('.csv'):
            loader = CSVLoader(file_path)
        elif file_name.endswith('.docx'):
            loader = Docx2txtLoader(file_path)
        elif file_name.endswith('.md'):
            loader = UnstructuredMarkdownLoader(file_path)
        else:
            continue  # Skip files with other extensions

        file = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=10)
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




    """
    Chains
    """

    # Define Chain
    if own_knowledge:
        prompt_template = """Use the following pieces of context to answer the question at the end. \
            If the answer does not become clear from the context, you can also use your own knowledge. \
            If you use your own knowledge, please indicate this clearly in your answer. \


        Context:
        {context}

        Question: {question}
        Helpful answer:"""

    if not own_knowledge:

        prompt_template = """Use the following pieces of context to answer the question at the end. \
            Do NOT use your own knowledge and give the best possible answer from the context.\

        Context:
        {context}

        Question: {question}
        Helpful answer:"""


    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context","question"]
    )

    chain_type_kwargs = {"prompt": PROMPT}

    chain = RetrievalQA.from_chain_type(
        llm=OpenAI(temperature=0),
        chain_type=chain_type,
        retriever=retriever,
        verbose=True,
        return_source_documents=True,
        memory=ConversationSummaryMemory(llm=OpenAI(temperature=0)),
        chain_type_kwargs=chain_type_kwargs
    )
    

    # Show Prompt Template
    #print(chain.combine_documents_chain.llm_chain.prompt.template)

    # Run Chain with parameters
    result = chain(query)


    # chain = RetrievalQAWithSourcesChain.from_chain_type(
    #     llm=model,
    #     chain_type=chain_type,
    #     retriever=retriever,
    #     verbose=True,
    #     chain_type_kwargs=chain_type_kwargs)

    # result = chain({"question": query})

    # # # Show Prompt Template
    print(chain.combine_documents_chain.llm_chain.prompt.template)



    # Run different chain. This chain does not first use a retriever to find the relevant 
    # documents, but instead retrieves the documents directly and prompt on them.
    # chain = load_qa_with_sources_chain(
    #     OpenAI(temperature=0), chain_type="stuff", verbose=True)
    # result = chain({"input_documents": docs, "question": query},
    #                return_only_outputs=True)

    
    """
    Print results
    """
    # print(f"This is the result: {result['result']}")
    # doc_content_list = [(doc.page_content,doc.metadata["source"]) for doc in result['source_documents']]
    # for doc in doc_content_list:
    #     print(doc)
    
    return result


chunk_size=1000
folder_path = r'C:\Users\cesar\OneDrive\Desktop\test2'
chain_type = "stuff"
query = "What is an LSTM model?"
query2 = "Can you repeat your answer from the last question?"
k = 4

result = qa(folder_path=folder_path, chain_type=chain_type, chunk_size=chunk_size, query=query, k=k, own_knowledge = False, show_pages=False)
result2 = qa(folder_path=folder_path, chain_type=chain_type, chunk_size=chunk_size, query=query2, k=k, own_knowledge = False, show_pages=False)

print(result)
print(f"This is the result: {result['result']}")
print(f"This is the result: {result2['result']}")
# list = [(os.path.basename(doc.metadata["source"]), f"page: {doc.metadata['page']}") for doc in result['source_documents']]
# #print(f"These are the sources: {result['source_documents']}")
# print(list)





"""
Functions for graphics
"""

def print_boxed_header(header, color):
    header_length = len(header)
    box_top = "╒" + "═" * (header_length + 2) + "╕"
    box_middle = f"│ {header} │"
    box_bottom = "╘" + "═" * (header_length + 2) + "╛"

    print(colored(box_top, color))
    print(colored(box_middle, color))
    print(colored(box_bottom, color))