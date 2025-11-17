sudo mn -c
sudo fuser -k 6633/tcp
sudo killall controller
python ~/pox/pox.py log.level --DEBUG load_balancer
