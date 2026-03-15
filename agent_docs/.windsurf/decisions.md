# Technical Decisions Log

## 2026-02 — מעבר הדרגתי מ־REST ל־GraphQL
הרציונל: מסכי Board/Timeline דורשים אגרגציה של נתונים (משימות + משתמשים + labels + counters) וה־REST הקלאסי יצר הרבה קריאות וסיבוכיות ב־client. ההחלטה היא לבצע מעבר הדרגתי: REST נשאר עבור auth ופעולות פשוטות, בעוד GraphQL מכסה מסכי ליבה עם סכמות ברורות.

הנחיות ליישום:
- GraphQL חייב לאכוף הרשאות בכל resolver (לא רק ב־gateway).
- להעדיף query שמחזיר בדיוק את השדות הדרושים; להימנע מ־mega query אחת.
- caching ברמת response אפשרי רק עבור queries ללא מידע פר־משתמש רגיש.

## 2026-02 — State Management: Server-first + Client store מינימלי
החלטנו לא לנהל store כבד לכל האפליקציה. במקום זאת:
- נתונים “אמת” מגיעים מהשרת (SSR/Server Components/GraphQL) ומעודכנים באמצעות revalidation.
- בלקוח נשמר state UI בלבד: פילטרים, sort, modal states, selection.

סיבה: store גדול יצר באגים של stale data, במיוחד ב־multi-tab. הגישה החדשה מפחיתה דריפט ומקלה על debugging.

## 2026-03 — Cache-aside ב־Redis עבור summaries
החלטנו להוסיף שכבת Redis לפריטים חמים:
- ספירות משימות לפי סטטוס/אחראי.
- last viewed projects.
- rate limit counters.

כללים:
- Redis הוא לא מקור אמת.
- TTL קצר + invalidation על כתיבה.
- מדדים על hit/miss כדי להעריך ROI.

## 2026-03 — Audit Events: לוג אירועים במקום “history tables” מרובות
במקום ליצור טבלת היסטוריה לכל ישות, הוחלט על טבלת `audit_events` אחידה עם `diff` ב־JSONB. זה מאפשר:
- אחידות בין entities.
- חיפוש/פילטרים על פעולות משתמש.
- הרחבה לעתיד (webhooks, compliance exports).

סיכון ידוע: שאילתות על diff דורשות אינדוקס/פונקציות; לכן נשמור גם שדות “מפתח” כעמודות (entity_type, entity_id, actor_id, created_at).

## 2026-03 — RTL-first כעיקרון תשתיתי
נקבע כי RTL הוא ברירת מחדל:
- שימוש ב־CSS logical properties בכל מקום.
- בדיקות ויזואליות ייעודיות למסכים מרכזיים.
- הימנעות מהנחות על left/right ב־components.

הסיבה היא למנוע חוב טכני: אם RTL מגיע “בסוף”, העלות מתפוצצת, במיוחד ברכיבי drag & drop.
