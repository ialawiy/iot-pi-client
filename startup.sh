LOG_FILE="~/dc/log.txt"

until ping -c1 google.com &>/dev/null; do sleep 1; done;

tailscale up 
sudo service motion restart 
cd dc && node js-client.js >> $LOG_FILE  
cd dc && python MPPT-client.py >> $LOG_FILE  




