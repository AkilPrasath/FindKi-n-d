from flask import Flask, render_template, url_for, redirect , flash ,request,send_from_directory, make_response
from forms import signupform, LoginForm 
# from bottle import response
import os
import pymongo
import numpy as np
# import requests
import cv2
import pickle
from bson.binary import Binary
# from PIL import Image
import face_recognition
import smtplib 
# import flask_login

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

client = pymongo.MongoClient("mongodb+srv://FindKind:FindKindpassword@findkind-he7yk.mongodb.net/test?retryWrites=true&w=majority")
db = client['database']

username_ =""
cv2_img = ""
parent_mail = ""
# database = pymongo.MongoClient(mongodb+srv://<username>:<password>@cluster0-bfyqk.mongodb.net/test?retryWrites=true&w=majority)
# dc=database['database']
# app.config['MONGODB_SETTINGS'] = {
#     'db': 'FindKind',
#     'host': 'mongodb+srv://FindKind:FindKindpassword@findkind-he7yk.mongodb.net/test?retryWrites=true&w=majority'
# }


@app.route("/")
@app.route("/signin", methods=["GET","POST"])
def signin():
    return render_template("login.html",title="login")


@app.route("/login",methods=["GET","POST"])
def login():
    emails= request.form.get("username")
    password = request.form.get("password")
    print(emails,password)
    for x in db.login.find():
        if(x["email"]==emails and x["password"]== password):
            global username_
            username_ = emails
            flash(f' Welcome {emails} !','success')
            return redirect(url_for('about'))
    
    flash(f'username or password invalid','danger')
    return render_template('login.html',title='login')


@app.route("/register", methods=["GET","POST"])
def register():
    return render_template('signup.html',title="register")

@app.route("/signup",methods=["GET","POST"])
def signup():
        usern= request.form.get("username")
        email= request.form.get("email")
        
        passw= request.form.get("password")
        mobile=request.form.get("number") 
        rec={"i":db.inc.find_one()['i'],
             "email":email,
             "username":usern,
             "mobile":mobile,
             "password":passw}
        db.login.insert_one(rec) 
        x=db.inc.find_one()
        db.inc.update({"i":x["i"]},{'$set':{"i":x["i"]+1}})
        
        #print(x["i"])     
        flash(f' Welcome {usern} !','success')
        return render_template('login.html',title='Login')

@app.route("/about")
def about():
    return render_template('about.html',title='About')

@app.route("/post")
def post():
    return render_template('post.html',title='lost')


@app.route("/post_found")
def postfound():
    return render_template('post_found.html',title='found')

@app.route("/uploading",methods=["POST"])
def uploading():
    child_name = request.form.get('child_name')
    global username_
    images = request.files.getlist('images[]')
    bin_img =[]
    for image in images:
        image = image.read()
        np_image = np.fromstring( image, np.uint8 )
        cv2_img = cv2.imdecode( np_image,1 )
        # fr_img = cv2_img[:,:,::-1]
        # encoding = face_recognition.face_encodings(fr_img)[0]
        bin_img.append( cv2_to_bin ( cv2_img ) )
    record = { "username": username_, "child": child_name ,"cv2": bin_img }
    db.lost.insert_one(record)
    flash(f'Image uploaded successfully!! We will notify you if we get a match.','success')
    return redirect(url_for('about'))

@app.route("/uploadingFound", methods=["POST"])
def uploadingFound():
    child_name = request.form.get('child_name')
    global username_
    images = request.files.getlist('images[]')
    bin_img = []
    for image in images:
        image = image.read()
        np_image = np.fromstring( image, np.uint8 )
        global cv2_img
        cv2_img = cv2.imdecode( np_image,1 )
        bin_img.append( cv2_to_bin ( cv2_img ) )
    record = { "username": username_, "child": child_name ,"cv2": bin_img }
    db.found.insert_one(record)
    flash(f'Thanks for your effort on saving a kid!')
    return redirect(url_for("match"))

@app.route("/logout",methods=["GET","POST"])
def logout():
    parent_mail=""
    username_ = ""
    cv2_img = ""
    return redirect("/")

@app.route("/match", methods=["GET"])
def match():
    global username_
    x = db.found.find_one({"username":username_})
    bin_cv2_list = x["cv2"]
    i = -1
    
    found_encodings = []
    lost_encodings = []
    username_list =[]
    for bin_cv2 in bin_cv2_list:
        cv = bin_to_cv2( bin_cv2 ) 
        fr = cv[:,:,::-1]
        found_encodings.append( face_recognition.face_encodings(fr)[0] )

    for x in db.lost.find():
        bin_cv2_list = x["cv2"]
        for bin_cv2 in bin_cv2_list:
            username_list.append( x["username"] )
            cv = bin_to_cv2(bin_cv2)
            fr = cv[:,:,::-1]
            lost_encodings.append(face_recognition.face_encodings(fr)[0])
    
    for found_encoding in found_encodings:
        result = face_recognition.compare_faces(lost_encodings,found_encoding)
        if True in result:
            i = result.index(True)
            break
    if(i>=0):
        print(username_list[i])
        global parent_mail
        parent_mail = username_list[i]
        mail()
    else:
        print("No Face")
    
    flash(f'Thank You for your patience','success')
    return redirect(url_for('about'))


def display_ip():
    """  Function To Print GeoIP Latitude & Longitude """
    ip_request = requests.get('https://get.geojs.io/v1/ip.json')
    my_ip = ip_request.json()['ip']
    geo_request = requests.get('https://get.geojs.io/v1/ip/geo/' +my_ip + '.json')
    geo_data = geo_request.json()
    return (geo_data['latitude'],geo_data['longitude'])

def mail():  
     
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    s.starttls() 
    s.login("find.or.bekind@gmail.com", "Bhavikkpatel#1") 
    lat,lon = display_ip()
    message = ("Mail from Find Ki(n)d,\n\tYour child may have been spotted by one of our users. Click on the link to find the area.\nLink: http://maps.google.com/maps?z=18&q="+lat+","+lon)
    s.sendmail("find.or.bekind@gmail.com", parent_mail, message) 
    s.quit()
   
def cv2_to_bin( cv2_img ):
    bin = Binary(pickle.dumps( cv2_img, protocol = 2 ), subtype=128)
    return (bin) 


def bin_to_cv2( bin ):
    cv = pickle.loads( bin ) 
    return cv

if __name__ == '__main__':
    app.run(debug=True)
