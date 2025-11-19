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
<img width="1008" height="660" alt="topo" src="https://github.com/user-attachments/assets/d7ec2e46-ad5d-46af-9c79-c08f351fc9f7" />

Thuật toán Round Robin
- Thông kê lưu lượng:
<img width="602" height="113" alt="Stats_RoundRobin" src="https://github.com/user-attachments/assets/5a834495-4679-45c8-bf26-19e74607f6fb" />
- Biểu đồ phân phối tải:
<img width="464" height="243" alt="RequestCount_RoundRobin" src="https://github.com/user-attachments/assets/60b434fb-7e5b-4a9f-9e4d-018311a0e28d" />

Thuật toán Random
- Thông kê lưu lượng:
<img width="602" height="113" alt="Stats_Random" src="https://github.com/user-attachments/assets/2e7da3e6-1fb6-4a2c-889e-07fd2f6ee823" />
- Biểu đồ phân phối tải:
<img width="602" height="292" alt="RequetsCount_Radom" src="https://github.com/user-attachments/assets/32e1d7e2-367f-4947-ac06-d8dc538f7eac" />




