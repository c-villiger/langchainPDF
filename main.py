"""
Import libraries
"""
# Utils
import os
import panel as pn
import tempfile


# Import Functions
from langchain_pdf_bot.functions import qa

# Import API Key
from apikey import API_KEY

os.environ["OPENAI_API_KEY"] = API_KEY 


"""
Set Up Panel
"""

pn.extension('texteditor', template="bootstrap", sizing_mode='stretch_width')
pn.state.template.param.update(
    main_max_width="690px",
    header_background="#F08080",
)

"""
File Input
"""
# Allow for multiple files to be uploaded
folder_input = pn.widgets.TextInput(name='Folder Path', value='')


# Create a text area to display the file info
text_area = pn.widgets.TextAreaInput(value='Processed Files', height=100, scroll=True)

# Define the callback function to be executed when the button is clicked
def process_folder(event):
    folder_path = folder_input.value
    if os.path.isdir(folder_path):
        files = os.listdir(folder_path)
        # Process your files here...
        text_area.value = '\n'.join(files)  # Example: list the files
    else:
        text_area.value = 'Invalid folder path!'

# Watch for changes in the value of folder_input
folder_input.param.watch(process_folder, 'value')



"""
Other Widgets
"""

prompt = pn.widgets.TextEditor(
    value="", placeholder="Enter your questions here...", height=160, toolbar=False
)

run_button = pn.widgets.Button(name="Run!")

select_k = pn.widgets.IntInput(
    name="", start=1, end=5, step=1, value=2
)

select_chunk_size = pn.widgets.IntInput(
    name="", value=1000
)

select_chain_type = pn.widgets.RadioButtonGroup(
    name='Chain type',
    options=['stuff', 'map_reduce', "refine", "map_rerank"]
)

select_model = pn.widgets.RadioButtonGroup(
    name='ChatGPT model',
    options=['GPT-3.5', 'GPT-4']
)

show_pages = pn.widgets.RadioButtonGroup(
    name='Show single chunks/pages (False by default):',
    options=['True', 'False']
)

own_knowledge = pn.widgets.RadioButtonGroup(
    name='Use own knowledge (False by default):',
    options=['True', 'False']
)


"""
Output Widgets
"""


# result = qa("example.pdf", "what is the total number of AI publications?")
convos = []  # store all panel objects in a list


def qa_result(_):

    # save pdf file to a temp file
    folder_path = folder_input.value
    if os.path.isdir(folder_path):

        prompt_text = prompt.value
        if prompt_text:

            result = qa(folder_path=folder_path, query=prompt_text, chain_type=select_chain_type.value, k=select_k.value, chunk_size=select_chunk_size.value, own_knowledge=own_knowledge.value, show_pages=show_pages.value)
            
            convos.extend([
                pn.Row(
                    pn.panel("\U0001F60A", width=10),
                    prompt_text,
                    width=600
                ),
                pn.Row(
                    pn.panel("\U0001F916", width=10),
                    pn.Column(
                        result["result"],
                        "Relevant source text:",
                        pn.pane.Markdown('--------------------------------------------------------------------\n')
                    )
                )
            ])
            for i, doc in enumerate(result["source_documents"]):
                convos.append(pn.Row(
                    pn.panel(f"Source {i+1}: {os.path.basename(doc.metadata['source'])}, page: {doc.metadata['page']}.", width=150),
                    pn.panel(doc.page_content, width=400, max_height=400, sizing_mode='stretch_width'),
                    width=600,
                    sizing_mode='stretch_width'
                ))
    
    return pn.Column(*convos, margin=15, width=600, min_height=1000)


qa_interactive = pn.panel(
    pn.bind(qa_result, run_button),
    loading_indicator=True,
)

output = pn.WidgetBox('*Output will show up here:*',
                    qa_interactive, scroll=True)






widgets = pn.Column(
    pn.Row(pn.Column(folder_input, text_area), 
        pn.Card(
            pn.Column(
                pn.pane.Markdown("**Use own knowledge:**"),
                own_knowledge,
                pn.pane.Markdown("**Chain Type:**"),
                select_chain_type, 
                pn.pane.Markdown("**Number of Relevant Sources:**"), 
                select_k, 
                pn.pane.Markdown("**Length per Source:**"),
                select_chunk_size, 
                ),
            title="Advanced settings"
        ),
    ),
    pn.Column(prompt, run_button),
    pn.Column(output),
    sizing_mode='stretch_width'
)

widgets.servable()