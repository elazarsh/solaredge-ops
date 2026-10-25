/**
 * בונה חידון Google Forms מתוך JSON.
 *
 * איך משתמשים:
 * 1. פתחו script.google.com ← New project, והדביקו את כל הקובץ הזה.
 * 2. החליפו את תוכן QUIZ_JSON בפלט ה־JSON שקיבלתם מכלי ה־AI (ראו sample-quiz.json).
 * 3. הריצו את הפונקציה buildQuiz ואשרו הרשאות (הסקריפט יוצר טופס בדרייב שלכם).
 * 4. בלשונית Execution log תופיע כתובת העריכה וכתובת השיתוף, וגם טבלה של שאלה ← נושא.
 *
 * הסקריפט אינו אוסף שמות או אימיילים. אם בית הספר דורש הזדהות, השתמשו בקוד שקבעתם.
 */
var QUIZ_JSON = '{"title":"בדיקה קצרה","description":"","questions":[{"text":"שאלה לדוגמה?","topic":"נושא","options":["תשובה א","תשובה ב","תשובה ג"],"correct":1,"points":1,"feedbackCorrect":"נכון!","feedbackIncorrect":"נסו לחשוב שוב."}]}';

function buildQuiz() {
  var data = JSON.parse(QUIZ_JSON);
  var form = FormApp.create(data.title || 'חידון');
  form.setIsQuiz(true);
  form.setCollectEmail(false);
  if (data.description) form.setDescription(data.description);

  var topics = [];
  data.questions.forEach(function (q, index) {
    var item = form.addMultipleChoiceItem();
    item.setTitle(q.text);
    item.setRequired(true);
    item.setPoints(q.points || 1);
    var choices = q.options.map(function (text, i) {
      return item.createChoice(text, i === q.correct);
    });
    item.setChoices(choices);
    if (q.feedbackCorrect) {
      item.setFeedbackForCorrect(FormApp.createFeedback().setText(q.feedbackCorrect).build());
    }
    if (q.feedbackIncorrect) {
      item.setFeedbackForIncorrect(FormApp.createFeedback().setText(q.feedbackIncorrect).build());
    }
    topics.push((index + 1) + '. ' + q.text + '  ←  ' + (q.topic || 'ללא נושא'));
  });

  Logger.log('כתובת עריכה: ' + form.getEditUrl());
  Logger.log('כתובת לשיתוף עם התלמידים: ' + form.getPublishedUrl());
  Logger.log('שאלה ← נושא (שמרו לצורך הניתוח):\n' + topics.join('\n'));
}
