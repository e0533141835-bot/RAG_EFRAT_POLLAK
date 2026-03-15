# ארכיטקטורה: Task Management SaaS

## מטרות מערכת ודרישות לא־פונקציונליות
המערכת היא SaaS לניהול משימות ופרויקטים עם קצב שינוי גבוה, צוות מוצר שמבצע ניסויים (A/B) וממשק עשיר (board, calendar, timeline). הדגש הוא על זמן תגובה נמוך, יכולת סקייל אופקי, אבטחה חזקה ורמת עקיבות (observability) שמאפשרת לשחזר "מי שינה מה" ברמת שדה. בנוסף, המערכת חייבת לתמוך ב־RTL מלא (עברית/ערבית) ובחוויית עבודה מהירה גם במובייל.

החלטנו לתכנן את שכבת היישום באופן שמאפשר:
- עבודה “היברידית” בין רינדור שרת ורינדור לקוח (SEO למסכי שיווק + אינטראקטיביות כבדה באפליקציה).
- קונסיסטנטיות בנתונים ברמת טרנזקציה בפעולות קריטיות (שיוך משימה לפרויקט, הרשאות, גרסאות).
- זמן תגובה מהיר למטא־נתונים וקריאות נפוצות (ספירת משימות, תגיות, התראות) באמצעות Cache.

## למה Next.js (App Router)
Next.js נותן לנו שילוב פרקטי בין Server Components לבין Client Components, תוך ניצול SSR ו־Streaming כדי לקצר TTFB במסכים כבדים. בפרקטיקה של מוצר ניהול משימות, המסכים הראשיים (Projects/Board) נדרשים ל־Data Fetching מבוקר, Pagination, ויכולת לשלב prefetch חכם. App Router מאפשר חלוקה טבעית לפי routes, ושימוש ב־route handlers עבור APIs פנימיים עם גישה קלה ל־cookies/session.

שיקולים נוספים:
- **תמיכה חזקה ב־RTL**: ניהול `<html dir="rtl">`, התאמת CSS ו־layout, ויכולת לבצע server-side rendering בלי “קפיצות” של כיוון.
- **שיתוף קוד**: טיפוסים וסכמות ולידציה (למשל schema validation) יכולים להופיע גם בשרת וגם בלקוח.
- **ביצועים ותפעול**: יכולת לבנות edge-friendly paths למסכי שיווק/סטטיים, אך לשמור את הלוגיקה הרגישה על runtime מלא.

## למה Postgres
Postgres הוא הבחירה הטבעית למערכת שבה יש:
- רלציות ברורות: משתמשים ↔ פרויקטים ↔ משימות ↔ חברות/ארגונים.
- צורך בטרנזקציות אמינות (ACID) ואילוצי מפתח זר (FK) למניעת orphan records.
- חיפוש וסינון מתקדמים: אינדקסים מרוכבים, partial indexes, JSONB לשדות דינמיים (custom fields), ו־CTE עבור שאילתות מורכבות.

בנוסף, Postgres מאפשר לנו לנהל Audit Trail בצורה מסודרת (טבלאות events / history), וגם להטמיע Row Level Security בעתיד במידה ונרצה להקשיח את ההפרדה בין טננטים (multi-tenant) ברמת DB.

## למה Redis
Redis משמש כשכבה משלימה ל־Postgres עבור:
- **Cache לקריאות חמות**: למשל counters, summaries, ו־feature flags פר־טננט.
- **Rate limiting**: הגנה על endpoints רגישים (login, token refresh, search) בהתאם ל־IP ו־userId.
- **Queues והתראות**: תורים קלים לפעולות לא סינכרוניות (שליחת מייל, תזכורות, webhook retries) בלי להעמיס על השרת הראשי.
- **Session / token metadata (לא ה־JWT עצמו)**: שמירת state מינימלי לצורך invalidation מהיר במקרה של חשד לדליפה.

הדגש בהחלטה הוא לא להפוך את Redis למקור אמת (source of truth), אלא לשכבת האצה ותפעול. כל נתון קריטי נכתב ונאכף ב־Postgres, ו־Redis מתעדכן באמצעות invalidation/ttl ואירועים.

## עקרונות אינטגרציה בין השכבות
- **Source of Truth**: Postgres.
- **Cache-aside**: קריאה קודם מ־Redis, ואם אין—שאילתה ל־Postgres וכתיבה עם TTL קצר.
- **Idempotency**: פעולות כתיבה רגישות (למשל create task) מקבלות `idempotencyKey` כדי למנוע כפילויות במקרה של retries.
- **Observability**: כל route קריטי מדווח על latency + cache hit rate + db query count, כדי לזהות מהר רגרסיות.
