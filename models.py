from django.db import models

class Bankaccounts(models.Model):
    FirstName=models.CharField(max_length=20)
    MiddleName=models.CharField(max_length=20)
    LastName=models.CharField(max_length=20)
    Gender=models.CharField(max_length=10)
    BirthDate=models.CharField(max_length=10)
    AccType=models.CharField(max_length=10)
    Address=models.CharField(max_length=50)
    MobileNo=models.IntegerField()
    AltNumber=models.IntegerField()
    FamilyMem=models.CharField(max_length=2)
    OccuP=models.CharField(max_length=20)
    Income=models.IntegerField()
    EmailID=models.EmailField()
    AdharNo=models.IntegerField()
    PANno=models.CharField(max_length=11)
    NewAccountNo=models.IntegerField()
    NewAccountPass=models.IntegerField()
    DateTime=models.CharField(max_length=30)
    Account_bal=models.IntegerField()

class Transaction(models.Model):
    User_accnumber=models.IntegerField()
    Transaction_name=models.CharField(max_length=30)
    bill_number=models.IntegerField()
    Ammount=models.IntegerField()
    Transaction_id=models.IntegerField()
    Date_Time=models.CharField(max_length=20)