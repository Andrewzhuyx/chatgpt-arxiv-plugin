# ChatGPT ArXiv Plugin Quickstart

Get an Arxiv paper search/retrieval ChatGPT plugin up and running in under 5 minutes using Python. If you do not already have plugin developer access, please [join the waitlist](https://openai.com/waitlist/plugins).

## Setup

To install the required packages for this plugin, run the following command:

```bash
pip install -r requirements.txt
```

To run the plugin, enter the following command:

```bash
python main.py
```

Once the local server is running:

1. Navigate to https://chat.openai.com. 
2. In the Model drop down, select "Plugins" (note, if you don't see it there, you don't have access yet).
3. Select "Plugin store"
4. Select "Develop your own plugin"
5. Enter in `localhost:5001` since this is the URL the server is running on locally, then select "Find manifest file".

The plugin should now be installed and enabled! You can start with a question like "Search for papers on Segment Anything" or "Retrieve paper with ID 1706.03762" to see it in action!


## Limitations

The plugin utilizes the ArXiv Python package to search and retrieve papers from the ArXiv database. However, there are some limitations that users should be aware of:

- **Source TEX Files:** The plugin is designed to retrieve and display the source TEX files of papers. This choice was made because TEX files, being plain text and simpler in structure, are generally easier to parse than PDFs. PDFs can contain complex layouts, images, and other non-textual elements that can complicate text extraction. Furthermore, TEX files contain clear markup for mathematical symbols and equations, which are common in academic papers and can be challenging to extract correctly from PDFs. Despite these advantages, not all papers on ArXiv have TEX files available. Some authors choose not to upload the source files for their papers, or they may upload in formats other than TEX, such as PDF. 

- **Context Limitation of ChatGPT:** The plugin leverages OpenAI's ChatGPT to facilitate conversational interactions. However, ChatGPT has a context window limitation, which is the maximum number of tokens it can consider from the conversation history when generating a response. If a conversation, or the text of a paper, exceeds this limit, ChatGPT might lose context or not perform optimally. For instance, it might not remember details from earlier in the conversation, and long papers might have to be truncated or split into smaller parts for processing. This plugin currently works best with shorter papers.

## Getting help

If you run into issues or have questions building a plugin, please join OpenAI's [Developer community forum](https://community.openai.com/c/chat-plugins/20).

If you run into issues with the plugin, please email andrewyx@seas.upenn.edu
