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


@route('/')
@auth_required()
def server_view():
    return template("main", media_prefix=media_prefix)


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
