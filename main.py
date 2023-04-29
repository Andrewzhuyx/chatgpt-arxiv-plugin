import quart
import quart_cors
from quart import request
import arxiv
import json
import tarfile
import re

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

@app.route('/search', methods=['GET'])
async def search_papers():
    query = request.args.get('query')
    max_results = int(request.args.get('max_results', 10))
    sort_by = request.args.get('sort_by', 'Relevance')  # Default to Relevance if no sort_by is provided

    # Ensure sort_by is a valid choice
    valid_sort_by = ['SubmittedDate', 'Relevance', 'LastUpdatedDate']
    if sort_by not in valid_sort_by:
        return quart.Response(response=json.dumps({"error": "Invalid sort_by parameter. Choose from 'SubmittedDate', 'Relevance', or 'LastUpdatedDate'."}), status=400)

    # Convert sort_by to arxiv.SortCriterion
    if sort_by == 'SubmittedDate':
        sort_by = arxiv.SortCriterion.SubmittedDate
    elif sort_by == 'Relevance':
        sort_by = arxiv.SortCriterion.Relevance
    elif sort_by == 'LastUpdatedDate':
        sort_by = arxiv.SortCriterion.LastUpdatedDate

    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=sort_by
    )

    results = []
    for result in search.results():
        results.append({
            "id": result.entry_id.split('/')[-1],
            "title": result.title,
            "summary": result.summary,
            "published": str(result.published),
            "updated": str(result.updated),
            "authors": [str(author) for author in result.authors],
            "primary_category": result.primary_category,
            "categories": result.categories,
            "pdf_url": result.pdf_url,
            'comment': result.comment,
            'journal_ref': result.journal_ref,
            'doi': result.doi,
        })

    return quart.Response(response=json.dumps(results), status=200)


@app.route('/paper', methods=['GET'])
async def paper():
    paper_id = request.args.get('paper_id', default = '', type = str)
    search = arxiv.Search(id_list=[paper_id])
    paper = next(search.results())
    return quart.jsonify({
        'title': paper.title,
        'authors': [str(author) for author in paper.authors],
        'summary': paper.summary,
        'comment': paper.comment,
        'journal_ref': paper.journal_ref,
        'doi': paper.doi,
        'primary_category': paper.primary_category,
        'categories': paper.categories,
        'pdf_url': paper.pdf_url
    })

@app.route('/full_paper', methods=['GET'])
async def full_paper():
    paper_id = request.args.get('paper_id', default = '', type = str)
    search = arxiv.Search(id_list=[paper_id])
    paper = next(search.results())
    
    paper_source = paper.download_source(dirpath="./downloads")
    tex_files_content = {}

    with tarfile.open(paper_source, mode="r:gz") as tar:
        for tarinfo in tar:
            if tarinfo.name.endswith(".tex"):
                extracted_file = tar.extractfile(tarinfo.name)
                content = extracted_file.read().decode("utf-8")
                # Remove document class and preamble
                content = re.sub(r'\\documentclass.*\\begin\{document\}', '', content, flags=re.DOTALL)
                # Remove LaTeX commands
                content = re.sub(r'\\[a-z]*\{[^}]*\}', '', content) 
                # Remove figures and tables (including their content)
                content = re.sub(r'\\begin\{(figure|table)\}.*?\\end\{\1\}', '', content, flags=re.DOTALL)
                # Remove comments
                content = re.sub(r'%.*', '', content)
                # Remove \includegraphics commands
                content = re.sub(r'\\includegraphics\[[^\]]*\]\{[^}]*\}', '', content)
                # Remove \centering and \linewidth commands
                content = re.sub(r'\\centering', '', content)
                content = re.sub(r'\{\\linewidth\}', '', content)
                # Remove extra newlines
                content = re.sub(r'\n\s*\n', '\n', content)
                tex_files_content[tarinfo.name] = content
    
    return quart.jsonify({
        'title': paper.title,
        'authors': [str(author) for author in paper.authors],
        'summary': paper.summary,
        'tex_files_content': tex_files_content
    })

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=5001)


if __name__ == '__main__':
    main()
