# Changelog — Task Management SaaS

## 2026-03-05
- **ביצועים**: שיפור זמן טעינת לוח משימות (Board) באמצעות cache-aside ב־Redis עבור summaries (ספירות לפי סטטוס/אחראי).
- **תיקון באג**: מיון משימות לפי `dueDate` היה מתנהג שונה בין RTL ל־LTR בגלל שימוש ב־CSS left/right בסדרי עמודות.
- **UX**: הוספת skeleton אחיד לטבלת Projects כדי להפחית קפיצות פריסה בזמן טעינה.

## 2026-03-02
- **אבטחה**: הוספת rate limiting ל־`/api/auth/login` ול־`/api/auth/refresh` (מפתח משולב של IP + fingerprint) כדי להפחית brute-force.
- **DB**: הוספת אינדקס מרוכב על `tasks(project_id, status, updated_at)` בעקבות עומס על מסך Board בפרויקטים גדולים.
- **תיקון באג**: עדכון משימה היה מאפס `assigneeId` במקרים של patch חלקי (הגיע payload עם `assigneeId: null` בגלל mapping שגוי).

## 2026-02-26
- **שינוי ארכיטקטורה**: מעבר הדרגתי מ־REST endpoints מפורטים ל־GraphQL עבור מסכי אפליקציה מרכזיים (Board/Timeline) כדי לצמצם overfetching.
- **ניטור**: הוספת מדדים: `cache_hit_rate`, `db_query_count`, `p95_latency` לפי route.
- **תיקון באג**: הרשאות שיתוף פרויקט היו מאפשרות גישה לקריאת task metadata גם לאחר הסרת משתמש מהפרויקט — תוקן ע"י בדיקת membership בכל resolver.

## 2026-02-18
- **UI**: נעילה של tokens לפלטת צבעים והקשחת focus-visible בכל רכיבי input.
- **RTL**: טיפול באייקונים כיווניים (chevrons) בתוך breadcrumb וב־pagination, כולל mirroring לפי `dir`.
- **DB Cleanup**: הסרת שדה legacy `tasks.priority_text` לאחר מעבר מלא ל־enum `tasks.priority`.

## 2026-02-10
- **תשתית**: הפרדת Redis בין cache לבין queues באמצעות namespaces כדי למנוע collision במפתחות.
- **יציבות**: הוספת idempotency ל־Create Task כדי למנוע כפילויות בעת retries מהלקוח.
- **Known regression**: לעתים נדירות תזכורות נשלחות פעמיים בעת deploy (רשום ב־Known Issues). 
