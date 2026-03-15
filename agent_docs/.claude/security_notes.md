# Security Notes — Auth, JWT, Sensitive Routes

## עקרונות בסיס
המערכת מטפלת בנתוני לקוחות ארגוניים ולכן נדרשת הקשחה ברמה גבוהה. נקודת המוצא היא ש־frontend הוא "לא אמין" (untrusted), וכל החלטת הרשאה נאכפת בשרת. בנוסף, יש להניח ש־JWT יכול לדלוף (לוגים, תוספים, XSS), ולכן חייבים מנגנוני ביטול (revocation) ורענון מבוקר.

## JWT: דגשים והסתייגויות
- **לא לשים JWT ב־localStorage**: זה מגדיל משמעותית את סיכון ה־XSS. ההמלצה היא cookie `HttpOnly` עם `Secure` ו־`SameSite` מתאים.
- **תוקף קצר ל־access token**: 5–15 דקות, עם refresh token נפרד. refresh token חייב להיות rotate-on-use.
- **חתימה ואימות**: שימוש ב־`kid` (Key ID) לאפשר key rotation. אסור לסמוך על claims בלי אימות חתימה.
- **Scopes/Permissions**: לא להעמיס הרשאות מפורטות מדי בתוך JWT כדי לא “לנעול” הרשאות עד לפקיעה. במקום זה: JWT מזהה משתמש + tenant + sessionId, והרשאות נשלפות/מחושבות בשרת.

## תהליך Auth ורענון (Refresh)
נקודות תורפה נפוצות שראינו בפרויקטים דומים:
- **Refresh endpoint ללא rate l
imit**: מאפשר brute-force של refresh token. חייבים הגבלת קצב + חוקים לפי device fingerprint.
- **Reuse detection**: אם refresh token כבר שומש פעם אחת, יש להחשיב שימוש נוסף כחשוד ולבטל את כל ה־sessions של המשתמש בטננט.
- **Session binding**: לקשור refresh token ל־sessionId ול־device metadata בסיסי (UA hash / ip range) כדי להקשות על שימוש חוזר.

## Routes רגישים ומדיניות לוגים
יש routes שאסור שידלפו מהם פרטים:
- **`/api/auth/*`**: לא ללוגג payload מלא. לכל היותר `userId` אחרי אימות, ו־error codes לא מפורטים.
- **`/api/admin/*`**: חייבים audit log מלא (מי, מתי, מה שונה), אבל ללא סודות (tokens, api keys).
- **`/api/projects/:id/invite`**: קישורי הזמנה חייבים להיות חד־פעמיים/עם TTL, ולא להחזיר מידע על קיום משתמש (מניעת user enumeration).

כללי לוגים:
- **No secrets in logs**: לא להדפיס Authorization header, cookies, refresh tokens, או query params שמכילים token.
- **Correlation ID**: לכל בקשה להוסיף מזהה עקיבות (trace/correlation) כדי לשחזר אירועים בלי לחשוף מידע.

## הרשאות (Authorization) ומניעת עקיפה
הטעויות הקלאסיות בפרויקט multi-tenant:
- **בדיקת tenant רק ברמת route**: צריך לאכוף גם ברמת query/resolver. כל fetch לפי `taskId` חייב לכלול `tenantId`/`projectId` של המשתמש.
- **בעלות לעומת חברות**: משתמש יכול להיות חבר בפרויקט בלי להיות הבעלים. הפעולות (delete, billing, invite) חייבות role ברור.
- **Mass assignment**: endpoints שמקבלים payload של `task` חייבים whitelist של שדות מותרי עדכון.

## הגנות משלימות
- **CSRF**: אם משתמשים ב־cookies ל־auth, חייבים הגנה (SameSite + CSRF token בפעולות state-changing).
- **CSP**: להפעיל Content Security Policy כדי לצמצם XSS.
- **Webhooks**: אימות חתימה (HMAC) לכל webhook נכנס/יוצא, ורישום retries בצורה שלא תחשוף payloadים רגישים.
