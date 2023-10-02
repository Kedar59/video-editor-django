from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse
from django.core.files.storage import FileSystemStorage
import re,random,os,time
from django.contrib import messages
from django.conf import settings

def cleanDir(folder_name):
    dir = os.path.join(settings.MEDIA_ROOT,folder_name)
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))

def existsDir(folder_name):
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT,folder_name)):
        path=os.path.join(settings.MEDIA_ROOT,folder_name)
        os.mkdir(path)
def getFilePath(foldername,root):
    for file in os.listdir(os.path.join(settings.MEDIA_ROOT,foldername)):
        if root:
            return os.path.join(settings.MEDIA_ROOT,foldername,file)
        else:
            return os.path.join(settings.MEDIA_URL,foldername,file)
def time_to_seconds(time_str):
    hours, minutes, seconds = map(int, time_str.split(':'))
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds
# video editing stuff
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip

def getDuration(input_file_path):
    return VideoFileClip(input_file_path).duration

def trim_video(input_file, output_file, start_time, end_time):
    ffmpeg_extract_subclip(input_file, start_time, end_time, targetname=output_file)

def home(request):
    return render(request,'editor/home.html')
def trim(request):
    if 'trimed_count' not in request.session:
        request.session['trimed_count'] = 0 
    if request.method == 'POST':
        if 'video_file' in request.FILES:
            uploaded_video = request.FILES['video_file']
            fs = FileSystemStorage()
            existsDir('trim')
            if len(os.listdir(os.path.join(settings.MEDIA_ROOT,'trim')))!=0:
                cleanDir('trim')

            filename = fs.save(os.path.join('trim', uploaded_video.name), uploaded_video)
            video_url = fs.url(filename)
            
            context = {
                'vid_not_selected': False,
                'not_trimed':True,
                'video_preview_url': video_url,
            }               
            return render(request, 'trim.html', context)
        elif 'reset' in request.POST:
            request.session['trimed_count'] = 0
            context={
                'vid_not_selected':True,
                'not_trimed':True,     
                'video_preview_url':None}
            cleanDir('trim')
            cleanDir('temp_trim')
            return render(request,'editor/trim.html', context)
        elif 'download' in request.POST:
            trimmed_video_path = getFilePath('temp_trim',True)
            print(trimmed_video_path)
            if trimmed_video_path:
                with open(trimmed_video_path, 'rb') as video_file:
                    # Use FileResponse to send the file for download
                    response = FileResponse(video_file)
                    # Set content type for the response
                    response['Content-Type'] = 'video/mp4'
                    # Set content-disposition to trigger download
                    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(trimmed_video_path)}"'
                    return response
            context={
                'vid_not_selected':True,
                'not_trimed':True,
                'video_preview_url':None
            }   
            return render(request,'editor/trim.html',context)
        else:
            start_time = time_to_seconds(request.POST['start_time'])
            end_time = time_to_seconds(request.POST['end_time'])
            input_file_path = getFilePath('trim',True)
            duration = getDuration(input_file_path)
            if end_time > duration:
                messages.error(request,f"Duration : {duration} smaller than end time:{end_time}")
                context = {
                    'vid_not_selected': False,
                    'not_trimed':True,
                    'video_preview_url': getFilePath('trim',False),
                }   
                return render(request,'editor/trim.html',context)
            elif end_time < start_time:
                messages.error(request,f"End time : {end_time} smaller than start time:{start_time}")
                context = {
                    'vid_not_selected': False,
                    'not_trimed':True,
                    'video_preview_url': getFilePath('trim',False),
                }   
                return render(request,'editor/trim.html',context)
            existsDir('temp_trim')
            output_file_path = os.path.join(settings.MEDIA_ROOT,'temp_trim',os.path.basename(input_file_path).split('/')[-1])
            request.session['trimed_count'] += 1
            output_file_path = f"{output_file_path[:-4]}-v{request.session['trimed_count']}.mp4"
            trim_video(input_file_path,output_file_path,start_time,end_time)
            context={
                'vid_not_selected':False,
                'not_trimed':False,
                'video_preview_url':getFilePath('temp_trim',False)
            }
            return render(request,'editor/trim.html',context)
    existsDir('trim')
    existsDir('temp_trim')
    context={
        'vid_not_selected':True,
        'not_trimed':True,
        'video_preview_url':None
    }
    if len(os.listdir(os.path.join(settings.MEDIA_ROOT,'trim')))!=0:
        context['vid_not_selected']=False
        context['video_preview_url']=getFilePath('trim',False)
    if len(os.listdir(os.path.join(settings.MEDIA_ROOT,'temp_trim')))!=0:
        context['not_trimed']=False
        context['video_preview_url']=getFilePath('temp_trim',False)
    return render(request, 'editor/trim.html', context)
def split(request):
    return render(request,'editor/split.html')
def merge(request):
    return render(request,'editor/merge.html')