# Server-Load-Balancing

Đồ án môn học Công Nghệ mạng khả lập trình 2025.

Dự án này triển khai một bộ cân bằng tải (Load Balancer - LB) trên mạng được định nghĩa bằng phần mềm (SDN) sử dụng POX OpenFlow Controller và Mininet để mô phỏng.
Load Balancer hoạt động ở tầng Network (L3) và sử dụng kỹ thuật NAT (Network Address Translation) để phân phối lưu lượng truy cập từ các client đến một nhóm các server backend.

Dự án hỗ trợ hai thuật toán cân bằng tải cơ bản: Round Robin (RR) và Random (Ngẫu nhiên), kèm theo tính năng ghi log và trực quan hóa dữ liệu bằng Matplotlib.

Yêu Cầu Hệ Thống

- Ubuntu 20.04
- Python 2.7+
- Mininet
- POX Controller
- Git
