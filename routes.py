# coding=utf-8

from mole import route, run, static_file, error, get, post, put, delete, Mole  # 均来自Mole类
from mole.template import template, Jinja2Template
from mole import request
from mole import response
from mole.mole import json_dumps
from mole import redirect
from mole.sessions import get_current_session, authenticator

from config import media_prefix
import config
import i18n

import nginx
import json
import os
import glob

auth_required = authenticator(login_url='/auth/login')


@route('/%s/:file#.*#' % media_prefix)
def media(file):
    return static_file(file, root='./media')


@route('/nginx_tree')
@auth_required()
def nginx_tree():
    jsonlist = []
    # jsondict = {"id": 1, "pId": 0, "name": "nginx_conf"}
    # jsonlist.append(jsondict)
    f_id=1
    for file in os.listdir(config.nginx_conf_path):
        jsonlist.append({"id": f_id, "pId": 0, "name": file})
        # f_id=f_id+1
        c = nginx.loadf(config.nginx_conf_path+file)
        jsonlist.append({"id": int(str(f_id)+"2"), "pId": f_id, "name": "upstream"})
        jsonlist.append({"id": int(str(f_id)+"3"), "pId": f_id, "name": "servers"})
        Upstreams = c.filter(btype="Upstream")
        u_id = 0
        s_id = 0
        for i in Upstreams:
            id = int(str(f_id)+"2" + str(u_id + 1))
            jsondict = {"id": id, "pId": int(str(f_id)+"2"), "name": i.value}
            u_id = u_id + 1
            # print type(u_id),u_id
            jsonlist.append(jsondict)
        Servers = c.filter(btype="Server", name='')
        for i in Servers:
            server_name = i.filter("key", "server_name")[0].value
            id = int(str(f_id)+"3" + str(s_id + 1))
            jsondict = {"id": id, "pId": int(str(f_id)+"3"), "name": server_name}
            s_id = s_id + 1
            # print type(s_id),s_id
            jsonlist.append(jsondict)
        f_id = f_id + 1
        # mylocation = c.children
        # print Upstreams,"-----------",Servers
    return template('nginx_tree',nginx_tree=json.dumps(jsonlist),media_prefix=media_prefix)

@route('/nginxview')
@auth_required()
def nginxview():
    return template('nginxview',
                    nginx_version="20170101",
                    nginx_cons="1.2.3",
                    last_save="qqqq",
                    uptime_in_seconds="41434",
                    last_save_time="12123213",
                    media_prefix=media_prefix)


@route('/upstream_edit')
@auth_required()
def upstream_edit():
    upstream_name = request.GET.get('upstream_name', '')
    # print upstream_name,"qqqqqqqqqqqqqqqqqqqqqqqqqqqqq"
    c = nginx.loadf("modules.conf")
    u = c.filter(btype="Upstream", name=upstream_name)
    keys=u[0].keys
    rows=len(keys)
    upstream_value=""
    for i in keys:
        upstream_value= upstream_value+i.name+" "+i.value+"\r\n"
    return template('upstream_edit',upstream_name=upstream_name,upstream_value=upstream_value,rows=rows+5,media_prefix=media_prefix)


@route('/upstream_submit',method='POST')
@auth_required()
def upstream_submit():
    upstreams=request.POST.get('upstreams_name', '')
    print upstreams

    return upstreams

@route('/server_edit')
@auth_required()
def server_edit():
    server_name = request.GET.get('server_name', '')
    print server_name
    c = nginx.loadf("modules.conf")
    servers = c.filter("Server")
    for i in servers:
        if server_name==i.filter("key","server_name")[0].value:
            # print type(i),222222,server_name
            server_value = "".join(i.as_strings)
            rows=len(i.as_strings)

            # server_value=json.dumps(server_value)
            # if server_name==
    # keys=u[0].keys
    # upstream_value=""
    # for i in keys:
    #     upstream_value= upstream_value+i.name+" "+i.value+"\r\n"
    return template('server_edit',server_name=server_name,server_value=server_value,rows=rows+5,media_prefix=media_prefix)


@route('/db_tree')
@auth_required()
def db_tree():
    from over_view import get_all_trees
    import config
    try:
        cur_server_index = int(request.GET.get('s', '0'))
        cur_db_index = int(request.GET.get('db', '0'))
        cur_scan_cursor = int(request.GET.get('cursor', '0'))
    except:
        cur_server_index = 0
        cur_db_index = 0
        cur_scan_cursor = 0
    key = request.GET.get('k', '*')
    all_trees = get_all_trees(cur_server_index, key, db=cur_db_index, cursor=cur_scan_cursor)
    if type(all_trees) == list:
        next_scan_cursor, count = all_trees.pop()
        all_trees_json = json_dumps(all_trees)
        error_msg = ''
    else:
        next_scan_cursor, count = 0, 0
        all_trees_json = []
        error_msg = all_trees
    m_config = config.base
    return template('db_tree',
                    all_trees=all_trees_json,
                    config=m_config,
                    cur_server_index=cur_server_index,
                    cur_db_index=cur_db_index,
                    cur_scan_cursor=next_scan_cursor,
                    pre_scan_cursor=cur_scan_cursor,
                    cur_search_key=(key != '*' and key or ''),
                    count=count,
                    error_msg=error_msg,
                    media_prefix=media_prefix
                    )


@route('/db_view')
@auth_required()
def db_view():
    try:
        cur_server_index = int(request.GET.get('s', 'server0').replace('server', ''))
        cur_db_index = int(request.GET.get('db', 'db0').replace('db', ''))
    except:
        cur_server_index = 0
        cur_db_index = 0
    key = request.GET.get('k', '*')
    return template("db_view", media_prefix=media_prefix, cur_server_index=cur_server_index, cur_db_index=cur_db_index,
                    keyword=key)


@route('/server_tree')
@auth_required()
def server_tree():
    from over_view import get_db_trees
    all_trees = get_db_trees()
    return template("server_tree", all_trees=json_dumps(all_trees), media_prefix=media_prefix)


@route('/')
@auth_required()
def server_view():
    return template("main", media_prefix=media_prefix)


@route('/overview')
@auth_required()
def overview():
    from over_view import get_redis_info
    return template('overview', redis_info=get_redis_info(), media_prefix=media_prefix)


@route('/view')
@auth_required()
def view():
    from data_view import general_html, title_html
    fullkey = request.GET.get('key', '')
    refmodel = request.GET.get('refmodel', None)
    cl, cur_server_index, cur_db_index = get_cl()
    if cl.exists(fullkey):
        title_html = title_html(fullkey, cur_server_index, cur_db_index)
        general_html = general_html(fullkey, cur_server_index, cur_db_index, cl)
        out_html = title_html + general_html
        if refmodel:
            return out_html
        else:
            return template('view', out_html=out_html, media_prefix=media_prefix)
    else:
        return '  This key does not exist.'


@route('/edit')
@auth_required()
def edit():
    from data_change import edit_value
    key = request.GET.get('key', None)
    value = request.GET.get('value', None)
    type = request.GET.get('type', None)
    new = request.GET.get('new', None)
    score = request.GET.get('score', None)
    cl, cur_server_index, cur_db_index = get_cl()
    edit_value(key, value, new, score, type, cl)
    if new:
        return '<script type=text/javascript> alert("ok");window.location.href=document.referrer</script>'
    else:
        return '<script type=text/javascript> alert("error: missing new value");'\
               'window.location.href=document.referrer</script>'


@route('/add')
@auth_required()
def add():
    from data_change import add_value
    key = request.GET.get('key', None)
    value = request.GET.get('value', None)
    type = request.GET.get('type', None)
    name = request.GET.get('name', None)
    score = request.GET.get('score', None)
    cl, cur_server_index, cur_db_index = get_cl()
    add_value(key, value, name, score, type, cl)
    return '<script type=text/javascript> alert("ok");window.location.href=document.referrer</script>'


def get_cl():
    from config import base
    from redis_api import get_client
    try:
        cur_server_index = int(request.GET.get('s', '0'))
        cur_db_index = int(request.GET.get('db', '0'))
    except:
        cur_server_index = 0
        cur_db_index = 0
    server = base['servers'][cur_server_index]
    cl = get_client(host=server['host'], port=server['port'], db=cur_db_index,
                    password=server.has_key('password') and server['password'] or None)
    return cl, cur_server_index, cur_db_index


@route('/delete')
@auth_required()
def delete():
    from data_change import delete_key, delete_value
    key = request.GET.get('key', '')
    value = request.GET.get('value', None)
    type = request.GET.get('type', None)
    cur_scan_cursor = request.GET.get('cursor', None)
    cl, cur_server_index, cur_db_index = get_cl()
    if value:
        delete_value(key, value, type, cl)
    else:
        delete_key(key, cl, cursor=cur_scan_cursor)
        return '<script type=text/javascript> alert("ok")</script>'
    return '<script type=text/javascript> alert("ok");window.location.href=document.referrer</script>'


@route('/ttl')
@auth_required()
def ttl():
    from data_change import change_ttl
    cl, cur_server_index, cur_db_index = get_cl()
    key = request.GET.get('key', None)
    new = request.GET.get('new', None)
    if new:
        change_ttl(key, int(new), cl)
    return '<script type=text/javascript> alert("ok");window.location.href=document.referrer</script>'


@route('/rename')
@auth_required()
def rename():
    from data_change import rename_key
    cl, cur_server_index, cur_db_index = get_cl()
    key = request.GET.get('key', None)
    new = request.GET.get('new', None)
    rename_key(key, new, cl)
    return '<script type=text/javascript> alert("ok");parent.location.reload();</script>'


@route('/export')
def export():
    return 'Still in developme. You can see it in next version.'


@route('/import')
def iimport():
    return 'Still in developme. You can see it in next version.'


@route('/save')
@auth_required()
def save():
    cl, cur_server_index, cur_db_index = get_cl()
    cl.bgsave()
    return '<script type=text/javascript> alert("ok");window.location.href=document.referrer</script>'


@route('/auth/login', method=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.POST.get("username", '')
        password = request.POST.get("password", '')
        if password == config.admin_pwd and username == config.admin_user:
            session = get_current_session()
            session['username'] = username
            return {'code': 0, 'msg': 'OK'}
        else:
            return {'code': -1, 'msg': '用户名或密码错误'}
    else:
        return template('auth/login.html', config=config, media_prefix=media_prefix)


@route('/auth/logout')
def logout():
    session = get_current_session()
    del session['username']
    return redirect(request.params.get('next') or '/')


if __name__ == "__main__":
    from mole.mole import default_app
    from mole.sessions import SessionMiddleware

    app = SessionMiddleware(app=default_app(), cookie_key="457rxK3w54tkKiqkfqwfoiQS@kaJSFOo8h", no_datastore=True)
    run(app=app, host=config.host, port=config.port, reloader=config.debug)
