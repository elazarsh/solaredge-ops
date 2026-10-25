/* העמקה: פרויקטים, עיצוב דרך HTML, הערכה דיגיטלית, Skills וסוכנים, פרטיות ואחריות */
(function (TS) {
  'use strict';
  var esc = TS.esc, icon = TS.icon, $ = TS.$, $$ = TS.$$;

  var TABS = [
    ['projects', 'פרויקטים וקובצי ידע', 'folder', 'הקמת תיק עבודה קבוע ב־ChatGPT וב־Claude, וערכה של שבעה קבצים'],
    ['html', 'עיצוב דרך HTML', 'window', 'מבקשים תוצר כ־HTML, משפרים בסבבים ומייצאים רק בסוף'],
    ['assess', 'הערכה דיגיטלית', 'check', 'מבדק קצר, משוב, תובנות למורה, והסקריפט שבונה חידון Google Forms'],
    ['skills', 'Skills, סוכנים ו־Hooks', 'binder', 'מה זה, איפה מעלים, ומה מתאים למורה'],
    ['privacy', 'פרטיות ואחריות', 'lock', 'הנחיות משרד החינוך, כללי הדבקה, ובדיקת טקסט מקומית']
  ];

  function tabsNav(cur) {
    return '<div class="wrap"><div class="tabs" role="navigation" aria-label="נושאי העמקה">' + TABS.map(function (t) {
      return '<a href="#adv-' + t[0] + '" data-route="adv-' + t[0] + '"' + (t[0] === cur ? ' aria-current="page"' : '') + '>' + esc(t[1]) + '</a>';
    }).join('') + '</div></div>';
  }
  function head(eyebrow, title, lead) {
    return '<div class="wrap page-head"><span class="eyebrow">' + esc(eyebrow) + '</span><h1>' + esc(title) + '</h1>' + (lead ? '<p class="lead">' + esc(lead) + '</p>' : '') + '</div>';
  }
  function tag(s) { return '<span class="tag ' + s + '">' + esc(TS.statusLabels[s]) + '</span>'; }
  function code(id, title, text, ltr) {
    return '<div class="codebox"><header><span>' + esc(title) + '</span><span class="row" style="gap:6px"><button class="btn sm" type="button" data-copy-sel="#' + id + '">' + icon('copy') + 'העתקה</button></span></header><pre id="' + id + '"' + (ltr ? ' class="ltr"' : '') + '>' + esc(text) + '</pre></div>';
  }
  function table(heads, rows) {
    return '<div class="tbl-wrap"><table class="tbl"><thead><tr>' + heads.map(function (h) { return '<th>' + esc(h) + '</th>'; }).join('') + '</tr></thead><tbody>' + rows.map(function (r) { return '<tr>' + r.map(function (c) { return '<td>' + c + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table></div>';
  }
  function src(list) { return '<p class="small muted" style="margin-top:10px">מקורות: ' + list.map(function (s) { return '<a href="' + esc(s[1]) + '" target="_blank" rel="noopener">' + esc(s[0]) + '</a>'; }).join(' · ') + '</p>'; }
  function wrapPage(cur, body) { return tabsNav(cur) + '<div class="wrap stack lg" style="padding-block:28px 56px">' + body + '</div>'; }

  /* ---------------- פרויקטים ---------------- */
  function projects() {
    var kit = TS.library.kitFiles;
    var body =
      '<section class="stack"><h2>למה פרויקט</h2><div class="cols"><div><h3 style="font-size:1.1rem">חוסך הסברים חוזרים</h3><p class="muted">ההנחיות והקבצים נשארים בפרויקט, ולא צריך לכתוב אותם בכל שיחה.</p></div><div><h3 style="font-size:1.1rem">מחזיק סגנון עקבי</h3><p class="muted">אותן הנחיות לכל השיחות, כך שדפי העבודה נראים אותו דבר.</p></div><div><h3 style="font-size:1.1rem">שיחה לכל משימה</h3><p class="muted">שיחה חדשה לכל משימה שומרת על שולחן נקי. הפרויקט מספק את הרקע.</p></div></div></section>' +
      '<section class="stack"><h2>שש פעולות להקמה</h2><ol class="plain" style="display:flex;flex-direction:column;gap:12px">' +
        [['פותחים פרויקט', 'שם ברור, למשל ״חשבון ד׳״ או ״הודעות להורים״.'], ['כותבים הנחיות קבועות', 'מדביקים את הקובץ 01 מהערכה ומתאימים. מי אתם, איך לעבוד, מה אסור.'], ['מוסיפים מקורות מורשים', 'פרק מהספר, קטע מתוכנית הלימודים, הנחיות בית הספר. רק מה שמותר לשכפל.'], ['מוסיפים דוגמת תוצר טוב', 'דף עבודה או מערך שאהבתם. ה־AI לומד ממנו את הסגנון.'], ['פותחים שיחה נפרדת לכל משימה', 'שיחות בפרויקט אינן משתפות הקשר זו עם זו, אלא דרך ההנחיות והקבצים.'], ['מעדכנים ידע ויומן החלטות', 'אחרי כל שבוע: שורה ביומן החלטות, ושיטה שהוכיחה את עצמה בידע המצטבר.']].map(function (s) { return '<li><b>' + esc(s[0]) + '.</b> ' + esc(s[1]) + '</li>'; }).join('') + '</ol></section>' +
      '<section class="stack"><h2>איך מקימים, לפי הכלי</h2><div class="seg" id="seg-tool" role="group" aria-label="בחירת כלי"><button type="button" data-t="claude" aria-pressed="true">Claude</button><button type="button" data-t="chatgpt" aria-pressed="false">ChatGPT</button></div>' +
        '<div id="tool-claude" class="panel stack"><ol class="plain"><li>בתפריט הצד: Projects, או הכתובת claude.ai/projects.</li><li>״+ New Project״ בפינה העליונה. כותבים שם ותיאור (Claude אינו רואה אותם).</li><li>״Set project instructions״: מדביקים את קובץ 01 ולוחצים ״Save instructions״.</li><li>כפתור ״+״ בצד הימני של דף הפרויקט: מעלים את קבצים 02 עד 07.</li><li>פותחים שיחה בתוך הפרויקט.</li></ol>' +
          '<div>' + tag('ok') + ' פרויקטים זמינים לכולם. בחשבון חינמי: עד חמישה פרויקטים.</div><div>' + tag('ok') + ' במנוי בתשלום, כשהידע בפרויקט מתקרב לגבול ההקשר, Claude עובר אוטומטית לאחזור (RAG) וקיבולת הידע גדלה.</div><div>' + tag('ok') + ' שיתוף פרויקט זמין בחשבונות Team ו־Enterprise בלבד.</div>' +
          src([['Claude: מהם פרויקטים', 'https://support.claude.com/en/articles/9517075-what-are-projects'], ['Claude: יצירה וניהול', 'https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects']]) + '</div>' +
        '<div id="tool-chatgpt" class="panel stack" hidden><ol class="plain"><li>יוצרים פרויקט חדש (דורש התחברות).</li><li>שלוש הנקודות בפינת הפרויקט ← Project settings ← מדביקים את קובץ 01 כהנחיות.</li><li>מעלים את קבצים 02 עד 07 לאזור הקבצים של הפרויקט (התווית המדויקת עשויה להשתנות).</li><li>פותחים שיחה בתוך הפרויקט.</li></ol>' +
          '<div>' + tag('ok') + ' פרויקטים זמינים בכל סוגי החשבון, כולל חינמי. מספר הקבצים תלוי בחשבון.</div><div>' + tag('ok') + ' שיתוף עם עמיתים זמין בחשבונות Business, Enterprise ו־Edu.</div><div>' + tag('chk') + ' תווית כפתור הוספת הקבצים ומגבלות מדויקות: בדקו בכלי.</div>' +
          src([['OpenAI: Projects in ChatGPT', 'https://help.openai.com/en/articles/10169521-projects-in-chatgpt']]) + '</div></section>' +
      '<section class="stack"><h2>ערכת שבעת הקבצים</h2><div class="tbl-wrap"><table class="tbl"><thead><tr><th>קובץ</th><th>מה זה</th><th>לאן</th><th></th></tr></thead><tbody>' +
        kit.slice(1).map(function (f, i) { return '<tr><td><code>' + esc(f[0]) + '</code></td><td>' + esc(f[2]) + '</td><td>' + (i === 0 ? 'שדה ההנחיות' : 'קובץ בפרויקט') + '</td><td><button class="btn sm" type="button" data-dl="downloads/project-kit/' + f[0] + '" data-name="' + f[0] + '">' + icon('download') + '</button></td></tr>'; }).join('') + '</tbody></table></div>' +
        '<div class="row"><button class="btn primary" type="button" data-dl="' + TS.library.zips.kit + '" data-name="project-kit.zip">' + icon('download') + 'הורדת הערכה (ZIP)</button><a class="btn" href="#library" data-route="library">לספרייה</a></div></section>' +
      '<div class="callout warn">' + icon('warn') + '<p><b>אל תבטיחו הפעלה אוטומטית.</b> קובץ בשם מסוים אינו ״מופעל״ אוטומטית בכל מוצר. הפרויקט משתמש בקבצים כחומר רקע, ולכן ההנחיות בקובץ 01 מפנות אליהם בשמם. אם משהו לא נראה לכלי, אמרו לו.</p></div>' +
      '<details class="more"><summary>למתקדמים: שיחה רגילה מול Claude Code או Codex</summary><div class="stack">' +
        table(['', 'שיחה רגילה (צ׳אט)', 'כלי סוכן עם קבצים (למשל Claude Code, Codex)'], [
          ['עובד על', 'טקסט וקבצים שצירפתם לשיחה', 'תיקייה במחשב, עם קבצים ותוכנות'],
          ['פעולות', 'מייצר תוכן. בחלק מהכלים גם קבצים בסביבה מבודדת', 'קורא וכותב קבצים ומריץ פקודות, לפי הרשאות שנתתם'],
          ['הנחיות קבועות', 'הנחיות פרויקט או הוראות מותאמות', 'קובץ הנחיות בתיקייה. השמות מוסכמים ותלויים בכלי (למשל CLAUDE.md או AGENTS.md): בדקו בתיעוד'],
          ['סיכון', 'תוכן שגוי או מומצא', 'גם פעולה שגויה על קבצים. נדרשת תשומת לב להרשאות'],
          ['למי מתאים', 'רוב המורים, רוב המשימות', 'מי שמנהלת ספריית חומרים גדולה בקבצים ורוצה אוטומציה']]) +
        '<p class="muted small">למורה רגילה אין צורך בכלי כאלה. שיחה ופרויקט מכסים את רוב הצרכים.</p></div></details>';
    return { title: 'פרויקטים וקובצי ידע', html: head('העמקה', 'פרויקטים וקובצי ידע', 'פרויקט הוא מסגרת ארגונית: הנחיות וקבצים קבועים, ושיחה נפרדת לכל משימה.') + wrapPage('projects', body),
      after: function (root) {
        $('#seg-tool', root).addEventListener('click', function (e) {
          var b = e.target.closest('[data-t]'); if (!b) return;
          $$('[data-t]', root).forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
          $('#tool-claude', root).hidden = b.getAttribute('data-t') !== 'claude'; $('#tool-chatgpt', root).hidden = b.getAttribute('data-t') !== 'chatgpt';
        });
      } };
  }

  /* ---------------- HTML ---------------- */
  var HTML_BRIEF = 'הכן לי [דף עבודה / הזמנה / מסמך] כקובץ HTML יחיד ושלם בעברית (lang="he" dir="rtl").\nתוכן: [הדביקו או תארו]. קהל: [ ]. סגנון: [צבע מותג, גופן, לוגו אם מצורף].\nדרישות: צבעים, גופנים וגודל כתב כמשתני CSS ב־:root. כללי @media print עם @page A4 ושוליים.\nבלי שבירת עמוד באמצע שאלה או טבלה. בלי קבצים חיצוניים. אל תייצא ל־PDF, אבדוק בדפדפן.\nבסבב הראשון: מבנה ותוכן בלבד. בסבבים הבאים אבקש שינויים ממוקדים.';
  var PRINT_CSS = '@page { size: A4; margin: 12mm; }\nhtml { direction: rtl; }\n.question, table { break-inside: avoid; }\n* { -webkit-print-color-adjust: economy; print-color-adjust: economy; }';

  function html() {
    var body =
      '<section class="stack"><h2>המשל: כיתה וצילום</h2><p class="lead">מסמך שבנוי כ־HTML הוא כמו כיתה שאפשר להזיז בה שולחנות ולשנות שלטים. תמונה סופית (PDF, JPG) היא צילום של הכיתה. מצלמים רק כשמרוצים מהסידור, ושומרים את הכיתה עצמה למקרה שרוצים לשנות בעתיד.</p></section>' +
      '<section class="stack"><h2>ששת השלבים</h2><ol class="plain" style="display:flex;flex-direction:column;gap:10px">' + ['מגדירים תוכן, קהל ושפה עיצובית: מה כתוב, למי, באיזה צבע וגופן.', 'מבקשים HTML עם מבנה מסודר ועיצוב שאפשר לשנות (משתני CSS).', 'מבקשים שינויים ממוקדים: אחד בכל פעם.', 'בודקים קריאות, דיוק והדפסה.', 'מאשרים ומייצאים.', 'שומרים גם את קובץ המקור לעריכה בעתיד.'].map(function (s) { return '<li>' + esc(s) + '</li>'; }).join('') + '</ol></section>' +
      '<section class="stack"><h2>נסו בעצמכם: שינוי ממוקד</h2><p class="muted">הדף שלמטה הוא HTML אמיתי. כל כפתור מדמה בקשה אחת. שימו לב שמשתנה אחד משתנה, והשאר נשאר.</p>' +
        '<div class="html-demo"><div class="toolbar no-print" id="demo-bar">' +
          '<button class="btn sm" type="button" data-d="size">הגדל את הכתב</button><button class="btn sm" type="button" data-d="color">שנה את צבע הכותרות</button><button class="btn sm" type="button" data-d="ans">הסתר או הוסף שורות כתיבה</button><button class="btn sm" type="button" data-d="bw">גרסה חסכונית (שחור־לבן)</button><button class="btn sm ghost" type="button" data-d="reset">איפוס</button></div>' +
          '<div class="sheet" id="sheet"><h4>דף עבודה: זכר ונקבה</h4><div class="q"><b>1.</b> השלימו: הילד גדול, והילדה ______.<div class="ans"></div></div><div class="q"><b>2.</b> חברו כל שם עצם לשם התואר המתאים.<div class="ans"></div></div><div class="q"><b>3.</b> כתבו משפט עם שם עצם ברבים.<div class="ans"></div></div></div>' +
          '<div class="xp-note" id="demo-note">לחצו על כפתור כדי לראות איזו בקשה הייתם שולחים ל־AI.</div></div></section>' +
      '<section class="stack"><h2>בקשה להעתקה</h2>' + code('html-brief', 'בקשת HTML', HTML_BRIEF) + code('print-css', 'כללי הדפסה בסיסיים (CSS)', PRINT_CSS, true) + '</section>' +
      '<section class="stack"><h2>ייצוא: מה אפשר ומה לא</h2>' + table(['פורמט', 'איך', 'מגבלה'], [
        ['PDF', 'הדפסה מהדפדפן ושמירה כ־PDF', 'לבדוק חלוקת עמודים בתצוגה המקדימה'],
        ['JPG או PNG', 'צילום מסך או כלי ייצוא מתאים', 'זה צילום: אי אפשר לערוך אחר כך'],
        ['Word', 'HTML פשוט ותואם, או בקשה ליצירת DOCX', 'Word אינו משמר תמיד עיצוב HTML מורכב'],
        ['RTF', 'רק כקובץ RTF תקין', 'לבקש במפורש ולפתוח לבדיקה'],
        ['MP4', 'רינדור או הקלטת מסך', 'אנימציית HTML אינה קובץ וידאו']]) +
        '<p class="muted small">מקור מובנה מקל על שינוי ממוקד, אבל אינו מבטיח חיסכון בטוקנים בכל מצב.</p></section>' +
      '<section class="stack"><h2>כלים זמינים כיום</h2><div class="fact">' + tag('ok') + '<span>Claude יוצר קבצי PowerPoint, Word, Excel ו־PDF כשהאפשרות ״יצירת קבצים״ מופעלת.</span></div><div class="fact">' + tag('ok') + '<span>Gemini Canvas בונה חידונים, מדריכי לימוד, צירי זמן ואבות טיפוס אינטראקטיביים.</span></div><div class="fact">' + tag('chk') + '<span>הצגת HTML בחלון צד בשיחה (Artifacts ב־Claude, Canvas ב־ChatGPT): זמינות ותנאים משתנים לפי חשבון.</span></div><div class="fact">' + tag('sec') + '<span>Canva מציע תבניות ועיצוב משולב, וגרסת Education חינמית דווחה למורים מאומתים.</span></div>' +
        '<p><a href="#tools" data-route="tools">למדריך הכלים</a></p></section>';
    return { title: 'עיצוב דרך HTML', html: head('העמקה', 'עיצוב ויצוא דרך HTML', 'מבקשים תוצר כ־HTML, משפרים בסבבים, ורק כשמרוצים מייצאים לפורמט הסופי.') + wrapPage('html', body),
      after: function (root) {
        var sheet = $('#sheet', root), note = $('#demo-note', root);
        var colors = [['#1D4E89', 'כחול'], ['#2B7A4B', 'ירוק'], ['#8A5600', 'חום'], ['#7A1F5C', 'סגול']], ci = 0, sizes = [1, 1.18, 1.36], si = 0;
        var asks = {
          size: 'בקשה: ״הגדל את הכתב בדף ב־18 אחוז, בלי לשנות את הסידור״. מה השתנה: משתנה אחד (--d-size).',
          color: 'בקשה: ״שנה את צבע הכותרות והקו שמתחתן לצבע מותג, בלי לגעת בשאר״. מה השתנה: משתנה אחד (--d-accent).',
          ans: 'בקשה: ״הסר את שורות הכתיבה מתחת לכל שאלה, ושמור גרסה עם השורות״. מה השתנה: תצוגה של רכיב אחד.',
          bw: 'בקשה: ״הוסף גרסה חסכונית להדפסה: שחור־לבן, בלי צבע״. מה השתנה: גרסה נוספת, אותו תוכן.',
          reset: 'חזרה למצב ההתחלה. בעבודה אמיתית אפשר לבקש ״חזור לגרסה הקודמת״.' };
        $('#demo-bar', root).addEventListener('click', function (e) {
          var b = e.target.closest('[data-d]'); if (!b) return; var k = b.getAttribute('data-d');
          if (k === 'size') { si = (si + 1) % sizes.length; sheet.style.setProperty('--d-size', sizes[si] + 'rem'); }
          if (k === 'color') { ci = (ci + 1) % colors.length; sheet.style.setProperty('--d-accent', colors[ci][0]); }
          if (k === 'ans') sheet.classList.toggle('noans');
          if (k === 'bw') sheet.classList.toggle('bw');
          if (k === 'reset') { sheet.removeAttribute('style'); sheet.className = 'sheet'; si = 0; ci = 0; }
          note.textContent = asks[k];
        });
      } };
  }

  /* ---------------- הערכה דיגיטלית ---------------- */
  var QUIZ = [
    { topic: 'שברים שקולים', q: 'איזה שבר שווה ל־1/2?', o: ['1/4', '2/4', '2/3', '1/3'], c: 1, fb: { 0: 'טעות נפוצה: מסתכלים רק על המכנה. 1/4 הוא רבע ולא חצי.', 2: 'טעות נפוצה: מתייחסים למונה ולמכנה כמספרים נפרדים. 2/3 גדול מחצי.', 3: '1/3 הוא שליש. נסו לצייר חצי ושליש על ציר מספרים.' } },
    { topic: 'שברים שקולים', q: 'מהו שבר שקול ל־2/3?', o: ['4/6', '3/4', '2/6', '4/3'], c: 0, fb: { 1: 'טעות נפוצה: מוסיפים 1 למונה ולמכנה. שבר שקול מתקבל בהכפלה באותו מספר.', 2: 'טעות נפוצה: מכפילים רק את המכנה.', 3: 'הפכתם את השבר. 4/3 גדול מ־1.' } },
    { topic: 'השוואת שברים', q: 'איזה שבר גדול יותר: 3/8 או 5/8?', o: ['3/8', '5/8', 'שווים', 'אי אפשר לדעת'], c: 1, fb: { 0: 'כשהמכנה זהה, המונה הגדול יותר מייצג שבר גדול יותר.', 2: 'החלקים באותו גודל, אבל ב־5/8 יש יותר מהם.', 3: 'אפשר לדעת: המכנים זהים.' } },
    { topic: 'חיבור שברים', q: 'מה התוצאה של 2/5 + 1/5?', o: ['3/10', '3/5', '2/10', '1/5'], c: 1, fb: { 0: 'טעות נפוצה: מחברים גם את המכנים. במכנה זהה מחברים רק מונים.', 2: 'טעות נפוצה: מכפילים או מחברים לא נכון.', 3: 'חיסרתם במקום לחבר.' } }
  ];

  var APPS_STEPS = ['מכינים שאלות לפי מטרות הלמידה במסלול ״פעילות הערכה דיגיטלית״ בסטודיו, ובוחרים פלט JSON.', 'פותחים script.google.com, פרויקט חדש, ומדביקים את הקובץ build-quiz.gs. מחליפים את QUIZ_JSON בפלט.', 'מריצים buildQuiz ומאשרים הרשאות. מתקבל טופס חידון בדרייב, וכתובת לשיתוף ביומן הריצה.', 'פותחים את הטופס כתלמיד ובודקים. הגדרות החידון: Settings ← Make this a quiz.', 'משתפים עם התלמידים בלי שדה שם, בכלי שבית הספר אישר.', 'אחרי התשובות: לשונית Responses (סיכום אוטומטי) או הסקריפט summarize-responses.gs לקבלת סיכום בלי שמות.', 'מדביקים את הסיכום במסלול ״ניתוח תשובות ותוצאות״ ומקבלים המלצה. ההחלטה נשארת שלכם.'];

  function assess() {
    var body =
      '<section class="stack"><h2>שני דברים שונים</h2><div class="cols c2"><div class="panel"><h3 style="font-size:1.15rem">הדגמה מקומית בדפדפן</h3><p class="muted">מורה אחד מנסה חידון ורואה איך נראה סיכום. הנתונים נשארים במכשיר הזה ואינם נשמרים. זה ללמוד, לא ללמד כיתה.</p></div><div class="panel"><h3 style="font-size:1.15rem">איסוף תשובות אמיתי</h3><p class="muted">תשובות מכמה מכשירים דורשות כלי טפסים, כמו Google Forms. דף אינטרנט רגיל בלי שרת אינו יכול לאסוף תשובות בין מכשירים. localStorage נשאר בדפדפן אחד, והוא אינו מערכת כיתתית.</p></div></div></section>' +
      '<section class="stack"><h2>הדגמה מקומית: חידון קצר וסיכום</h2><div class="callout warn">' + icon('warn') + '<p>זו הדגמה. הסיכום בסוף מבוסס אך ורק על התשובות שתזינו עכשיו, בלי שמות ובלי שמירה. בכיתה אמיתית כל שורה בסיכום מייצגת הרבה משיבים.</p></div>' +
        '<div class="panel" id="quiz">' + QUIZ.map(function (q, i) {
          return '<div class="quiz-q" data-i="' + i + '"><b>' + (i + 1) + '. ' + esc(q.q) + '</b><div class="opts">' + q.o.map(function (o, j) { return '<button type="button" class="opt" data-j="' + j + '">' + esc(o) + '</button>'; }).join('') + '</div><div class="fb" role="status"></div></div>';
        }).join('') + '<div class="row" style="margin-top:12px"><button class="btn primary" type="button" id="quiz-sum" disabled>הצגת סיכום למורה</button><button class="btn ghost" type="button" id="quiz-reset">התחלה מחדש</button></div><div id="quiz-out" class="stack" style="margin-top:16px"></div></div></section>' +
      '<section class="stack"><h2>איסוף אמיתי: התהליך</h2><ol class="plain" style="display:flex;flex-direction:column;gap:8px">' + APPS_STEPS.map(function (s) { return '<li>' + esc(s) + '</li>'; }).join('') + '</ol>' +
        '<div class="row"><button class="btn" type="button" data-view="downloads/guides/build-quiz.gs" data-name="build-quiz.gs">צפייה: בניית חידון</button><button class="btn primary" type="button" data-dl="downloads/guides/build-quiz.gs" data-name="build-quiz.gs">' + icon('download') + 'build-quiz.gs</button><button class="btn" type="button" data-dl="downloads/guides/summarize-responses.gs" data-name="summarize-responses.gs">' + icon('download') + 'summarize-responses.gs</button><button class="btn" type="button" data-dl="downloads/guides/sample-quiz.json" data-name="sample-quiz.json">' + icon('download') + 'דוגמת JSON</button></div>' +
        '<div class="callout">' + icon('info') + '<p>הסקריפטים נבדקו בבדיקת תחביר ובהרצה מול הדמיה של ממשקי Google. הרצה אמיתית מול Google Forms לא נבדקה בסביבת הבנייה. הריצו קודם על טופס ניסיון.</p></div>' +
        src([['Google: יצירה וציון חידונים ב־Forms', 'https://support.google.com/docs/answer/7032287?hl=en']]) + '</section>' +
      '<section class="stack"><h2>איך קוראים תוצאות</h2><ul class="plain"><li><b>מה ללמד מחדש:</b> נושא שבו רוב המשיבים טעו, ובעיקר באותה טעות.</li><li><b>מי זקוק לתמיכה:</b> לפי קודים שקבעתם, כקבוצה זמנית ולא כתווית.</li><li><b>מי מוכן להעמקה:</b> מי שענה נכון על הכול ומסוגל להסביר מדוע.</li></ul><p class="muted small">אל תזינו ל־AI שמות או נתונים מזהים. השתמשו בקודים ובסיכום מצטבר.</p></section>';
    return { title: 'הערכה דיגיטלית', html: head('העמקה', 'הערכה דיגיטלית ותובנות למורה', 'מבדק קצר, משוב ברור, וסיכום שעוזר להחליט מה ללמד בשיעור הבא.') + wrapPage('assess', body),
      after: function (root) {
        var ans = {};
        var quiz = $('#quiz', root);
        quiz.addEventListener('click', function (e) {
          var b = e.target.closest('.opt'); if (!b) return;
          var qEl = b.closest('.quiz-q'), i = +qEl.getAttribute('data-i'), j = +b.getAttribute('data-j'), q = QUIZ[i];
          if (ans[i] !== undefined) return;
          ans[i] = j;
          $$('.opt', qEl).forEach(function (o, k) { o.disabled = true; if (k === q.c) o.classList.add('right'); if (k === j && j !== q.c) o.classList.add('wrong'); });
          $('.fb', qEl).textContent = j === q.c ? 'נכון.' : (q.fb[j] || 'לא מדויק. נסו שוב בפעם הבאה.');
          $('#quiz-sum', root).disabled = Object.keys(ans).length < QUIZ.length;
        });
        $('#quiz-sum', root).addEventListener('click', function () {
          var topics = {};
          QUIZ.forEach(function (q, i) { var t = topics[q.topic] = topics[q.topic] || { r: 0, n: 0, wrong: [] }; t.n++; if (ans[i] === q.c) t.r++; else t.wrong.push(q.o[ans[i]]); });
          $('#quiz-out', root).innerHTML = '<h3 style="font-size:1.15rem">סיכום למורה (הדגמה, מבוסס על ההזנה שלכם עכשיו)</h3>' + table(['נושא', 'נכון', 'המלצה'], [].concat(Object.keys(topics).map(function (k) {
            var t = topics[k]; return [esc(k), t.r + ' מתוך ' + t.n, esc(t.r === t.n ? 'מוכנים להעמקה: שאלת העברה או הסבר ״מדוע״' : t.r === 0 ? 'ללמד מחדש בהסבר אחר' : 'חיזוק קצר, ובדיקה אילו טעויות חוזרות')];
          }))) + '<p class="small muted">כך ייראה סיכום אמיתי, אבל עם הרבה משיבים. כאן הוא מבוסס על ' + QUIZ.length + ' תשובות שלכם בלבד.</p>';
        });
        $('#quiz-reset', root).addEventListener('click', function () { TS.go('adv-assess', { keepScroll: true, noFocus: true }); });
      } };
  }

  /* ---------------- Skills ---------------- */
  var SKILL_EX = '---\nname: my-lesson-skill\ndescription: "מכין מערך שיעור קצר בעברית. להפעלה כשמבקשים תכנון שיעור."\n---\n\n# מערך שיעור\n\n## מתי להפעיל\nכשהמורה מבקשת לתכנן שיעור.\n\n## שלבי עבודה\n1. לנסח מטרות נצפות.\n2. לתכנן הוראה בצעדים קטנים.\n3. לבדוק הבנה בסוף.\n\n## כללים\n- עברית תקנית. לא להמציא עובדות.';

  function skills() {
    var L = TS.library;
    var body =
      '<section class="stack"><h2>מה זה Skill</h2><p class="lead">Skill הוא חבילה של הוראות (ולפעמים גם קבצים וסקריפטים) שהמערכת טוענת כשהבקשה מתאימה. כמו קלסר שיטות עבודה שנפתח בזמן הנכון. התמיכה תלויה בכלי: ב־Claude זה קיים, ובכלים אחרים יש מקבילות חלקיות כמו GPT מותאם או Gem.</p></section>' +
      '<section class="stack"><h2>איך נראה Skill</h2><p class="muted">תיקייה אחת בשם ה־Skill, ובה קובץ <code>SKILL.md</code> עם שדות <code>name</code> (אותיות לטיניות קטנות ומקפים) ו־<code>description</code> (מה הוא עושה ומתי להפעיל). שם התיקייה זהה לשם ה־Skill.</p>' + code('skill-ex', 'דוגמה: SKILL.md', SKILL_EX, true) + '</section>' +
      '<section class="stack"><h2>איפה מעלים (Claude)</h2><ol class="plain"><li>Settings ← Capabilities: מוודאים שהאפשרות Code execution and file creation פעילה (בהגדרות החדשות: Create and edit files).</li><li>Customize ← Skills.</li><li>״+״ ← Create skill ← Upload a skill.</li><li>בוחרים קובץ ZIP שבתוכו תיקיית ה־Skill (לא הקבצים ישירות בשורש).</li><li>ה־Skill מופיע ברשימה ואפשר להפעיל או לכבות.</li></ol><div>' + tag('ok') + ' Skills זמינים בחשבונות Free, Pro, Max, Team ו־Enterprise, ודורשים הפעלת code execution.</div>' +
        '<div class="callout warn">' + icon('warn') + '<p><b>אבטחה.</b> התקינו Skills רק ממקורות מהימנים. קראו את הקבצים לפני הפעלה, במיוחד סקריפטים והוראות להתחבר למקורות חיצוניים. Skills עלולים להפעיל קוד או לבקש התקנת חבילות, והסיכונים העיקריים הם prompt injection ודליפת מידע.</p></div>' +
        src([['Claude: שימוש ב־Skills', 'https://support.claude.com/en/articles/12512180-using-skills-in-claude'], ['מאגר Skills של Anthropic', 'https://github.com/anthropics/skills']]) + '</section>' +
      '<section class="stack"><h2>Skills של הסטודיו</h2><p class="muted">חמישה Skills מקוריים, ארוזים לפי המפרט. כל אחד קצר ונקרא, כדי שתוכלו לשנות אותו לצרכים שלכם.</p><ul class="plain">' + L.skills.map(function (s) { return '<li><b>' + esc(s.title) + '</b> (<code>' + esc(s.id) + '</code>): ' + esc(s.desc) + '</li>'; }).join('') + '</ul><a class="btn primary" href="#skills-anchor" data-route="library">להורדה בספרייה ' + icon('arrow-left') + '</a></section>' +
      '<section class="stack"><h2>משאבים קיימים</h2><p class="muted">אלה חומרים של אחרים. בדקו רישיון והתאמה לישראל.</p>' + table(['מקור', 'מה יש', 'רישיון והערות'], [
        ['<a href="https://github.com/anthropics/k12-teacher-skills" target="_blank" rel="noopener">anthropics/k12-teacher-skills</a>', 'תכנון שיעור, דיפרנציאציה, הכנה לשיעור, בדיקת הבנה במתמטיקה', 'Apache 2.0. מבוסס על סטנדרטים אמריקאיים ומחבר Learning Commons'],
        ['<a href="https://github.com/polytheseus/teacher-skills" target="_blank" rel="noopener">polytheseus/teacher-skills</a>', 'הודעות להורים, מחוונים, מחוללי חידונים ועוד', 'MIT. סביבה בריטית באנגלית. חלק בתשלום. מתוחזק על ידי אדם אחד, בלי כוכבים או גרסאות']]) + '</section>' +
      '<section class="stack"><h2>סוכנים ו־Hooks: מה למורה</h2>' + table(['מושג', 'מתי זה שימושי', 'האם צריך'], [
        ['סוכן', 'משימה גדולה שאפשר לפצל, כמו איסוף חומרים וסיכומם', 'לרוב לא. יש עלות תיאום, והוא אינו חוסך תמיד זמן או טוקנים'],
        ['Hook', 'פעולה אוטומטית בעקבות אירוע, למשל בדיקה אחרי שמירת קובץ', 'לא למורה רגילה. קיים בעיקר בכלי פיתוח, והתמיכה תלויה בכלי']]) + '<p class="muted small">תמיכה ב־Skills וב־Hooks תלויה בכלי. בדקו בתיעוד לפני שמתכננים עבודה סביבם.</p></section>';
    return { title: 'Skills וסוכנים', html: head('העמקה', 'Skills, סוכנים ו־Hooks', 'שיטות עבודה שנשמרות וחוזרות, ומה מזה באמת מתאים למורה.') + wrapPage('skills', body) };
  }

  /* ---------------- פרטיות ---------------- */
  function privacy() {
    var body =
      '<div class="callout warn">' + icon('lock') + '<p><b>הכלל הראשון.</b> אין להזין לכלי AI מידע אישי, רגיש או מזהה על עצמכם, על תלמידים או על חברי צוות. מידע מוגן נשמר רק במערכות משרד החינוך ובשירותים מאושרים.</p></div>' +
      '<section class="stack"><h2>מה מותר לתלמידים, לפי כיתה</h2>' + table(['כיתות', 'מה מוגדר'], [['א׳–ג׳', 'אין אישור שימוש לתלמידים. שימוש לצוות ההוראה בלבד, להכנת תוכן וניהול למידה'], ['ד׳', 'התנסות רק דרך בוט משרד החינוך המוגן, ולא בכלים חיצוניים'], ['ה׳–ז׳', 'המורה מפעילה את הכלי, התלמידים משתתפים במליאה, בלי שימוש עצמאי'], ['ח׳ ומעלה', 'שימוש עצמאי בכלי בינה יוצרת מרשימת הכלים המאושרים']]) +
        '<p class="small muted">מקור: עמוד הכלים הבין־לאומיים במרחב הפדגוגי. אישורי הכלים משתנים, ויש לבדוק בקטלוג העדכני.</p></section>' +
      '<section class="stack"><h2>כללי עבודה מומלצים</h2><ul class="plain"><li>הירשמו לכלי AI בדוא״ל נפרד שאינו כולל את שמכם.</li><li>השתמשו בדפדפן ייעודי, והימנעו מגלישה לאתרים רגישים כמו הבנק במקביל.</li><li>היזהרו מאתרים מתחזים שגובים כסף על שירות שמוצע בחינם. בדקו את כתובת האתר.</li><li>אל תאפשרו לתלמידים לעבוד על מחשבים ברשת המנהלתית.</li><li>אל תזינו מספרי כרטיס אשראי או תעודת זהות בדפדפן.</li></ul></section>' +
      '<section class="stack"><h2>בדיקת טקסט לפני הדבקה</h2><p class="muted">הדביקו כאן טקסט כדי לבדוק אם נראה בו מספר זהות, טלפון או דוא״ל. הבדיקה מתבצעת במכשיר שלכם ואינה נשלחת לשום מקום. היא אינה תופסת שמות, ולכן קראו בעצמכם גם.</p>' +
        '<div class="field"><label for="pv-text">טקסט לבדיקה</label><textarea id="pv-text" rows="5" placeholder="הדביקו כאן"></textarea></div><div id="pv-out" class="callout ok" role="status">' + icon('check') + '<p>הדביקו טקסט כדי לבדוק.</p></div></section>' +
      '<section class="stack"><h2>אם נחשף מידע מוגן</h2><ol class="plain"><li>מבטלים מיד את הפעולה (הרשאה לענן, שליחת דוא״ל).</li><li>מיידעים בהקדם את מנהל בית הספר.</li><li>המנהל מיידע את משרד החינוך: <span dir="ltr">school_security@education.gov.il</span></li></ol><p><b>מוקד בינה מלאכותית של המשרד:</b> <span dir="ltr">*6552</span> (עברית 1). לצוותי הוראה: 1 ואז 6. א׳–ה׳ 07:30–17:00, ו׳ 07:30–13:00.</p></section>' +
      '<section class="stack"><h2>אחריות מקצועית</h2><p class="prose">ה־AI יכול לטעות, להטות ולהמציא. משרד החינוך מדגיש עקרון של אדם בתוך התהליך: אתם בודקים, מתאימים ומחליטים. לכל מסלול בסטודיו יש רשימת בדיקה. ההחלטות על תלמידים נשארות בידי בני אדם.</p>' +
        src([['שאלות ותשובות על AI לצוות החינוך', 'https://pop.education.gov.il/teaching-tools/ai-education/questions-answers/'], ['כלים בין־לאומיים וכלי AI', 'https://pop.education.gov.il/sherutey-tiksuv-bachinuch/international-digital-ai-tools/'], ['מובילים AI בחינוך', 'https://pop.education.gov.il/teaching-tools/ai-education/']]) + '<p class="small muted">נבדק ב־' + TS.meta.checkedOn + '. המסמכים הרשמיים של המשרד הם המחייבים.</p></section>';
    return { title: 'פרטיות ואחריות', html: head('העמקה', 'פרטיות ואחריות', 'מה להזין ומה לא, מה מותר לתלמידים, ומה עושים אם משהו השתבש.') + wrapPage('privacy', body),
      after: function (root) {
        $('#pv-text', root).addEventListener('input', function () {
          var r = TS.privacyScan(this.value), out = $('#pv-out', root);
          out.className = 'callout ' + (r.length ? 'warn' : 'ok');
          out.innerHTML = r.length ? icon('warn') + '<p>' + esc(r.join(' ')) + ' מחקו או החליפו בקוד לפני ההדבקה.</p>' : icon('check') + '<p>לא זוהה מספר זהות, טלפון או דוא״ל. עדיין, קראו בעצמכם ובדקו שאין שמות.</p>';
        });
      } };
  }

  TS.views.advanced = function (param) {
    if (param === 'projects') return projects();
    if (param === 'html') return html();
    if (param === 'assess') return assess();
    if (param === 'skills') return skills();
    if (param === 'privacy') return privacy();
    return {
      title: 'העמקה',
      html: head('העמקה', 'העמקה למתקדמים', 'התוכן כאן אינו נדרש כדי להתחיל. הוא מיועד למי שרוצה להתקדם משיחה פשוטה לעבודה עם פרויקטים, ידע מותאם ו־Skills.') +
        '<hr class="ruler"><div class="wrap section tight"><div class="paths">' + TABS.map(function (t) { return '<a class="path" href="#adv-' + t[0] + '" data-route="adv-' + t[0] + '"><span class="ic">' + icon(t[2]) + '</span><span><b>' + esc(t[1]) + '</b><small>' + esc(t[3]) + '</small></span>' + icon('arrow-left') + '</a>'; }).join('') + '</div></div>'
    };
  };

})(window.TS = window.TS || {});
