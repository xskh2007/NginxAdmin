base = {
    'servers':[
              {'index':0,
               'name': 'server1', 
              'host': '192.168.4.69',
              'port': 30001,
              'password': '',
              'databases':16
              },
              {'index':1,
               'name': 'server2', 
              'host': '192.168.4.69',
              'port': 30002,
              'databases':16
              },
          ],
    'seperator' : ':',
    'maxkeylen' : 100
}
media_prefix = "pyred_media"

host = '0.0.0.0'
port = 8085
debug = True

scan_batch = 10000
show_key_self_count = False

lang = 'zh_CN'

admin_user = 'admin'
admin_pwd = 'admin'

nginx_conf_path="nginx_conf/"
nginx_cmd="/usr/local/nginx/sbin/nginx -s"