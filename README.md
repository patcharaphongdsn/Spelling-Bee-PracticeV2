# Spelling Bee Practice

พร้อมใช้งานบน GitHub Pages

## วิธีใช้
1. อัปโหลด `index.html` ไปยัง repository
2. เปิด Settings → Pages
3. เลือก Deploy from a branch → `main` / root
4. เปิดลิงก์เว็บไซต์

ระบบมี Lower/Upper Level, Easy/Moderate/Difficult, สุ่มครบ 56 คำ, เสียงจาก Web Speech API, จับเวลา/พักเวลา, Teacher-led/Self-practice, บันทึกคะแนน, ทบทวนคำผิด, CSV และ Save as PDF ผ่านหน้าพิมพ์

หมายเหตุ: เสียงขึ้นอยู่กับ voice ที่ติดตั้งในอุปกรณ์และเบราว์เซอร์

อัปเดต: ทุกคำมีประโยคตัวอย่างเฉพาะของตนเอง ไม่ใช้ประโยค placeholder ซ้ำกัน

อัปเดต v3:
- เพิ่ม Tie-breaker เป็นโหมดที่ 4: Lower 30 คำ และ Upper 30 คำ
- เพิ่มปุ่ม Listen on Cambridge ทุกคำ
- ระบบเสียงรองรับ 3 ชั้น: Cambridge UK/US URL (เมื่อใส่ไว้ในข้อมูล) → Cambridge อีกสำเนียง → Web Speech API
- ค่า audioUk/audioUs เตรียมไว้ในข้อมูลทุกคำแล้ว ปัจจุบันเว้นว่างเพื่อให้ระบบใช้เสียงสังเคราะห์จนกว่าจะใส่ URL เสียงที่ได้รับอนุญาต

## เติม Cambridge UK/US audio URL อัตโนมัติ

เวอร์ชันนี้มี GitHub Action สำหรับค้นหา URL เสียง Cambridge ของทุกคำโดยอัตโนมัติ

1. อัปโหลดไฟล์และโฟลเดอร์ทั้งหมดขึ้น GitHub โดยต้องมีโฟลเดอร์ `.github/workflows` และ `scripts`
2. เปิดแท็บ **Actions**
3. เลือก **Fill Cambridge audio URLs**
4. กด **Run workflow**
5. ระบบจะตรวจทุกคำ แล้วเขียน `audioUk` และ `audioUs` กลับเข้า `index.html`
6. ดูจำนวนเสียงที่ค้นพบได้ใน `cambridge-audio-report.json`

เว็บจะลอง Cambridge สำเนียงที่เลือกก่อน จากนั้นลองอีกสำเนียง และใช้เสียงจากอุปกรณ์เป็นตัวสำรอง
