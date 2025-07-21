# from flask import Blueprint, render_template, request
# import requests
# import cohere
# import os
# import config

# genereport_bp = Blueprint('genereport', __name__)


# COHERE_API_KEY = config.COHERE_API_KEY
# co = cohere.Client(COHERE_API_KEY)
# ENSEMBL_LOOKUP_URL = "https://rest.ensembl.org/lookup/symbol/homo_sapiens/{}?content-type=application/json"
# ENSEMBL_IMAGE_URL = "https://rest.ensembl.org/image/region/human/{}:{}..{}?;label=gene;content-type=image/png"
# WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"

# # Utility Functions
# def get_wikipedia_info(gene_name):
#     search_params = {
#         "action": "query", "list": "search", "srsearch": gene_name, "format": "json"
#     }
#     res = requests.get(WIKIPEDIA_API_URL, params=search_params)
#     if res.status_code != 200:
#         return None
#     data = res.json()
#     results = data.get("query", {}).get("search", [])
#     if not results:
#         return None
#     title = results[0]['title']
#     page_params = {
#         "action": "query", "format": "json", "titles": title,
#         "prop": "extracts|pageimages", "exintro": True,
#         "explaintext": True, "pithumbsize": 600
#     }
#     page_response = requests.get(WIKIPEDIA_API_URL, params=page_params)
#     if page_response.status_code != 200:
#         return None
#     pages = page_response.json().get("query", {}).get("pages", {})
#     for page in pages.values():
#         return {
#             "description": page.get("extract", "No description available."),
#             "image_url": page.get("thumbnail", {}).get("source")
#         }
# def get_ncbi_summary(gene_name):
#     try:
#         url = f"https://api.ncbi.nlm.nih.gov/datasets/v1/gene/symbol/homo_sapiens/{gene_name}/summary"
#         response = requests.get(url)
#         if response.ok:
#             return response.json().get("gene", {}).get("description", "")
#     except:
#         return ""
#     return ""

# def get_ensembl_info(gene_name):
#     try:
#         url = f"https://rest.ensembl.org/xrefs/symbol/homo_sapiens/{gene_name}?"
#         headers = {"Content-Type": "application/json"}
#         response = requests.get(url, headers=headers)
#         if response.ok and response.json():
#             return response.json()[0].get("description", "")
#     except:
#         return ""
#     return ""
# def get_medical_summary(gene_name):
#     prompt = f"""
# Provide a detailed summary of the human gene {gene_name}, organized into the following sections:
# 1. Structure: Describe the gene's structure, including exon count, chromosomal location, and protein domains.
# 2. History: Outline the discovery and research history of the gene.
# 3. Biological Background: Explain the gene's role in cellular processes and its biological significance.
# 4. Disease Associations: List diseases and conditions associated with mutations or dysregulation of the gene.
# 5. ASD Associations: Detail any known associations between the gene and Autism Spectrum Disorder.
# Please provide comprehensive information under each section.

# """
#     response = co.generate(
#         model="command-light", prompt=prompt, max_tokens=900, temperature=0.7
#     )
#     return response.generations[0].text.strip()

# def parse_summary(summary):
#     sections = {}
#     current = None
#     for line in summary.split('\n'):
#         line = line.strip()
#         if line.startswith("1."):
#             current = "structure"
#             sections[current] = line[2:].strip()
#         elif line.startswith("2."):
#             current = "history"
#             sections[current] = line[2:].strip()
#         elif line.startswith("3."):
#             current = "biological_background"
#             sections[current] = line[2:].strip()
#         elif line.startswith("4."):
#             current = "disease_associations"
#             sections[current] = line[2:].strip()
#         elif line.startswith("5."):
#             current = "asd_associations"
#             sections[current] = line[2:].strip()
#         elif current:
#             sections[current] += ' ' + line
#     return sections

# # Routes
# @genereport_bp.route('/genereport')
# def genereport():
#     return render_template('GeneReport/geneReportForm.html')

# @genereport_bp.route('/gene', methods=['POST'])
# def gene_info():
#     gene_name = request.form['gene_name'].strip()
#     url = ENSEMBL_LOOKUP_URL.format(gene_name)
#     res = requests.get(url)
#     if res.status_code != 200:
#         return render_template('GeneReport/GeneReportOutput.html', error="Gene not found. Try again.")
#     gene_data = res.json()

#     image_url = ENSEMBL_IMAGE_URL.format(gene_data['seq_region_name'], gene_data['start'], gene_data['end'])
#     if requests.get(image_url).status_code != 200:
#         wiki_info = get_wikipedia_info(gene_name)
#         image_url = wiki_info.get("image_url")
#         description = wiki_info.get("description")
#     else:
#         description = None

#     summary = get_medical_summary(gene_name)
#     sections = parse_summary(summary)

#     return render_template("GeneReport/GeneReportOutput.html", gene=gene_data, image_url=image_url, description=description, sections=sections)











from flask import Blueprint, render_template, request
import requests
import cohere
import config

genereport_bp = Blueprint('genereport', __name__)

# API Configuration
COHERE_API_KEY = config.COHERE_API_KEY
co = cohere.Client(COHERE_API_KEY)

ENSEMBL_LOOKUP_URL = "https://rest.ensembl.org/lookup/symbol/homo_sapiens/{}?content-type=application/json"
ENSEMBL_IMAGE_URL = "https://rest.ensembl.org/image/region/human/{}:{}..{}?;label=gene;content-type=image/png"
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"

# Utility Functions

def get_wikipedia_info(gene_name):
    search_params = {
        "action": "query", "list": "search", "srsearch": gene_name, "format": "json"
    }
    res = requests.get(WIKIPEDIA_API_URL, params=search_params)
    if res.status_code != 200:
        return None
    data = res.json()
    results = data.get("query", {}).get("search", [])
    if not results:
        return None
    title = results[0]['title']
    page_params = {
        "action": "query", "format": "json", "titles": title,
        "prop": "extracts|pageimages", "exintro": True,
        "explaintext": True, "pithumbsize": 600
    }
    page_response = requests.get(WIKIPEDIA_API_URL, params=page_params)
    if page_response.status_code != 200:
        return None
    pages = page_response.json().get("query", {}).get("pages", {})
    for page in pages.values():
        return {
            "description": page.get("extract", "No description available."),
            "image_url": page.get("thumbnail", {}).get("source")
        }
    return None

def get_ncbi_summary(gene_name):
    try:
        url = f"https://api.ncbi.nlm.nih.gov/datasets/v1/gene/symbol/homo_sapiens/{gene_name}/summary"
        response = requests.get(url)
        if response.ok:
            return response.json().get("gene", {}).get("description", "")
    except:
        return ""
    return ""

def get_ensembl_info(gene_name):
    try:
        url = f"https://rest.ensembl.org/xrefs/symbol/homo_sapiens/{gene_name}?"
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers)
        if response.ok and response.json():
            return response.json()[0].get("description", "")
    except:
        return ""
    return ""

def get_medical_summary(gene_name):
    prompt = f"""
Provide a detailed summary of the human gene {gene_name}, organized into the following sections:
1. Structure: Describe the gene's structure, including exon count, chromosomal location, and protein domains.
2. History: Outline the discovery and research history of the gene.
3. Biological Background: Explain the gene's role in cellular processes and its biological significance.
4. Disease Associations: List diseases and conditions associated with mutations or dysregulation of the gene.
5. ASD Associations: Detail any known associations between the gene and Autism Spectrum Disorder.
Please provide comprehensive information under each section.
"""
    response = co.generate(
        model="command-light", prompt=prompt, max_tokens=900, temperature=0.7
    )
    return response.generations[0].text.strip()

def parse_summary(summary):
    sections = {}
    current = None
    for line in summary.split('\n'):
        line = line.strip()
        if line.startswith("1."):
            current = "structure"
            sections[current] = line[2:].strip()
        elif line.startswith("2."):
            current = "history"
            sections[current] = line[2:].strip()
        elif line.startswith("3."):
            current = "biological_background"
            sections[current] = line[2:].strip()
        elif line.startswith("4."):
            current = "disease_associations"
            sections[current] = line[2:].strip()
        elif line.startswith("5."):
            current = "asd_associations"
            sections[current] = line[2:].strip()
        elif current:
            sections[current] += ' ' + line
    return sections

# Routes

@genereport_bp.route('/genereport')
def genereport():
    return render_template('GeneReport/geneReportForm.html')

@genereport_bp.route('/gene', methods=['POST'])
def gene_info():
    gene_name = request.form.get('gene_name', '').strip()
    if not gene_name:
        return render_template('GeneReport/GeneReportOutput.html', error="Gene name is required.")

    url = ENSEMBL_LOOKUP_URL.format(gene_name)
    res = requests.get(url)
    if res.status_code != 200:
        return render_template('GeneReport/GeneReportOutput.html', error="Gene not found. Try again.")
    
    gene_data = res.json()

    # Build Ensembl Image URL
    image_url = ENSEMBL_IMAGE_URL.format(
        gene_data.get('seq_region_name'),
        gene_data.get('start'),
        gene_data.get('end')
    )

    # Check if Ensembl image is available
    if requests.get(image_url).status_code != 200:
        wiki_info = get_wikipedia_info(gene_name)
        if wiki_info:
            image_url = wiki_info.get("image_url")
            description = wiki_info.get("description")
        else:
            image_url = None
            description = "No description available."
    else:
        description = None

    summary = get_medical_summary(gene_name)
    sections = parse_summary(summary)

    return render_template(
        "GeneReport/GeneReportOutput.html",
        gene=gene_data,
        image_url=image_url,
        description=description,
        sections=sections
    )
