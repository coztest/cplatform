from django.shortcuts import render_to_response
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
import gevent.subprocess
import gevent
import time
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
    username = request.POST['username']
    password = request.POST['password']
    if username == "123" and password == "1":
        request.session["username"] = 123

        return HttpResponseRedirect("/mainpage")
    else:
        return HttpResponse("username or password is not correct!")


def newproj(request):
    if request.method == "POST":

        proj_name = request.POST["proj_name"]
        proj = Project()
        proj.proj_name = proj_name

        current_user = User.objects.get(id=1)

        proj.user = current_user
        proj.save()
    return HttpResponseRedirect("/mainpage")

def mainpage(request):
    n = request.session["username"]

 #   i1_avai = request.session["instance1_available"]
    i1_avai = Instance.objects.get(id=1).available
    proj_list = Project.objects.all()


    return render_to_response("home.html",{"username":n,"proj_list":proj_list,"i1_avai":i1_avai})


def instance1(request):
    return render_to_response("instance1.html")

def upload1(request,proj_id):
    file_obj = request.FILES.get('upload')
    filename = file_obj.name
    print(filename)
    f = open("/home/li/abc/"+filename,"wb+")
    for chunk in  file_obj.chunks():
        f.write(chunk)
    f.close()
    popen_tar = gevent.subprocess.Popen(['tar','-zxf',"/home/li/abc/"+filename,"-C","/home/li/abc/"])
    popen2_rm = gevent.subprocess.Popen(['rm','/home/li/abc/'+filename])
    popen3_ls = gevent.subprocess.Popen(['ls /home/li/abc/'], stdout = gevent.subprocess.PIPE,shell=True)
    popen3_ls_out = popen3_ls.stdout.readlines()
    proj_sourcelist = ""
    i = 1
    for source_name in popen3_ls_out:
        if i != len(popen3_ls_out):
            proj_sourcelist += source_name.replace("\n",", ")
        else:
            proj_sourcelist += source_name.replace("\n","")
        i += 1
    del i

    print proj_sourcelist
    Project.objects.filter(id=proj_id).update(sourcelist=proj_sourcelist)

    return HttpResponseRedirect('/webterm1/'+proj_id)

@accept_websocket
def echo(request):
    if request.is_websocket:
        print "gogogo1"
        print "gogogo2"
        for ms in request.websocket:
            if ms == "go":
                print "gogogo3"
                g = gevent.spawn(runterm1,request)
                Instance.objects.filter(id=1).update(available=False)
                g.start()

            elif ms == "stop":
                print "gogogo4"
                g.kill()
                term1_pid = request.session.get("term1_pid")
                print "kill "+ term1_pid
                popen = gevent.subprocess.call("kill "+term1_pid,shell=True)
		Instance.objects.filter(id=1).update(available=True)


def runterm1(request):

    popen = gevent.subprocess.Popen(['bash','/home/li/run_instance1.sh'], stdout = gevent.subprocess.PIPE)
#    popen = gevent.subprocess.Popen(['ping','127.0.0.1'], stdout = gevent.subprocess.PIPE)

    term1_pid = str(popen.pid)
    request.session['term1_pid'] = term1_pid
    print term1_pid
    while popen.poll()==None :
        request.websocket.send(popen.stdout.readline()+"<br>")
        gevent.sleep(0.001)
    Instance.objects.filter(id=1).update(available=True)






def webterm1(request,proj_id):
    return render_to_response("webterm1.html",{"proj_id":proj_id})
