#coding=utf-8
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
import gevent.subprocess
import gevent
import time
import os
import signal
import shutil
from models import *
from gevent.local import local
from dwebsocket.decorators import accept_websocket
# Create your views here.

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def index(request):
    return render_to_response("login.html",context_instance=RequestContext(request))
def login(request):
    login_username = request.POST['username']
    login_password = request.POST['password']


    try:
        user = User.objects.get(username=login_username)
    except User.DoesNotExist:
            return HttpResponse("user is not exist, please register!")
    else:
        if login_password == user.password:
            request.session["username"] = user.username
            if os.path.exists('/home/li/souce-result/'+user.username+'/') == False:
                os.makedirs('/home/li/souce-result/'+user.username+'/')


            return HttpResponseRedirect("/mainpage")
        else:
            return HttpResponse("用户名或密码不正确!")






def newproj(request):
    if request.method == "POST":

        proj_name = request.POST["proj_name"]
        proj = Project()
        proj.proj_name = proj_name

        current_username = request.session["username"]
        current_user = User.objects.get(username=current_username)
        proj.user = current_user
        proj.save()
        if os.path.exists('/home/li/souce-result/'+current_username+'/'+str(proj.id)+'/') == False:
            os.makedirs('/home/li/souce-result/'+current_username+'/'+str(proj.id)+'/')
            if os.path.exists('/home/li/souce-result/'+current_username+'/'+str(proj.id)+'/'+'sources/') == False:
                os.makedirs('/home/li/souce-result/'+current_username+'/'+str(proj.id)+'/'+'sources/')
            if os.path.exists('/home/li/souce-result/'+current_username+'/'+str(proj.id)+'/'+'results/') == False:
                os.makedirs('/home/li/souce-result/'+current_username+'/'+str(proj.id)+'/'+'results/')
            if os.path.exists('/home/li/souce-result/'+current_username+'/'+str(proj.id)+'/'+'logs/') == False:
                os.makedirs('/home/li/souce-result/'+current_username+'/'+str(proj.id)+'/'+'logs/')



    return HttpResponseRedirect("/mainpage")

def mainpage(request):
    username = request.session["username"]
    current_user = User.objects.get(username=username)
 #   i1_avai = request.session["instance1_available"]
    i1_avai = Instance.objects.get(id=1).available


    proj_list = Project.objects.filter(user=current_user)


    return render_to_response("home.html",{"username":username,"proj_list":proj_list,"i1_avai":i1_avai})

def upload1(request,proj_id):
    #清理临时上传目录
    popen_clear_ls = gevent.subprocess.Popen(['ls /home/li/abc/'], stdout = gevent.subprocess.PIPE,shell=True)
    popen_clear_ls_out = popen_clear_ls.stdout.readlines()
    if popen_clear_ls_out != []:
          popen_clear_rm = gevent.subprocess.call('rm -r /home/li/abc/*', shell=True)

    #上传源码
    file_obj = request.FILES.get('upload')
    filename = file_obj.name
    f = open("/home/li/abc/"+filename,"wb+")
    for chunk in  file_obj.chunks():
        f.write(chunk)
    f.close()

    #解压源码目录，删除压缩包
    popen_tar = gevent.subprocess.Popen(['tar','-zxf',"/home/li/abc/"+filename,"-C","/home/li/abc/"])
    popen_tar.wait()
    popen2_rm = gevent.subprocess.Popen(['rm','/home/li/abc/'+filename])
    current_username = request.session["username"]
    #上传源码拷贝到用户工程sources目录下
    popen_cp = gevent.subprocess.call('cp -r /home/li/abc/*/ /home/li/souce-result/'+current_username+'/'+proj_id+'/'+'sources/', shell=True)
    #获取源码目录名，将其写入数据库
    popen3_ls = gevent.subprocess.Popen(['ls /home/li/abc/'], stdout = gevent.subprocess.PIPE,shell=True)
    popen3_ls_out = popen3_ls.stdout.readlines()
    proj_sourcelist = parse_pkgs_done(popen3_ls_out)
    Project.objects.filter(id=proj_id).update(sourcelist=proj_sourcelist)

    return HttpResponseRedirect('/webterm1/'+proj_id)

@accept_websocket
def echo(request):

    if request.is_websocket:
        for ms in request.websocket:
            if ms.split('-')[0] == "go":
                #启动编译任务
                proj_id = ms.split('-')[1]
                g = gevent.spawn(runterm1,request,proj_id)
                Instance.objects.filter(id=1).update(available=False)
                g.start()

            elif ms.split('-')[0] == "stop":
                #停止编译任务
                proj_id = ms.split('-')[1]
                term1_pid = request.session.get("term1_pid")
                print "kill "+ term1_pid

                os.kill(int(term1_pid),signal.SIGINT)
                g.kill()
                #停止任务后将已经编译成功的源码列表写入数据库
                popen_cat = gevent.subprocess.Popen(['cat /home/li/compile_env/workers/instance1/state/pkgs_done'], stdout = gevent.subprocess.PIPE,shell=True)
                popen_cat_out = popen_cat.stdout.readlines()
                proj_done_sourcelist = parse_pkgs_done(popen_cat_out)
                Project.objects.filter(id=proj_id).update(complete_proj=proj_done_sourcelist)
                #编译完成将日志和结果移动到用户工程目录
                current_username = request.session['username']
                popen_mv_logs = gevent.subprocess.call('mv /home/li/compile_env/workers/instance1/logs/* /home/li/souce-result/'+current_username+'/'+proj_id+'/'+'logs/', shell=True)
                popen_mv_results = gevent.subprocess.call('mv /home/li/compile_env/workers/instance1/results/* /home/li/souce-result/'+current_username+'/'+proj_id+'/'+'results/', shell=True)

                #更新编译环境1的运行状态，变为可用
                Instance.objects.filter(id=1).update(available=True)






def runterm1(request,proj_id):

    popen = gevent.subprocess.Popen(['bash','/home/li/run_instance1.sh'], stdout = gevent.subprocess.PIPE)
    term1_pid = str(popen.pid)
    request.session['term1_pid'] = term1_pid
    print term1_pid
    while popen.poll()==None :
        request.websocket.send(popen.stdout.readline()+"<br>")
        gevent.sleep(0.001)

    #更新编译环境1的运行状态，变为可用
    Instance.objects.filter(id=1).update(available=True)

    #编译完成将成功源码列表写入数据库
    popen_cat = gevent.subprocess.Popen(['cat /home/li/compile_env/workers/instance1/state/pkgs_done'], stdout = gevent.subprocess.PIPE,shell=True)
    popen_cat_out = popen_cat.stdout.readlines()
    proj_done_sourcelist = parse_pkgs_done(popen_cat_out)
    Project.objects.filter(id=proj_id).update(complete_proj=proj_done_sourcelist)
    #编译完成将日志和结果移动到用户工程目录
    current_username = request.session['username']
    popen_mv_logs = gevent.subprocess.call('mv /home/li/compile_env/workers/instance1/logs/* /home/li/souce-result/'+current_username+'/'+proj_id+'/'+'logs/', shell=True)
    popen_mv_results = gevent.subprocess.call('mv /home/li/compile_env/workers/instance1/results/* /home/li/souce-result/'+current_username+'/'+proj_id+'/'+'results/', shell=True)




def webterm1(request,proj_id):
    return render_to_response("webterm1.html",{"proj_id":proj_id})



#把结果从list转为字符串
def parse_pkgs_done(list):
    proj_done_sourcelist = ""
    for i,element in enumerate(list):
        if i < len(list)-1:
            proj_done_sourcelist += element.replace("\n",", ")
        else:
            proj_done_sourcelist += element.replace("\n","")

    return proj_done_sourcelist