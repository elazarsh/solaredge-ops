/* מנוע ההנחיות: בונה פרומפט ייחודי לכל משימה מתוך הנתונים שהמורה הזינה */
(function (TS) {
  'use strict';
  var E = TS.engine = {};

  E.byId = function (id) {
    for (var i = 0; i < TS.tasks.length; i++) if (TS.tasks[i].id === id) return TS.tasks[i];
    return null;
  };

  /* כל השדות של משימה, בסדר הצגה: משותפים ואז ייחודיים */
  E.fieldDefs = function (task) {
    var out = [];
    (task.common || []).forEach(function (id) {
      var f = TS.fields[id];
      if (f) out.push(Object.assign({ id: id, kind: 'common' }, f));
    });
    (task.extra || []).forEach(function (f) { out.push(Object.assign({ kind: 'extra' }, f)); });
    return out;
  };

  function defOf(task, id) {
    var d = E.fieldDefs(task);
    for (var i = 0; i < d.length; i++) if (d[i].id === id) return d[i];
    return { id: id, label: id, type: 'text' };
  }

  E.newState = function (task) {
    return {
      values: {},
      methods: (task.methodsDefault || []).slice(),
      adapt: [],
      applyTo: [],
      style: task.styleOptions ? task.styleOptions[0].id : '',
      format: 'balanced',
      printExtra: false,
      brand: [],
      html: !!task.printable,
      mode: 'ready'
    };
  };

  E.exampleState = function (task) {
    var ex = task.example || {};
    var s = E.newState(task);
    s.values = Object.assign({}, ex.values || {});
    if (ex.methods) s.methods = ex.methods.slice();
    if (ex.adapt) s.adapt = ex.adapt.slice();
    if (ex.applyTo) s.applyTo = ex.applyTo.slice();
    if (ex.style) s.style = ex.style;
    return s;
  };

  function v(state, id) { return String((state.values && state.values[id]) || '').trim(); }

  E.missing = function (task, state) {
    var miss = [];
    (task.required || []).forEach(function (id) {
      if (!v(state, id)) miss.push(defOf(task, id).label);
    });
    return miss;
  };

  /* מחליף {שדה} בערך. שדה ארוך מקבל הפניה לסעיף ייעודי. שדה ריק מקבל מצייין מקום. */
  function fill(task, state, str) {
    return String(str).replace(/\{([a-zA-Z]+)\}/g, function (m, id) {
      var d = defOf(task, id);
      var val = v(state, id);
      if (!val) return '[' + d.label + ']';
      if (d.type === 'textarea' && (val.indexOf('\n') > -1 || val.length > 60)) return 'המידע בסעיף ״' + d.label + '״';
      return val;
    });
  }

  function numbered(arr) { return arr.map(function (x, i) { return (i + 1) + '. ' + x; }); }
  function bullets(arr) { return arr.map(function (x) { return '- ' + x; }); }
  function find(list, id) { for (var i = 0; i < list.length; i++) if (list[i].id === id) return list[i]; return null; }

  E.build = function (task, state) {
    var L = [];
    var common = task.common || [];
    function sec(title) { L.push(''); L.push('## ' + title); }

    L.push(task.role);

    /* הקשר */
    sec('הקשר');
    L.push('- סוג בית הספר: יסודי ממלכתי־דתי (חמ״ד) לבנים');
    ['grade', 'subject', 'topic', 'duration', 'prior', 'constraints'].forEach(function (id) {
      if (common.indexOf(id) === -1) return;
      var d = TS.fields[id];
      var val = v(state, id);
      if (!val && (task.required || []).indexOf(id) === -1) return;
      L.push('- ' + d.label + ': ' + (val || '[' + d.label + ']'));
    });
    (task.extra || []).forEach(function (f) {
      if (f.type === 'textarea') return;
      var val = v(state, f.id);
      if (!val && (task.required || []).indexOf(f.id) === -1) return;
      L.push('- ' + f.label + ': ' + (val || '[' + f.label + ']'));
    });

    /* מקור */
    if (common.indexOf('source') > -1) {
      sec('מקור');
      var src = v(state, 'source');
      if (src) {
        L.push('להלן החומר שאעבוד איתו. הסתמך עליו לכל עובדה, ואם מוסיפים משהו מחוץ למקור, סמן אותו ״מחוץ למקור״.');
        L.push('"""');
        L.push(src);
        L.push('"""');
      } else {
        L.push('לא צירפתי מקור. אל תמציא ציטוטים או פרטים מדויקים (תאריכים, מספרים, נוסחים). אם נדרש מקור, שאל או סמן [לבדוק].');
      }
    }

    /* שדות ארוכים שהוזנו, כל אחד בסעיף משלו */
    (task.extra || []).forEach(function (f) {
      if (f.type !== 'textarea') return;
      var val = v(state, f.id);
      sec(f.label);
      L.push(val ? val : '[' + f.label + ']');
    });

    /* מטרות */
    var goalLines = [];
    if (common.indexOf('goal') > -1) {
      var gv = v(state, 'goal');
      if (gv || (task.required || []).indexOf('goal') > -1) goalLines.push(gv || '[' + TS.fields.goal.label + ']');
    }
    (task.goalsExtra || []).forEach(function (g) { goalLines.push(g); });
    sec(common.indexOf('goal') > -1 && v(state, 'goal') ? 'מטרות' : 'מטרות התוצר');
    L = L.concat(bullets(goalLines.map(function (x) { return fill(task, state, x); })));

    /* שלבי עבודה */
    sec('שלבי עבודה');
    L = L.concat(numbered((task.process || []).map(function (x) { return fill(task, state, x); })));

    /* מבנה התוצר */
    sec('מבנה התוצר');
    L = L.concat(bullets((task.structure || []).map(function (x) { return fill(task, state, x); })));

    /* שיטות הוראה או אופי */
    if (task.step2 === 'pedagogy' && task.showMethods !== false) {
      sec('שיטות הוראה');
      var ms = (state.methods || []).map(function (id) { return find(TS.methods, id); }).filter(Boolean);
      if (ms.length) {
        L = L.concat(bullets(ms.map(function (m) { return m.prompt; })));
      } else {
        L.push('- לבחור בעצמך שתי דרכי ייצוג שונות לפחות לרעיון המרכזי, בהתאם לתוכן, בלי להסתמך על ״טיפוסי למידה״.');
      }
    } else if (task.step2 === 'style') {
      var so = find(task.styleOptions || [], state.style);
      sec(task.styleLabel || 'אופי');
      L.push('- ' + (so ? so.prompt : '[' + (task.styleLabel || 'אופי') + ']'));
    }

    /* התאמות */
    var ad = (state.adapt || []).map(function (id) { return find(TS.adaptations, id); }).filter(Boolean);
    if (ad.length) {
      sec('התאמות');
      L.push('התאמות מבוקשות (תמיכה מעשית כללית, בלי אבחון ובלי להתייחס לתלמיד מסוים):');
      L = L.concat(bullets(ad.map(function (a) { return a.label + ': ' + a.support; })));
      var applies = (state.applyTo || []).map(function (id) { return find(TS.applyTo, id); }).filter(Boolean);
      L.push('החל את ההתאמות על: ' + (applies.length ? applies.map(function (a) { return a.label; }).join(', ') : 'כל החומר שנוצר') + '.');
      L.push('שמירה על המיומנות הנמדדת:');
      L = L.concat(bullets(ad.map(function (a) { return a.guard; })));
      if ((state.applyTo || []).indexOf('test') > -1) {
        L.push('במבחן: התאמות נעשות בהגשה ובתמיכה, בלי לשנות את המיומנות שהמבחן אמור למדוד. התאמות פורמליות בבחינות כפופות להנחיות בית הספר.');
      }
    }

    /* דגשים ייחודיים */
    if (task.specifics) {
      sec(task.specifics.title);
      L = L.concat(bullets(task.specifics.lines.map(function (x) { return fill(task, state, x); })));
    }

    /* עיצוב ופורמט */
    sec('עיצוב ופורמט');
    var fm = find(TS.formats, state.format) || TS.formats[1];
    L.push('- ' + fm.prompt);
    if (state.printExtra) L.push('- להוסיף בסוף גם גרסת הדפסה חסכונית: שחור־לבן, בלי רקעים, אותו תוכן.');
    if (state.html) {
      L.push('- להפיק את התוצר כקובץ HTML יחיד ושלם בעברית (lang="he" dir="rtl"), בלי קבצים חיצוניים וללא ספריות.');
      L.push('- להגדיר צבעים, גופנים וגודל כתב כמשתני CSS בראש הקובץ, כדי שיהיה קל לבקש שינויים.');
      if (task.printable) L.push('- להוסיף כללי @media print: @page בגודל A4 עם שוליים, בלי שבירת עמוד באמצע שאלה או טבלה, ושמירה על קריאות בשחור־לבן.');
      L.push('- לא לייצא ל־PDF או לתמונה בשלב זה. אבדוק בדפדפן ואבקש שינויים ממוקדים בכל סבב.');
    }
    var br = (state.brand || []).map(function (id) { return find(TS.brand, id); }).filter(Boolean);
    if (br.length) {
      L.push('- מצורפים לשיחה: ' + br.map(function (b) { return b.label; }).join(', ') + '. להשתמש בהם בעיצוב כפי שהם. אם הקבצים לא צורפו, לא להמציא לוגו או תמונות ולהשאיר מקום ריק.');
    }

    /* בדיקת איכות */
    sec('בדיקת איכות לפני המסירה');
    L.push('בדוק את התוצר מול הרשימה ותקן מה שחסר לפני שאתה מוסר. אל תציג את הבדיקה אלא אם ביקשתי.');
    L = L.concat(bullets((task.quality || []).map(function (x) { return fill(task, state, x); })));

    /* כללי עבודה */
    sec('כללי עבודה');
    L.push('- כתוב בעברית תקנית וברורה, בכיוון מימין לשמאל.');
    L.push('- אל תמציא עובדות, ציטוטים, מקורות או נתונים. מה שחסר, סמן [להשלים].');
    L.push('- אל תבקש ואל תכלול שמות או פרטים מזהים של תלמידים.');
    L.push('- התוצר הוא טיוטה מקצועית לבדיקה שלי, לא מוצר סופי.');

    /* אופן העבודה */
    sec('אופן העבודה');
    if (state.mode === 'ask') {
      L.push('לפני שאתה מכין את התוצר, שאל אותי עד שלוש שאלות מדויקות בלבד והמתן לתשובות. נושאים שחשוב לברר:');
      L = L.concat(numbered(task.askQs));
      L.push('אחרי שאענה, הכן את התוצר המלא לפי כל ההנחיות שלמעלה.');
    } else {
      L.push('יש לי מספיק פרטים. הכן את התוצר המלא עכשיו. אם חסר פרט שאי אפשר בלעדיו, סמן אותו [להשלים] והמשך.');
    }

    return { text: L.join('\n'), missing: E.missing(task, state) };
  };

  /* קובץ Markdown להורדה: הנחיות, כלי מומלץ, בדיקת איכות והמשך */
  E.markdown = function (task, state, opts) {
    opts = opts || {};
    var built = E.build(task, state);
    var M = [];
    M.push('# ' + task.title + ': הנחיה לכלי AI');
    M.push('');
    M.push('> נוצר ב״' + TS.meta.siteName + '״ · ' + TS.meta.school);
    if (opts.template) M.push('> זו תבנית ריקה. מלאו את מה שבסוגריים מרובעים, או השתמשו בסטודיו כדי למלא אותה.');
    M.push('');
    M.push('## איך משתמשים');
    M.push('1. פתחו שיחה חדשה בכלי ה־AI שבחרתם (ראו ״הכלי המומלץ״ למטה).');
    M.push('2. צרפו קבצים שצריך: לוגו, מקור, דוגמת עיצוב. אם לא תצרפו, ה־AI לא יראה אותם.');
    M.push('3. הדביקו את ההנחיה שבסעיף הבא ושלחו.');
    M.push('4. עברו על התוצר מול רשימת הבדיקה, ובקשו תיקון ממוקד אחד בכל פעם.');
    M.push('');
    M.push('## ההנחיה');
    M.push('');
    M.push('~~~text');
    M.push(built.text);
    M.push('~~~');
    M.push('');
    M.push('## הכלי המומלץ ולמה');
    (task.tools || []).forEach(function (t) {
      var tool = TS.tools[t.id];
      if (tool) M.push('- **' + tool.name + '**: ' + t.why);
    });
    M.push('');
    M.push('## רשימת בדיקת איכות');
    (task.quality || []).forEach(function (q) { M.push('- [ ] ' + fill(task, state, q)); });
    (task.teacherChecks || []).forEach(function (q) { M.push('- [ ] ' + q); });
    M.push('');
    M.push('## מה עושים אחרי שמקבלים תשובה');
    (task.next || []).forEach(function (n) { M.push('- ' + n); });
    M.push('');
    M.push('## אם רוצים שה־AI ידייק לפני שיכין');
    M.push('בהנחיה יש מצב ״עזרו לי לדייק״. שלוש השאלות המרכזיות שלו:');
    (task.askQs || []).forEach(function (q, i) { M.push((i + 1) + '. ' + q); });
    M.push('');
    M.push('## תזכורות');
    M.push('- אל תזינו לכלי AI שמות, מספרי זהות או מידע רגיש על תלמידים, על עצמכם או על הצוות.');
    M.push('- ה־AI יכול לטעות בביטחון. אתם האחראים לתוכן ולדיוק לפני שמעבירים לתלמידים.');
    M.push('- נכון ל־' + TS.meta.checkedOn + '. כלים משתנים: בדקו תנאי שימוש וזמינות באתר הכלי.');
    M.push('');
    return M.join('\n');
  };

  E.template = function (task) { return E.markdown(task, E.newState(task), { template: true }); };

  /* משמש גם לספירת מילים בבדיקות */
  E.wordCount = function (s) { return String(s).split(/\s+/).filter(Boolean).length; };

})(window.TS = window.TS || {});
