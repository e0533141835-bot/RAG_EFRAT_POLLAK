import os
import json
import asyncio
import gradio as gr
from dotenv import load_dotenv
from pinecone import Pinecone
from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.llms.cohere import Cohere
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.core.llms import ChatMessage
# ==========================================
# ייבוא ספריות ה-Workflow 
# ==========================================
from llama_index.core.workflow import (
    Workflow,
    Context,
    step,
    Event,
    StartEvent,
    StopEvent
)
from llama_index.utils.workflow import draw_all_possible_flows
# ביטול חסימות נטפרי
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""

load_dotenv()

# ==========================================
# 1. הגדרות מודלים (Cohere)
# ==========================================
Settings.context_window = 128000
Settings.llm = Cohere(api_key=os.environ["COHERE_API_KEY"], model="command-r-08-2024")
Settings.embed_model = CohereEmbedding(cohere_api_key=os.environ["COHERE_API_KEY"], model_name="embed-multilingual-v3.0")

# ==========================================
# 2. חיבור למסד הנתונים הווקטורי (Pinecone)
# ==========================================
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"], ssl_verify=False)
pinecone_index = pc.Index("agentic-docs")
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

# ==========================================
# 3. טעינת הנתונים המובנים (JSON)
# ==========================================
try:
    with open("extracted_data.json", "r", encoding="utf-8") as f:
        structured_data = json.load(f)
except FileNotFoundError:
    structured_data = {"items": []}

def search_in_json(query):
    results = []
    clean_query = query.replace("?", "").replace(".", "").replace("(", "").replace(")", "").lower()
    query_words = []
    for word in clean_query.split():
        if len(word) > 3:
            if word.startswith("ה-") or word.startswith("ב-") or word.startswith("ל-"):
                word = word[2:]
            query_words.append(word)
    
    if not query_words:
        return None

    for item in structured_data.get("items", []):
        title = item.get("title", "").lower()
        summary = item.get("summary", "").lower()
        full_text = f"{title} {summary}"
        
        if any(word in full_text for word in query_words):
            results.append(f"- [{item.get('category', 'מידע')}] {title}: {summary} (מקור: {item.get('source_file', '')})")

    return "\n".join(results) if results else None


# ==========================================
# 4. הגדרת אירועים (Events) - הוספנו אירוע ניתוב
# ==========================================
class RouterEvent(Event):
    """אירוע שיוצא מהראוטר ומפעיל את השליפה"""
    query: str

class RetrievedDataEvent(Event):
    """אירוע שמועבר אחרי שליפת הנתונים מה-DB וה-JSON"""
    structured_info: str | None
    semantic_text: str | None
    query: str

# ==========================================
# 5. מחלקת ה-Workflow עם הראוטר המפורש
# ==========================================
class AgenticRAGWorkflow(Workflow):
    
    @step
    async def router(self, ctx: Context, ev: StartEvent) -> RouterEvent:
        """שלב 1: הראוטר - מקבל את השאילתה ומנתב אותה להמשך"""
        query = ev.get("query")
        print(f"\n🚦 ראוטר: התקבלה שאלה חדשה -> {query}")
        # כאן הלוגיקה נשארת זהה - אנחנו פשוט מעבירים את השאלה לשלב הבא
        return RouterEvent(query=query)

    @step
    async def retrieve_data(self, ctx: Context, ev: RouterEvent) -> RetrievedDataEvent:
        """שלב 2: שליפת הנתונים (נשאר בדיוק אותו דבר!)"""
        query = ev.query
        
        # א. חילוץ מ-JSON (אותה לוגיקה בדיוק)
        structured_info = search_in_json(query)
        if structured_info:
            print("💎 נמצא מידע מובנה ב-JSON!")
            
        # ב. שליפה מ-Pinecone (אותה לוגיקה בדיוק)
        retriever = index.as_retriever(similarity_top_k=10)
        response_nodes = retriever.retrieve(query)
        semantic_text = "\n".join([n.node.get_content() for n in response_nodes])
        
        return RetrievedDataEvent(
            structured_info=structured_info,
            semantic_text=semantic_text,
            query=query
        )

    @step
    async def synthesize_response(self, ctx: Context, ev: RetrievedDataEvent) -> StopEvent:
        """שלב 3: יצירת התשובה (לא השתנה)"""
        # ... כל הקוד של הפרומפט נשאר פה בדיוק אותו דבר ...
        prompt = f"""
    אתה אנליסט מערכות מומחה המסייע למפתחים. עליך לענות על השאלה בצורה מקצועית על בסיס המידע המצורף בלבד.

    [מידע מה-JSON]
    {ev.structured_info if ev.structured_info else 'אין מידע מובנה.'}

    [טקסט מהמסמכים]
    {ev.semantic_text if ev.semantic_text else 'אין טקסט קשור.'}

    חוקי עבודה קריטיים:
    1. **דיוק טכני:** הסבר על Legacy/Removed.
    2. **חיבור מידע:** חבר בין JSON למסמכים.
    3. **ציטוט מקורות:** חובה לציין שם מקור.
    4. **חסימת הזיות:** "אין לי מידע על כך".

    השאלה: {ev.query}
    תשובה:
    """
        messages = [ChatMessage(role="user", content=prompt)]
        response = await asyncio.to_thread(Settings.llm.chat, messages)
        return StopEvent(result=str(response.message.content))

# ==========================================
# 6. יצירת ה-Workflow וממשק ה-Gradio
# ==========================================
rag_workflow = AgenticRAGWorkflow(timeout=120.0)
# יצירת קובץ HTML עם תרשים הזרימה 
draw_all_possible_flows(
    rag_workflow,
    filename="rag_workflow.html"
)
async def chat_interface(message, history):
    try:
        if not message or len(message.strip()) < 3:
            return "⚠️ השאלה קצרה מדי. אנא שאל שאלה ברורה ומלאה על הפרויקט."
            
        # הרצת ה-Workflow האסינכרוני שלנו בדיוק כמו שמלכה מצפה!
        result = await rag_workflow.run(query=message)
        return result
        
    except Exception as e:
        print(f"❌ שגיאה: {str(e)}")
        return f"קרתה שגיאה בתהליך: {str(e)}"

demo = gr.ChatInterface(
    fn=chat_interface, 
    title="פרויקט Rag Agentic - עוזר למפתחים",
    description="מערכת Agentic RAG המשלבת חיפוש סמנטי ושליפת נתונים מובנים (מבוסס Workflows & Steps)."
)

if __name__ == "__main__":
    demo.launch()
