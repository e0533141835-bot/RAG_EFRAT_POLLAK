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

LlamaIndex Workflows: שימוש במחלקת Workflow לניהול זרימת עבודה אסינכרונית מבוססת @step.

Event-Driven Design: העברת מידע בין שלבי השליפה (Retrieval) לשלבי הסינתזה (Synthesis) באמצעות אירועים מותאמים אישית (RetrievedDataEvent).

Visual Workflow Tracking: המערכת מייצרת אוטומטית קובץ rag_workflow.html המציג תרשים אינטראקטיבי של כל הצעדים בזמן אמת, בהתאם לדרישות המתקדמות של הקורס.

Hybrid Router: אינטגרציה עמוקה בין מנוע החיפוש ב-JSON (לנתונים קשיחים) לבין Pinecone (להבנה סמנטית).

🛠️ טכנולוגיות וכלים
Framework: LlamaIndex (Workflows, Steps, Events).

LLM & Embeddings: Cohere (Command-R & Multilingual v3).

Vector DB: Pinecone.

Visualization: Pyvis & LlamaIndex Utils (לייצור תרשים הזרימה הגרפי).

UI: Gradio ChatInterface.

🚀 הוראות הרצה
התקנת ספריות:

Bash
pip install -r requirements.txt
הכנת נתונים (פעם אחת):

Bash
python ingest.py
python extractor.py
הרצת האפליקציה:

Bash
python app.py
הערה: עם עליית האפליקציה, המערכת תייצר אוטומטית קובץ בשם rag_workflow.html בתיקייה הראשית. ניתן לפתוח אותו בדפדפן כדי לצפות בתרשים הזרימה של הסוכן.

🛡️ הגנות ומניעת הזיות (Guardrails)
Zero Hallucination Policy: הנחיית LLM מחמירה להסתמך על הקונטקסט בלבד.

Legacy Handling: זיהוי שדות שהוסרו (Legacy) והסבר עליהם למשתמש במקום מתן תשובת "לא נמצא מידע".

Source Attribution: חובת ציטוט מקורות (source_file) בסוף כל תשובה טכנית.