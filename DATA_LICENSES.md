# مستودع بيانات المصحف — المصادر والرخص

هذا المستودع قابل لإعادة الاستخدام وفق رخصة كل مصدر. لا تعني رخصة `LICENSE` أن البيانات الخارجية أصبحت MIT.

## النص العربي

- الملفات: `quran/uthmani-tanzil.txt` و`quran/pages/ar/`.
- المصدر: [Tanzil Project](https://tanzil.net/).
- الرخصة: [CC BY 3.0 وشروط Tanzil](https://tanzil.net/docs/text_license).
- يسمح المصدر بالنسخ والتوزيع التجاري للنسخ المطابقة، ولا يسمح بتغيير النص؛ يجب إبقاء الإسناد والرابط.

## التفاسير العربية والإنجليزية

- الملفات: `tafsir/ar-mukhtasar.json` و`tafsir/en-mukhtasar.json`.
- المصدر: [Tafsir Center for Quranic Studies](https://tafsir.net)، من قاعدة `tafsir-mcp-data` الرسمية.
- الرخصة: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- نص إذن المصدر: يسمح بالمشاركة والتعديل والاستخدام التجاري، مع إسناد `Tafsir Center for Quranic Studies (https://tafsir.net)` ورابط الرخصة وبيان التغييرات.
- لا تتضمن الرخصة شرطًا لمراقبة التحديثات أو تحديث النسخة. هذه نسخة مثبتة؛ لا يعتمد التوزيع على متابعة تحديثات المصدر.
- التعديل المعلن: استخراج حقلي `Mukhtasarar` و`Mukhtasaren` وتسلسلهما إلى JSON دون تغيير صياغة النصوص.

## المحتوى الأصلي

`devotional/adhkar.json` و`devotional/names-of-allah.json` و`devotional/ruqyah.json` محتوى أصلي ضمن MIT © 2026 Abdullah Qatan، ولا تشمل الرخصة مواد طرف ثالث غير موثقة.

## الترجمات

- الملفات: `quran/translations/en-english_pickthall.json` و`quran/translations/id-indonesian_kemenag.json`.
- المصدر: [Tanzil](https://tanzil.net/)، ترجمة Pickthall بالإنجليزية وترجمة وزارة الشؤون الدينية الإندونيسية.
- الرخصة/الشروط: شروط إعادة توزيع Tanzil، وليست MIT؛ وهي CC BY 3.0 مع شروط Tanzil الخاصة بالنقل الحرفي وعدم التغيير. النصان محفوظان حرفياً؛ يجب إبقاء الإسناد ومعلومات الإصدار ومعلومات النسخة الأصلية، وعدم تعديل النص، ونشر ملاحظات المصدر، ومراعاة متطلبات التحديث.
- لا يُعلن المستودع أن هاتين الترجمتين مرخصتان ترخيصاً مفتوحاً عاماً؛ راجع شروط Tanzil قبل أي توزيع تجاري.

## الجامع الوجيز

- المؤلف: الشيخ الدكتور أيمن فاتح آل عامر؛ المصدر [quran-tafsir-jami-wajiz](https://github.com/yamanamr/quran-tafsir-jami-wajiz).
- الرخصة: [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/). تتطلب الإسناد ورابط الرخصة وبيان التغييرات، وتمنع توزيع نص تفسير معدّل.
- `tafsir/al-jami-al-wajiz/ar-jami-al-wajiz.json` هو المصدر القانوني الموحد؛ يحتفظ بقيم النصوص وHTML وبيانات السور وببصمات ملفات المصدر، ومعه `LICENSE.txt`.
- `tafsir/al-jami-al-wajiz/surah-manifest.json` و114 ملفًا في `tafsir/al-jami-al-wajiz/surahs/` شرائح نقل لكل سورة. إنها تقسم السجلات دون إعادة صياغة قيم النص، وتتحقق اختبارات البيانات من تطابق كل سجل وبيانات السورة مع المصدر القانوني.
- يجب إبقاء اسم المؤلف ورابط المصدر والرخصة وملف `LICENSE.txt` وعدم إعادة صياغة نص التفسير عند إعادة التوزيع. التطبيق يصرح بتغييرات النقل والعرض وينقي HTML/الأنماط عند العرض؛ هذه المعالجة لا تغير حقول النص الأصلية المحفوظة.

## سلامة البيانات

`SHA256SUMS.txt` يغطي الملفات المتعقبة. `scripts/check_data_integrity.py` يتحقق من هذه البصمات، واكتمال القرآن والتفاسير، وصيغ HTML المستخدمة، وبصمات الشرائح ومطابقتها الحرفية للمصدر.
