# BA Spec Harness

Một quy trình (pipeline) phân tích tài liệu nghiệp vụ gồm **4 bước**, chạy
**giống hệt nhau** trên 3 agent: **Kiro**, **Claude Code**, và **Gemini
CLI**. Toàn bộ logic nằm ở một chỗ (`harness/`); mỗi nền tảng chỉ cần một
file "loader" nhỏ trỏ vào đó.

---

## 1. Workflow này làm gì

Bạn đưa vào một bản nháp tài liệu (draft) thô, agent sẽ dẫn bạn qua 4 bước
để biến nó thành một bản đặc tả (spec) sạch, có truy vết, và có ước lượng.
Bạn chọn bước nào chạy trước — không bắt buộc theo thứ tự cố định.

| Bước | Làm gì | Có hỏi/duyệt không |
|---|---|---|
| **`rewrite`** | Sắp xếp bản nháp thô vào cấu trúc chuẩn (mục 1–10, đánh số `FR-NNN`). Không đặt câu hỏi. | Không — chạy một phát ra file. |
| **`ba_review`** | Soát tài liệu dưới góc nhìn BA, tìm chỗ thiếu/mơ hồ, chèn câu hỏi `[OPEN: ...]` ngay trong bản nháp. | Có — bản nháp → bạn trả lời → duyệt → chốt. |
| **`team_review`** | Giống `ba_review` nhưng soát qua **5 góc nhìn** (Backend, Frontend, QA, Design/UX, Product/Data) để kiểm tính khả thi. | Có — cùng kiểu nháp → duyệt → chốt. |
| **`estimation`** | Ước lượng cỡ (T-shirt size: S/M/L...) cho từng yêu cầu. | Không duyệt, nhưng sẽ hỏi nếu yêu cầu quá mơ hồ để ước lượng. |

**Nguyên tắc cốt lõi:** agent **không bao giờ tự bịa** thông tin. Mọi câu
nó viết trong spec đều phải truy ngược về một câu trong nguồn hoặc một câu
trả lời bạn đã duyệt. Chỗ nào thiếu, nó đánh dấu `[OPEN: ...]` để bạn giải
quyết, chứ không đoán.

**Một tài liệu chốt duy nhất:** `ba_review` và `team_review` cùng ghi vào
**một file "final" chung** cho mỗi input (không tách thành nhiều file).
Mỗi lần chốt, file mới luôn chứa đầy đủ nội dung file cũ cộng thêm một mục
truy vết (traceability) liệt kê mọi câu hỏi–trả lời, nhóm theo bước đã nêu
ra. Nhờ vậy `estimation` luôn đọc đúng bản spec mới nhất.

**Thư mục làm việc:**
- `inputs/` — bỏ bản nháp thô vào đây (agent chỉ đọc, không bao giờ sửa).
- `outputs/` — mọi kết quả của từng bước ra ở đây.
- `harness/` — toàn bộ rule chung (orchestrator, các bước, checklist...).
- `state.json` — agent tự ghi: bước nào đã chạy, trên file nào, lúc nào.

Sau mỗi lần ghi file, agent chạy `harness/scripts/validate_structure.py`
để kiểm cấu trúc, và sửa lỗi trước khi báo xong.

---

## 2. Cách dùng (prompt)

1. Bỏ một bản nháp vào `inputs/` (hoặc cứ dán nội dung thẳng vào chat).
2. Mở thư mục dự án trong Kiro / Claude Code / Gemini CLI, rồi nói ví dụ:

   ```
   analyze aircraft-spec.md
   ```

   File loader của nền tảng đó sẽ tự trỏ agent vào `harness/ORCHESTRATOR.md`
   và nó tiếp quản từ đây.
3. **Lần chạy đầu:** agent hỏi muốn viết kết quả bằng ngôn ngữ nào, rồi
   quét `inputs/` và báo đã làm được gì.
4. **Chọn bước** để chạy (bất kỳ thứ tự). Agent nói rõ nó sẽ đọc file nào
   làm nền, kế hoạch ra sao, rồi **chờ bạn gõ "approve"** mới chạy.
5. Với **`ba_review` / `team_review`**: agent viết **bản nháp** có các câu
   `[OPEN: ...]`. Bạn trả lời ngay trong file (thay thẳng vào chỗ tag, hoặc
   trả lời dưới mục Open Questions — cách nào cũng được), rồi gõ **"approve"**
   lần nữa để agent chốt vào tài liệu final chung.
6. **`rewrite`** và **`estimation`** chạy một phát ra file, không có vòng
   duyệt.
7. Giữa chừng bạn hỏi gì cũng được — agent trả lời xong luôn kèm một dòng
   cuối cho biết bạn đang ở bước nào và làm gì tiếp theo.

> **Mẹo:** input là PDF cũng được. Agent dùng skill `pdf` để đọc (xem phần
> cài đặt bên dưới để bật skill này).

---

## 3. Cài đặt bằng `npx`

Bộ harness đi kèm một CLI nhỏ. Đứng trong thư mục dự án bạn muốn cài, chạy:

```bash
# Nếu đã publish lên npm:
npx ai-ba-workflow

# Hoặc chạy thẳng từ GitHub (không cần publish):
npx github:nguyentanphat8694/ai-ba-workflow
```

CLI sẽ hỏi bạn dùng agent nào:

```
Which agent are you using?
  1) kiro    -> .kiro/steering/harness.md
  2) claude  -> CLAUDE.md
  3) gemini  -> GEMINI.md
```

Chọn 1 trong 3. CLI sẽ:

1. Tải toàn bộ thư mục `harness/` (rule chung) — bản mới nhất từ nhánh
   `main`, **ghi đè** file harness cũ nếu đã có.
2. Tải đúng file loader của agent đã chọn (`.kiro/steering/harness.md` /
   `CLAUDE.md` / `GEMINI.md`).
3. Tạo sẵn thư mục `inputs/` và `outputs/` (không đụng file bạn đã bỏ vào).
4. Hỏi có muốn cài **skill đọc PDF** không. Chọn `y` thì nó chạy
   `npx skills add https://github.com/anthropics/skills --skill pdf`;
   chọn `n` thì kết thúc.

Chạy lại trên thư mục đã cài là an toàn: thư mục có sẵn không gây lỗi, file
harness được cập nhật, còn file trong `inputs/` / `outputs/` giữ nguyên.

### Chế độ không tương tác (CI / script)

```bash
npx ai-ba-workflow kiro            # chọn agent luôn, bỏ qua menu
npx ai-ba-workflow kiro --pdf      # cài luôn skill PDF
npx ai-ba-workflow kiro --no-pdf   # bỏ qua skill PDF
# hoặc biến môi trường: AI_BA_PDF=1 (cài) / AI_BA_PDF=0 (bỏ qua)
```

### Publish lên npm (chủ repo, làm một lần)

Để lệnh ngắn `npx ai-ba-workflow` chạy được:

```bash
npm login
npm publish --access public
```

Nội dung `harness/` **không** nằm trong package npm — CLI tải nó từ GitHub
lúc chạy, nên sửa harness chỉ cần `git push`, không cần publish lại. Nếu
không publish, người dùng vẫn chạy được qua
`npx github:nguyentanphat8694/ai-ba-workflow`.

---

## Vì sao làm theo kiểu này

Kiro, Claude Code, và Gemini CLI có cơ chế mở rộng (skill / slash-command /
custom-command) khác nhau và không tương thích. Thứ duy nhất cả ba đều có
là: (1) một file tự nạp vào context lúc mở phiên, và (2) đọc/ghi file thô.
Harness này xây hoàn toàn trên hai thứ đó, nên chỉ có **một nguồn sự thật**
(`harness/`) thay vì ba bản song song phải đồng bộ. Ba file loader
(`.kiro/steering/harness.md`, `CLAUDE.md`, `GEMINI.md`) tương đương nhau về
chỉ thị — chỉ khác ở cú pháp nạp bắt buộc của từng nền tảng.
