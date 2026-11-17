import os
import certifi

# ==========================================
# FIX MAC SSL HANDSHAKE
# ==========================================
# Tell Python to use certifi's root certificates for all SSL connections
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain

# ==========================================
# 0. SETUP CREDENTIALS
# ==========================================
# OpenAI Key
os.environ["OPENAI_API_KEY"] = "your api key" 

# Using neo4j+s:// now that certifi is handling the handshake
os.environ["NEO4J_URI"] = "neo4j+s://<instanceoid>.databases.neo4j.io"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "your password"

# ==========================================
# 1. DOCUMENT LOADER
# ==========================================
print("\n--- Loading Document ---")
loader = TextLoader("sample.txt")
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)
print(f"Total chunks created: {len(chunks)}")

# ==========================================
# 2 & 3. EXTRACTION & MAPPING
# ==========================================
print("\n--- Extracting Nodes and Relationships ---")
llm = ChatOpenAI(temperature=0, model_name="gpt-4o")
llm_transformer = LLMGraphTransformer(llm=llm)
graph_documents = llm_transformer.convert_to_graph_documents(chunks)
print(f"Found {len(graph_documents[0].nodes)} nodes and {len(graph_documents[0].relationships)} relationships.")

# ==========================================
# 4. GRAPH STORAGE
# ==========================================
print("\n--- Saving to Neo4j Database ---")
graph = Neo4jGraph(database="9fc7a34a") 
graph.add_graph_documents(graph_documents)
print("Successfully saved data to Neo4j!")

# ==========================================
# 5. GRAPH QUERY
# ==========================================
print("\n--- Querying the Graph ---")
graph.refresh_schema()
chain = GraphCypherQAChain.from_llm(
    graph=graph,
    cypher_llm=ChatOpenAI(temperature=0, model="gpt-4o"), 
    qa_llm=ChatOpenAI(temperature=0, model="gpt-4o-mini"), 
    verbose=True, 
    allow_dangerous_requests=True, # <--- This is the required fix
    return_intermediate_steps=True  # <--- Add this to capture the query
)

# Rephrasing the question so the LLM writes a simpler MATCH query without unions
my_question = "List all nodes and their relationships in the graph. Return the source node, the relationship type, and the target node."
print(f"\nQuestion: {my_question}")

# Run the query
response = chain.invoke({"query": my_question})

print("\n=== EXTRACTED CYPHER QUERY ===")
# The query is stored in the first item of the intermediate_steps list
cypher_query = response["intermediate_steps"][0]["query"]
print(cypher_query)

print("\n=== FINAL ANSWER ===")
print(response["result"])