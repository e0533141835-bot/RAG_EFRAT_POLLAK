# Known Issues / Technical Debt

## 1) תזכורות נשלחות פעמיים בעת Deploy (Intermittent)
- **סימפטום**: משתמשים מקבלים שתי התראות email עבור אותו due date.
- **השערה**: worker נרשם פעמיים ל־queue בזמן rolling deploy, או שמנגנון lock ב־Redis לא אטומי.
- **השפעה**: בינונית (אמון משתמשים + רעש).
- **כיוון פתרון**:
  - להוסיף distributed lock חזק (SET NX עם TTL) סביב job dispatch.
  - להוסיף idempotency key ברמת notification.

## 2) GraphQL resolvers: N+1 בקריאות משולבות
- **סימפטום**: board query שמחזיר tasks + assignee + counters מייצר הרבה שאילתות.
- **השפעה**: גבוהה בפרויקטים גדולים (p95 עולה).
- **כיוון פתרון**:
  - DataLoader / batching.
  - prefetch מרוכב: join על users לפי assignee_id.
  - ניטור `db_query_count` לכל query.

## 3) Drag & Drop: קפיצות סדר (ordering) בקונפליקט multi-user
- **סימפטום**: שני משתמשים גוררים במקביל ומשימות “מחליפות” מקום בצורה לא צפויה.
- **גורם אפשרי**: אלגוריתם position מבוסס מספרים צפופים מדי, וחוסר טיפול ב־concurrent updates.
- **כיוון פתרון**:
  - שימוש ב־fractional indexing + rebalancing.
  - הוספת optimistic concurrency control (version / updated_at check).

## 4) הרשאות: edge case בהסרת חבר מפרויקט
- **סימפטום**: משתמש שהוסר מהפרויקט עדיין רואה metadata של משימות אם הוא מחזיק URL ישיר וה־cache חם.
- **השפעה**: גבוהה (security/privacy).
- **כיוון פתרון**:
  - לוודא שכל resolver כולל בדיקת membership ולא מסתמך על cache.
  - לקשור cache keys גם ל־membership version.

## 5) חוב UI: חוסר אחידות ב־empty states
- **סימפטום**: חלק מהמסכים מציגים “אין נתונים” בלי call-to-action.
- **השפעה**: נמוכה-בינונית (UX).
- **כיוון פתרון**:
  - רכיב EmptyState אחיד עם כותרת, הסבר, פעולה מומלצת.
  - בדיקת RTL על כל הווריאציות.

## 6) DB: אינדקסים חסרים לפילטרים דינמיים
- **סימפטום**: פילטרים על `custom_fields` איטיים אצל טננטים עם הרבה נתונים.
- **השפעה**: בינונית.
- **כיוון פתרון**:
  - אינדקס GIN מבוקר על keys נפוצים בלבד.
  - להגביל queries דינמיות ולהציע saved views.
