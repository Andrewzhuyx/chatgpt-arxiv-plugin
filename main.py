import quart
import quart_cors
from quart import request
import arxiv
import json

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
