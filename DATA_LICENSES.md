# مستودع بيانات المصحف — المصادر والرخص

هذا المستودع قابل لإعادة الاستخدام تجاريًا وفق رخصة كل مصدر. لا تعني رخصة `LICENSE` أن البيانات الخارجية أصبحت MIT.

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

- `devotional/adhkar.json` و`devotional/names-of-allah.json` و`devotional/ruqyah.json` محتوى أصلي ضمن MIT © 2026 Abdullah Qatan، ولا تشمل الرخصة مواد طرف ثالث غير موثقة.

## API الطوارئ

- التطبيق يبدأ من الملفات المحلية في هذا المستودع.
- عند تعذر ملف القرآن العربي فقط، يمكنه استخدام AlQuran.cloud كخطة طوارئ للنص العربي دون ترجمة أو تفسير.
- لا يستخدم التطبيق أي مصدر غير معتمد أو أي API للترجمات أو التفاسير.

## التحقق

```bash
sha256sum -c SHA256SUMS.txt
```

احتفظ بإسناد كل مصدر ورخصته، ولا تنسب بيانات Tanzil أو Tafsir Center إلى MIT.
