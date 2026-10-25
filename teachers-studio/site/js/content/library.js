/* ספריית ההורדות. הקבצים נוצרים בבנייה (build.mjs) מתוך kit/ ומתוך מנוע ההנחיות. */
(function (TS) {
  'use strict';

  var skills = [
    { id: 'hebrew-lesson-planner', title: 'מתכנן שיעור בעברית', desc: 'מערך שיעור יסודי עם מטרות נצפות, חלוקת זמן ובדיקת הבנה.' },
    { id: 'differentiated-materials', title: 'חומר לרמות שונות', desc: 'גרסאות תמיכה, רגיל והעמקה לאותו חומר, בלי לשנות את המטרה.' },
    { id: 'assessment-builder', title: 'בונה מבחנים ומבדקים', desc: 'מיפוי, מסיחים מבוססי טעויות, מחוון ומפתח נפרד.' },
    { id: 'parent-message-writer', title: 'הודעות להורים', desc: 'הודעה קצרה ומכבדת עם פעולה ותאריך, בלי פרטים מזהים.' },
    { id: 'rtl-html-worksheet', title: 'דף עבודה כ־HTML בעברית', desc: 'כללי RTL, משתני CSS והדפסה ל־A4, כולל תבנית HTML לדוגמה.', extra: ['print-template.html'] }
  ];

  var kitFiles = [
    ['00-README.md', 'הוראות הקמה', 'מה בערכה ואיך מעלים ל־Claude ול־ChatGPT.'],
    ['01-project-instructions.md', 'הנחיות לפרויקט', 'הנחיות קבועות שמדביקים בשדה ההנחיות.'],
    ['02-class-profile.md', 'מאפייני הכיתה', 'תיאור קבוצתי של הכיתה, ללא פרטים מזהים.'],
    ['03-pedagogical-principles.md', 'עקרונות פדגוגיים', 'מה זה שיעור טוב אצלכם, כדי שה־AI יתכנן בהתאם.'],
    ['04-design-rules.md', 'כללי עיצוב', 'RTL, צבעים, גופנים והדפסה.'],
    ['05-quality-check.md', 'בדיקת איכות', 'רשימה לפני שמעבירים תוצר לתלמידים.'],
    ['06-accumulated-knowledge.md', 'ידע מקצועי מצטבר', 'מסמך חי של שיטות וניסוחים שהוכיחו את עצמם.'],
    ['07-decision-log.md', 'יומן החלטות', 'החלטות קצרות כדי להמשיך משיחה לשיחה.']
  ];

  var guides = [
    ['guides/prompt-improvement-guide.md', 'שיפור בקשה ועבודה עם מקורות', 'שש שכבות לבקשה טובה, כללי מקורות וביטויי תיקון.', 'md'],
    ['guides/html-design-guide.md', 'עיצוב ויצוא דרך HTML', 'תהליך, בקשה להעתקה, כללי הדפסה וטבלת ייצוא.', 'md'],
    ['guides/digital-assessment-guide.md', 'הערכה דיגיטלית ותובנות', 'ההבדל בין הדגמה מקומית לאיסוף אמיתי, ותהליך עם Google Forms.', 'md'],
    ['guides/build-quiz.gs', 'סקריפט: בניית חידון Google Forms', 'מדביקים ב־Apps Script ומקבלים חידון מתוך JSON.', 'gs'],
    ['guides/summarize-responses.gs', 'סקריפט: סיכום תשובות בלי שמות', 'מסכם אחוזי הצלחה וטעויות נפוצות לפי שאלה.', 'gs'],
    ['guides/sample-quiz.json', 'דוגמת JSON לחידון', 'המבנה שהמסלול ״פעילות הערכה דיגיטלית״ מייצר.', 'json'],
    ['guides/safe-use-checklist.md', 'שימוש בטוח בכלי AI', 'רשימת תזכורת לפי הנחיות משרד החינוך.', 'md'],
    ['guides/tools-cheatsheet.md', 'כלים במבט אחד', 'תמצית כלי ה־AI עם רמת אימות ומקורות.', 'md'],
    ['guides/existing-resources.md', 'משאבים קיימים שמצאנו', 'רשימת חומרים של אחרים, עם רישיון והערות, כדי להבדיל אותם מהתבניות שלנו.', 'md']
  ];

  var external = [
    { title: 'פרקטיקות AI להוראה, ללמידה ולהערכה', by: 'משרד החינוך', url: 'https://pop.education.gov.il/teaching-tools/teaching-practices/artificial-intelligence/', note: 'עשרות פרקטיקות מוכנות, בהן הערכה, כתיבת משוב ובניית מחוון.' },
    { title: 'AI בחינוך היסודי: הנחיות, ערכות ומצגות', by: 'משרד החינוך', url: 'https://pop.education.gov.il/teaching-tools/ai-education/elementary/', note: 'הנחיות לפי שכבת גיל, ערכות לצוות, מצגות לכיתות א׳–ו׳.' },
    { title: 'שאלות ותשובות על AI לצוות החינוך', by: 'משרד החינוך', url: 'https://pop.education.gov.il/teaching-tools/ai-education/questions-answers/', note: 'פרטיות, בחירת כלים ומה לעשות במקרה של חשיפת מידע.' },
    { title: 'k12-teacher-skills', by: 'Anthropic', url: 'https://github.com/anthropics/k12-teacher-skills', note: 'Skills למורים: תכנון שיעור, דיפרנציאציה, הכנה לשיעור ובדיקת הבנה. רישיון Apache 2.0. מבוסס על סטנדרטים אמריקאיים ומחבר Learning Commons, כך שיש להתאים לישראל.' },
    { title: 'anthropics/skills', by: 'Anthropic', url: 'https://github.com/anthropics/skills', note: 'המאגר הציבורי של Skills ושל מפרט ה־Skill. רוב הדוגמאות ברישיון Apache 2.0. Skills של מסמכים הם source-available, לא קוד פתוח.' },
    { title: 'teacher-skills', by: 'polytheseus', url: 'https://github.com/polytheseus/teacher-skills', note: 'Skills למורים, כולל הודעות להורים ומחוונים. רישיון MIT. מכוון לסביבה בריטית באנגלית, חלק מהחבילה בתשלום, ומתוחזק על ידי אדם יחיד. בדקו תוכן לפני שימוש.' },
    { title: 'OpenAI Academy: כתיבת בקשות טובות למורים', by: 'OpenAI', url: 'https://academy.openai.com/public/clubs/k-12-education-aacga/blogs/write-better-prompts-teachers-2026-05-28', note: 'מסגרת של משימה, הקשר ופלט, עם דוגמה לשיעור מדעים.' },
    { title: 'איך מתחילים לעבוד עם ChatGPT: מדריך למחנכים', by: 'OpenAI', url: 'https://help.openai.com/en/articles/8313929-how-can-educators-get-started-with-chatgpt', note: 'כולל הנחיית תכנון שיעור שנכתבה עם אית׳ן ולילך מוליק.' }
  ];

  /* מתכוני ZIP: קבצי ZIP נבנים בדפדפן מהקבצים שפורסמו (בפרסום כ־Artifact אי אפשר לצרף ZIP).
     כל מתכון הוא רשימת [נתיב בתוך ה־ZIP, נתיב קובץ מפורסם]. */
  function recipe(zipPath) {
    var d = 'downloads/', L = TS.library, out = [], root;
    if (zipPath === L.zips.kit) {
      L.kitFiles.forEach(function (f) { out.push(['project-kit/' + f[0], d + 'project-kit/' + f[0]]); });
      return out;
    }
    if (zipPath === L.zips.prompts) {
      TS.tasks.forEach(function (t) { out.push(['prompts/' + t.id + '.md', d + 'prompts/' + t.id + '.md']); });
      return out;
    }
    if (zipPath === L.zips.everything) {
      root = 'teachers-studio-kit/';
      out.push([root + 'README.md', d + 'kit-README.md']);
      L.kitFiles.forEach(function (f) { out.push([root + 'project-kit/' + f[0], d + 'project-kit/' + f[0]]); });
      TS.tasks.forEach(function (t) { out.push([root + 'prompts/' + t.id + '.md', d + 'prompts/' + t.id + '.md']); });
      L.guides.forEach(function (g) { out.push([root + g[0], d + g[0]]); });
      L.skills.forEach(function (s) {
        out.push([root + 'skills/' + s.id + '/SKILL.md', d + 'skills/' + s.id + '/SKILL.md']);
        (s.extra || []).forEach(function (x) { out.push([root + 'skills/' + s.id + '/' + x, d + 'skills/' + s.id + '/' + x]); });
      });
      return out;
    }
    var m = /^downloads\/skills\/([a-z-]+)\.zip$/.exec(zipPath);
    if (m) {
      var s = L.skills.filter(function (x) { return x.id === m[1]; })[0];
      if (!s) return null;
      out.push([s.id + '/SKILL.md', d + 'skills/' + s.id + '/SKILL.md']);
      (s.extra || []).forEach(function (x) { out.push([s.id + '/' + x, d + 'skills/' + s.id + '/' + x]); });
      return out;
    }
    return null;
  }

  TS.library = {
    recipe: recipe,
    skills: skills, kitFiles: kitFiles, guides: guides, external: external,
    zips: {
      kit: 'downloads/project-kit.zip',
      prompts: 'downloads/prompts.zip',
      everything: 'downloads/teachers-studio-kit.zip'
    }
  };

})(window.TS = window.TS || {});
