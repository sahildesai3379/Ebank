from django.shortcuts import render,redirect
from datetime import datetime
import random
import string
import re
from django.contrib import messages
from .models import *
import requests
import json

def index(request):
    request.session.flush()
    return render(request,'index.html')

def createaccountpage(request):
    return render(request,'createaccount.html')

def check_acc_data(request):
    # try:
        global firstName,middlename,lastname,gndr,bday,actyp,add,mobilenumber,altnum,familymember,occupation,myincome,emailid,adharnumber,pannumber,len_of_mobile_and_pan,len_of_adharno,acc_bal,acc_create_OTP,acc_create_pass,acc_create_number,dt_string
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        acc_create_number=''.join(random.choice(string.digits) for _ in range(10))
        acc_create_pass=''.join(random.choice(string.digits) for _ in range(6))
        acc_create_OTP =''.join(random.choice(string.digits) for _ in range(6))
        firstName=request.POST['fname']
        middlename=request.POST['mname']
        lastname=request.POST['lname']
        gndr=request.POST['gender']
        bday=request.POST['birthday']
        actyp=request.POST['actype']
        add=request.POST['address']
        mobilenumber=request.POST['mnumber']
        altnum=request.POST['altnumber']
        familymember=request.POST['fmember']
        occupation=request.POST['occu']
        myincome=request.POST['income']
        emailid=request.POST['eid']
        adharnumber=request.POST['adharno']
        pannumber=request.POST['panno']
        len_of_mobile_and_pan=10
        len_of_adharno=12
        acc_bal=0
        
        if mobilenumber.isnumeric() and altnum.isnumeric() and familymember.isnumeric() and adharnumber.isnumeric() and firstName.isalpha() and middlename.isalpha() and lastname.isalpha() and occupation.isalpha() and len(adharnumber)==len_of_adharno and len(mobilenumber)==len_of_mobile_and_pan and len(altnum)==len_of_mobile_and_pan and len(pannumber)==len_of_mobile_and_pan:
            if Bankaccounts.objects.filter(AdharNo = adharnumber):
                return redirect('createaccountpage')
            elif Bankaccounts.objects.filter(MobileNo = mobilenumber):
                return redirect('createaccountpage')
            elif Bankaccounts.objects.filter(PANno= pannumber):
                return redirect('createaccountpage')
            else:
                print(acc_create_OTP)
                send_sms(mobilenumber,acc_create_OTP+":OTP For E-banking Account Create")
                messages.error(request,'OTP Was Sended To Your Registered Number')
                return render(request,'registration_otp.html')
        else:
            messages.error(request,'Something Is Wrong Fill Proper Details')
            return redirect('createaccountpage')
    # except:
    #     print('no')
        # messages.error(request,'Something Goes Wrong!!! Fill Proper Details')
        # return redirect('createaccountpage')

def registration_otp(request):
    acc_get_OTP=request.POST['create_acc_otp']
    global get_acc_id
    try:
        if acc_create_OTP==acc_get_OTP:
            account_list=Bankaccounts.objects.create(
                FirstName=firstName,
                MiddleName=middlename,
                LastName=lastname,
                Gender=gndr,
                BirthDate=bday,
                AccType=actyp,
                Address=add,
                MobileNo=mobilenumber,
                AltNumber=altnum,
                FamilyMem=familymember,
                OccuP=occupation,
                Income=myincome,
                EmailID=emailid,
                AdharNo=adharnumber,
                PANno=pannumber,
                NewAccountNo=acc_create_number,
                NewAccountPass=acc_create_pass,
                DateTime=dt_string,
                Account_bal=acc_bal
                )
            get_acc_id=account_list.id
            send_sms(mobilenumber,f"Your Account Create SuccessFully...Your Account Number is:{acc_create_number} and Account Paasword is:{acc_create_pass}")
            return redirect('datashow_after_acc_create')
        else:
            messages.error(request,'Incorrect OTP Please Try Again...')
            return redirect('index')
    except:
        messages.error(request,'Something Was Wrong.Please Try Again...')
        return redirect('index')

def datashow_after_acc_create(request):
    ac_details_show=Bankaccounts.objects.filter(id =get_acc_id)
    return render(request,'Datashow_aftAcc_create.html',{'ac_details':ac_details_show})

def login(request):
    login_acc_number=request.POST['account_number']
    login_acc_password=request.POST['account_Password']
    if Bankaccounts.objects.filter(NewAccountNo =login_acc_number,NewAccountPass=login_acc_password):
        request.session['account_number']=login_acc_number
        return redirect('home')
    else:
        messages.success(request, 'Incorrect Account Number And Password')
        return redirect('index')
       
        
def deletepage(request):
    login_acc_number=request.session['account_number']
    get_accid=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'delete.html',{'ac_holder_name':get_accid})

def delete_otp_page(request):
    dlt_acc_number=request.POST['ac_number']
    dlt_adhar_number=request.POST['adhar_number']
    login_acc_number=request.session['account_number']
    get_accid=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    get_mobno=Bankaccounts.objects.get(NewAccountNo =login_acc_number)
    global acc_dlt_OTP
    if Bankaccounts.objects.filter(NewAccountNo =dlt_acc_number,AdharNo=dlt_adhar_number):
        acc_dlt_OTP =''.join(random.choice(string.digits) for _ in range(6))
        print(acc_dlt_OTP)
        send_sms(get_mobno.MobileNo,acc_dlt_OTP+":OTP For E-banking Account Delete")
        return render(request,'deleteotp.html',{'ac_holder_name':get_accid})
    else:
        messages.success(request, 'Incorrect Account/Adhar Number')
        return redirect('deletepage')

def deletefinal(request,pk):
    otp_entered=request.POST['otp']
    delete_acc= Bankaccounts.objects.get(pk=pk)
    if int(acc_dlt_OTP)==int(otp_entered):
        delete_acc.delete()
        messages.success(request, 'Your Account Is Successfully Deleted')
        return redirect('index')
    else:
        messages.success(request, 'Incorrect OTP Number')
        return redirect('deletepage')

def home(request):
    login_acc_number=request.session['account_number']
    get_accid=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'home.html',{'ac_holder_name':get_accid})

def ac_details(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'inside_acc_detail.html',{'acc_data':showtopage})

def change_password(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'changepass.html',{'acc_data':showtopage})

def chack_change_pass(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    oldpass=request.POST['old_password']
    newpass=request.POST['new_password']
    renewpass=request.POST['re_new_password']
    now = datetime.now()
    dt_time = now.strftime("%d/%m/%Y %H:%M:%S")
    trans_number=''.join(random.choice(string.digits) for _ in range(8))

    if newpass==renewpass:
        old_fatched_pass=Bankaccounts.objects.get(NewAccountNo =login_acc_number)
        obj_check_pass=old_fatched_pass.NewAccountPass
        if int(oldpass)==int(obj_check_pass):
            Bankaccounts.objects.filter(NewAccountNo =login_acc_number).update(NewAccountPass=int(newpass))
            
            Transaction.objects.create(
                User_accnumber=login_acc_number,
                Transaction_name='Change Password',
                bill_number=0,
                Ammount=0,
                Transaction_id=trans_number,
                Date_Time=dt_time,
            )
            send_sms(old_fatched_pass.MobileNo,"Your E-banking Account Password Is Changed Successfully")
            return redirect('change_password')
        else:
            messages.success(request, 'Your Account Password Can Not Match')
            return redirect('change_password')
    else:
        messages.success(request, 'Your New Password And Confirm password Not Match')
        return redirect('change_password')

def bal_check(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'balance_check.html',{'bal_show':showtopage})


def money_trans_page(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'moneytransfer.html',{'ac_details':showtopage})

def money_transfer(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.get(NewAccountNo =login_acc_number)
    recive_acc=request.POST['recive_acc']
    account_passwd=request.POST['Ac_pass']
    amnt_transfer=request.POST['trans_Ammount']
    get_acc_bal=Bankaccounts.objects.get(NewAccountNo=int(recive_acc))
    now = datetime.now()
    dt_time = now.strftime("%d/%m/%Y %H:%M:%S")
    trans_number=''.join(random.choice(string.digits) for _ in range(8))
    
    if login_acc_number!=recive_acc:
        if Bankaccounts.objects.filter(NewAccountNo=recive_acc):
            if showtopage.NewAccountPass==int(account_passwd):
                if showtopage.Account_bal>=int(amnt_transfer):
                    reduct=showtopage.Account_bal-int(amnt_transfer)
                    Bankaccounts.objects.filter(NewAccountNo=showtopage.NewAccountNo).update(Account_bal=reduct)
                    credit=get_acc_bal.Account_bal+int(amnt_transfer)
                    Bankaccounts.objects.filter(NewAccountNo=int(recive_acc)).update(Account_bal=credit)
                    send_sms(showtopage.MobileNo,f"{amnt_transfer}/-INR Is Debited From Your Account and current balance is:{reduct}")
                    send_sms(get_acc_bal.MobileNo,f"{amnt_transfer}/-INR Is Credited to Your Account and current balance is:{credit}")
                    Transaction.objects.create(
                        User_accnumber=login_acc_number,
                        Transaction_name='Money Transfer',
                        bill_number=recive_acc,
                        Ammount=amnt_transfer,
                        Transaction_id=trans_number,
                        Date_Time=dt_time,
                    )
                    return redirect('/money_trans_page')
                else:
                    messages.success(request, 'Your Account Balance Is Low!!!')
                    return redirect('/money_trans_page')
            else:
                messages.success(request, 'Your Account Password Is Wrong')
                return redirect('/money_trans_page')
        else:
            messages.success(request, 'Entered Account Number Is Not Exiest')
            return redirect('/money_trans_page')
    else:
        messages.success(request, 'Entered Account Number Is Not Valid')
        return redirect('/money_trans_page')
    

def customer_care(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.get(NewAccountNo =login_acc_number)
    return render(request,'customercare.html',{'ac_details':showtopage})

def logout(request):
    del request.session['account_number']
    request.session.flush()
    return redirect('index')

def transaction(request):
    login_acc_number=request.session['account_number']
    datatopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    showtopage=Transaction.objects.filter(User_accnumber =login_acc_number)
    return render(request,'transaction.html',{'ac_details':showtopage,'headername':datatopage})

def mobilerecharge(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'billpay/mobilerecharge.html',{'ac_details':showtopage})

def rechargedone(request):
    mobnumber=request.POST['mnumber']
    rechrg_amt=request.POST['rechargamt']
    rechrg_pass=request.POST['password']
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.get(NewAccountNo =login_acc_number)
    now = datetime.now()
    dt_time = now.strftime("%d/%m/%Y %H:%M:%S")
    trans_number=''.join(random.choice(string.digits) for _ in range(8))

    if len(mobnumber)==10:
        if int(rechrg_pass)==showtopage.NewAccountPass:
            if int(rechrg_amt)<=showtopage.Account_bal:
                reduct=showtopage.Account_bal-int(rechrg_amt)
                Bankaccounts.objects.filter(NewAccountNo=showtopage.NewAccountNo).update(Account_bal=reduct)
                Transaction.objects.create(
                    User_accnumber=login_acc_number,
                    Transaction_name='Mobile Recharge',
                    bill_number=mobnumber,
                    Ammount=rechrg_amt,
                    Transaction_id=trans_number,
                    Date_Time=dt_time,
                )
                return redirect('mobilerecharge')
            else:
                messages.success(request, 'Your Account Balance Is Low...')
                return redirect('mobilerecharge')
        else:
            messages.success(request, 'Your Account Password Is Wrong...')
            return redirect('mobilerecharge')
    else:
        messages.success(request, 'Enter Valid Mobile Number...')
        return redirect('mobilerecharge')    

def Electricitypay(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'billpay/elacbillpay.html',{'ac_details':showtopage})

def Electricitydone(request):
    mobnumber=request.POST['mnumber']
    rechrg_amt=request.POST['rechargamt']
    rechrg_pass=request.POST['password']
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.get(NewAccountNo =login_acc_number)
    now = datetime.now()
    dt_time = now.strftime("%d/%m/%Y %H:%M:%S")
    trans_number=''.join(random.choice(string.digits) for _ in range(8))

    if len(mobnumber)==6:
        if int(rechrg_pass)==showtopage.NewAccountPass:
            if int(rechrg_amt)<=showtopage.Account_bal:
                reduct=showtopage.Account_bal-int(rechrg_amt)
                Bankaccounts.objects.filter(NewAccountNo=showtopage.NewAccountNo).update(Account_bal=reduct)
                Transaction.objects.create(
                    User_accnumber=login_acc_number,
                    Transaction_name='Electricity Bill Pay',
                    bill_number=mobnumber,
                    Ammount=rechrg_amt,
                    Transaction_id=trans_number,
                    Date_Time=dt_time,
                )
                return redirect('Electricitypay')
            else:
                messages.success(request, 'Your Account Balance Is Low...')
                return redirect('Electricitypay')
        else:
            messages.success(request, 'Your Account Password Is Wrong...')
            return redirect('Electricitypay')
    else:
        messages.success(request, 'Enter Valid Bill Number...')
        return redirect('Electricitypay') 

def DTHrecharge(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'billpay/dth.html',{'ac_details':showtopage})

def DTHrechargedone(request):
    mobnumber=request.POST['mnumber']
    rechrg_amt=request.POST['rechargamt']
    rechrg_pass=request.POST['password']
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.get(NewAccountNo =login_acc_number)
    now = datetime.now()
    dt_time = now.strftime("%d/%m/%Y %H:%M:%S")
    trans_number=''.join(random.choice(string.digits) for _ in range(8))

    if len(mobnumber)==10:
        if int(rechrg_pass)==showtopage.NewAccountPass:
            if int(rechrg_amt)<=showtopage.Account_bal:
                reduct=showtopage.Account_bal-int(rechrg_amt)
                Bankaccounts.objects.filter(NewAccountNo=showtopage.NewAccountNo).update(Account_bal=reduct)
                Transaction.objects.create(
                    User_accnumber=login_acc_number,
                    Transaction_name='DTH Bill Pay',
                    bill_number=mobnumber,
                    Ammount=rechrg_amt,
                    Transaction_id=trans_number,
                    Date_Time=dt_time,
                )
                return redirect('DTHrecharge')
            else:
                messages.success(request, 'Your Account Balance Is Low...')
                return redirect('DTHrecharge')
        else:
            messages.success(request, 'Enter Valid Password...')
            return redirect('DTHrecharge')
    else:
        messages.success(request, 'Enter Valid Bill Number...')
        return redirect('DTHrecharge') 


def Broadband(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'billpay/broadband.html',{'ac_details':showtopage})

def Broadbanddone(request):
    mobnumber=request.POST['mnumber']
    rechrg_amt=request.POST['rechargamt']
    rechrg_pass=request.POST['password']
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.get(NewAccountNo =login_acc_number)
    now = datetime.now()
    dt_time = now.strftime("%d/%m/%Y %H:%M:%S")
    trans_number=''.join(random.choice(string.digits) for _ in range(8))

    if len(mobnumber)==10:
        if int(rechrg_pass)==showtopage.NewAccountPass:
            if int(rechrg_amt)<=showtopage.Account_bal:
                reduct=showtopage.Account_bal-int(rechrg_amt)
                Bankaccounts.objects.filter(NewAccountNo=showtopage.NewAccountNo).update(Account_bal=reduct)
                Transaction.objects.create(
                    User_accnumber=login_acc_number,
                    Transaction_name='Broadband Bill Pay',
                    bill_number=mobnumber,
                    Ammount=rechrg_amt,
                    Transaction_id=trans_number,
                    Date_Time=dt_time,
                )
                return redirect('Broadband')
            else:
                messages.success(request, 'Your Account Balance Is Low...')
                return redirect('Broadband')
        else:
            messages.success(request, 'Enter Valid Account Password...')
            return redirect('Broadband')
    else:
        messages.success(request, 'Enter Valid Bill Number...')
        return redirect('Broadband') 

def FASTag(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'billpay/fastag.html',{'ac_details':showtopage})

def FASTagdone(request):
    mobnumber=request.POST['mnumber']
    rechrg_amt=request.POST['rechargamt']
    rechrg_pass=request.POST['password']
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.get(NewAccountNo =login_acc_number)
    now = datetime.now()
    dt_time = now.strftime("%d/%m/%Y %H:%M:%S")
    trans_number=''.join(random.choice(string.digits) for _ in range(8))

    if len(mobnumber)==10:
        if int(rechrg_pass)==showtopage.NewAccountPass:
            if int(rechrg_amt)<=showtopage.Account_bal:
                reduct=showtopage.Account_bal-int(rechrg_amt)
                Bankaccounts.objects.filter(NewAccountNo=showtopage.NewAccountNo).update(Account_bal=reduct)
                Transaction.objects.create(
                    User_accnumber=login_acc_number,
                    Transaction_name='FASTag Recharge',
                    bill_number=mobnumber,
                    Ammount=rechrg_amt,
                    Transaction_id=trans_number,
                    Date_Time=dt_time,
                )
                return redirect('FASTag')
            else:
                messages.success(request, 'Your Account Balance Is low...')
                return redirect('FASTag')
        else:
            messages.success(request, 'Enter Valid Account Password...')
            return redirect('FASTag')
    else:
        messages.success(request, 'Enter Valid FASTag Number...')
        return redirect('FASTag') 

def Gassbill(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'billpay/gassbill.html',{'ac_details':showtopage})

def Gassbilldone(request):
    mobnumber=request.POST['mnumber']
    rechrg_amt=request.POST['rechargamt']
    rechrg_pass=request.POST['password']
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.get(NewAccountNo =login_acc_number)
    now = datetime.now()
    dt_time = now.strftime("%d/%m/%Y %H:%M:%S")
    trans_number=''.join(random.choice(string.digits) for _ in range(8))

    if len(mobnumber)==10:
        if int(rechrg_pass)==showtopage.NewAccountPass:
            if int(rechrg_amt)<=showtopage.Account_bal:
                reduct=showtopage.Account_bal-int(rechrg_amt)
                Bankaccounts.objects.filter(NewAccountNo=showtopage.NewAccountNo).update(Account_bal=reduct)
                Transaction.objects.create(
                    User_accnumber=login_acc_number,
                    Transaction_name='Gassbill Pay',
                    bill_number=mobnumber,
                    Ammount=rechrg_amt,
                    Transaction_id=trans_number,
                    Date_Time=dt_time,
                )
                return redirect('Gassbill')
            else:
                messages.success(request, 'Account Balance Is Low...')
                return redirect('Gassbill')
        else:
            messages.success(request, 'Enter Valid Account Password...')
            return redirect('Gassbill')
    else:
        messages.success(request, 'Enter Valid Bill Number...')
        return redirect('Gassbill')

def Landline(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'billpay/landline.html',{'ac_details':showtopage})


def Landlinedone(request):
    mobnumber=request.POST['mnumber']
    rechrg_amt=request.POST['rechargamt']
    rechrg_pass=request.POST['password']
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.get(NewAccountNo =login_acc_number)
    now = datetime.now()
    dt_time = now.strftime("%d/%m/%Y %H:%M:%S")
    trans_number=''.join(random.choice(string.digits) for _ in range(8))

    if len(mobnumber)==10:
        if int(rechrg_pass)==showtopage.NewAccountPass:
            if int(rechrg_amt)<=showtopage.Account_bal:
                reduct=showtopage.Account_bal-int(rechrg_amt)
                Bankaccounts.objects.filter(NewAccountNo=showtopage.NewAccountNo).update(Account_bal=reduct)
                Transaction.objects.create(
                    User_accnumber=login_acc_number,
                    Transaction_name='Landline Bill Pay',
                    bill_number=mobnumber,
                    Ammount=rechrg_amt,
                    Transaction_id=trans_number,
                    Date_Time=dt_time,
                )
                return redirect('Landline')
            else:
                messages.success(request, 'Account Balance Is Low...')
                return redirect('Landline')
        else:
            messages.success(request, 'Enter Valid Account Password...')
            return redirect('Landline')
    else:
        messages.success(request, 'Enter Valid Number...')
        return redirect('Landline')


def Waterbill(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'billpay/waterbill.html',{'ac_details':showtopage})

def Waterbilldone(request):
    mobnumber=request.POST['mnumber']
    rechrg_amt=request.POST['rechargamt']
    rechrg_pass=request.POST['password']
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.get(NewAccountNo =login_acc_number)
    now = datetime.now()
    dt_time = now.strftime("%d/%m/%Y %H:%M:%S")
    trans_number=''.join(random.choice(string.digits) for _ in range(8))

    if len(mobnumber)==10:
        if int(rechrg_pass)==showtopage.NewAccountPass:
            if int(rechrg_amt)<=showtopage.Account_bal:
                reduct=showtopage.Account_bal-int(rechrg_amt)
                Bankaccounts.objects.filter(NewAccountNo=showtopage.NewAccountNo).update(Account_bal=reduct)
                Transaction.objects.create(
                    User_accnumber=login_acc_number,
                    Transaction_name='Waterbill Bill Pay',
                    bill_number=mobnumber,
                    Ammount=rechrg_amt,
                    Transaction_id=trans_number,
                    Date_Time=dt_time,
                )
                return redirect('Waterbill')
            else:
                messages.success(request, 'Your Account Balance Is Low...')
                return redirect('Waterbill')
        else:
            messages.success(request, 'Enter Valid Account Password...')
            return redirect('Waterbill')
    else:
        messages.success(request, 'Enter Valid Bill Number...')
        return redirect('Waterbill')

def carbikeInsurance(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'billpay/car_bike_insurance.html',{'ac_details':showtopage})

def carbikeInsurancedone(request):
    mobnumber=request.POST['mnumber']
    rechrg_amt=request.POST['rechargamt']
    rechrg_pass=request.POST['password']
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.get(NewAccountNo =login_acc_number)
    now = datetime.now()
    dt_time = now.strftime("%d/%m/%Y %H:%M:%S")
    trans_number=''.join(random.choice(string.digits) for _ in range(8))

    if len(mobnumber)==10:
        if int(rechrg_pass)==showtopage.NewAccountPass:
            if int(rechrg_amt)<=showtopage.Account_bal:
                reduct=showtopage.Account_bal-int(rechrg_amt)
                Bankaccounts.objects.filter(NewAccountNo=showtopage.NewAccountNo).update(Account_bal=reduct)
                Transaction.objects.create(
                    User_accnumber=login_acc_number,
                    Transaction_name='Vehicle Insurance Renewal',
                    bill_number=mobnumber,
                    Ammount=rechrg_amt,
                    Transaction_id=trans_number,
                    Date_Time=dt_time,
                )
                return redirect('carbikeInsurance')
            else:
                messages.success(request, 'Your Account Balance Is low...')
                return redirect('carbikeInsurance')
        else:
            messages.success(request, 'Enter Valid Account Password...')
            return redirect('carbikeInsurance')
    else:
        messages.success(request, 'Enter Valid Insurance Number...')
        return redirect('carbikeInsurance')

def Municipal(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'billpay/municipal.html',{'ac_details':showtopage})

def Municipaldone(request):
    mobnumber=request.POST['mnumber']
    rechrg_amt=request.POST['rechargamt']
    rechrg_pass=request.POST['password']
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.get(NewAccountNo =login_acc_number)
    now = datetime.now()
    dt_time = now.strftime("%d/%m/%Y %H:%M:%S")
    trans_number=''.join(random.choice(string.digits) for _ in range(8))

    if len(mobnumber)==10:
        if int(rechrg_pass)==showtopage.NewAccountPass:
            if int(rechrg_amt)<=showtopage.Account_bal:
                reduct=showtopage.Account_bal-int(rechrg_amt)
                Bankaccounts.objects.filter(NewAccountNo=showtopage.NewAccountNo).update(Account_bal=reduct)
                Transaction.objects.create(
                    User_accnumber=login_acc_number,
                    Transaction_name='Municipal Bill Pay',
                    bill_number=mobnumber,
                    Ammount=rechrg_amt,
                    Transaction_id=trans_number,
                    Date_Time=dt_time,
                )
                return redirect('Municipal')
            else:
                messages.success(request, 'Your Account Balance Is Low...')
                return redirect('Municipal')
        else:
            messages.success(request, 'Enter Valid Account Password...')
            return redirect('Municipal')
    else:
        messages.success(request, 'Enter Valid Bill Number...')
        return redirect('Municipal')

def OYOHotel(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'billpay/oyohotel.html',{'ac_details':showtopage})

def Flights(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'billpay/flight.html',{'ac_details':showtopage})

def Busbook(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'billpay/bus.html',{'ac_details':showtopage})

def Trianbook(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'billpay/train.html',{'ac_details':showtopage})

def Moviebook(request):
    login_acc_number=request.session['account_number']
    showtopage=Bankaccounts.objects.filter(NewAccountNo =login_acc_number)
    return render(request,'billpay/movie.html',{'ac_details':showtopage})

def forgetpage(request):
    return render(request,'forgot.html')

def forgetpass(request):
    f_adhar_number=request.POST['adharno_number']
    f_mobile_number=request.POST['mobile_number']

    if Bankaccounts.objects.filter(AdharNo =int(f_adhar_number),MobileNo=int(f_mobile_number)):
        print('hello')
        messages.success(request, 'Account Number And Password Is Sended To Your Number...')
        return redirect('index')
    else:
        messages.success(request, 'Enter Valid Account Details...')
        return render(request,'forgot.html')

def send_sms(number,message):
    url="https://www.fast2sms.com/dev/bulk"
    params={
        'authorization':'CqVsIYwfrjZmyoF3MAO9uiNpDPetRBdQJg4Ln21kxhSEavKU6XHaU21MFk3uEGOnm70PQBoXxrw5R8is',
        'sender_id':'FSTSMS',
        'message':message,
        'language':'english',
        'route':'p',
        'numbers': number
    }
    response=requests.get(url,params=params)
    dic=response.json()
        