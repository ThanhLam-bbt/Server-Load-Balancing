# Server-Load-Balancing

Đồ án môn học Công Nghệ mạng khả lập trình 2025.

Dự án này triển khai một bộ cân bằng tải (Load Balancer - LB) trên mạng được định nghĩa bằng phần mềm (SDN) sử dụng POX OpenFlow Controller và Mininet để mô phỏng.
Load Balancer hoạt động ở tầng Network (L3) và sử dụng kỹ thuật NAT (Network Address Translation) để phân phối lưu lượng truy cập từ các client đến một nhóm các server backend.

Dự án mô phỏng một Load Balancer dựa trên SDN: controller POX xử lý ARP/ICMP, chọn server backend (Random hoặc Round-Robin), cài flow rules xuống switch Open vSwitch (Mininet) và ghi log sử dụng server để phân tích.

Yêu Cầu Hệ Thống

- Ubuntu 20.04
- Python 2.7+
- Mininet
- POX Controller
- Git

Mô hình mạng
<img width="3054" height="3713" alt="sdn_topo" src="https://github.com/user-attachments/assets/3f6e9e6a-e00f-451e-bd1f-83a77946e053" />

Thuật toán Random
- Thống kê lưu lượng: Port 9 (Server 9) có 111 gói tin tx_packets, Port 11 (Server 11) chỉ có 51 gói tin tx_packets => chênh lệch 60 gói tin (50%).
<img width="6600" height="1056" alt="Random_1" src="https://github.com/user-attachments/assets/70c86f8b-7971-4254-9971-4bd1156b4a56" />

- Biểu đồ phân phối tải: Phân bố tải không đồng đều, có sự chênh lệch lớn giữa các Server.
<img width="6640" height="3022" alt="Random_2" src="https://github.com/user-attachments/assets/0c8a8fca-b6ce-483c-a99e-faecd4fb49eb" />

Thuật toán Round Robin
- Thống kê lưu lượng: tx_packets giữa các server chỉ chêch lệch khoảng 3 gói tin (82 - 84).
<img width="6600" height="1072" alt="rr_1" src="https://github.com/user-attachments/assets/b2827d5d-0d94-4c93-a8c9-8c2c63fe60a3" />

- Biểu đồ phân phối tải: Tải được chia đều cho 6 Server với độ chênh lệch không đáng kể.
<img width="6600" height="3020" alt="rr_2" src="https://github.com/user-attachments/assets/323977bf-82db-4191-ae50-5480bbe5172b" />

Tính năng Heal Check
- Biểu đồ phân phối tải: Giả lập sự cố ngắt kết nối vật lý tới một Server. Hệ thống tự động điều hướng lưu lượng sang các Server còn sống, đảm bảo dịch vụ không bị gián đoạn.
<img width="6600" height="2929" alt="heal check" src="https://github.com/user-attachments/assets/e47d1ce1-c69e-4d2e-9c4d-414e11714f78" />




