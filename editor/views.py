from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse
from django.core.files.storage import FileSystemStorage
import re,random,os,time
from django.contrib import messages
from django.conf import settings
import mimetypes

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
from moviepy.editor import VideoFileClip,concatenate_videoclips

def getDuration(input_file_path):
    return VideoFileClip(input_file_path).duration

def trim_video(input_file, output_file, start_time, end_time):
    ffmpeg_extract_subclip(input_file, start_time, end_time, targetname=output_file)

def home(request):
    return render(request,'editor/home.html')

def trim(request):  
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
            context={
                'vid_not_selected':True,
                'not_trimed':True,     
                'video_preview_url':None}
            cleanDir('trim')
            cleanDir('temp_trim')
            return render(request,'editor/trim.html', context)
        elif 'download' in request.POST:
            trimmed_video_path = getFilePath('temp_trim',True)
            if trimmed_video_path:
                with open(trimmed_video_path, 'rb') as video_file:
                    fl_path =  trimmed_video_path
                    filename = os.path.basename(fl_path)  
                    fl = open(fl_path, 'rb')
                    response = HttpResponse(fl, content_type='video/mp4')
                    response['Content-Disposition'] = "attachment; filename=%s" % filename
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
    if request.method=='POST':
        if 'video_file' in request.FILES:
            uploaded_video = request.FILES['video_file']
            fs = FileSystemStorage()
            existsDir('split')
            if len(os.listdir(os.path.join(settings.MEDIA_ROOT,'split')))!=0:
                cleanDir('split')
            filename = fs.save(os.path.join('split', uploaded_video.name), uploaded_video)
            video_url = fs.url(filename)
            context = {
                'vid_not_selected': False,
                'notSplit':True,
                'video_preview_url': video_url,
                'part_1':None,
                'part_2':None,
            }               
            return render(request, 'editor/split.html', context)
        elif 'reset' in request.POST:
            context={
                'vid_not_selected':True,
                'notSplit':True,     
                'video_preview_url':None,
                'part_1':None,
                'part_2':None,
            }
            cleanDir('split')
            cleanDir(os.path.join('temp_split','part1'))
            cleanDir(os.path.join('temp_split','part2'))
            return render(request,'editor/split.html', context)
        elif 'download1' in request.POST:
            split_video_path = getFilePath(os.path.join('temp_split','part1'),True)
            if split_video_path:
                with open(split_video_path, 'rb') as video_file:
                    fl_path =  split_video_path
                    filename = os.path.basename(fl_path)  
                    fl = open(fl_path, 'rb')
                    response = HttpResponse(fl, content_type='video/mp4')
                    response['Content-Disposition'] = "attachment; filename=%s" % filename
                    return response
            context={
                'vid_not_selected':False,
                'notSplit':False,
                'part_1':getFilePath(os.path.join('temp_split','part1'),False),
                'part_2':getFilePath(os.path.join('temp_split','part2'),False)
            }   
            return render(request,'editor/split.html',context)
        elif 'download2' in request.POST:
            split_video_path = getFilePath(os.path.join('temp_split','part2'),True)
            if split_video_path:
                with open(split_video_path, 'rb') as video_file:
                    fl_path =  split_video_path
                    filename = os.path.basename(fl_path)  
                    fl = open(fl_path, 'rb')
                    response = HttpResponse(fl, content_type='video/mp4')
                    response['Content-Disposition'] = "attachment; filename=%s" % filename
                    return response
            context={
                'vid_not_selected':False,
                'notSplit':False,
                'part_1':getFilePath(os.path.join('temp_split','part1'),False),
                'part_2':getFilePath(os.path.join('temp_split','part2'),False)
            }   
            return render(request,'editor/split.html',context)
        else:
            split_time = time_to_seconds(request.POST['split_time'])
            input_file_path = getFilePath('split',True)
            duration = getDuration(input_file_path)
            if split_time > duration:
                messages.error(request,f"Duration : {duration} smaller than split time:{split_time}")
                context = {
                    'vid_not_selected':False,
                    'notSplit':True,
                    'video_preview_url':getFilePath('split',False),
                    'part_1':None,
                    'part_2':None,
                }   
                return render(request,'editor/split.html',context)
            video = VideoFileClip(input_file_path)
            part1 = video.subclip(0, split_time)
            part2 = video.subclip(split_time, duration)
            part1.write_videofile(os.path.join(settings.MEDIA_ROOT,'temp_split','part1',os.path.basename(input_file_path).split('/')[-1]))
            part2.write_videofile(os.path.join(settings.MEDIA_ROOT,'temp_split','part2',os.path.basename(input_file_path).split('/')[-1]))
            context = {
                'vid_not_selected':False,
                'notSplit':False,
                'video_preview_url':None,
                'part_1':getFilePath(os.path.join('temp_split','part1'),False),
                'part_2':getFilePath(os.path.join('temp_split','part2'),False),
            } 
            return render(request,'editor/split.html',context)
    context = {
        'vid_not_selected':True,
        'notSplit':True,
        'video_preview_url':None,
        'part_1':None,
        'part_2':None,
    }
    existsDir('split')
    existsDir('temp_split')
    existsDir(os.path.join('temp_split','part1'))
    existsDir(os.path.join('temp_split','part2'))
    if len(os.listdir(os.path.join(settings.MEDIA_ROOT,'split')))!=0:
        context['vid_not_selected']=False
        context['video_preview_url']=getFilePath('split',False)
    if len(os.listdir(os.path.join(settings.MEDIA_ROOT,'temp_split','part1')))!=0:
        context['notSplit']=False
        context['part_1']=getFilePath(os.path.join('temp_split','part1'),False)
        context['part_2']=getFilePath(os.path.join('temp_split','part2'),False)
    return render(request,'editor/split.html',context)

def merge(request):
    if request.method == 'POST':
        if 'video_file1' in request.FILES:
            video1 = request.FILES['video_file1']
            video2 = request.FILES['video_file2']
            fs = FileSystemStorage()
            video_path1 = fs.save(os.path.join('merge', 'part1',video1.name), video1)
            video_path2 = fs.save(os.path.join('merge', 'part2',video2.name), video2)
            video1_clip = VideoFileClip(os.path.join(settings.MEDIA_ROOT,video_path1))
            video2_clip = VideoFileClip(os.path.join(settings.MEDIA_ROOT,video_path2))
            # Merge the two video clips
            final_video = concatenate_videoclips([video1_clip, video2_clip])
            # Save the final video to the output path
            final_video.write_videofile(os.path.join(settings.MEDIA_ROOT,'temp_merge','output.mp4'),codec="libx264")
            context = {
                'vids_not_merged':False,
                'video_preview_url':getFilePath('temp_merge',False)
            }
            return render(request,'editor/merge.html',context)
        elif 'reset' in request.POST:
            context={
                'vids_not_merged':True,
                'video_preview_url':None,
            }
            cleanDir('temp_merge')
            cleanDir(os.path.join('merge','part1'))
            cleanDir(os.path.join('merge','part2'))
            return render(request,'editor/merge.html', context)
        elif 'download' in request.POST:
            merged_video_path = getFilePath('temp_merge',True)
            if merged_video_path:
                with open(merged_video_path, 'rb') as video_file:
                    fl_path =  merged_video_path
                    filename = os.path.basename(fl_path)  
                    fl = open(fl_path, 'rb')
                    response = HttpResponse(fl, content_type='video/mp4')
                    response['Content-Disposition'] = "attachment; filename=%s" % filename
                    return response
            context={
                'vids_not_merged':False,
                'video_preview_url':getFilePath('temp_trim',False),
            }   
            return render(request,'editor/merge.html',context)
    existsDir('temp_merge')
    existsDir('merge')
    existsDir(os.path.join('merge','part1'))
    existsDir(os.path.join('merge','part2'))
    context = {
        'vids_not_merged':True,
        'video_preview_url':None
    }
    if len(os.listdir(os.path.join(settings.MEDIA_ROOT,'temp_merge')))!=0:
        context['vids_not_merged']=False
        context['video_preview_url']=getFilePath('temp_merge',False)
    return render(request,'editor/merge.html',context)