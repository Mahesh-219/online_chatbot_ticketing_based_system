from datetime import datetime
import base64
import os.path
import time
import json
from flask import Flask, request, redirect, url_for, render_template, session, jsonify
import firebase_admin
import random
from firebase_admin import credentials, firestore
from MailSent import send_email
import razorpay
from chatbot import get_chatbot_response

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)
app = Flask(__name__)
app.secret_key = "OnlineChatbotSystem@123"
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

RAZOR_KEY_ID="rzp_test_bwFUQvFdcBdnqI"
RAZOR_KEY_SECRET="NN9Yi7mL7s15FtqgWGOLr5Zp"
razorpay_client = razorpay.Client(auth=(RAZOR_KEY_ID, RAZOR_KEY_SECRET))

@app.route('/customerchatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        data = request.get_json()
        user_message = data.get('message')
        bot_response = get_chatbot_response(user_message)
        return jsonify({"response": bot_response})
    else:
        return render_template('customerchatbot.html')  # Render the chatbot page if accessed via GET

@app.route('/')
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        return str(e)

@app.route('/customermainpage')
def customermainpage():
    try:
        return render_template("customermainpage.html")
    except Exception as e:
        return str(e)

@app.route('/index')
def indexpage():
    try:
        return render_template("index.html")
    except Exception as e:
        return str(e)

@app.route('/logout')
def logoutpage():
    try:
        session['id']=None
        return render_template("index.html")
    except Exception as e:
        return str(e)

@app.route('/about')
def aboutpage():
    try:
        return render_template("about.html")
    except Exception as e:
        return str(e)

@app.route('/services')
def servicespage():
    try:
        return render_template("services.html")
    except Exception as e:
        return str(e)

@app.route('/gallery')
def gallerypage():
    try:
        return render_template("gallery.html")
    except Exception as e:
        return str(e)

@app.route('/adminlogin', methods=['GET','POST'])
def adminloginpage():
    msg=""
    if request.method == 'POST':
        uname = request.form['uname'].lower()
        pwd = request.form['pwd'].lower()
        print("Uname : ", uname, " Pwd : ", pwd)
        if uname == "admin" and pwd == "admin":
            return redirect("adminmainpage")
        else:
            msg = "UserName/Password is Invalid"
    return render_template("adminlogin.html", msg=msg)

@app.route('/customerlogin', methods=['GET','POST'])
def customerlogin():
    msg=""
    if request.method == 'POST':
        uname = request.form['uname']
        pwd = request.form['pwd']
        db = firestore.client()
        dbref = db.collection('newcustomer')
        userdata = dbref.get()
        data = []
        for doc in userdata:
            print(doc.to_dict())
            print(f'{doc.id} => {doc.to_dict()}')
            data.append(doc.to_dict())
        flag = False
        for temp in data:
            print("Pwd : ", temp['Password'])
            decode = base64.b64decode(temp['Password']).decode("utf-8")
            if uname == temp['UserName'] and pwd == decode:
                session['userid'] = temp['id']
                session['username'] = temp['FirstName'] + " " + temp['LastName']
                flag = True
                break
        if (flag):
            return render_template("customermainpage.html")
        else:
            msg = "UserName/Password is Invalid"
    return render_template("customerlogin.html", msg=msg)

@app.route('/stafflogin', methods=['GET','POST'])
def staffloginpage():
    msg=""
    if request.method == 'POST':
        uname = request.form['uname']
        pwd = request.form['pwd']
        db = firestore.client()
        dbref = db.collection('newstaff')
        userdata = dbref.get()
        data = []
        for doc in userdata:
            print(doc.to_dict())
            print(f'{doc.id} => {doc.to_dict()}')
            data.append(doc.to_dict())
        flag = False
        for temp in data:
            #decMessage = fernet.decrypt(temp['Password']).decode()
            decode = base64.b64decode(temp['Password']).decode("utf-8")
            if uname == temp['UserName'] and pwd == decode:
                session['userid'] = temp['id']
                flag = True
                break
        if (flag):
            return render_template("staffmainpage.html")
        else:
            msg = "UserName/Password is Invalid"
    return render_template("stafflogin.html", msg=msg)

@app.route('/staffviewprofile')
def staffviewprofile():
    try:
        id = session['userid']
        db = firestore.client()
        data = db.collection('newstaff').document(id).get().to_dict()
        print("User Data ", data)
        return render_template("staffviewprofile.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/customerviewprofile')
def customerviewprofile():
    try:
        id=session['userid']
        db = firestore.client()
        data = db.collection('newcustomer').document(id).get().to_dict()
        print("Customer Data ", data)
        return render_template("customerviewprofile.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/newcustomer', methods=['POST','GET'])
def addnewemployee():
    try:
        msg=""
        print("Add New Customer page")
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            uname = request.form['uname']
            pwd = request.form['pwd']
            email = request.form['email']
            phnum = request.form['phnum']
            address = request.form['address']
            id = str(round(time.time()))
            encode = base64.b64encode(pwd.encode("utf-8"))
            print("str-byte : ", encode)
            json = {'id': id,
                    'FirstName': fname, 'LastName': lname,
                    'UserName': uname, 'Password': encode,
                    'EmailId': email, 'PhoneNumber': phnum,
                    'Address':address}
            db = firestore.client()
            newuser_ref = db.collection('newcustomer')
            newuser_ref.document(id).set(json)
            print("Customer Inserted Success")
            msg = "New Customer Added Success"            
        return render_template("newcustomer.html", msg=msg)
    except Exception as e:
        return str(e)

@app.route('/customerbookticket')
def customerbookticket():
    try:
        id=session['userid']
        db = firestore.client()
        data = db.collection('newcustomer').document(id).get().to_dict()
        print("Customer Data ", data)
        # current time and date
        # datetime object
        time = datetime.now()
        # formatting date using strftime
        # format = MM/DD/YY
        today=time.strftime("%Y-%m-%d")
        print(today)
        return render_template("customerbookticket.html",data=data,
                               today=today)
    except Exception as e:
        return str(e)

@app.route('/customerbookticket1', methods=['POST','GET'])
def customerbookticket1():
    try:
        print("Add New Customer page")
        if request.method == 'POST':
            cid = request.form['cid']
            fname = request.form['fname']
            lname = request.form['lname']
            email = request.form['email']
            phnum = request.form['phnum']
            address = request.form['address']
            ticketdate = request.form['ticketdate']
            amount = request.form['amount']
            id = str(round(time.time()))
            json = {'id': id, 'CustomerId':cid,'TicketDate':ticketdate,
                    'Amount':amount,'FirstName': fname, 
                    'LastName': lname, 'PaymentStatus':'NotDone',
                    'EmailId': email, 'PhoneNumber': phnum,
                    'Address':address,'TicketStatus':'Booked'}
            db = firestore.client()
            newuser_ref = db.collection('ticketbooking')
            newuser_ref.document(id).set(json)
            print("Ticket Booking Success")           
        return redirect(url_for("customerviewbooked"))
    except Exception as e:
        return str(e)

@app.route('/customerviewreports', methods=['POST','GET'])
def customerviewreports():
    try:
        db = firestore.client()
        userid=session['userid']
        print("User Id : ",userid)
        newdata_ref = db.collection('ticketbooking')
        newdata = newdata_ref.get()
        data=[]
        total=0
        context = {}
        for doc in newdata:
            temp=doc.to_dict()
            if(str(temp['CustomerId'])==str(userid)):
                data.append(doc.to_dict())
                if(str(temp['PaymentStatus'])=='NotDone' and str(temp['TicketStatus'])=='Booked'):
                    total+=int(temp['Amount'])
        currency = 'INR'
        amount = 200*100  # Rs. 200
        if(total>0):
            amount=total*100
        session['total']=amount
        # Create a Razorpay Order
        razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                           currency=currency,
                                                           payment_capture='0'))
        # order id of newly created order.
        razorpay_order_id = razorpay_order['id']
        callback_url = 'usermakepayment'
        # we need to pass these details to frontend.
        context['razorpay_order_id'] = razorpay_order_id
        context['razorpay_merchant_key'] = RAZOR_KEY_ID
        context['razorpay_amount'] = amount
        context['currency'] = currency
        context['callback_url'] = callback_url        
        print("Customer View Reports Data " , data)
        return render_template("customerviewreports.html", data=data, total=total, context=context)
    except Exception as e:
        return str(e)

@app.route('/usermakepayment', methods=['POST','GET'])
def usermakepayment():
    # only accept POST request.
    if request.method == "POST":
        try:
            id = str(session['userid'])
            db = firestore.client()
            data_ref = db.collection('ticketbooking')
            newdata = data_ref.get()
            array=[]
            for doc in newdata:
                temp = doc.to_dict()
                if (str(temp['CustomerId']) == id and temp['TicketStatus'] == 'Booked' 
                    and temp['PaymentStatus'] == 'NotDone'):
                    array.append(temp['id'])
            for x in array:
                db = firestore.client()
                data_ref = db.collection(u'ticketbooking').document(x)
                data_ref.update({u'PaymentStatus': 'PaymentDone'})

            total=session['total']
            # get the required parameters from post request.
            payment_id = request.form['razorpay_payment_id', '']
            razorpay_order_id = request.form['razorpay_order_id', '']
            signature = request.form['razorpay_signature', '']
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            razorpay_client.payment.capture(payment_id, total)
            print("Res : ", json.dumps(razorpay_client.payment.fetch(payment_id)))
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            print("Result : ", result)
            if result is not None:
                amount = total  # Rs. 200
                try:
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)
                    # render success page on successful caputre of payment
                    return render_template('paymentsuccess.html')
                except:
                    # if there is an error while capturing payment.
                    return render_template('paymentfailure.html')
            else:
                # if signature verification fails.
                return render_template('paymentfailure.html')
        except:
            # if we don't find the required parameters in POST data
            #return HttpResponseBadRequest()
            return render_template('paymentfailure.html')
    else:
        # if other than POST request is made.
        #return HttpResponseBadRequest()
        return render_template('paymentfailure.html')

@app.route('/customerviewbooked', methods=['POST','GET'])
def customerviewbooked():
    try:
        db = firestore.client()
        userid=session['userid']
        print("User Id : ",userid)
        newdata_ref = db.collection('ticketbooking')
        newdata = newdata_ref.get()
        data=[]
        for doc in newdata:
            temp=doc.to_dict()
            print("Temp : ", temp)
            if(str(temp['CustomerId'])==str(userid) and temp['TicketStatus']=='Booked'):
                data.append(doc.to_dict())
        print("Customer Ticket Booked Data " , data)
        return render_template("customerviewbooked.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/customerviewcancelled', methods=['POST','GET'])
def customerviewcancelled():
    try:
        db = firestore.client()
        userid=session['userid']
        newdata_ref = db.collection('ticketbooking')
        newdata = newdata_ref.get()
        data=[]
        for doc in newdata:
            temp=doc.to_dict()
            if(str(temp['CustomerId'])==str(userid) and temp['TicketStatus']=='Cancelled'):
                data.append(doc.to_dict())
        print("Customer Ticket Cencelled Data " , data)
        return render_template("customerviewcancelled.html", data=data)
    except Exception as e:
        return str(e)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/contact', methods=['POST','GET'])
def contactpage():
    try:
        msg=""
        if request.method == 'POST':
            cname = str(request.form['cname'])
            subject = request.form['subject']
            message = request.form['message']
            email = request.form['email']
            id = str(round(time.time()))
            json = {'id': id,
                    'ContactName': cname, 'Subject': subject,
                    'Message': message,
                    'EmailId': email}
            db = firestore.client()
            newdb_ref = db.collection('newcontact')
            id = json['id']
            newdb_ref.document(id).set(json)
            body = "Thank you for contacting us, " + str(cname) + " We will keep in touch with in 24 Hrs"
            receipients = [email]
            send_email(subject,body,receipients)
            msg = "New Contact Added Success"
        return render_template("contact.html", msg=msg)
    except Exception as e:
        return str(e)

@app.route('/customercancelbooking', methods=['POST','GET'])
def customercancelbooking():
    try:
        ticketid=request.args['id']
        db = firestore.client()
        data_ref = db.collection('ticketbooking').document(ticketid)
        data_ref.update({u'TicketStatus': 'Cancelled'})
        return redirect(url_for("customerviewcancelled"))
    except Exception as e:
        return str(e)

@app.route('/adminviewcustomers', methods=['POST','GET'])
def adminviewcustomers():
    try:
        db = firestore.client()
        newdata_ref = db.collection('newcustomer')
        newdata = newdata_ref.get()
        data=[]
        for doc in newdata:
            data.append(doc.to_dict())
        print("Customer Data " , data)
        return render_template("adminviewcustomers.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminviewcancelled', methods=['POST','GET'])
def adminviewcancelled():
    try:
        db = firestore.client()
        data_ref = db.collection('ticketbooking')
        newdata = data_ref.get()
        data=[]
        for doc in newdata:
            temp=doc.to_dict()
            if(temp['TicketStatus']=='Cancelled'):
                data.append(doc.to_dict())
        print("Tickets Data " , data)
        return render_template("adminviewcancelled.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminviewbooked', methods=['POST','GET'])
def adminviewbooked():
    try:
        db = firestore.client()
        data_ref = db.collection('ticketbooking')
        newdata = data_ref.get()
        data=[]
        for doc in newdata:
            temp=doc.to_dict()
            if(temp['TicketStatus']=='Booked'):
                data.append(doc.to_dict())
        print("Tickets Data " , data)
        return render_template("adminviewbooked.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminviewreports', methods=['POST','GET'])
def adminviewreports():
    try:
        db = firestore.client()
        data_ref = db.collection('ticketbooking')
        newdata = data_ref.get()
        data=[]
        for doc in newdata:
            data.append(doc.to_dict())
        print("Tickets Data " , data)
        return render_template("adminviewreports.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminviewcontacts', methods=['POST','GET'])
def adminviewcontacts():
    try:
        db = firestore.client()
        newdata_ref = db.collection('newcontact')
        newdata = newdata_ref.get()
        data=[]
        for doc in newdata:
            data.append(doc.to_dict())
        print("Contact Data " , data)
        return render_template("adminviewcontacts.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminmainpage')
def adminmainpage():
    try:
        return render_template("adminmainpage.html")
    except Exception as e:
        return str(e)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.debug = True
    app.run()