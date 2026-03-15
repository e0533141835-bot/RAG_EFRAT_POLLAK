import os
import json
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, Settings
from llama_index.llms.cohere import Cohere
from pydantic import BaseModel, Field
from typing import List
from llama_index.core.program import LLMTextCompletionProgram

# ביטול חסימות נטפרי
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""

load_dotenv()

# הגדרת המודל
llm = Cohere(api_key=os.environ["COHERE_API_KEY"], model="command-r-08-2024")

# הגדרת המבנה של פריט בודד (הסכימה של שלב ג')
class ExtractedItem(BaseModel):
    category: str = Field(description="The category of the item: 'decision', 'rule', or 'warning'")
    title: str = Field(description="A short, clear title for the item")
    summary: str = Field(description="A detailed but concise summary of the information in Hebrew")
    source_file: str = Field(description="The name of the source file")

class ExtractionResult(BaseModel):
    items: List[ExtractedItem]

# יצירת התוכנית לחילוץ המידע
prompt_template_str = (
    "Extract all technical decisions, UI rules, and security warnings from the following text.\n"
    "Text content:\n"
    "---------------------\n"
    "{text}\n"
    "---------------------\n"
    "Respond ONLY with the extracted items in a structured format."
)

def main():
    print("🕵️‍♀️ מתחיל בחילוץ נתונים מובנים (שיטה מתקדמת)...")
    
    # טעינת הקבצים
    reader = SimpleDirectoryReader("agent_docs", recursive=True, exclude_hidden=False)
    documents = reader.load_data()
    
    all_extracted_items = []

    # הגדרת ה-Program שמחברת בין הפרומפט למודל ולסכימה
    program = LLMTextCompletionProgram.from_defaults(
        output_cls=ExtractionResult,
        prompt_template_str=prompt_template_str,
        llm=llm,
        verbose=False
    )

    for doc in documents:
        file_path = doc.metadata.get('file_path', 'unknown')
        base_file_name = os.path.basename(file_path)
        print(f"📖 סורק את הקובץ: {base_file_name}...")
        
        try:
            # הרצת החילוץ המובנה
            output = program(text=doc.text)
            
            for item in output.items:
                item.source_file = base_file_name
                # וודאי שהתשובה בעברית (לפעמים המודל מתבלבל)
                all_extracted_items.append(item.dict())
                
        except Exception as e:
            print(f"❌ שגיאה בחילוץ מקובץ {base_file_name}: {e}")

    # שמירה לקובץ JSON
    output_data = {
        "generated_at": "2026-03-10",
        "total_items": len(all_extracted_items),
        "items": all_extracted_items
    }
    
    with open("extracted_data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
        
    print(f"\n✅ הצלחנו! חולצו {len(all_extracted_items)} פריטים.")
    print(f"📁 הנתונים המובנים מחכים לך ב-extracted_data.json")

if __name__ == "__main__":
    main()