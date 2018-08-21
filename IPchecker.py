import json
import sqlite3
import subprocess

# y = subprocess.check_output('curl -X GET "http://127.0.0.1:22999/api/proxies" -H "accept: application/json"', shell=True)
# print json.dumps(json.loads(y), indent=4, sort_keys=True)
try:
    output = subprocess.check_output(
        'curl -X GET "http://127.0.0.1:22999/api/proxies_running" -H "accept: application/json"', shell=True,
         stderr=subprocess.DEVNULL)
    json_output = json.loads(output)
except:
    print('Connect to Iluminati Proxy Manager failed. Check to make sure it is running.')
    exit()


# Create list of tuples of IPs which will be used as inputs to an EXECUTEMANY INSERT SQL QUERY
ips = []
for proxy in json_output:
    if 'ips' in proxy:
        for ip in proxy['ips']:
            ips.append((ip.encode('ascii', 'ignore'),))

# INSERT IPs and timestamp in DB table
sqlite_file = './fb_db.sqlite'
try:
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS iplogger (time timestamp NOT NULL, ip text NOT NULL);''')
    c.executemany('''INSERT INTO iplogger (time, ip) VALUES(CURRENT_TIMESTAMP, ?)''', ips)
    conn.commit()
except Exception as e:
    # Roll back any change if something goes wrong
    conn.rollback()
    raise e
finally:
    # Close the db connection
    conn.close()
