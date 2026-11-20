# ePlus AI Toolkit — Tiếng Việt

> [!NOTE]
> Tài liệu tham khảo lịch sử; đây **không phải bản dịch đầy đủ được cập nhật** của README hiện tại. Đọc [README tiếng Việt mới nhất](../../README.vi.md) trước khi làm theo hướng dẫn, đặc biệt là các bước có rủi ro thanh toán.

[← Bản dịch tiếng Việt hiện hành](../../README.vi.md) · [Documentation home](../README.md) · [English user guide](../USAGE.md)

[English](../../README.md) · **Tiếng Việt** · [简体中文](../../README.zh-CN.md) · [日本語](../../README.ja.md) · [한국어](../../README.ko.md) · [Español](../../README.es.md) · [Français](../../README.fr.md)

**macOS Preview:** [Bản dành cho Mac](../../docs/MACOS-PREVIEW.md) đã có luồng Steps 0–5 tương tự Windows; các bước 2–5 có thể phát sinh thanh toán thật và cần xác nhận riêng từng bước. Chưa kiểm thử thanh toán trên Mac/MuMu thực tế, CI chỉ xác minh bằng mock.

> **Nguồn chuẩn:** [README tiếng Anh](../../README.md). Bản dịch này giúp sử dụng công cụ; nếu có khác biệt về tính năng, hãy đối chiếu mã nguồn và README tiếng Anh.

Bộ công cụ dòng lệnh dành chủ yếu cho **Windows**, sử dụng **PowerShell, Python, ADB, Frida và máy ảo Android (MuMuPlayer)** để kiểm tra ưu đãi Google AI Pro thông qua Google One/Google Play. Giao diện Textual sử dụng chung bộ xử lý với chế độ CLI.

![Giao diện ePlus AI Toolkit](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **Đây là công cụ không chính thức và có rủi ro thanh toán.** Các bước **2–5** có thể mở quy trình thanh toán thật trên Google Play và tự nhấn **Subscribe**. Việc nhìn thấy ưu đãi hoặc mức giá ban đầu bằng 0 **không chứng minh** tài khoản đủ điều kiện, được miễn phí, đã kích hoạt hay đã gia hạn. Trước khi checkout, phải xác minh tài khoản, số tiền trả hôm nay, giá gia hạn và ngày thanh toán tiếp theo **trên Google Play**. Dừng công cụ không thể hoàn tác giao dịch đã gửi.

> [!NOTE]
> **Xác thực thẻ có thể tạm giữ tiền dù hóa đơn Google Play hiển thị 0 USD.** Bạn có thể thấy khoản **giữ tiền chờ xử lý khoảng 3 USD** (hoặc mức khác) để xác thực thẻ. **3 USD chỉ là mức tham khảo, không phải phí cố định của Google hoặc bằng chứng đã thanh toán gói đăng ký.** Khoản tạm giữ có thể làm giảm số dư khả dụng; theo Google, lệnh xác thực này không phải giao dịch mua hàng và thường được giải tỏa trong **1–14 ngày làm việc**, tùy ngân hàng. Nếu tiền được hạch toán thành khoản trừ thực tế hoặc lệnh giữ tiền còn tồn tại sau 14 ngày làm việc, hãy liên hệ ngân hàng và Google Payments. [Nguồn chính thức của Google Play](https://support.google.com/googleplay/answer/6224192?hl=en).

## Tuyên bố miễn trừ trách nhiệm

Dự án độc lập, **không liên kết, được tài trợ hoặc chứng thực** bởi Google, Google One, Google Play, NetEase hay MuMuPlayer. Phần mềm cung cấp **nguyên trạng**, không bảo đảm ưu đãi, khả năng tương thích hay kết quả đăng ký. Chỉ sử dụng với thiết bị và tài khoản mà bạn có quyền kiểm soát, tuân thủ quy định và điều khoản dịch vụ. Xem [Disclaimer đầy đủ (tiếng Anh)](../../DISCLAIMER.md) và [Lưu ý bảo mật](../../SECURITY.md).

## 1. Chuẩn bị

- **Windows**, PowerShell **5.1+** và Python **3.10+**.
- Tự cài **MuMuPlayer**, bật quyền root và ADB trên máy ảo Android.
- Cài **Google Play Store** và **Google One** trong Android; đăng nhập đúng tài khoản cần kiểm tra.
- Công cụ có thể tìm hoặc tải **Android SDK Platform-Tools (ADB)** và cài **Frida 16.5.9** khi cần. **Không tự tải hoặc cài MuMuPlayer**. Tính tương thích Frida phụ thuộc phiên bản Android.

**Link MuMu chính thức:** [mumuplayer.com/download](https://www.mumuplayer.com/download/) (chọn bản Windows). Không dùng nguồn tải không chính thức.

Hướng dẫn cài đặt bổ sung: [GitHub Wiki — Install](https://github.com/hoangsvit/google-ai/wiki/Install).

## 2. Cài và khởi động

Mở PowerShell:

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

Nếu đã tải repo trước đó:

```powershell
git pull --ff-only
.\run-all.ps1
```

Chạy **không tham số** sẽ mở giao diện **Textual TUI**; không tự chạy checkout. Khi bắt đầu kiểm tra, chương trình có thể tự chuẩn bị Textual, ADB và Frida. Thường **không cần** chạy `setup_env.py` trước. Bước chuẩn bị có thể thay đổi công cụ, proxy/mạng và cấu hình máy ảo.

Nếu ADB có trong PATH, kiểm tra kết nối:

```powershell
adb devices
```

Thiết bị phải ở trạng thái `device`, không phải `offline` hoặc `unauthorized`. Nếu không tìm thấy ADB, xem [hướng dẫn xử lý lỗi](../../docs/DETAILED-GUIDE.md).

### Phương án thay thế: sử dụng bản phát hành khi gặp lỗi

Nếu phiên bản mới nhất chạy từ source gặp lỗi, bạn có thể thử **bản phát hành đã công bố** tại [GitHub Releases](https://github.com/hoangsvit/google-ai/releases). Chọn một phiên bản, đọc ghi chú phát hành và tải gói Windows **nếu có file đính kèm**. Nếu chỉ có **Source code (zip)** do GitHub cung cấp, hãy tải ZIP, giải nén, mở PowerShell ngay trong thư mục đã giải nén rồi chạy:

```powershell
.\run-all.ps1
```

**Source code (zip) không phải ứng dụng `.exe` hay bộ cài dựng sẵn.** Nên giữ bản phát hành trong **thư mục riêng**, không chép đè lên bản source đang dùng. Bản phát hành cũ có thể chưa chứa những bản sửa lỗi mới và vẫn cần Windows, Python, MuMuPlayer, ADB/Frida cùng các lưu ý về thanh toán. Nếu lỗi vẫn xảy ra, xem [hướng dẫn khắc phục](../../docs/DETAILED-GUIDE.md) hoặc [tạo Issue](https://github.com/hoangsvit/google-ai/issues).

## 3. Sử dụng giao diện

Chọn **Check Device & Offers** để thực hiện **Step 1 — Available offers**, truy vấn ưu đãi **không khởi tạo checkout**. Theo dõi **Live Status**, mở **Show technical details** khi cần và kiểm tra tài khoản trong Google Play. Việc không có log mới trong 30 giây chỉ là cảnh báo thiếu hoạt động, **không phải kết luận treo**.

Mục **Advanced: Run by step** gồm:

| Chế độ | Chức năng |
| --- | --- |
| **One step only** | Chỉ chạy một bước được chọn từ 0 đến 5 |
| **From selected step** | Bắt đầu chuỗi có hướng dẫn từ Step 2–5 |
| **All: Steps 2–5** | Bắt đầu chuỗi từ Step 2; Step 5 là tùy chọn |

| Bước | Vai trò | Rủi ro |
| --- | --- | --- |
| **0 — Environment** | Kiểm tra/chuẩn bị Android, ADB và Frida | Không checkout, nhưng có thể đổi cấu hình |
| **1 — Available offers** | Truy vấn ưu đãi | Không checkout, nhưng preflight có thể đổi môi trường |
| **2 — Pro 12 months** | Thử ưu đãi gốc 12 tháng | **Có thể thanh toán thật** |
| **3 — Pro +6 months** | Thử cập nhật gói | **Có thể thanh toán thật** |
| **4 — Pro +6 months (second)** | Thử cập nhật lần tiếp | **Có thể thanh toán thật** |
| **5 — Optional +6 months** | Thử ưu đãi tùy chọn | **Có thể thanh toán thật** |

Tên 12/6 tháng là **tên lịch sử của các bước**, không phải cam kết được cộng thêm thời hạn. Nếu đã có gói đang hoạt động, **không chạy lại Step 2**.

Trước **mỗi bước checkout trên TUI**, cần phê duyệt riêng. Khi công cụ báo đã thử gửi checkout, hãy xác minh gói đang hoạt động, số tiền và ngày gia hạn tại [Google Play Subscriptions](https://play.google.com/store/account/subscriptions). Chỉ chọn **Verified in Google Play → Next** sau khi đã tự xác minh; tool **không thể tự chứng minh giao dịch thành công**.

**Stop/Exit:** Step 0–1 có thể yêu cầu dừng tiến trình cục bộ. Với Step 2–5, **Stop after this step** ngăn chạy bước tiếp theo, **không ép dừng giao dịch đang xử lý**. **Q / Exit** sẽ đợi bước thanh toán hiện tại kết thúc. **D** mở/đóng log kỹ thuật; **R** chạy chế độ đã chọn.

## 4. PowerShell CLI (nâng cao)

**Kiểm tra, không mua hàng:**

```powershell
.\run-all.ps1 -Step 1
.\run-all.ps1 -Step 1 -Debug
.\run-all.ps1 -Step 0
.\run-all.ps1 -Cli
```

**Các lệnh sau có thể kích hoạt thanh toán thật:**

```powershell
.\run-all.ps1 -Step 2
.\run-all.ps1 -Step 3
.\run-all.ps1 -Step 4
.\run-all.ps1 -Step 5
```

Khác với TUI, chạy một bước riêng bằng `-Step 2..5` **không có thêm hộp thoại phê duyệt trong PowerShell**. Chỉ thực hiện khi thực sự có ý định checkout và đã xem điều khoản.

Chuỗi có xác nhận từng giai đoạn:

```powershell
.\run-all.ps1 -AllStages
.\run-all.ps1 -AllStages -StartStep 3
```

CLI dùng **1 = Continue, 2 = End run, 0 = Stop**. Tự kiểm tra kết quả trong Google Play trước khi chuyển bước. `-StartStep 3` không xác minh các bước trước đã thành công.

Chọn thiết bị hoặc tài khoản dự kiến:

```powershell
.\run-all.ps1 -Step 1 -Serial emulator-5554
.\run-all.ps1 -AllStages -Email "account@gmail.com"
```

Chỉ sử dụng serial thực tế từ ADB. Tránh `-Force` vì nó bỏ qua bước kiểm tra khớp tài khoản, **không** vượt qua điều kiện ưu đãi hay giới hạn thanh toán của Google.

## 5. Kết quả và xử lý lỗi

- **Không tìm thấy MuMu/ADB:** kiểm tra máy ảo, root, ADB và trạng thái kết nối.
- **Lỗi Frida:** mở log và kiểm tra phiên bản **16.5.9**/khả năng tương thích Android.
- **Không có ưu đãi:** mở Google One/Play Store, rồi chạy lại **Step 1**.
- **Sai tài khoản:** xác nhận đúng hồ sơ Google Play, không bỏ qua xác minh.
- **Checkout đã gửi nhưng chưa xác nhận:** không coi là gia hạn; kiểm tra trực tiếp Google Play trước khi thử lại.
- **Lỗi bảo mật thanh toán (ví dụ OR-REH-04):** dừng các bước thanh toán, kiểm tra thông báo bảo mật chính thức.

Log được lưu trong `logs/`, báo cáo trong `ultra0-report/`. **Không chia sẻ log/report chưa ẩn email, token hoặc dữ liệu thanh toán**. CI chỉ kiểm thử tĩnh/mock, không kiểm chứng mua hàng thật. **macOS chưa được hỗ trợ đầy đủ**.

## Hỗ trợ cộng đồng và dự án liên quan

Nếu gặp vấn đề khi cài đặt hoặc sử dụng ePlus AI Toolkit, hãy truy cập [bài đăng hỗ trợ trên Telegram ePlus](https://t.me/eplus_news/29) để liên lạc, trao đổi kinh nghiệm và nhờ cộng đồng hỗ trợ. Với lỗi kỹ thuật có thể tái hiện, bạn cũng có thể [tạo GitHub Issue](https://github.com/hoangsvit/google-ai/issues). **Không chia sẻ mật khẩu, mã OTP/2FA, offer/purchase token, log chưa che thông tin cá nhân hoặc dữ liệu thẻ thanh toán.** Đây là hỗ trợ cộng đồng, không phải kênh hỗ trợ chính thức của Google.

**Không tham gia được chương trình Google AI Pro?** Bạn có thể tham khảo [Muse Invite Hub](https://github.com/ePlus-DEV/muse-invite-hub), một dự án khác của ePlus.DEV để [tìm kiếm hoặc chia sẻ mã mời Muse](https://muse.eplus.dev/). **Muse là dịch vụ riêng**, mã mời Muse **không kích hoạt và không thay thế** quyền đăng ký Google AI Pro. Mã mời có thể hết lượt hoặc bị giới hạn theo khu vực/tài khoản.

## Tài liệu và tác giả

[README tiếng Anh](../../README.md) · [Wiki Install](https://github.com/hoangsvit/google-ai/wiki/Install) · [Hướng dẫn kỹ thuật](../../docs/DETAILED-GUIDE.md) · [Các bước gốc](../../docs/ORIGINAL-STEPS.md) · [Disclaimer](../../DISCLAIMER.md) · [Bảo mật](../../SECURITY.md) · [Đóng góp](../../CONTRIBUTING.md) · [Thông báo bản quyền](../../THIRD_PARTY_NOTICES.md)

**Tác giả gốc:** [@gylive](https://github.com/gylive) — [google-ultra](https://github.com/gylive/google-ultra). **Người duy trì:** [David Nguyen (@hoangsvit)](https://github.com/hoangsvit) / [ePlus.DEV](https://eplus.dev). Giữ nguyên thông báo MIT của tác giả gốc trong `THIRD_PARTY_NOTICES.md`.
