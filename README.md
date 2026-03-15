# 🚀 Agentic RAG Helper for Developers - Advanced Workflow Edition

מערכת סיוע טכנית חכמה המבוססת על ארכיטקטורת **Agentic Workflow** מתקדמת. המערכת משלבת בין חיפוש סמנטי וקטורי לבין שליפת נתונים מובנים (Hybrid RAG) תוך שימוש במנגנון Steps ו-Events של LlamaIndex.

## 📊 תרשים זרימה - ה-Workflow החדש
בגרסה זו, המערכת עובדת כסוכן (Agent) המנהל את זרימת המידע בצורה מודולרית ומבוססת אירועים:

```mermaid
graph TD
    subgraph Ingestion_Phase [שלב הכנת הנתונים]
        A[מסמכי Markdown] --> B[LlamaIndex Reader]
        B --> C{מפצל נתונים}
        C -->|Semantic| D[Pinecone Vector DB]
        C -->|Structured| E[extracted_data.json]
    end

    subgraph Agentic_Workflow [ניהול השאילתה - Workflow]
        F[User Query] --> G[StartEvent]
        G --> H[Step 1: Context Retrieval]
        H -->|Hybrid Search| I[Pinecone + JSON Search]
        I --> J[RetrievedDataEvent]
        J --> K[Step 2: Answer Generation]
        K --> L[StopEvent]
        L --> M[Gradio UI Response]
    end
🏗️ חידושים בארכיטקטורה (Workflows & Steps)
הפרויקט שודרג מ-RAG לינארי פשוט למערכת Event-Driven מורכבת:

LlamaIndex Workflows: שימוש במחלקת Workflow לניהול זרימת עבודה אסינכרונית מבוססת שלבים.

Event-Driven Design: העברת מידע בין שלבי השליפה לסינתזה באמצעות אירועים מותאמים אישית.

Visual Workflow Tracking: ייצור אוטומטי של קובץ rag_workflow.html המציג תרשים אינטראקטיבי.

Hybrid Router: אינטגרציה בין מנוע החיפוש ב-JSON לבין Pinecone.

🛠️ טכנולוגיות וכלים
Framework: LlamaIndex Workflows, Steps, Events

LLM & Embeddings: Cohere Command-R & Multilingual v3

Vector DB: Pinecone

UI: Gradio ChatInterface

🚀 הוראות הרצה
התקנת ספריות:

Bash
pip install -r requirements.txt
הכנת נתונים:

Bash
python ingest.py
python extractor.py
הרצת האפליקציה:

Bash
python app.py
הערה: עם עליית האפליקציה, ייווצר קובץ בשם rag_workflow.html בתיקייה הראשית.

🛡️ הגנות ומניעת הזיות (Guardrails)
Zero Hallucination Policy: הסתמכות על הקונטקסט בלבד.

Legacy Handling: טיפול בשדות שהוסרו והסבר עליהם למשתמש.

Source Attribution: חובת ציטוט מקורות בסוף כל תשובה.