import os
from dotenv import load_dotenv
from pinecone import Pinecone
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings, StorageContext # הוספנו את StorageContext!
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.cohere import CohereEmbedding

# ביטול חסימות נטפרי
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""

load_dotenv()

def main():
    print("מתחיל בתהליך קריאת הקבצים...")
    
    # טעינת המסמכים מכל הכלים
    claude_docs = SimpleDirectoryReader("agent_docs/.claude", recursive=True, exclude_hidden=False).load_data()
    for doc in claude_docs:
        doc.metadata["tool"] = "claude"
        
    cursor_docs = SimpleDirectoryReader("agent_docs/.cursor", recursive=True, exclude_hidden=False).load_data()
    for doc in cursor_docs:
        doc.metadata["tool"] = "cursor"
        
    windsurf_docs = SimpleDirectoryReader("agent_docs/.windsurf", recursive=True, exclude_hidden=False).load_data()
    for doc in windsurf_docs:
        doc.metadata["tool"] = "windsurf"
        
    all_docs = claude_docs + cursor_docs + windsurf_docs
    print(f"נטענו {len(all_docs)} מסמכים מ-3 כלים שונים!")

    # חיתוך ל-Chunks
    parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    nodes = parser.get_nodes_from_documents(all_docs)
    print(f"המסמכים נחתכו ל-{len(nodes)} מקטעים (Chunks).")

    # הגדרת המודל
    Settings.embed_model = CohereEmbedding(
        cohere_api_key=os.environ["COHERE_API_KEY"],
        model_name="embed-multilingual-v3.0"
    )

    # התחברות ל-Pinecone
    print("מתחבר ל-Pinecone ושומר את הנתונים (כולל Metadata)...")
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"], ssl_verify=False)
    pinecone_index = pc.Index("agentic-docs")
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    
    # ==========================================================
    # התיקון: שימוש ב-StorageContext כדי באמת לדחוף ל-Pinecone!
    # ==========================================================
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex(nodes, storage_context=storage_context)
    
    print("התהליך הסתיים בהצלחה! כל הנתונים משלושת הכלים אונדקסו ושמורים ב-Pinecone. 🎉")

if __name__ == "__main__":
    main()