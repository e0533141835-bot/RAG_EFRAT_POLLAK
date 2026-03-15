# DB Schema Notes — Users / Projects / Tasks

## עקרונות סכימה כלליים
הסכימה מתוכננת לתמוך ב־multi-tenant. כל ישות עסקית משמעותית מכילה `tenant_id` (או נגזרת ממנו דרך `project_id`) כדי לאפשר אכיפת בידוד נתונים. מפתחות זרים (FK) חובה כדי לשמור על עקביות, ומתווספים אינדקסים לפי דפוסי השאילתות בפועל (Board, Timeline, Search).

הנחות:
- `id` הוא UUID.
- `created_at`, `updated_at` קיימים בכל טבלה מרכזית.
- מחיקות רכות (soft delete) מיושמות רק היכן שיש ערך עסקי לשחזור (למשל Projects), אחרת מחיקה קשיחה + audit event.

## טבלת Users
**users**
- `id` (uuid, pk)
- `tenant_id` (uuid, not null)
- `email` (citext, unique per tenant)
- `name` (text)
- `avatar_url` (text, nullable)
- `role` (enum: owner/admin/member)
- `status` (enum: active/suspended/invited)
- `last_login_at` (timestamptz, nullable)
- `password_hash` (text, nullable אם SSO בלבד)
- `created_at`, `updated_at`

שינויים אחרונים:
- **נוסף**: `status` כדי לתמוך במשתמש “invited” לפני הפעלה.
- **נוסף**: `last_login_at` לצורך ניתוח שימוש ואיתור חשבונות חשודים.
- **הוסר**: `users.username` שהיה legacy ונוצר user confusion מול email.

אינדקסים מומלצים:
- `(tenant_id, email)` unique
- `(tenant_id, status)` לשאילתות ניהול

## טבלת Projects
**projects**
- `id` (uuid, pk)
- `tenant_id` (uuid, not null)
- `name` (text)
- `description` (text, nullable)
- `visibility` (enum: private/internal)
- `archived_at` (timestamptz, nullable)
- `created_by` (uuid, fk -> users.id)
- `created_at`, `updated_at`

שינויים אחרונים:
- **נוסף**: `archived_at` במקום boolean `is_archived` כדי לשמור מועד ארכוב.
- **שונה**: `visibility` החליף `is_public` כדי לתמוך ב־internal ללא חשיפה חיצונית.

אינדקסים:
- `(tenant_id, archived_at)` עבור מסכי פרויקטים פעילים/ארכיון

## טבלת Tasks
**tasks**
- `id` (uuid, pk)
- `tenant_id` (uuid, not null)
- `project_id` (uuid, fk -> projects.id)
- `title` (text)
- `description` (text, nullable)
- `status` (enum: todo/in_progress/done/blocked)
- `priority` (enum: low/medium/high/urgent)
- `assignee_id` (uuid, fk -> users.id, nullable)
- `reporter_id` (uuid, fk -> users.id)
- `due_date` (date, nullable)
- `start_at` (timestamptz, nullable)
- `completed_at` (timestamptz, nullable)
- `position` (numeric או bigint, לצורך ordering ב־board columns)
- `labels` (jsonb, nullable)  
- `custom_fields` (jsonb, nullable)
- `created_at`, `updated_at`

שינויים אחרונים:
- **נוסף**: `position` כדי לאפשר drag & drop יציב בלוח.
- **נוסף**: `custom_fields` לתמיכה בשדות דינמיים לפי טננט.
- **הוסר**: `priority_text` (legacy), לאחר מעבר ל־enum.
- **שונה**: `completed_at` במקום boolean `is_done` כדי לשמור זמן השלמה.

אינדקסים קריטיים:
- `(project_id, status, updated_at desc)` למסך Board.
- `(tenant_id, due_date)` לתזכורות וחיפוש קרוב.
- GIN על `labels`/`custom_fields` אם משתמשים בפילטרים דינמיים.

## טבלאות נלוות (בקצרה)
- **project_members**: קשר users↔projects עם role פרויקטלי (viewer/editor).
- **task_comments**: הערות + mention parsing.
- **audit_events**: רישום שינויים (actor_id, entity_type, entity_id, diff jsonb).

הערה תפעולית:
- חובה לוודא שכל שאילתה לפי `task.id` מסננת גם לפי `tenant_id` או לפחות `project_id` שמקושר לטננט של המשתמש, כדי למנוע leakage בין טננטים.
