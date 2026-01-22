
from django.db.models import  Count, Avg
from django.shortcuts import render, redirect
from django.db.models import Count
from django.db.models import Q
import datetime
import csv
import xlwt
import openpyxl
from django.http import HttpResponse
import numpy as np

import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.metrics import accuracy_score

from sklearn.tree import DecisionTreeClassifier

# Create your views here.
from Remote_User.models import ClientRegister_Model,predict_flight_trajectory,evdatasets,detection_ratio,detection_accuracy


def serviceproviderlogin(request):
    if request.method  == "POST":
        admin = request.POST.get('username')
        password = request.POST.get('password')
        if admin == "Admin" and password =="Admin":
            detection_accuracy.objects.all().delete()
            return redirect('View_Remote_Users')

    return render(request,'SProvider/serviceproviderlogin.html')


def Upload_Datasets(request):
    if "GET" == request.method:
        return render(request, 'SProvider/Upload_Datasets.html', {})
    else:

        evdatasets.objects.all().delete()

        csv_file = request.FILES['csv_file'].read().decode('utf-8').splitlines()
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            evdatasets.objects.create(
                Fid=row['Fid'],
                Airline=row['Airline'],
                Flight=row['Flight'],
                DateTime=row['DateTime'],
                Lat=row['Lat'],
                Lon=row['Lon'],
                Geoaltitude=row['Geoaltitude'],
                Lat2=row['Lat2'],
                Lon2=row['Lon2'],
                Geoaltitude2=row['Geoaltitude2'],
                Lat3=row['Lat3'],
                Lon3=row['Lon3'],
                Geoaltitude3=row['Geoaltitude3'],
                Lat4=row['Lat4'],
                Lon4=row['Lon4'],
                Geoaltitude4=row['Geoaltitude4'],
                Lat5=row['Lat5'],
                Lon5=row['Lon5'],
                Geoaltitude5=row['Geoaltitude5'],
            )

    obj = evdatasets.objects.all()

    return render(request, 'SProvider/Upload_Datasets.html', {'csvdatasets': obj})

def View_Remote_Users(request):
    obj=ClientRegister_Model.objects.all()
    return render(request,'SProvider/View_Remote_Users.html',{'objects':obj})

def ViewTrendings(request):
    topic = predict_flight_trajectory.objects.values('topics').annotate(dcount=Count('topics')).order_by('-dcount')
    return  render(request,'SProvider/ViewTrendings.html',{'objects':topic})

def charts(request,chart_type):
    chart1 = detection_ratio.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts.html", {'form':chart1, 'chart_type':chart_type})

def charts1(request,chart_type):
    chart1 = detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts1.html", {'form':chart1, 'chart_type':chart_type})

def View_Prediction_Of_Flight_Trajectory_Status(request):
    obj =predict_flight_trajectory.objects.all()
    return render(request, 'SProvider/View_Prediction_Of_Flight_Trajectory_Status.html', {'list_objects': obj})


def View_All_Uploaded_Datasets(request):
    obj =evdatasets.objects.all()
    return render(request, 'SProvider/View_All_Uploaded_Datasets.html', {'csvdatasets': obj})

def likeschart(request,like_chart):
    charts =detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/likeschart.html", {'form':charts, 'like_chart':like_chart})


def Download_Predicted_DataSets(request):

    response = HttpResponse(content_type='application/ms-excel')
    # decide file name
    response['Content-Disposition'] = 'attachment; filename="Predicted_Data.xls"'
    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    # adding sheet
    ws = wb.add_sheet("sheet1")
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True
    # writer = csv.writer(response)
    obj = predict_flight_trajectory.objects.all()
    data = obj  # dummy method to fetch data.
    for my_row in data:
        row_num = row_num + 1

        ws.write(row_num, 0, my_row.Fid, font_style)
        ws.write(row_num, 1, my_row.Airline, font_style)
        ws.write(row_num, 2, my_row.Flight, font_style)
        ws.write(row_num, 3, my_row.DateTime, font_style)
        ws.write(row_num, 4, my_row.Lat, font_style)
        ws.write(row_num, 5, my_row.Lon, font_style)
        ws.write(row_num, 6, my_row.Geoaltitude, font_style)
        ws.write(row_num, 7, my_row.Lat2, font_style)
        ws.write(row_num, 8, my_row.Lon2, font_style)
        ws.write(row_num, 9, my_row.Geoaltitude2, font_style)
        ws.write(row_num, 10, my_row.Lat3, font_style)
        ws.write(row_num, 11, my_row.Lon3, font_style)
        ws.write(row_num, 12, my_row.Geoaltitude3, font_style)
        ws.write(row_num, 13, my_row.Lat4, font_style)
        ws.write(row_num, 14, my_row.Lon4, font_style)
        ws.write(row_num, 15, my_row.Geoaltitude4, font_style)
        ws.write(row_num, 16, my_row.Lat5, font_style)
        ws.write(row_num, 17, my_row.Lon5, font_style)
        ws.write(row_num, 18, my_row.Geoaltitude5, font_style)
        ws.write(row_num, 19, my_row.Prediction, font_style)


    wb.save(response)
    return response

def train_model(request):
    detection_accuracy.objects.all().delete()

    dataset = pd.read_csv("Datasets.csv", encoding='latin-1')

    def apply_results(label):
        if (label == 0):
            return 0  # Appropriate
        elif (label == 1):
            return 1  # Inappropriate

    dataset['Results'] = dataset['Label'].apply(apply_results)

    cv = CountVectorizer()

    x = dataset['Fid'].apply(str)
    y = dataset['Results']

    cv = CountVectorizer()

    print(x)
    print("Y")
    print(y)

    x = cv.fit_transform(x)

    models = []
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.20)
    X_train.shape, X_test.shape, y_train.shape

    print("Gradient Boosting Classifier")

    from sklearn.ensemble import GradientBoostingClassifier
    clf = GradientBoostingClassifier(n_estimators=100, learning_rate=1.0, max_depth=1, random_state=0).fit(
        X_train,
        y_train)
    clfpredict = clf.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, clfpredict) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, clfpredict))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, clfpredict))
    models.append(('GradientBoostingClassifier', clf))
    detection_accuracy.objects.create(names="Gradient Boosting Classifier",
                                      ratio=accuracy_score(y_test, clfpredict) * 100)

    # SVM Model
    print("SVM")
    from sklearn import svm

    lin_clf = svm.LinearSVC()
    lin_clf.fit(X_train, y_train)
    predict_svm = lin_clf.predict(X_test)
    svm_acc = accuracy_score(y_test, predict_svm) * 100
    print("ACCURACY")
    print(svm_acc)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, predict_svm))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, predict_svm))
    detection_accuracy.objects.create(names="SVM", ratio=svm_acc)

    print("Logistic Regression")

    from sklearn.linear_model import LogisticRegression

    reg = LogisticRegression(random_state=0, solver='lbfgs').fit(X_train, y_train)
    y_pred = reg.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, y_pred) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, y_pred))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, y_pred))
    detection_accuracy.objects.create(names="Logistic Regression", ratio=accuracy_score(y_test, y_pred) * 100)

    print("Extra Tree Classifier")
    from sklearn.tree import ExtraTreeClassifier
    etc_clf = ExtraTreeClassifier()
    etc_clf.fit(X_train, y_train)
    etcpredict = etc_clf.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, etcpredict) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, etcpredict))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, etcpredict))
    models.append(('Extra Tree Classifier', etc_clf))
    detection_accuracy.objects.create(names="Extra Tree Classifier", ratio=accuracy_score(y_test, etcpredict) * 100)

    labeled = 'Labled_data.csv'
    dataset.to_csv(labeled, index=False)
    dataset.to_markdown

    obj = detection_accuracy.objects.all()
    return render(request,'SProvider/train_model.html', {'objs': obj})