# حمّلها — محمّل تيك توك

صُمّم بواسطة MSHARIDSN

موقع تلصق فيه رابط مقطع تيك توك فيحمّله لك بصيغة MP4.

## رفعه أونلاين من الجوال (مجاناً)

1. **GitHub:** أنشئ مستودعاً جديداً باسم `hammilha`، ثم Add file ← Upload files وارفع الملفات الثلاثة.
2. **Render:** سجّل في render.com بحساب GitHub ← New ← Web Service ← اختر المستودع.
   - Name: `msharidsn` (يصير الرابط msharidsn.onrender.com)
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --timeout 120`
   - Instance Type: Free ← Deploy

## ملاحظات

- الخطة المجانية تنام بعد فترة بلا زيارات، فأول فتح بعدها يأخذ قرابة دقيقة.
- إذا توقف التحميل، حدّث yt-dlp بإعادة النشر من Render (Manual Deploy ← Clear build cache & deploy).
- حمّل فقط مقاطعك أو المقاطع التي لديك إذن بها.
