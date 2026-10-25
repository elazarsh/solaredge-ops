/* גשר לתוכניות הלימודים. כל הקישורים נלקחו מעמודי המרחב הפדגוגי של משרד החינוך ונבדקו ב־25.10.2026. */
(function (TS) {
  'use strict';
  var B = 'https://pop.education.gov.il';

  TS.curriculum = {
    sourceUrl: B + '/tchumey_daat/bible-hemed/elementary/',
    sourceLabel: 'המרחב הפדגוגי: תנ״ך חמ״ד, יסודי',
    note: 'האתר אינו מעתיק את תוכניות הלימודים. הוא עוזר לכם להגיע למקור הרשמי, לבחור את החומר ולהעביר אותו להכנת תוצר. את השיוך של נושא לכיתה בוחרים ידנית, כי העמודים הרשמיים אינם מחולקים כולם לפי כיתה, ולא אימתנו שיוך כזה.',

    general: [
      { label: 'כל תחומי הדעת', url: B + '/tchumey_daat/knowledge-areas/' },
      { label: 'תוכניות לימודים', url: B + '/tchumey_daat/curriculum/' },
      { label: 'מאגר יחידות הוראה מתוקשבות', url: B + '/tchumey_daat/teaching-units-stock/' },
      { label: 'מעגל השנה', url: B + '/maagal_hashana/' },
      { label: 'בינה מלאכותית בחינוך היסודי', url: B + '/teaching-tools/ai-education/elementary/' }
    ],

    subjects: [
      { id: 'bible', name: 'תנ״ך חמ״ד', hemed: true, studio: 'תנ״ך', url: B + '/tchumey_daat/bible-hemed/elementary/',
        links: [
          { label: 'תוכנית לימודים כללית בתנ״ך חמ״ד לכיתות א–ו', url: B + '/tchumey_daat/bible-hemed/elementary/pedagogy-of-the-hamad-bible/bible-hemed-curriculum/' },
          { label: 'חומרי הוראה ולמידה', url: B + '/tchumey_daat/bible-hemed/elementary/teaching-materials/' },
          { label: 'חוברות עבודה מאושרות', url: B + '/tchumey_daat/bible-hemed/elementary/pedagogy-of-the-hamad-bible/approved-workbooks/' },
          { label: 'ספרי לימוד וסביבות תוכן', url: B + '/tchumey_daat/bible-hemed/elementary/pedagogy-of-the-hamad-bible/digital-books/' },
          { label: 'מיומנויות למידה, הערכה ומדידה', url: B + '/tchumey_daat/bible-hemed/elementary/pedagogy-of-the-hamad-bible/measurement/' },
          { label: 'מאמרים וחומרי העשרה למורה', url: B + '/tchumey_daat/bible-hemed/elementary/pedagogy-of-the-hamad-bible/articles-enrichment-materials/' }
        ],
        tip: 'בחרו חומש או פרק בספר הלימוד, והדביקו קטע קצר שמותר לכם לשכפל כמקור במחולל.' },
      { id: 'toshba', name: 'תלמוד ותושב״ע חמ״ד', hemed: true, studio: 'תושב״ע', url: B + '/tchumey_daat/toshba/elementary/', links: [],
        tip: 'העמוד מרכז את תוכנית הלימודים והחומרים. עברו לעמוד המקור כדי לבחור נושא.' },
      { id: 'hebrew', name: 'עברית: חינוך לשוני', hemed: false, studio: 'עברית (חינוך לשוני)', url: B + '/tchumey_daat/ivrit_chinhch_leshony/yesodi/', links: [], tip: '' },
      { id: 'math', name: 'מתמטיקה', hemed: false, studio: 'מתמטיקה', url: B + '/tchumey_daat/matmatika/yesodi/', links: [], tip: '' },
      { id: 'science', name: 'מדע וטכנולוגיה', hemed: false, studio: 'מדע וטכנולוגיה', url: B + '/tchumey_daat/mada-tehnologia/yesodi/', links: [], tip: '' },
      { id: 'english', name: 'אנגלית', hemed: false, studio: 'אנגלית', url: B + '/tchumey_daat/english/yesodi/', links: [], tip: '' },
      { id: 'geo', name: 'גאוגרפיה: אדם וסביבה', hemed: false, studio: 'גאוגרפיה', url: B + '/tchumey_daat/geography_adam_sviva/yesodi/',
        links: [{ label: 'תוכנית לימודים', url: B + '/learning-plans/geography/elementary/' }], tip: '' },
      { id: 'moledet', name: 'מולדת, חברה ואזרחות', hemed: false, studio: 'מולדת, חברה ואזרחות', url: B + '/tchumey_daat/moledet_hevra_ezrahut/yesodi/',
        links: [{ label: 'תוכנית לימודים', url: B + '/learning-plans/homeland_society_citizenship/elementary/' }], tip: '' },
      { id: 'culture', name: 'תרבות יהודית־ישראלית', hemed: false, studio: 'תרבות יהודית־ישראלית', url: B + '/tchumey_daat/israeli-jewish-culture/elementary/',
        links: [{ label: 'תוכנית לימודים', url: B + '/tchumey_daat/israeli-jewish-culture/elementary/curriculum/' }], tip: '' },
      { id: 'heart', name: 'מפתח הלב', hemed: false, studio: 'מפתח הלב / חינוך חברתי', url: B + '/tchumey_daat/heart-key/elementary/', links: [], tip: '' },
      { id: 'art', name: 'אמנות חזותית', hemed: false, studio: 'אמנות חזותית', url: B + '/tchumey_daat/visual-art/elementary/', links: [], tip: '' },
      { id: 'music', name: 'מוזיקה', hemed: false, studio: 'מוזיקה', url: B + '/tchumey_daat/music/elementary/', links: [], tip: '' },
      { id: 'pe', name: 'חינוך גופני', hemed: false, studio: 'חינוך גופני', url: B + '/tchumey_daat/physical-education/elementary/', links: [], tip: '' },
      { id: 'health', name: 'בריאות', hemed: false, studio: 'בריאות', url: B + '/tchumey_daat/health/elementary/', links: [], tip: '' },
      { id: 'digital', name: 'אוריינות דיגיטלית', hemed: false, studio: 'מקצוע אחר', url: B + '/tchumey_daat/oryanot-digitalit/yesodi/', links: [], tip: '' },
      { id: 'climate', name: 'שינוי אקלים', hemed: false, studio: 'מקצוע אחר', url: B + '/tchumey_daat/climate-change/elementary/', links: [], tip: '' }
    ],

    steps: [
      'בחרו כיתה ומקצוע. הכיתה נבחרת ידנית.',
      'פתחו את המקור הרשמי ובחרו נושא או קטע.',
      'חזרו לכאן, כתבו את הנושא או הדביקו קטע שמותר לכם לשכפל.',
      'שלחו למסלול בסטודיו והמשיכו מהצעד הבא.'
    ]
  };

})(window.TS = window.TS || {});
