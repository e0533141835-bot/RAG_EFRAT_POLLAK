# Product Spec — Task Management SaaS

## חזון מוצר
מטרת המוצר היא לספק לארגונים כלי לניהול עבודה שמחבר בין צוותים, משימות, דדליינים ותהליכים — עם חוויית שימוש מהירה, חיפוש חכם, ושקיפות מלאה של “מה קורה עכשיו”. המוצר חייב להתאים לסביבה רב־לשונית עם RTL, ולהציע יכולות מתקדמות (אוטומציות, דוחות, הרשאות) בלי להפוך למורכב מדי לשימוש.

הנחות מוצר:
- המערכת multi-tenant עם הפרדה חזקה בין ארגונים.
- משתמשים עובדים בעיקר על מסכי Board ו־Project Overview.
- יש צורך בהיסטוריית שינויים (audit) כדי להבין מי שינה סטטוס/דדליין.

## ישויות וזרימות מרכזיות
- **User**: משתמש מזוהה עם role ארגוני (owner/admin/member). יכול להשתייך לפרויקטים שונים עם role פרויקטלי.
- **Project**: יחידת עבודה עיקרית. כולל תצוגות: Board, List, Calendar, Timeline.
- **Task**: משימה עם סטטוס, עדיפויות, אחראי, תאריך יעד ושדות דינמיים.

זרימות ליבה:
- יצירת פרויקט → הזמנת משתמשים → יצירת משימות → תעדוף/שיוך → מעקב התקדמות → ארכוב.
- פילטרים מתקדמים (לפי assignee, label, due date) עם שמירת views.

## דרישות פונקציונליות (MVP+)
- **Board עם Drag & Drop**: שינוי `status` ו־`position` בצורה יציבה, כולל optimistic UI עם rollback במקרה שגיאה.
- **חיפוש**: חיפוש לפי כותרת/תיאור/label; בהמשך full-text.
- **Notifications**:
  - התראות על mentions והקצאה (assignment).
  - תזכורות לדדליינים.
- **Permissions**:
  - roles ברמת ארגון וברמת פרויקט.
  - פעולות רגישות (invite, delete project, billing) רק לבעלי הרשאה.
- **Audit Trail**: צפייה בהיסטוריה של משימה (שינוי סטטוס/דדליין/אחראי).

## דרישות לא־פונקציונליות
- **Latency**: p95 < 300ms לפעולות קריאה עיקריות בפרויקטים ממוצעים.
- **Availability**: יעד 99.9%, עם graceful degradation (למשל disabling advanced filters אם cache down).
- **Observability**: trace id לכל בקשה, מדדים על cache hit rate, ושגיאות הרשאה.
- **Security**: מנגנון refresh בטוח, הגנה על endpoints רגישים, ומניעת data leakage בין טננטים.

## Future Features (Roadmap)
- **GraphQL מלא למסכי אפליקציה**: איחוד שכבת ה־data fetching והפחתת overfetching.
- **Automations**: חוקים בסגנון “כאשר משימה עוברת ל־Done → שלח הודעה ב־Slack/Teams”.
- **Templates**: תבניות פרויקט (סטטוסים, שדות, תהליכים) להקמה מהירה.
- **Time Tracking**: מעקב שעות, דו"חות, וחיוב.
- **Advanced Search**: full-text search עם ranking, ואפשרות saved queries.
- **Offline Mode בסיסי**: קריאה וצפייה בנתונים אחרונים, עם sync מבוקר.

## הגבלות ידועות (Spec-level)
- אין תמיכה מלאה ב־subtasks ב־MVP; יש רק "related tasks".
- אין multi-project task; משימה שייכת לפרויקט יחיד.
- אין public sharing של פרויקטים בשלב ראשון.
