# Al-Moshaf Data

Public data distribution repository for the Al-Moshaf Android/Web application.

The application uses this repository as its preferred network source for Arabic Quran page data and the audited English Al-Mukhtasar tafsir. If a file is unavailable, the app automatically falls back to its original upstream APIs or bundled copy.

## Layout

- `quran/pages/ar/page-001.json` … `page-604.json`: Arabic page payloads used by the reader.
- `quran/uthmani-tanzil.txt`: verbatim Tanzil Uthmani text with aya numbers.
- `tafsir/en-mukhtasar.json`: English tafsir dataset, CC BY 4.0.
- `manifest.json`: public base URL and source metadata.
- `DATA_LICENSES.md`: required attribution and redistribution conditions.

See `DATA_LICENSES.md` before copying, modifying, or redistributing any data. The original application integration and repository metadata are MIT; external data retain their own licenses.
