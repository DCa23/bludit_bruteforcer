# Tool to brute force bludit CMS #

Usage example:
```
./bruteforcer.py --url http://127.0.0.1:8000/admin/login -U userlist.txt -W wordlist.txt -T 50
```
**Options:**
```
--url - target url with a bludit cms, login path should be included
-U - path to the userlist file
-W - path to the wordlist file
-T - number max of threads (default: 20)
-wt - watinig time betwen retrys when bluedit blocks ip (default: 120)
```

**startbuldit.sh** this scripts starts a bludit instance in the port 8080, just to help developing
