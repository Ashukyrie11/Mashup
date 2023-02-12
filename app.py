from flask import Flask, render_template,request
import glob
import os
import sys
from youtube_search import YoutubeSearch
from pydub import AudioSegment
import youtube_dl
import moviepy.editor as mp
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pydub import AudioSegment
import moviepy.editor as mp
import zipfile
app=Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route("/",methods=['POST'])
def home():
    singer=request.form['singername']
    num_videos=request.form['no_of_videos']
    duration=request.form['timestamp']
    email=request.form['email']
    main(singer,num_videos,duration,email)
    return "<h1><center>10 rupaye ki pepsi. Rana sir sexy.</center></h1>"

def download_audios(youtube_links):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(title)s.%(ext)s',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl: 
        ydl.download([youtube_links])

def cut_audios(audio_file, start, end):
    audio = mp.AudioFileClip("./"+audio_file)
    audio_cut = audio.subclip(start, end)
    audio_cut.write_audiofile(audio_file)

def main(singer,num_videos,duration,email):
    num_videos = int(num_videos)
    duration = int(duration)
    results = YoutubeSearch(singer, max_results=num_videos).to_dict()
    youtube_links=[]
    for i in range(num_videos):
        youtube_links.append(results[i]['url_suffix'])
        youtube_links[i]="https://www.youtube.com/"+youtube_links[i]
        download_audios(youtube_links[i])
    files = glob.glob('./*.mp3')
    for i in range(0,num_videos):
        audio_file = files[i]
        cut_audios(audio_file, 0, duration)
    audio_folder='.'
    audio_files = [audio_folder+'/'+img for img in os.listdir(audio_folder) if img.endswith(".mp3")]
    print(audio_files)
    audios = []
    for audio in audio_files :
        audios.append(mp.AudioFileClip(audio))
    audioClips = mp.concatenate_audioclips([audio for audio in audios])
    audioClips.write_audiofile("./102003614.mp3")
    zip = zipfile.ZipFile("102003614.zip", "w", zipfile.ZIP_DEFLATED)
    zip.write("./102003614.mp3")
    zip.close()
    fromaddr = "email id "
    toaddr = email
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "DS Assignment-2"
    filename = "102003614.zip"
    attachment = open("./102003614.zip", "rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, "password")
    text = msg.as_string()
    s.sendmail(fromaddr, toaddr, text)
    s.quit()
    
if __name__=="__main_":
    app.run(debug=True)