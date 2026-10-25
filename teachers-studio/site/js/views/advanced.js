/* העמקה: פרויקטים, עיצוב דרך HTML, הערכה דיגיטלית, Skills, פרטיות. מינימום טקסט גלוי, השאר בתוך אקורדיונים */
(function (TS) {
  'use strict';
  var esc = TS.esc, icon = TS.icon, $ = TS.$, $$ = TS.$$;

  var TABS = [
    ['projects', 'פרויקטים וקובצי ידע', 'folder', 'תיק עבודה קבוע ב־ChatGPT וב־Claude, וערכה של שבעה קבצים'],
    ['html', 'עיצוב דרך HTML', 'window', 'מבקשים תוצר כ־HTML, משפרים בסבבים, מייצאים בסוף'],
    ['assess', 'הערכה דיגיטלית', 'check', 'מבדק קצר, משוב, וסקריפט שבונה חידון Google Forms'],
    ['skills', 'Skills, סוכנים ו־Hooks', 'binder', 'מה זה, איפה מעלים, ומה מתאים למורה'],
    ['privacy', 'פרטיות ואחריות', 'lock', 'הנחיות המשרד, כללי הדבקה ובדיקת טקסט מקומית']
  ];

  function tabsNav(cur) {
    return '<div class="wrap"><div class="tabs-line" role="navigation" aria-label="נושאי העמקה">' + TABS.map(function (t) {
      return '<a href="#adv-' + t[0] + '" data-route="adv-' + t[0] + '"' + (t[0] === cur ? ' aria-current="page"' : '') + '>' + esc(t[1]) + '</a>';
    }).join('') + '</div></div>';
  }
  function head(title, lead) {
    return '<div class="wrap page-head"><span class="eyebrow">העמקה</span><h1 data-words>' + esc(title) + '</h1>' + (lead ? '<p class="lead" data-rv>' + esc(lead) + '</p>' : '') + '</div>';
  }
  function page(cur, title, lead, body) {
    return head(title, lead) + tabsNav(cur) + '<div class="wrap stack lg" style="padding-block:28px 60px">' + body + '</div>';
  }
  function tag(s) { return '<span class="tag ' + s + '">' + esc(TS.statusLabels[s]) + '</span>'; }
  function acc(title, body, open, count) {
    return '<details class="acc" data-rv' + (open ? ' open' : '') + '><summary><span>' + esc(title) + (count ? ' <span class="tag">' + esc(count) + '</span>' : '') + '</span><span class="pm">' + icon('plus') + '</span></summary><div class="acc-body stack">' + body + '</div></details>';
  }
  function code(id, title, text, ltr) {
    return '<div class="codebox"><header><span>' + esc(title) + '</span><button class="btn sm" type="button" data-copy-sel="#' + id + '">' + icon('copy') + 'העתקה</button></header><pre id="' + id + '"' + (ltr ? ' class="ltr"' : '') + '>' + esc(text) + '</pre></div>';
  }
  function table(heads, rows) {
    return '<div class="tbl-wrap"><table class="tbl"><thead><tr>' + heads.map(function (h) { return '<th>' + esc(h) + '</th>'; }).join('') + '</tr></thead><tbody>' + rows.map(function (r) { return '<tr>' + r.map(function (c) { return '<td>' + c + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table></div>';
  }
  function src(list) { return '<p class="small muted">מקורות: ' + list.map(function (s) { return '<a href="' + esc(s[1]) + '" target="_blank" rel="noopener">' + esc(s[0]) + '</a>'; }).join(' · ') + '</p>'; }
  function steps(arr) { return '<ol class="plain stack" style="gap:10px">' + arr.map(function (s) { return '<li>' + (Array.isArray(s) ? '<b>' + esc(s[0]) + '.</b> ' + esc(s[1]) : esc(s)) + '</li>'; }).join('') + '</ol>'; }
  function mini(h, p) { return '<div><h3 style="font-size:1.1rem">' + esc(h) + '</h3><p class="muted">' + esc(p) + '</p></div>'; }

  /* ---------------- פרויקטים ---------------- */
  function projects() {
    var kit = TS.library.kitFiles;
    var body =
      '<div class="cols" data-rv>' + mini('חוסך הסברים חוזרים', 'ההנחיות והקבצים נשארים בפרויקט.') + mini('סגנון עקבי', 'אותן הנחיות לכל השיחות.') + mini('שיחה לכל משימה', 'שולחן נקי, והפרויקט מספק את הרקע.') + '</div>' +
      '<section class="card stack" data-rv aria-labelledby="pj-h"><h2 id="pj-h" style="font-size:1.5rem">איך מקימים</h2><div class="seg" id="seg-tool" role="group" aria-label="בחירת כלי"><button type="button" data-t="claude" aria-pressed="true">Claude</button><button type="button" data-t="chatgpt" aria-pressed="false">ChatGPT</button></div>' +
        '<div id="tool-claude" class="stack">' + steps(['בתפריט הצד: Projects, או claude.ai/projects.', '״+ New Project״ בפינה העליונה. שם ותיאור (Claude אינו רואה אותם).', '״Set project instructions״: מדביקים את קובץ 01 ולוחצים Save.', 'כפתור ״+״ בצד הימני: מעלים את קבצים 02 עד 07.', 'פותחים שיחה בתוך הפרויקט.']) +
          '<div class="fact">' + tag('ok') + '<span>פרויקטים זמינים לכולם. בחשבון חינמי: עד חמישה.</span></div><div class="fact">' + tag('ok') + '<span>במנוי בתשלום, כשהידע מתקרב לגבול ההקשר, Claude עובר אוטומטית לאחזור (RAG).</span></div><div class="fact">' + tag('ok') + '<span>שיתוף פרויקט: Team ו־Enterprise בלבד.</span></div>' +
          src([['Claude: מהם פרויקטים', 'https://support.claude.com/en/articles/9517075-what-are-projects'], ['יצירה וניהול', 'https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects']]) + '</div>' +
        '<div id="tool-chatgpt" class="stack" hidden>' + steps(['יוצרים פרויקט חדש (דורש התחברות).', 'שלוש הנקודות ← Project settings ← מדביקים את קובץ 01 כהנחיות.', 'מעלים את קבצים 02 עד 07 לאזור הקבצים של הפרויקט (התווית המדויקת עשויה להשתנות).', 'פותחים שיחה בתוך הפרויקט.']) +
          '<div class="fact">' + tag('ok') + '<span>פרויקטים זמינים בכל סוגי החשבון. מספר הקבצים תלוי בחשבון.</span></div><div class="fact">' + tag('ok') + '<span>שיתוף: Business, Enterprise ו־Edu.</span></div><div class="fact">' + tag('chk') + '<span>תווית כפתור הקבצים ומגבלות מדויקות: בדקו בכלי.</span></div>' +
          src([['OpenAI: Projects in ChatGPT', 'https://help.openai.com/en/articles/10169521-projects-in-chatgpt']]) + '</div></section>' +
      '<section class="card stack" data-rv aria-labelledby="kt-h"><div class="row between"><h2 id="kt-h" style="font-size:1.5rem">ערכת שבעת הקבצים</h2><button class="btn primary sm" type="button" data-dl="' + TS.library.zips.kit + '" data-name="project-kit.zip">' + icon('download') + 'הורדת ZIP</button></div>' +
        table(['קובץ', 'מה זה', 'לאן', ''], kit.slice(1).map(function (f, i) { return ['<code>' + esc(f[0]) + '</code>', esc(f[2]), i === 0 ? 'שדה ההנחיות' : 'קובץ בפרויקט', '<button class="btn sm" type="button" data-dl="downloads/project-kit/' + f[0] + '" data-name="' + f[0] + '" aria-label="הורדת ' + esc(f[0]) + '">' + icon('download') + '</button>']; })) + '</section>' +
      '<div class="callout warn" data-rv>' + icon('warn') + '<p><b>אל תבטיחו הפעלה אוטומטית.</b> קובץ בשם מסוים אינו ״מופעל״ אוטומטית בכל מוצר. הפרויקט משתמש בקבצים כחומר רקע, ולכן ההנחיות בקובץ 01 מפנות אליהם בשמם.</p></div>' +
      acc('שש פעולות לתחזוקה', steps([['פותחים פרויקט', 'שם ברור, למשל ״חשבון ד׳״.'], ['הנחיות קבועות', 'קובץ 01, מותאם: מי אתם, איך לעבוד, מה אסור.'], ['מקורות מורשים', 'רק מה שמותר לשכפל.'], ['דוגמת תוצר טוב', 'ה־AI לומד ממנה את הסגנון.'], ['שיחה לכל משימה', 'שיחות אינן משתפות הקשר זו עם זו, אלא דרך ההנחיות והקבצים.'], ['עדכון שבועי', 'שורה ביומן החלטות, ושיטה שהוכיחה את עצמה בידע.']])) +
      acc('למתקדמים: צ׳אט רגיל מול Claude Code או Codex', table(['', 'צ׳אט', 'כלי סוכן עם קבצים'], [
        ['עובד על', 'טקסט וקבצים בשיחה', 'תיקייה במחשב'],
        ['פעולות', 'מייצר תוכן', 'קורא וכותב קבצים ומריץ פקודות, לפי הרשאות'],
        ['הנחיות קבועות', 'הנחיות פרויקט', 'קובץ הנחיות בתיקייה (למשל CLAUDE.md או AGENTS.md): בדקו בתיעוד'],
        ['סיכון', 'תוכן שגוי', 'גם פעולה שגויה על קבצים'],
        ['למי', 'רוב המורים', 'מי שמנהלת ספריית חומרים גדולה ורוצה אוטומציה']]) + '<p class="muted small">למורה רגילה אין צורך בכלים כאלה.</p>');
    return {
      title: 'פרויקטים וקובצי ידע', html: page('projects', 'פרויקטים וקובצי ידע', 'מסגרת קבועה של הנחיות וקבצים, ושיחה נפרדת לכל משימה.', body),
      after: function (root) {
        $('#seg-tool', root).addEventListener('click', function (e) {
          var b = e.target.closest('[data-t]'); if (!b) return;
          $$('#seg-tool [data-t]', root).forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
          $('#tool-claude', root).hidden = b.getAttribute('data-t') !== 'claude'; $('#tool-chatgpt', root).hidden = b.getAttribute('data-t') !== 'chatgpt';
        });
      }
    };
  }

  /* ---------------- HTML ---------------- */
  var HTML_BRIEF = 'הכן לי [דף עבודה / הזמנה / מסמך] כקובץ HTML יחיד ושלם בעברית (lang="he" dir="rtl").\nתוכן: [הדביקו או תארו]. קהל: [ ]. סגנון: [צבע מותג, גופן, לוגו אם מצורף].\nדרישות: צבעים, גופנים וגודל כתב כמשתני CSS ב־:root. כללי @media print עם @page A4 ושוליים.\nבלי שבירת עמוד באמצע שאלה או טבלה. בלי קבצים חיצוניים. אל תייצא ל־PDF, אבדוק בדפדפן.\nבסבב הראשון: מבנה ותוכן בלבד. בסבבים הבאים אבקש שינויים ממוקדים.';
  var PRINT_CSS = '@page { size: A4; margin: 12mm; }\nhtml { direction: rtl; }\n.question, table { break-inside: avoid; }\n* { -webkit-print-color-adjust: economy; print-color-adjust: economy; }';

  function html() {
    var body =
      '<div class="callout" data-rv>' + icon('info') + '<p><b>המשל.</b> מסמך שבנוי כ־HTML הוא כיתה שאפשר להזיז בה שולחנות ולהחליף שלטים. PDF או JPG הם צילום של הכיתה. מצלמים רק כשמרוצים מהסידור, ושומרים את הכיתה עצמה למקרה שתרצו לשנות.</p></div>' +
      '<section class="card stack" data-rv aria-labelledby="hd-h"><h2 id="hd-h" style="font-size:1.5rem">נסו: שינוי ממוקד</h2><p class="muted">זה HTML אמיתי. כל כפתור מדמה בקשה אחת: משתנה אחד משתנה, והשאר נשאר.</p>' +
        '<div class="html-demo"><div class="toolbar no-print" id="demo-bar">' +
          '<button class="btn sm" type="button" data-d="size">הגדל כתב</button><button class="btn sm" type="button" data-d="color">שנה צבע כותרות</button><button class="btn sm" type="button" data-d="ans">שורות כתיבה</button><button class="btn sm" type="button" data-d="bw">שחור־לבן</button><button class="btn sm ghost" type="button" data-d="reset">איפוס</button></div>' +
          '<div class="sheet" id="sheet"><h4>דף עבודה: זכר ונקבה</h4><div class="q"><b>1.</b> השלימו: הילד גדול, והילדה ______.<div class="ans"></div></div><div class="q"><b>2.</b> חברו כל שם עצם לשם התואר המתאים.<div class="ans"></div></div><div class="q"><b>3.</b> כתבו משפט עם שם עצם ברבים.<div class="ans"></div></div></div>' +
          '<div class="xp-note" id="demo-note" aria-live="polite">לחצו על כפתור כדי לראות איזו בקשה הייתם שולחים ל־AI.</div></div></section>' +
      '<section class="card stack" data-rv aria-labelledby="hb-h"><h2 id="hb-h" style="font-size:1.5rem">בקשה להעתקה</h2>' + code('html-brief', 'בקשת HTML', HTML_BRIEF) + '</section>' +
      acc('ששת השלבים', steps(['מגדירים תוכן, קהל ושפה עיצובית: מה כתוב, למי, באיזה צבע וגופן.', 'מבקשים HTML עם מבנה מסודר ועיצוב שאפשר לשנות (משתני CSS).', 'מבקשים שינויים ממוקדים: אחד בכל פעם.', 'בודקים קריאות, דיוק והדפסה.', 'מאשרים ומייצאים.', 'שומרים גם את קובץ המקור לעריכה בעתיד.']), false, '6') +
      acc('כללי הדפסה בסיסיים (CSS)', code('print-css', 'CSS להדפסה', PRINT_CSS, true)) +
      acc('ייצוא: מה אפשר ומה לא', table(['פורמט', 'איך', 'מגבלה'], [
        ['PDF', 'הדפסה מהדפדפן ושמירה כ־PDF', 'לבדוק חלוקת עמודים בתצוגה המקדימה'],
        ['JPG או PNG', 'צילום מסך או כלי ייצוא', 'זה צילום: אי אפשר לערוך אחר כך'],
        ['Word', 'HTML פשוט ותואם, או בקשה ליצירת DOCX', 'Word אינו משמר תמיד עיצוב HTML מורכב'],
        ['RTF', 'רק כקובץ RTF תקין', 'לבקש במפורש ולפתוח לבדיקה'],
        ['MP4', 'רינדור או הקלטת מסך', 'אנימציית HTML אינה קובץ וידאו']]) + '<p class="muted small">מקור מובנה מקל על שינוי ממוקד, אבל אינו מבטיח חיסכון בטוקנים בכל מצב.</p>') +
      acc('כלים זמינים כיום', '<div class="fact">' + tag('ok') + '<span>Claude יוצר קבצי PowerPoint, Word, Excel ו־PDF כשהאפשרות ״יצירת קבצים״ מופעלת.</span></div><div class="fact">' + tag('ok') + '<span>Gemini Canvas בונה חידונים, מדריכי לימוד, צירי זמן ואבות טיפוס אינטראקטיביים.</span></div><div class="fact">' + tag('chk') + '<span>הצגת HTML בחלון צד (Artifacts ב־Claude, Canvas ב־ChatGPT): זמינות ותנאים לפי חשבון.</span></div><div class="fact">' + tag('sec') + '<span>Canva מציע תבניות ועיצוב משולב; גרסת Education חינמית דווחה למורים מאומתים.</span></div><p><a href="#tools" data-route="tools">למדריך הכלים</a></p>');
    return {
      title: 'עיצוב דרך HTML', html: page('html', 'עיצוב ויצוא דרך HTML', 'מבקשים תוצר כ־HTML, משפרים בסבבים, ורק כשמרוצים מייצאים.', body),
      after: function (root) {
        var sheet = $('#sheet', root), note = $('#demo-note', root);
        var colors = ['#2D4BFF', '#2B7A4B', '#8A5600', '#7A1F5C'], ci = 0, sizes = [1, 1.18, 1.36], si = 0;
        var asks = {
          size: 'בקשה: ״הגדל את הכתב בדף ב־18 אחוז, בלי לשנות את הסידור״. מה השתנה: משתנה אחד (--d-size).',
          color: 'בקשה: ״שנה את צבע הכותרות והקו שמתחתן לצבע מותג, בלי לגעת בשאר״. מה השתנה: משתנה אחד (--d-accent).',
          ans: 'בקשה: ״הסר את שורות הכתיבה מתחת לכל שאלה, ושמור גרסה עם השורות״. מה השתנה: תצוגה של רכיב אחד.',
          bw: 'בקשה: ״הוסף גרסה חסכונית להדפסה: שחור־לבן, בלי צבע״. מה השתנה: גרסה נוספת, אותו תוכן.',
          reset: 'חזרה למצב ההתחלה. בעבודה אמיתית אפשר לבקש ״חזור לגרסה הקודמת״.' };
        $('#demo-bar', root).addEventListener('click', function (e) {
          var b = e.target.closest('[data-d]'); if (!b) return; var k = b.getAttribute('data-d');
          if (k === 'size') { si = (si + 1) % sizes.length; sheet.style.setProperty('--d-size', sizes[si] + 'rem'); }
          if (k === 'color') { ci = (ci + 1) % colors.length; sheet.style.setProperty('--d-accent', colors[ci]); }
          if (k === 'ans') sheet.classList.toggle('noans');
          if (k === 'bw') sheet.classList.toggle('bw');
          if (k === 'reset') { sheet.removeAttribute('style'); sheet.className = 'sheet'; si = 0; ci = 0; }
          note.textContent = asks[k];
        });
      }
    };
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
      '<div class="cols" data-rv><div class="card flat"><h3 style="font-size:1.15rem">הדגמה מקומית</h3><p class="muted">מורה אחד מנסה חידון ורואה סיכום. הנתונים נשארים במכשיר ואינם נשמרים. ללמוד, לא ללמד כיתה.</p></div><div class="card flat"><h3 style="font-size:1.15rem">איסוף אמיתי</h3><p class="muted">תשובות מכמה מכשירים דורשות כלי טפסים כמו Google Forms. דף בלי שרת אינו יכול לאסוף ביניהם, ו־localStorage אינו מערכת כיתתית.</p></div></div>' +
      '<section class="card stack" data-rv aria-labelledby="qz-h"><h2 id="qz-h" style="font-size:1.5rem">הדגמה: חידון קצר וסיכום</h2><p class="muted small">הסיכום בסוף מבוסס רק על התשובות שתזינו עכשיו, בלי שמות ובלי שמירה.</p>' +
        '<div id="quiz">' + QUIZ.map(function (q, i) {
          return '<div class="quiz-q" data-i="' + i + '"><b>' + (i + 1) + '. ' + esc(q.q) + '</b><div class="opts">' + q.o.map(function (o, j) { return '<button type="button" class="opt" data-j="' + j + '">' + esc(o) + '</button>'; }).join('') + '</div><div class="fb" role="status"></div></div>';
        }).join('') + '</div><div class="row"><button class="btn primary" type="button" id="quiz-sum" disabled>הצגת סיכום למורה</button><button class="btn ghost" type="button" id="quiz-reset">התחלה מחדש</button></div><div id="quiz-out" class="stack" aria-live="polite"></div></section>' +
      '<section class="card stack" data-rv aria-labelledby="ap-h"><h2 id="ap-h" style="font-size:1.5rem">איסוף אמיתי: Google Forms</h2>' + steps(APPS_STEPS) +
        '<div class="row"><button class="btn primary" type="button" data-dl="downloads/guides/build-quiz.gs" data-name="build-quiz.gs">' + icon('download') + 'build-quiz.gs</button><button class="btn" type="button" data-view="downloads/guides/build-quiz.gs" data-name="build-quiz.gs">צפייה</button><button class="btn" type="button" data-dl="downloads/guides/summarize-responses.gs" data-name="summarize-responses.gs">' + icon('download') + 'summarize-responses.gs</button><button class="btn" type="button" data-dl="downloads/guides/sample-quiz.json" data-name="sample-quiz.json">' + icon('download') + 'דוגמת JSON</button></div>' +
        '<div class="callout">' + icon('info') + '<p>הסקריפטים נבדקו בבדיקת תחביר ובהרצה מול הדמיה של ממשקי Google. הרצה אמיתית מול Google Forms לא נבדקה. הריצו קודם על טופס ניסיון.</p></div>' +
        src([['Google: יצירה וציון חידונים ב־Forms', 'https://support.google.com/docs/answer/7032287?hl=en']]) + '</section>' +
      acc('איך קוראים תוצאות', '<ul class="plain"><li><b>מה ללמד מחדש:</b> נושא שבו רוב המשיבים טעו, ובעיקר באותה טעות.</li><li><b>מי זקוק לתמיכה:</b> לפי קודים שקבעתם, כקבוצה זמנית ולא כתווית.</li><li><b>מי מוכן להעמקה:</b> מי שענה נכון על הכול ומסוגל להסביר מדוע.</li></ul><p class="muted small">אל תזינו ל־AI שמות או נתונים מזהים. השתמשו בקודים ובסיכום מצטבר.</p>');
    return {
      title: 'הערכה דיגיטלית', html: page('assess', 'הערכה דיגיטלית ותובנות למורה', 'מבדק קצר, משוב ברור, וסיכום שעוזר להחליט מה ללמד הלאה.', body),
      after: function (root) {
        var ans = {};
        function reset() {
          ans = {}; $('#quiz-out', root).innerHTML = ''; $('#quiz-sum', root).disabled = true;
          $$('.quiz-q', root).forEach(function (el) { $$('.opt', el).forEach(function (o) { o.disabled = false; o.classList.remove('right', 'wrong'); }); $('.fb', el).textContent = ''; });
        }
        $('#quiz', root).addEventListener('click', function (e) {
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
          QUIZ.forEach(function (q, i) { var t = topics[q.topic] = topics[q.topic] || { r: 0, n: 0 }; t.n++; if (ans[i] === q.c) t.r++; });
          $('#quiz-out', root).innerHTML = '<div class="rise stack"><h3 style="font-size:1.15rem">סיכום למורה (הדגמה, לפי ההזנה שלכם)</h3>' + table(['נושא', 'נכון', 'המלצה'], Object.keys(topics).map(function (k) {
            var t = topics[k]; return [esc(k), t.r + ' מתוך ' + t.n, esc(t.r === t.n ? 'מוכנים להעמקה: שאלת העברה או הסבר ״מדוע״' : t.r === 0 ? 'ללמד מחדש בהסבר אחר' : 'חיזוק קצר, ובדיקה אילו טעויות חוזרות')];
          })) + '<p class="small muted">בכיתה אמיתית כל שורה מייצגת הרבה משיבים. כאן ' + QUIZ.length + ' תשובות שלכם בלבד.</p></div>';
        });
        $('#quiz-reset', root).addEventListener('click', reset);
      }
    };
  }

  /* ---------------- Skills ---------------- */
  var SKILL_EX = '---\nname: "my-lesson-skill"\ndescription: "מכין מערך שיעור קצר בעברית. להפעלה כשמבקשים תכנון שיעור."\n---\n\n# מערך שיעור\n\n## מתי להפעיל\nכשהמורה מבקשת לתכנן שיעור.\n\n## שלבי עבודה\n1. לנסח מטרות נצפות.\n2. לתכנן הוראה בצעדים קטנים.\n3. לבדוק הבנה בסוף.\n\n## כללים\n- עברית תקנית. לא להמציא עובדות.';

  function skills() {
    var L = TS.library;
    var body =
      '<div class="callout" data-rv>' + icon('info') + '<p><b>Skill הוא קלסר שיטות עבודה שנפתח בזמן הנכון:</b> חבילה של הוראות (ולפעמים קבצים וסקריפטים) שהמערכת טוענת כשהבקשה מתאימה. ב־Claude זה קיים; בכלים אחרים יש מקבילות חלקיות, כמו GPT מותאם או Gem.</p></div>' +
      '<section class="card stack" data-rv aria-labelledby="sk-h"><div class="row between"><h2 id="sk-h" style="font-size:1.5rem">Skills של הסטודיו</h2><a class="btn primary sm" href="#library" data-route="library">להורדה בספרייה ' + icon('arrow-left') + '</a></div><ul class="plain">' +
        L.skills.map(function (s) { return '<li><b>' + esc(s.title) + '</b> (<code>' + esc(s.id) + '</code>): ' + esc(s.desc) + '</li>'; }).join('') + '</ul></section>' +
      '<section class="card stack" data-rv aria-labelledby="up-h"><h2 id="up-h" style="font-size:1.5rem">איפה מעלים (Claude)</h2>' + steps(['Settings ← Capabilities: מוודאים שהאפשרות Code execution and file creation פעילה (בהגדרות החדשות: Create and edit files).', 'Customize ← Skills.', '״+״ ← Create skill ← Upload a skill.', 'בוחרים קובץ ZIP שבתוכו תיקיית ה־Skill (לא הקבצים ישירות בשורש).', 'ה־Skill מופיע ברשימה ואפשר להפעיל או לכבות.']) +
        '<div class="fact">' + tag('ok') + '<span>Skills זמינים בחשבונות Free, Pro, Max, Team ו־Enterprise, ודורשים הפעלת code execution.</span></div>' +
        '<div class="callout warn">' + icon('warn') + '<p><b>אבטחה.</b> התקינו Skills רק ממקורות מהימנים וקראו אותם לפני הפעלה, במיוחד סקריפטים והוראות להתחבר למקורות חיצוניים. הסיכונים העיקריים: prompt injection ודליפת מידע.</p></div>' +
        src([['Claude: שימוש ב־Skills', 'https://support.claude.com/en/articles/12512180-using-skills-in-claude'], ['מאגר Skills של Anthropic', 'https://github.com/anthropics/skills']]) + '</section>' +
      acc('איך נראה Skill', '<p class="muted">תיקייה בשם ה־Skill ובה קובץ <code>SKILL.md</code> עם <code>name</code> (אותיות לטיניות קטנות ומקפים) ו־<code>description</code> (מה הוא עושה ומתי להפעיל).</p>' + code('skill-ex', 'דוגמה: SKILL.md', SKILL_EX, true)) +
      acc('משאבים קיימים של אחרים', '<p class="muted">בדקו רישיון והתאמה לישראל.</p>' + table(['מקור', 'מה יש', 'רישיון והערות'], [
        ['<a href="https://github.com/anthropics/k12-teacher-skills" target="_blank" rel="noopener">anthropics/k12-teacher-skills</a>', 'תכנון שיעור, דיפרנציאציה, הכנה לשיעור, בדיקת הבנה במתמטיקה', 'Apache 2.0. מבוסס על סטנדרטים אמריקאיים ומחבר Learning Commons'],
        ['<a href="https://github.com/polytheseus/teacher-skills" target="_blank" rel="noopener">polytheseus/teacher-skills</a>', 'הודעות להורים, מחוונים, מחוללי חידונים ועוד', 'MIT. סביבה בריטית באנגלית. חלק בתשלום. מתוחזק על ידי אדם אחד, בלי כוכבים או גרסאות']])) +
      acc('סוכנים ו־Hooks: מה למורה', table(['מושג', 'מתי זה שימושי', 'האם צריך'], [
        ['סוכן', 'משימה גדולה שאפשר לפצל, כמו איסוף חומרים וסיכומם', 'לרוב לא. יש עלות תיאום, והוא אינו חוסך תמיד זמן או טוקנים'],
        ['Hook', 'פעולה אוטומטית בעקבות אירוע, למשל בדיקה אחרי שמירת קובץ', 'לא למורה רגילה. קיים בעיקר בכלי פיתוח, והתמיכה תלויה בכלי']]) + '<p class="muted small">תמיכה ב־Skills וב־Hooks תלויה בכלי. בדקו בתיעוד לפני שמתכננים עבודה סביבם. <a href="#story" data-route="story">למושגים בסיפור</a></p>');
    return { title: 'Skills וסוכנים', html: page('skills', 'Skills, סוכנים ו־Hooks', 'שיטות עבודה שנשמרות וחוזרות, ומה מהן באמת מתאים למורה.', body) };
  }

  /* ---------------- פרטיות ---------------- */
  function privacy() {
    var body =
      '<div class="callout warn" data-rv>' + icon('lock') + '<p><b>הכלל הראשון.</b> אין להזין לכלי AI מידע אישי, רגיש או מזהה על עצמכם, על תלמידים או על חברי צוות. מידע מוגן נשמר רק במערכות משרד החינוך ובשירותים מאושרים.</p></div>' +
      '<section class="card stack" data-rv aria-labelledby="pv-h"><h2 id="pv-h" style="font-size:1.5rem">בדיקת טקסט לפני הדבקה</h2><p class="muted">הבדיקה מתבצעת במכשיר שלכם ואינה נשלחת לשום מקום. היא מזהה מספר זהות, טלפון ודוא״ל, אבל לא שמות: קראו גם בעצמכם.</p>' +
        '<div class="field"><label for="pv-text">טקסט לבדיקה</label><textarea id="pv-text" rows="5" placeholder="הדביקו כאן"></textarea></div><div id="pv-out" class="callout ok" role="status">' + icon('check') + '<p>הדביקו טקסט כדי לבדוק.</p></div></section>' +
      acc('מה מותר לתלמידים, לפי כיתה', table(['כיתות', 'מה מוגדר'], [['א׳–ג׳', 'אין אישור שימוש לתלמידים. שימוש לצוות ההוראה בלבד, להכנת תוכן וניהול למידה'], ['ד׳', 'התנסות רק דרך בוט משרד החינוך המוגן, ולא בכלים חיצוניים'], ['ה׳–ז׳', 'המורה מפעילה את הכלי, התלמידים משתתפים במליאה, בלי שימוש עצמאי'], ['ח׳ ומעלה', 'שימוש עצמאי בכלי בינה יוצרת מרשימת הכלים המאושרים']]) + '<p class="small muted">מקור: עמוד הכלים הבין־לאומיים במרחב הפדגוגי. אישורי הכלים משתנים, ויש לבדוק בקטלוג העדכני.</p>', true) +
      acc('כללי עבודה מומלצים', '<ul class="plain"><li>הירשמו לכלי AI בדוא״ל נפרד שאינו כולל את שמכם.</li><li>השתמשו בדפדפן ייעודי, והימנעו מגלישה לאתרים רגישים כמו הבנק במקביל.</li><li>היזהרו מאתרים מתחזים שגובים כסף על שירות שמוצע בחינם. בדקו את כתובת האתר.</li><li>אל תאפשרו לתלמידים לעבוד על מחשבים ברשת המנהלתית.</li><li>אל תזינו מספרי כרטיס אשראי או תעודת זהות בדפדפן.</li></ul>') +
      acc('אם נחשף מידע מוגן', steps(['מבטלים מיד את הפעולה (הרשאה לענן, שליחת דוא״ל).', 'מיידעים בהקדם את מנהל בית הספר.', 'המנהל מיידע את משרד החינוך: school_security@education.gov.il']) +
        '<p><b>מוקד בינה מלאכותית של המשרד:</b> <span dir="ltr">*6552</span> (עברית 1). לצוותי הוראה: 1 ואז 6. א׳–ה׳ 07:30–17:00, ו׳ 07:30–13:00.</p>') +
      acc('אחריות מקצועית', '<p class="prose">ה־AI יכול לטעות, להטות ולהמציא. משרד החינוך מדגיש עקרון של אדם בתוך התהליך: אתם בודקים, מתאימים ומחליטים. לכל מסלול בסטודיו יש רשימת בדיקה. ההחלטות על תלמידים נשארות בידי בני אדם.</p>' +
        src([['שאלות ותשובות על AI לצוות החינוך', 'https://pop.education.gov.il/teaching-tools/ai-education/questions-answers/'], ['כלים בין־לאומיים וכלי AI', 'https://pop.education.gov.il/sherutey-tiksuv-bachinuch/international-digital-ai-tools/'], ['מובילים AI בחינוך', 'https://pop.education.gov.il/teaching-tools/ai-education/']]) + '<p class="small muted">נבדק ב־' + TS.meta.checkedOn + '. המסמכים הרשמיים של המשרד הם המחייבים.</p>');
    return {
      title: 'פרטיות ואחריות', html: page('privacy', 'פרטיות ואחריות', 'מה להזין ומה לא, מה מותר לתלמידים, ומה עושים אם משהו השתבש.', body),
      after: function (root) {
        $('#pv-text', root).addEventListener('input', function () {
          var r = TS.privacyScan(this.value), out = $('#pv-out', root);
          out.className = 'callout ' + (r.length ? 'warn' : 'ok');
          out.innerHTML = r.length ? icon('warn') + '<p>' + esc(r.join(' ')) + ' מחקו או החליפו בקוד לפני ההדבקה.</p>' : icon('check') + '<p>לא זוהה מספר זהות, טלפון או דוא״ל. עדיין, קראו בעצמכם ובדקו שאין שמות.</p>';
        });
      }
    };
  }

  TS.views.advanced = function (param) {
    if (param === 'projects') return projects();
    if (param === 'html') return html();
    if (param === 'assess') return assess();
    if (param === 'skills') return skills();
    if (param === 'privacy') return privacy();
    return {
      title: 'העמקה',
      html: head('העמקה למתקדמים', 'לא נדרש כדי להתחיל. למי שרוצה להתקדם משיחה פשוטה לפרויקטים, ידע מותאם ו־Skills.') +
        '<div class="wrap" style="padding-bottom:60px"><div class="bento">' + TABS.map(function (t, i) {
          return '<a class="tile spot' + (i === 0 ? ' hl' : '') + '" style="grid-column: span ' + (i < 2 ? 3 : 2) + '" href="#adv-' + t[0] + '" data-route="adv-' + t[0] + '" data-rv="' + (i % 3) + '"><span class="ic">' + icon(t[2]) + '</span><span class="go">' + icon('arrow-left') + '</span><div><h3>' + esc(t[1]) + '</h3><p>' + esc(t[3]) + '</p></div></a>';
        }).join('') + '</div></div>'
    };
  };

})(window.TS = window.TS || {});
