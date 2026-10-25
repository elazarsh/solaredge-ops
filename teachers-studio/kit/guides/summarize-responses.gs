/**
 * מסכם תשובות של חידון Google Forms לפי שאלה, בלי שמות.
 * הפלט מתאים להדבקה במסלול ״ניתוח תשובות ותוצאות״ בסטודיו.
 *
 * איך משתמשים:
 * 1. פתחו script.google.com ← New project והדביקו את הקובץ.
 * 2. החליפו את FORM_ID במזהה הטופס (החלק שבכתובת העריכה בין /d/ ל־/edit).
 * 3. הריצו summarize ואשרו הרשאות. הסיכום יופיע ב־Execution log.
 *
 * הסקריפט סופר תשובות ואינו קורא או שומר שמות. אם האיסוף כלל אימיילים, הם לא מוצגים.
 */
var FORM_ID = 'הדביקו כאן את מזהה הטופס';

function summarize() {
  var form = FormApp.openById(FORM_ID);
  var responses = form.getResponses();
  var stats = {};

  responses.forEach(function (response) {
    response.getGradableItemResponses().forEach(function (ir) {
      var item = ir.getItem();
      var title = item.getTitle();
      var points = item.asMultipleChoiceItem().getPoints();
      var s = stats[title] = stats[title] || { right: 0, total: 0, wrong: {} };
      s.total++;
      if (ir.getScore() >= points) {
        s.right++;
      } else {
        var answer = String(ir.getResponse());
        s.wrong[answer] = (s.wrong[answer] || 0) + 1;
      }
    });
  });

  var lines = ['מספר משיבים: ' + responses.length, ''];
  Object.keys(stats).forEach(function (title) {
    var s = stats[title];
    var pct = Math.round((s.right / s.total) * 100);
    var wrongList = Object.keys(s.wrong).map(function (a) { return '"' + a + '" (' + s.wrong[a] + ')'; }).join(', ');
    lines.push(title + ': ' + pct + '% ענו נכון' + (wrongList ? '. תשובות שגויות: ' + wrongList : ''));
  });
  Logger.log(lines.join('\n'));
}
