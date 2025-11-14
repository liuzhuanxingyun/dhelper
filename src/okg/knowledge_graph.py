import requests
import rdflib
from rdflib import Graph, URIRef, Literal, Namespace
import xml.etree.ElementTree as ET  # 添加导入

# 定义命名空间
MED = Namespace("http://example.org/medical/")

def fetch_pubmed_data(query, max_results=10):
    """从 PubMed API 获取数据"""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json"
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    return data.get("esearchresult", {}).get("idlist", [])

def fetch_pubmed_details(pubmed_ids):
    """获取文章详情"""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pubmed_ids),
        "retmode": "xml"
    }
    response = requests.get(base_url, params=params)
    root = ET.fromstring(response.text)
    details = []
    for article in root.findall(".//PubmedArticle"):
        title_elem = article.find(".//ArticleTitle")
        abstract_elem = article.find(".//AbstractText")
        title = title_elem.text if title_elem is not None else "No Title"
        abstract = abstract_elem.text if abstract_elem is not None else "No Abstract"
        details.append({"title": title, "abstract": abstract})
    return details  # 返回详情列表

def build_knowledge_graph(pubmed_ids):
    """构建简单知识图谱"""
    g = Graph()
    details = fetch_pubmed_details(pubmed_ids)  # 获取详情
    for pid, detail in zip(pubmed_ids, details):
        article_uri = URIRef(f"http://pubmed.ncbi.nlm.nih.gov/{pid}/")
        g.add((article_uri, MED.hasTitle, Literal(detail['title'])))
        g.add((article_uri, MED.hasAbstract, Literal(detail['abstract'])))
    return g

def query_knowledge_graph(graph, query_term):
    """查询图谱中与查询词相关的文章"""
    results = []
    for s, p, o in graph:
        if query_term.lower() in str(o).lower():  # 简单文本匹配
            results.append((str(s), str(p), str(o)))
    return results

# 示例使用
if __name__ == "__main__":
    ids = fetch_pubmed_data("thymoma", max_results=5)  # 修改查询词为胸腺瘤
    graph = build_knowledge_graph(ids)
    print(graph.serialize(format="turtle"))  # 输出图谱