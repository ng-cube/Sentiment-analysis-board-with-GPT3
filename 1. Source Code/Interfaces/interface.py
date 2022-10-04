import re
import tkinter as tk
from tkinter import ttk, messagebox, StringVar, IntVar
from PIL import ImageTk, Image
import nltk
# nltk.download('vader_lexicon')

from datetime import datetime
import datetime as dt
import time
from datetime import date, timedelta, datetime
import numpy as np
import pandas as pd
import requests, json

import sys
import os
import shutil
sys.path.insert(0, r'/Users/jacky/Repo/CZ2006/')
from twitterConnectionClass import twitterConnection
from Report import Report
from graph import Graph
from userdb_new import *
from sqlConnectionClass import *

directory = '/Users/jacky/Repo/CZ2006/'


class tkinterApp(tk.Tk):
     
    def __init__(self, *args, **kwargs):
         
        tk.Tk.__init__(self, *args, **kwargs)

        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}")
        self.title("CZ2006 Project")

        style = ttk.Style(self)
        style.theme_use('default')
        
        global container 
        container = tk.Frame(self) 
        container.pack(side = "top", fill = "both", expand = True)
  
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
  
        # initializing frames to an empty array
        self.frames = {} 
  
        # iterating through a tuple consisting of the different page layouts
        for F in (DashboardPage, LoginPage, SignupPage, PaymentPage, ConfirmationPage, ForgotPasswordPage, SettingsPage, ChangePasswordPage):
  
            frame = F(container, self)
  
            self.frames[F] = frame
  
            self.frames[F].grid(row = 0, column = 0, sticky = "nsew")
  
        self.show_frame(DashboardPage)

    def show_frame(self, cont): 
        
        self.frames[cont].destroy()
        self.frames[cont] = cont(container, self)
        self.frames[cont].grid(row=0, column=0, sticky="nsew")
        self.frames[cont].tkraise()

        # frame = self.frames[cont]
        # frame.tkraise()


class Pages:
    # user
    email = ""
    username = ""
    password = ""
    plan = ""
    ans = ""
    loginStatus = False
    change = False # used when logged in user wants to change plan
    limit = 5
    count = 0

    # dashboard
    keyword = "@ntusg" # default keyword at application start up
    progressValue = 0 # tracks progress of keyword that is being fetched
    progressDone = False
    exists = False # check whether keyword exists in db
    progressKeyword = ''
    selected_date = 0

    # bottom section of dashboard
    posPer = 0
    negPer = 0
    neuPer = 0
    avgSc = 0
    varSc = 0
    
    sentiment = []
    currentPositive = 'Select a date to display the sentiment.'
    currentNegative = 'Select a date to display the sentiment.'

    history = ['@ntusg'] # default history keywords
    fav = [] # default favourite keywords

    def getMsg(loginStatus, username):
        if loginStatus == True:
            msg = f"Welcome, {username}!" 
        else:
            msg = "Welcome!"
        return msg

    def getConfirmation(username, email, plan, verificationA):
        confirmation = f'\n\nConfirmation\n\nUsername: {username}\n\nEmail: {email}\n\nSelected Plan: {plan}\n\nVerification Answer: {verificationA}\n\n'
        return confirmation


class DashboardPage(tk.Frame, Pages):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        '''initialization'''
        def checkIfProgressDone(keyword):
            url = 'https://daa3d4b86b74.ngrok.io/'

            threadidurl = url + f'/getAllThreads/'
            json_string = requests.get(threadidurl).text
            obj = json.loads(json_string)
            keysList = list(obj.keys())
           
            index = -1
            for i in range(len(obj)):
                if obj[keysList[i]]['keyword'] == keyword:
                    index = i
                    break

            if index == -1:
                # keyword not in api -> not fetching
                return True
            return False

        db = sqlConnection()

        if db.checkIfExists(Pages.keyword) == True:
            print("checkIfExists(): " + Pages.keyword + " exists")
            Pages.exists = True
        else:
            print("checkIfExists(): " + Pages.keyword + " does not exists")
            Pages.exists = False

        if checkIfProgressDone(Pages.keyword) == True:
            Pages.progressDone = True
        else:
            Pages.progressDone = False

        if Pages.exists == True: # getting statistics
            Pages.posPer = db.calposperc(Pages.keyword)
            Pages.negPer = db.calnegperc(Pages.keyword)
            Pages.neuPer = db.calneuperc(Pages.keyword)
            Pages.avgSc = db.getmean(Pages.keyword)
            Pages.varSc = db.getvar(Pages.keyword)

            # used to generate report
            stats = [Pages.posPer,Pages.negPer,Pages.neuPer,Pages.avgSc,Pages.varSc] 
        
        else:
            Pages.posPer = 0
            Pages.negPer = 0
            Pages.neuPer = 0
            Pages.avgSc = 0
            Pages.varSc = 0

            Pages.currentPositive = "No tweets pulled."
            Pages.currentNegative = "No tweets pulled."

        global panel 

        def replacePlot(path, panel):
            img = ImageTk.PhotoImage(Image.open(path))

            try:
                shutil.rmtree('images')
                os.mkdir('images')
            except FileNotFoundError:
                os.mkdir('images')
            imgpil = ImageTk.getimage(img)

            # fig1 used to generate report
            imgpil.save(os.path.join("/Users/jacky/Repo/CZ2006/Interfaces/", 'fig1.png'), "PNG")
            imgpil.close()

            panel = ttk.Label(self.Frame6, image = img, borderwidth=0, compound='center')
            panel.image = img
            panel.grid(row=2, column=1)

        def get_dataframe():
            if db.checkIfExists(Pages.keyword) == True:
                keyword1 = Pages.keyword
                df = Graph(None, keyword1).getDataframe()
                return df
            else:
                print("get_dataframe(): " + f"{Pages.keyword} doesn't exist")
                return None
        
        
        '''grid layout'''
        self.Frame1 = tk.Frame(self, bg="grey") 
        self.Frame2 = tk.Frame(self, bg="snow3") 
        self.Frame3 = tk.Frame(self, bg="snow3")
        self.Frame4 = tk.Frame(self, bg="snow3") 
        self.Frame5 = tk.Frame(self, bg="grey") 
        self.Frame6 = tk.Frame(self, bg="white")
        self.Frame7 = tk.Frame(self, bg="snow3") 
        self.Frame8 = tk.Frame(self, bg="white")
        self.Frame9 = tk.Frame(self, bg="white")
        self.Frame10 = tk.Frame(self, bg="grey") 
        self.Frame11 = tk.Frame(self, bg="snow3") 
        self.Frame12 = tk.Frame(self, bg="snow3")
        self.Frame13 = tk.Frame(self, bg="white")
        self.Frame14 = tk.Frame(self, bg='white')
        self.Frame15 = tk.Frame(self, bg='white')

        # left section
        self.Frame1.grid(row=0, column=0, rowspan=1, columnspan=2, sticky="nsew")
        self.Frame12.grid(row=1, column=0, rowspan=1, columnspan=2, sticky="nsew")
        self.Frame3.grid(row=2, column=0, rowspan=4, columnspan=2, sticky="nsew")
        self.Frame2.grid(row=6, column=0, rowspan=3, columnspan=2, sticky="nsew")
        self.Frame4.grid(row=9, column=0, rowspan=1, columnspan=2, sticky="nsew")
        
        # middle section
        self.Frame5.grid(row=0, column=2, rowspan=1, columnspan=7, sticky="nsew")
        self.Frame6.grid(row=1, column=2, rowspan=6, columnspan=7, sticky="nsew")
        self.Frame8.grid(row=8, column=2, rowspan=2, columnspan=2, sticky="nsew")        
        self.Frame9.grid(row=8, column=4, rowspan=2, columnspan=3, sticky="nsew")
        self.Frame13.grid(row=8, column=7, rowspan=2, columnspan=3, sticky="nsew")
        self.Frame14.grid(row=7, column=2, rowspan=1, columnspan=7, sticky="nsew")

        # right section
        self.Frame10.grid(row=0, column=9, rowspan=1, columnspan=1, sticky="nsew")
        self.Frame11.grid(row=1, column=9, rowspan=6, columnspan=1, sticky="nsew")
        self.Frame7.grid(row=7, column=9, rowspan=1, columnspan=1, sticky="nsew")

        for r in range(10):
            self.rowconfigure(r, weight=1)
        for c in range(10):
            self.columnconfigure(c, weight=1)
        

        '''dashboard button section'''
        self.Frame1.grid_propagate(False)
        self.Frame1.grid_columnconfigure(0, weight=1)
        self.Frame1.grid_columnconfigure(2, weight=1)
        self.Frame1.grid_rowconfigure(0, weight=1)
        self.Frame1.grid_rowconfigure(2, weight=1)

        b1 = ttk.Button(self.Frame1, text='Dashboard', command=lambda:controller.show_frame(DashboardPage))
        b1.grid(row=1, column=1)


        '''search section'''
        self.Frame12.grid_propagate(False)
        self.Frame12.grid_columnconfigure(0, weight=1)
        self.Frame12.grid_columnconfigure(4, weight=1)
        self.Frame12.grid_rowconfigure(0, weight=1)
        self.Frame12.grid_rowconfigure(2, weight=1)

        b2 = ttk.Button(self.Frame12, text="Search", command=lambda:searchKeyword())
        e1 = ttk.Entry(self.Frame12)
        
        b2.grid(row=1, column=3, padx=2)
        e1.grid(row=1, column=1, padx=2, columnspan=2)


        '''history section'''
        self.Frame3.grid_propagate(False)
        self.Frame3.grid_columnconfigure(0, weight=1)
        self.Frame3.grid_columnconfigure(3, weight=1)
        for r in range(9):
            self.Frame3.rowconfigure(r, weight=1)
        
        l1 = ttk.Label(self.Frame3, text="History")
        l1.grid(row=0, column=1)

        for i in range(len(Pages.history)):
            ttk.Button(self.Frame3, text=Pages.history[i], command=lambda i=i:searchKeywordBtn(Pages.history[i])).grid(row=i+1, column=1, padx=10)
            ttk.Button(self.Frame3, text="Add", command=lambda i=i:addFav(Pages.history[i])).grid(row=i+1, column=2, padx=10)

        def addFav(word):
            Pages.fav.append(word)
            controller.show_frame(DashboardPage)
            

        '''favourites section'''
        self.Frame2.grid_propagate(False)
        self.Frame2.grid_columnconfigure(0, weight=1)
        self.Frame2.grid_columnconfigure(3, weight=1)
        for r in range(9):
            self.Frame2.rowconfigure(r, weight=1)
        
        l1 = ttk.Label(self.Frame2, text="Favourites")
        l1.grid(row=0, column=1)

        for i in range(len(Pages.fav)):
            ttk.Label(self.Frame2, text=Pages.fav[i]).grid(row=i+1, column=1, padx=10)
            ttk.Button(self.Frame2, text="Search", command=lambda i=i:searchKeywordBtn(Pages.fav[i])).grid(row=i+1, column=2, padx=10)


        '''generate report section'''
        self.Frame4.grid_propagate(False)
        self.Frame4.grid_columnconfigure(0, weight=1)
        self.Frame4.grid_columnconfigure(2, weight=1)
        self.Frame4.grid_rowconfigure(0, weight=1)
        self.Frame4.grid_rowconfigure(2, weight=1)

        myDir = directory+'myDir'
        name = f'Report for {Pages.keyword}'
        b4 = ttk.Button(self.Frame4, text="Generate Report", command=lambda:generateReport(myDir, name, Pages.sentiment, stats))
        b4.grid(row=1, column=1)


        '''title section'''
        self.Frame5.grid_propagate(False)
        self.Frame5.grid_columnconfigure(0, weight=1)
        self.Frame5.grid_columnconfigure(2, weight=1)
        self.Frame5.grid_rowconfigure(0, weight=1)
        self.Frame5.grid_rowconfigure(2, weight=1)

        title = ttk.Label(self.Frame5, text="Sentiment Dashboard", background="grey")
        title.grid(column=1, row=1)
        title.config(font=('helvetica', 44))


        '''graph section'''
        self.Frame6.grid_propagate(False)
        self.Frame6.grid_columnconfigure(0, weight=1)
        self.Frame6.grid_columnconfigure(2, weight=1)
        self.Frame6.grid_rowconfigure(0, weight=1)
        self.Frame6.grid_rowconfigure(3, weight=1)

        # keyword title
        keywordtitle = ttk.Label(self.Frame6, text=Pages.keyword)
        keywordtitle.grid(row=1, column=1)
        keywordtitle.config(font=('helvetica', 28))

        # graph image
        if Pages.exists == True:
            placeholderImg = ImageTk.PhotoImage(Image.open(directory+"Interfaces/fig_line.png"))
            panel = ttk.Label(self.Frame6, image=placeholderImg, borderwidth=0, compound="center")
            panel.image = placeholderImg
            panel.grid(row=2, column=1)

        else:
            panel = ttk.Label(self.Frame6, text = "Please press 'update tweets' to pull the lastest data.", borderwidth=0, compound="center")
            panel.grid(row=2, column=1, pady = 20)

        def lineplot(dataframe,keyword):
            Graph(dataframe, keyword).showGraph()
            replacePlot(directory+'Interfaces/fig_line.png', panel)

        def densityplot(dataframe,keyword):
            Graph(dataframe, keyword).chooseIndicator('Histogram').indicatorTransform()
            replacePlot(directory+'Interfaces/fig_histogram.png', panel)


        '''type of plots section'''
        self.Frame7.grid_propagate(False)
        for i in range(4):
            self.Frame7.grid_rowconfigure(i, weight=1)
        self.Frame7.grid_columnconfigure(0, weight=1)
        self.Frame7.grid_columnconfigure(2, weight=1)

        ttk.Radiobutton(self.Frame7, text="Scatter Plot", value=15, command=lambda:lineplot(get_dataframe(), Pages.keyword)).grid(row=1, column=1, sticky='w')
        ttk.Radiobutton(self.Frame7, text="Density Plot", value=16, command=lambda:densityplot(get_dataframe(), Pages.keyword)).grid(row=2, column=1, sticky='w')


        '''statistics section'''
        self.Frame8.grid_propagate(False)
        self.Frame8.grid_columnconfigure(0, weight=1)
        self.Frame8.grid_rowconfigure(0, weight=1)

        statistics = f'Percentage of Positive tweets:\n{Pages.posPer}%\nPercentage of Negative tweets:\n{Pages.negPer}%\nPercentage of Neutral tweets:\n{Pages.neuPer}%\nMean Sentiment Scores: {Pages.avgSc}\nVar Sentiment Scores: {Pages.varSc}'

        msg1 = tk.Message(self.Frame8, text=statistics)
        msg1.grid(row=0, column=0, sticky='nsew')
        msg1.config(borderwidth=2, relief='groove')

        def getSummary(keyword):
            tweetdb = sqlConnection()
            tweetdb.create_connection()
            posMsgList = tweetdb.getPositiveSummary(keyword)
            negMsgList = tweetdb.getNegativeSummary(keyword)

            Pages.sentiment = []    

            if len(posMsgList) < 7 or len(negMsgList) < 7:
                Pages.currentNegative = "Not enough data."
                Pages.currentPositive = "Not enough data."

                Pages.posPer = 0
                Pages.negPer = 0
                Pages.neuPer = 0
                Pages.avgSc = 0
                Pages.varSc = 0

                return
            
            if posMsgList == None or negMsgList == None:
                print("getSummary(): Keyword doesn't exist in database")
            
            else:
                for i in range(7):
                    dtObj = datetime.fromtimestamp(posMsgList[i][1])

                    positive = posMsgList[i][0]
                    if positive == '':
                        positive = 'Positive sentiment not available.'
                    else: 
                        positive = 'Positive sentiment: ' + positive

                    positive = positive.encode('latin-1','replace')
                    positive = positive.decode('latin-1','replace')

                    negative = negMsgList[i][0]
                    if negative == '':
                        negative = 'Negative sentiment not available.'
                    else:
                        negative = 'Negative sentiment: ' + negative

                    negative = negative.encode('latin-1','replace')
                    negative = negative.decode('latin-1','replace')

                    temp = [str(dtObj), positive, negative]
                    Pages.sentiment.append(temp)
                
                Pages.currentPositive = Pages.sentiment[Pages.selected_date][1]
                Pages.currentNegative = Pages.sentiment[Pages.selected_date][2]

        if Pages.exists == True:
            getSummary(Pages.keyword)


        '''positive section'''
        self.Frame9.grid_propagate(False)
        self.Frame9.grid_columnconfigure(0, weight=1)
        self.Frame9.grid_rowconfigure(0, weight=1)

        self.msg2 = tk.Message(self.Frame9, text=Pages.currentPositive)
        self.msg2.grid(row=0, column=0, sticky="nsew")
        self.msg2.config(borderwidth=2, relief='groove')


        '''negative section'''
        self.Frame13.grid_propagate(False)
        self.Frame13.grid_columnconfigure(0, weight=1)
        self.Frame13.grid_rowconfigure(0, weight=1)
        
        self.msg3 = tk.Message(self.Frame13, text=Pages.currentNegative)
        self.msg3.grid(column=0, row=0, sticky='nsew')
        self.msg3.config(borderwidth=2, relief='groove')
        

        '''customize parameters section'''
        self.Frame14.grid_propagate(False)
        self.Frame14.grid_rowconfigure(0, weight=1)
        self.Frame14.grid_rowconfigure(2, weight=1)
        for r in range(7):
            self.Frame14.columnconfigure(r, weight=1)

        # progress bar section
        pb = ttk.Progressbar(self.Frame14, orient='horizontal', mode='determinate', length=200)
        pb["maximum"] = 1
        pb["value"] = Pages.progressValue
        pb.grid(column=1, row=1)

        if Pages.progressDone == True:
            self.progressLabel = ttk.Label(self.Frame14, text="Done")
            self.progressLabel.grid(column=1, row=2, pady=5)
        else:
            self.progressUpdate = ttk.Button(self.Frame14, text="Refresh", command=lambda:updateProgress(Pages.keyword))
            self.progressUpdate.grid(column=1, row=2, pady=5)

        def updateProgress(keyword):
            url = 'https://daa3d4b86b74.ngrok.io/'
            '''
            API CALLS (IN ORDER)
            - /estTime/?keyword=YOURKEYWORD
            - /fetchTweets/?keyword=YOURKEYWORD
            - /fetchTweets/progress/?thread_id=YOURTHREDID
            '''
            
            threadidurl = url + f'/getAllThreads/'
            json_string = requests.get(threadidurl).text
            obj = json.loads(json_string)
            keysList = list(obj.keys())
           
            index = -1
            for i in range(len(obj)):
                if obj[keysList[i]]['keyword'] == keyword:
                    index = i
                    break
            
            if index != -1:
                Pages.progressValue = float(obj[keysList[index]]['progress'])
                pb['value'] = Pages.progressValue
            else:
                pb['value'] = 0


        # fetch tweets section
        fetchTweets = ttk.Button(self.Frame14, text='Update Tweets', command=lambda:updateTweets(Pages.keyword))
        fetchTweets.grid(row=1, column=3)

        def updateTweets(keyword):
            url = 'https://daa3d4b86b74.ngrok.io/'
            fetchurl = url + f'/fetchTweets/?keyword={keyword}'
            print('updateTweets funtion called. ')
            '''fetches tweets with api'''
            Pages.count += 1
            if Pages.count == Pages.limit:
                tk.messagebox.showerror("Information", "You have reached the limit for the month. Please upgrade your plan.")
            else:
                requests.get(fetchurl)  
                Pages.progressDone = False
            
            controller.show_frame(DashboardPage)

        
        # dates combobox
        today = date.today()
        days = [str(today), str(today - timedelta(days=1)), str(today - timedelta(days=2)), str(today - timedelta(days=3)), str(today - timedelta(days=4)), str(today - timedelta(days=5)), str(today - timedelta(days=6))]
        
        variable = tk.StringVar(self.Frame14)
        
        dates = ttk.Combobox(self.Frame14, textvariable=variable)
        dates['values'] = days
        dates['state'] = 'readonly'
        dates.current(Pages.selected_date)
        dates.grid(row=1, column=5)

        def change_date(event):
            # returns the index of the selected date
            Pages.selected_date = days.index(variable.get())
            Pages.currentPositive = Pages.sentiment[Pages.selected_date][1]
            Pages.currentNegative = Pages.sentiment[Pages.selected_date][2]
            self.msg2['text'] = Pages.currentPositive[:325] + " ..."
            self.msg3['text'] = Pages.currentNegative[:325] + " ..."

        dates.bind('<<ComboboxSelected>>', change_date)


        '''user account'''
        self.Frame10.grid_propagate(False)
        self.Frame10.grid_columnconfigure(0, weight=1)
        self.Frame10.grid_columnconfigure(2, weight=1)
        self.Frame10.grid_rowconfigure(0, weight=1)
        self.Frame10.grid_rowconfigure(2, weight=1)

        l3 = ttk.Button(self.Frame10, text=Pages.getMsg(Pages.loginStatus, Pages.username), command=lambda:nextFrame())
        l3.grid(row=1, column=1)


        '''indicators section'''
        self.Frame11.grid_propagate(False)
        self.Frame11.grid_columnconfigure(0, weight=1)
        self.Frame11.grid_columnconfigure(2, weight=1)
        for i in range(16):
            self.Frame11.grid_rowconfigure(i, weight=1)

        c1 = ttk.Radiobutton(self.Frame11, text="Moving Avg 5", value=1, command=lambda:MAIndicator5(get_dataframe(), Pages.keyword))
        c2 = ttk.Radiobutton(self.Frame11, text="Moving Avg 10", value=2, command=lambda:MAIndicator10(get_dataframe(), Pages.keyword))
        c3 = ttk.Radiobutton(self.Frame11, text="Moving Avg 20", value=3, command=lambda:MAIndicator20(get_dataframe(), Pages.keyword))
        c4 = ttk.Radiobutton(self.Frame11, text="Exp Avg 0.1", value=4, command=lambda:expIndicator(get_dataframe(), Pages.keyword))
        c5 = ttk.Radiobutton(self.Frame11, text="Exp Avg 0.2", value=5, command=lambda:expIndicator1(get_dataframe(), Pages.keyword))
        c6 = ttk.Radiobutton(self.Frame11, text="Exp Avg 0.3", value=6, command=lambda:expIndicator2(get_dataframe(), Pages.keyword))
        c7 = ttk.Radiobutton(self.Frame11, text="Quantile/Day", value=7, command=lambda:quanIndicator(get_dataframe(), Pages.keyword))
        c8 = ttk.Radiobutton(self.Frame11, text="Quantile", value=8, command=lambda:quantileIndicator(get_dataframe(), Pages.keyword))
        c9 = ttk.Radiobutton(self.Frame11, text="Min&Max/day", value=9, command=lambda:minmaxdayIndicator(get_dataframe(), Pages.keyword))
        c10 = ttk.Radiobutton(self.Frame11, text="Min/Max", value=10, command=lambda:minmaxIndicator(get_dataframe(), Pages.keyword))
        c11 = ttk.Radiobutton(self.Frame11, text="Count", value=11, command=lambda:countIndicator(get_dataframe(), Pages.keyword))
        c12 = ttk.Radiobutton(self.Frame11, text="Positive", value=12, command=lambda:positiveIndicator(get_dataframe(), Pages.keyword))
        c13 = ttk.Radiobutton(self.Frame11, text="Negative", value=13, command=lambda:negativeIndicator(get_dataframe(), Pages.keyword))
        c14 = ttk.Radiobutton(self.Frame11, text="Neutral", value=14, command=lambda:neutralIndicator(get_dataframe(), Pages.keyword))

        c1.grid(row=1, column=1, sticky='w')
        c2.grid(row=2, column=1, sticky='w')
        c3.grid(row=3, column=1, sticky='w')
        c4.grid(row=4, column=1, sticky='w')
        c5.grid(row=5, column=1, sticky='w')
        c6.grid(row=6, column=1, sticky='w')
        c7.grid(row=7, column=1, sticky='w')
        c8.grid(row=8, column=1, sticky='w')
        c9.grid(row=9, column=1, sticky='w')
        c10.grid(row=10, column=1, sticky='w')
        c11.grid(row=11, column=1, sticky='w')
        c12.grid(row=12, column=1, sticky='w')
        c13.grid(row=13, column=1, sticky='w')
        c14.grid(row=14, column=1, sticky='w')

        def MAIndicator5(dataframe,keyword):
            Pages.slider = True
            Graph(dataframe, keyword).chooseIndicator('Moving Average 5').indicatorTransform()
            replacePlot(directory+'Interfaces/fig_ma.png', panel)

        def MAIndicator10(dataframe,keyword):
            Pages.slider = True
            Graph(dataframe, keyword).chooseIndicator('Moving Average 10').indicatorTransform()
            replacePlot(directory+'Interfaces/fig_ma.png', panel)

        def MAIndicator20(dataframe,keyword):
            Pages.slider = True
            Graph(dataframe, keyword).chooseIndicator('Moving Average 20').indicatorTransform()
            replacePlot(directory+'Interfaces/fig_ma.png', panel)

        def expIndicator(dataframe,keyword):
            Pages.slider = True
            Graph(dataframe, keyword).chooseIndicator('Exponential Average 0.1').indicatorTransform()
            replacePlot(directory+'Interfaces/fig_exp.png', panel)

        def expIndicator1(dataframe,keyword):
            Pages.slider = True
            Graph(dataframe, keyword).chooseIndicator('Exponential Average 0.2').indicatorTransform()
            replacePlot(directory+'Interfaces/fig_exp.png', panel)

        def expIndicator2(dataframe,keyword):
            Pages.slider = True
            Graph(dataframe, keyword).chooseIndicator('Exponential Average 0.3').indicatorTransform()
            replacePlot(directory+'Interfaces/fig_exp.png', panel)
        
        def quanIndicator(dataframe,keyword):
            Graph(dataframe,keyword).chooseIndicator('Quantile Day').indicatorTransform()
            replacePlot(directory+'Interfaces/fig_25qi.png', panel)
        
        def quantileIndicator(dataframe,keyword):
            Graph(dataframe,keyword).chooseIndicator('Quantile Interval').indicatorTransform()
            replacePlot(directory+'Interfaces/fig_qi.png', panel)

        def minmaxIndicator(dataframe,keyword):
            Graph(dataframe,keyword).chooseIndicator('Maximum and Minimum').indicatorTransform()
            replacePlot(directory+'Interfaces/fig_minmax.png', panel)
            
        def minmaxdayIndicator(dataframe,keyword):
            Graph(dataframe,keyword).chooseIndicator('MaxMin Day').indicatorTransform()
            replacePlot(directory+'Interfaces/fig_maxminday.png', panel)
        
        def positiveIndicator(dataframe,keyword):
            #Graph(dataframe,keyword='love').showGraph()
            Graph(dataframe,keyword).chooseIndicator('Positive').PositiveCount()
            replacePlot(directory+'Interfaces/fig_positive.png', panel)
            
        def negativeIndicator(dataframe,keyword):
            #Graph(dataframe,keyword='love').showGraph()
            Graph(dataframe,keyword).chooseIndicator('Negative').NegativeCount()
            replacePlot(directory+'Interfaces/fig_negative.png', panel)
            
        def neutralIndicator(dataframe,keyword):
            #Graph(dataframe,keyword='love').showGraph()
            Graph(dataframe,keyword).chooseIndicator('Neutral').NeutralCount()
            replacePlot(directory+'Interfaces/fig_neutral.png', panel)
            
        def countIndicator(dataframe,keyword):
            Graph(dataframe,keyword).showGraph()
            Graph(dataframe,keyword).chooseIndicator('Positive').allCount()
            replacePlot(directory+'Interfaces/fig_allCount.png', panel)
               
        def generateReport(myDir, name, summary, stats):
            if Pages.plan == "" or Pages.plan == "1":
                tk.messagebox.showerror("Information", "Please sign in or upgrade to premium plan to unlock this feature.")
            else: 
                rp = Report(myDir, name)
                rp.showReport(summary, stats)
                tk.messagebox.showinfo("Information", "Report generated!")

        def searchKeyword():
            keyword = e1.get()
            Pages.history.append(keyword)
            print('Searching keyword: ' + keyword)
            Pages.keyword = keyword

            if db.checkIfExists(Pages.keyword) == True:
                lineplot(get_dataframe(), Pages.keyword)    

            controller.show_frame(DashboardPage)

        def searchKeywordBtn(word): 
            Pages.keyword = word

            if db.checkIfExists(word) == True:
                lineplot(get_dataframe(), Pages.keyword) 
            
            controller.show_frame(DashboardPage)

        def nextFrame():
            if Pages.loginStatus == True:
                controller.show_frame(SettingsPage)
            else:
                controller.show_frame(LoginPage)


class LoginPage(tk.Frame, Pages): 
    
    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        # configure the grid
        self.Frame1 = tk.Frame(self, bg="grey")
        self.Frame5 = tk.Frame(self, bg="grey")
        self.Frame6 = tk.Frame(self)
        self.Frame10 = tk.Frame(self, bg="grey")

        self.Frame1.grid(row=0, column=0, rowspan=1, columnspan=2, sticky="nsew")
        self.Frame5.grid(row=0, column=2, rowspan=1, columnspan=7, sticky="nsew")
        self.Frame6.grid(row=1, column=0, rowspan=9, columnspan=10, sticky="nsew")
        self.Frame10.grid(row=0, column=9, rowspan=1, columnspan=1, sticky="nsew")

        for r in range(10):
            self.rowconfigure(r, weight=1)
        for c in range(10):
            self.columnconfigure(c, weight=1)


        # top-left section
        self.Frame1.grid_propagate(False)
        self.Frame1.grid_columnconfigure(0, weight=1)
        self.Frame1.grid_columnconfigure(2, weight=1)
        self.Frame1.grid_rowconfigure(0, weight=1)
        self.Frame1.grid_rowconfigure(2, weight=1)

        b1 = ttk.Button(self.Frame1, text='Dashboard', command = lambda : controller.show_frame(DashboardPage))
        b1.grid(row=1, column=1)


        # title section
        self.Frame5.grid_propagate(False)
        self.Frame5.grid_columnconfigure(0, weight=1)
        self.Frame5.grid_columnconfigure(2, weight=1)
        self.Frame5.grid_rowconfigure(0, weight=1)
        self.Frame5.grid_rowconfigure(2, weight=1)

        title = ttk.Label(self.Frame5, text="Sentiment Dashboard", background="grey")
        title.grid(column=1, row=1)
        title.config(font=('helvetica', 44))


        # user account
        self.Frame10.grid_propagate(False)
        self.Frame10.grid_columnconfigure(0, weight=1)
        self.Frame10.grid_columnconfigure(2, weight=1)
        self.Frame10.grid_rowconfigure(0, weight=1)
        self.Frame10.grid_rowconfigure(2, weight=1)

        l3 = ttk.Button(self.Frame10, text=Pages.getMsg(Pages.loginStatus, Pages.username), command = lambda : nextFrame())
        l3.grid(row=1, column=1)


        # main frame
        self.Frame6.grid_propagate(False)
        for r in range(10):
            self.Frame6.rowconfigure(r, weight=1)
        for c in range(10):
            self.Frame6.columnconfigure(c, weight=1)

        # username
        username_label = ttk.Label(self.Frame6, text="Username:")
        username_label.grid(column=4, row=3, sticky="e", padx=10)

        username_entry = ttk.Entry(self.Frame6)
        username_entry.grid(column=5, row=3, sticky='w', padx=10)

        # password
        password_label = ttk.Label(self.Frame6, text="Password:")
        password_label.grid(column=4, row=4, sticky="e", padx=10)

        password_entry = ttk.Entry(self.Frame6, show="*")
        password_entry.grid(column=5, row=4, sticky="w", padx=10)

        # login button
        login_button = ttk.Button(self.Frame6, text="Login", command = lambda: getLogin())
        login_button.grid(column=4, row=6, sticky="e", padx=10)

        # signup button
        signup_button = ttk.Button(self.Frame6, text="Signup", command = lambda: controller.show_frame(SignupPage))
        signup_button.grid(column=5, row=6, padx=10)

        # forget password
        forgotPw_button = ttk.Button(self.Frame6, text="Forgot Password?", command = lambda: controller.show_frame(ForgotPasswordPage))
        forgotPw_button.grid(column=5, row=7, padx=10)

        db = sqlManagement()

        # initialize db
        # db.initialize_db() #DONE, create users_info database
        # db.initialize_user_table() #DONE, create users table
        # db.initialize_usersfav_table() #DONE, create usersfav table
        # db.display_current_table()

        # Link to SQL
        def getLogin():
            username = username_entry.get()
            password = password_entry.get()

            if username == "" or password == "":
                tk.messagebox.showinfo("Information", "Please fill in all the required information.")

            else:
                result = db.checkuserNpass(username,password)
                tk.messagebox.showinfo("Information", result)

                if re.search(r'Welcome', result):
                    '''successfully log in'''
                    Pages.loginStatus = True
                    Pages.username = username
                    Pages.password = password
                    Pages.email = db.getemail(username)
                    Pages.plan = db.getplan(username)
                    Pages.ans = db.getnickname(username)
                    
                    if Pages.plan == 1:
                        Pages.limit = 5
                    elif Pages.plan == 2:
                        Pages.limit = 50
                    else:
                        Pages.limit = 10000000
                    
                    controller.show_frame(DashboardPage)

        def nextFrame():
            if Pages.loginStatus == True:
                controller.show_frame(SettingsPage)
            else:
                controller.show_frame(LoginPage)


class SignupPage(tk.Frame, Pages):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        Pages.change = False

        # configure the grid
        self.Frame1 = tk.Frame(self, bg="grey")
        self.Frame5 = tk.Frame(self, bg="grey")
        self.Frame6 = tk.Frame(self)
        self.Frame10 = tk.Frame(self, bg="grey")

        self.Frame1.grid(row=0, column=0, rowspan=1, columnspan=2, sticky="nsew")
        self.Frame5.grid(row=0, column=2, rowspan=1, columnspan=7, sticky="nsew")
        self.Frame6.grid(row=1, column=0, rowspan=9, columnspan=10, sticky="nsew")
        self.Frame10.grid(row=0, column=9, rowspan=1, columnspan=1, sticky="nsew")

        for r in range(10):
            self.rowconfigure(r, weight=1)
        for c in range(10):
            self.columnconfigure(c, weight=1)


        # top-left section
        self.Frame1.grid_propagate(False)
        self.Frame1.grid_columnconfigure(0, weight=1)
        self.Frame1.grid_columnconfigure(2, weight=1)
        self.Frame1.grid_rowconfigure(0, weight=1)
        self.Frame1.grid_rowconfigure(2, weight=1)

        b1 = ttk.Button(self.Frame1, text='Dashboard', command = lambda : controller.show_frame(DashboardPage))
        b1.grid(row=1, column=1)


        # title section
        self.Frame5.grid_propagate(False)
        self.Frame5.grid_columnconfigure(0, weight=1)
        self.Frame5.grid_columnconfigure(2, weight=1)
        self.Frame5.grid_rowconfigure(0, weight=1)
        self.Frame5.grid_rowconfigure(2, weight=1)

        title = ttk.Label(self.Frame5, text="Sentiment Dashboard", background="grey")
        title.grid(column=1, row=1)
        title.config(font=('helvetica', 44))


        # user account
        self.Frame10.grid_propagate(False)
        self.Frame10.grid_columnconfigure(0, weight=1)
        self.Frame10.grid_columnconfigure(2, weight=1)
        self.Frame10.grid_rowconfigure(0, weight=1)
        self.Frame10.grid_rowconfigure(2, weight=1)

        l3 = ttk.Button(self.Frame10, text=Pages.getMsg(Pages.loginStatus, Pages.username), command = lambda : nextFrame())
        l3.grid(row=1, column=1)


        # main frame
        self.Frame6.grid_propagate(False)
        for r in range(10):
            self.Frame6.rowconfigure(r, weight=1)
        for c in range(10):
            self.Frame6.columnconfigure(c, weight=1)

        # username
        username_label = ttk.Label(self.Frame6, text="Username:")
        username_label.grid(column=4, row=2, sticky="e", padx=10)

        username_entry = ttk.Entry(self.Frame6)
        username_entry.grid(column=5, row=2, sticky="w", padx=10)

        # email
        email_label = ttk.Label(self.Frame6, text="Email:")
        email_label.grid(column=4, row=3, sticky="e", padx=10)

        email_entry = ttk.Entry(self.Frame6)
        email_entry.grid(column=5, row=3, sticky="w", padx=10)

        # password
        password_label = ttk.Label(self.Frame6, text="Password:")
        password_label.grid(column=4, row=4, sticky="e", padx=10)

        password_entry = ttk.Entry(self.Frame6,  show="*")
        password_entry.grid(column=5, row=4, sticky="w", padx=10)

        # confirm password
        password_label1 = ttk.Label(self.Frame6, text="Confirm Password:")
        password_label1.grid(column=4, row=5, sticky="e", padx=10)

        password_entry1 = ttk.Entry(self.Frame6,  show="*")
        password_entry1.grid(column=5, row=5, sticky="w", padx=10)

        # verification
        question = ttk.Label(self.Frame6, text="Verification Question:\nWhat was your\nchildhood nickname?")
        question.grid(column=4, row=6, sticky='e', padx=10)

        ans = ttk.Entry(self.Frame6)
        ans.grid(column=5, row=6, sticky='w', padx=10)

        # create account
        create_button = ttk.Button(self.Frame6, text="Continue", command=lambda:signup())
        create_button.grid(column=5, row=8) 

        db = sqlManagement()

        def signup():
            email = email_entry.get()
            username = username_entry.get()
            password = password_entry.get()
            password1 = password_entry1.get()
            answer = ans.get()

            if email == "" or username == "" or password == "" or password1 == "" or answer == "":
                tk.messagebox.showinfo("Information", "Please fill in all the required information.")
            
            else:
                validUser = db.validate_username(username) 
                validPassword = validatePassword(password, password1)

                if not validUser:
                    tk.messagebox.showerror("Information", "This username already exists.")
                elif not validPassword:
                    tk.messagebox.showerror("Information", "Passwords don't match!")

                else:
                    if len(password) > 3:
                        Pages.username = username
                        Pages.password = password
                        Pages.email = email
                        Pages.ans = answer
                        controller.show_frame(PaymentPage)

                    else:
                        tk.messagebox.showerror("Information", "Your password needs to be longer than 3 characters.")

        def validatePassword(password, password1):
            if password == password1:
                return True
            return False            

        def nextFrame():
            if Pages.loginStatus == True:
                controller.show_frame(SettingsPage)
            else:
                controller.show_frame(LoginPage)


class PaymentPage(tk.Frame, Pages):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        # configure the grid
        self.Frame1 = tk.Frame(self, bg="grey")
        self.Frame5 = tk.Frame(self, bg="grey")
        self.Frame6 = tk.Frame(self)
        self.Frame10 = tk.Frame(self, bg="grey")

        self.Frame1.grid(row=0, column=0, rowspan=1, columnspan=2, sticky="nsew")
        self.Frame5.grid(row=0, column=2, rowspan=1, columnspan=7, sticky="nsew")
        self.Frame6.grid(row=1, column=0, rowspan=9, columnspan=10, sticky="nsew")
        self.Frame10.grid(row=0, column=9, rowspan=1, columnspan=1, sticky="nsew")

        for r in range(10):
            self.rowconfigure(r, weight=1)
        for c in range(10):
            self.columnconfigure(c, weight=1)


        # top-left section
        self.Frame1.grid_propagate(False)
        self.Frame1.grid_columnconfigure(0, weight=1)
        self.Frame1.grid_columnconfigure(2, weight=1)
        self.Frame1.grid_rowconfigure(0, weight=1)
        self.Frame1.grid_rowconfigure(2, weight=1)

        b1 = ttk.Button(self.Frame1, text='Dashboard', command = lambda : controller.show_frame(DashboardPage))
        b1.grid(row=1, column=1)


        # title section
        self.Frame5.grid_propagate(False)
        self.Frame5.grid_columnconfigure(0, weight=1)
        self.Frame5.grid_columnconfigure(2, weight=1)
        self.Frame5.grid_rowconfigure(0, weight=1)
        self.Frame5.grid_rowconfigure(2, weight=1)

        title = ttk.Label(self.Frame5, text="Sentiment Dashboard", background="grey")
        title.grid(column=1, row=1)
        title.config(font=('helvetica', 44))


        # user account
        self.Frame10.grid_propagate(False)
        self.Frame10.grid_columnconfigure(0, weight=1)
        self.Frame10.grid_columnconfigure(2, weight=1)
        self.Frame10.grid_rowconfigure(0, weight=1)
        self.Frame10.grid_rowconfigure(2, weight=1)

        l3 = ttk.Button(self.Frame10, text=Pages.getMsg(Pages.loginStatus, Pages.username), command = lambda : nextFrame())
        l3.grid(row=1, column=1)


        # main frame
        self.Frame6.grid_propagate(False)
        for r in range(10):
            self.Frame6.rowconfigure(r, weight=1)
        for c in range(7):
            self.Frame6.columnconfigure(c, weight=1)

        plan1button = ttk.Button(self.Frame6, text="Select", command=lambda: selectPlan(1))
        plan2button = ttk.Button(self.Frame6, text="Select", command=lambda: selectPlan(2))
        plan3button = ttk.Button(self.Frame6, text="Select", command=lambda: selectPlan(3))

        text1="Starter\nFree\nForever\n✔️ 30 keywords per month.\n❌ Cannot generate reports\n❌ Limit to number of\ntweets to extract."
        text2="Professional\n$7.99 per user/month\nBilled annually or $9.99\nmonth-to-month\n✔️ 50 keywords per month.\n✔️ Can generate 3 reports."
        text3="Organisation\n$19.99 per user/month\nBilled annually or $24.99\nmonth-to-month\n✔️ Unlimited keywords per\nmonth.\n✔️ Can generate unlimited\nreports."
        texts = text1,text2,text3

        for i in range(len(texts)):
            msg = tk.Message(self.Frame6, text=texts[i], width=500, justify='center', bg='DarkGrey')
            msg.grid(column = 2*i+1, row=4, sticky='nsew')

        plan1button.grid(column = 1, row = 6)
        plan2button.grid(column = 3, row = 6)
        plan3button.grid(column = 5, row = 6)

        db = sqlManagement()

        def selectPlan(planNum):
            Pages.plan = planNum
            if Pages.change == True:
                db.editUserSubscription(Pages.username, Pages.password, Pages.plan)
                tk.messagebox.showinfo("Information", "Plan successfully changed.")
                controller.show_frame(SettingsPage)
            else:
                controller.show_frame(ConfirmationPage)

        def nextFrame():
            if Pages.loginStatus == True:
                controller.show_frame(SettingsPage)
            else:
                controller.show_frame(LoginPage)


class ConfirmationPage(tk.Frame, Pages):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        # configure the grid
        self.Frame1 = tk.Frame(self, bg="grey")
        self.Frame5 = tk.Frame(self, bg="grey")
        self.Frame6 = tk.Frame(self)
        self.Frame10 = tk.Frame(self, bg="grey")

        self.Frame1.grid(row=0, column=0, rowspan=1, columnspan=2, sticky="nsew")
        self.Frame5.grid(row=0, column=2, rowspan=1, columnspan=7, sticky="nsew")
        self.Frame6.grid(row=1, column=0, rowspan=9, columnspan=10, sticky="nsew")
        self.Frame10.grid(row=0, column=9, rowspan=1, columnspan=1, sticky="nsew")

        for r in range(10):
            self.rowconfigure(r, weight=1)
        for c in range(10):
            self.columnconfigure(c, weight=1)


        # top-left section
        self.Frame1.grid_propagate(False)
        self.Frame1.grid_columnconfigure(0, weight=1)
        self.Frame1.grid_columnconfigure(2, weight=1)
        self.Frame1.grid_rowconfigure(0, weight=1)
        self.Frame1.grid_rowconfigure(2, weight=1)

        b1 = ttk.Button(self.Frame1, text='Dashboard', command = lambda : controller.show_frame(DashboardPage))
        b1.grid(row=1, column=1)


        # title section
        self.Frame5.grid_propagate(False)
        self.Frame5.grid_columnconfigure(0, weight=1)
        self.Frame5.grid_columnconfigure(2, weight=1)
        self.Frame5.grid_rowconfigure(0, weight=1)
        self.Frame5.grid_rowconfigure(2, weight=1)

        title = ttk.Label(self.Frame5, text="Sentiment Dashboard", background="grey")
        title.grid(column=1, row=1)
        title.config(font=('helvetica', 44))


        # user account
        self.Frame10.grid_propagate(False)
        self.Frame10.grid_columnconfigure(0, weight=1)
        self.Frame10.grid_columnconfigure(2, weight=1)
        self.Frame10.grid_rowconfigure(0, weight=1)
        self.Frame10.grid_rowconfigure(2, weight=1)

        l3 = ttk.Button(self.Frame10, text=Pages.getMsg(Pages.loginStatus, Pages.username), command = lambda : nextFrame())
        l3.grid(row=1, column=1)


        # main frame
        self.Frame6.grid_propagate(False)
        for r in range(10):
            self.Frame6.rowconfigure(r, weight=1)
        for c in range(3):
            self.Frame6.columnconfigure(c, weight=1)     

        confirmationMsg = Pages.getConfirmation(Pages.username, Pages.email, Pages.plan, Pages.ans)
        confirmation = tk.Message(self.Frame6, text=confirmationMsg, width=500, justify='center', bg='DarkGrey')
        confirmation.grid(column = 1, row=4)

        create = ttk.Button(self.Frame6, text="Create Account", command=lambda: createAccount())
        create.grid(column = 1, row = 6)
       
        db = sqlManagement()

        def createAccount():
            Pages.loginStatus = True
            db.createNew(Pages.username, Pages.email, Pages.password, Pages.plan, Pages.ans)
            controller.show_frame(DashboardPage)

        def nextFrame():
            if Pages.loginStatus == True:
                controller.show_frame(SettingsPage)
            else:
                controller.show_frame(LoginPage)


class SettingsPage(tk.Frame, Pages):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        # configure the grid
        self.Frame1 = tk.Frame(self, bg="grey")
        self.Frame5 = tk.Frame(self, bg="grey")
        self.Frame6 = tk.Frame(self)
        self.Frame10 = tk.Frame(self, bg="grey")

        self.Frame1.grid(row=0, column=0, rowspan=1, columnspan=2, sticky="nsew")
        self.Frame5.grid(row=0, column=2, rowspan=1, columnspan=7, sticky="nsew")
        self.Frame6.grid(row=1, column=0, rowspan=9, columnspan=10, sticky="nsew")
        self.Frame10.grid(row=0, column=9, rowspan=1, columnspan=1, sticky="nsew")

        for r in range(10):
            self.rowconfigure(r, weight=1)
        for c in range(10):
            self.columnconfigure(c, weight=1)


        # top-left section
        self.Frame1.grid_propagate(False)
        self.Frame1.grid_columnconfigure(0, weight=1)
        self.Frame1.grid_columnconfigure(2, weight=1)
        self.Frame1.grid_rowconfigure(0, weight=1)
        self.Frame1.grid_rowconfigure(2, weight=1)

        b1 = ttk.Button(self.Frame1, text='Dashboard', command = lambda : controller.show_frame(DashboardPage))
        b1.grid(row=1, column=1)


        # title section
        self.Frame5.grid_propagate(False)
        self.Frame5.grid_columnconfigure(0, weight=1)
        self.Frame5.grid_columnconfigure(2, weight=1)
        self.Frame5.grid_rowconfigure(0, weight=1)
        self.Frame5.grid_rowconfigure(2, weight=1)

        title = ttk.Label(self.Frame5, text="Sentiment Dashboard", background="grey")
        title.grid(column=1, row=1)
        title.config(font=('helvetica', 44))


        # user account
        self.Frame10.grid_propagate(False)
        self.Frame10.grid_columnconfigure(0, weight=1)
        self.Frame10.grid_columnconfigure(2, weight=1)
        self.Frame10.grid_rowconfigure(0, weight=1)
        self.Frame10.grid_rowconfigure(2, weight=1)

        l3 = ttk.Button(self.Frame10, text=Pages.getMsg(Pages.loginStatus, Pages.username), command = lambda : nextFrame())
        l3.grid(row=1, column=1)


        # main frame
        self.Frame6.grid_propagate(False)
        for r in range(10):
            self.Frame6.rowconfigure(r, weight=1)
        for c in range(3):
            self.Frame6.columnconfigure(c, weight=1)     

        # information
        infoText = f'\n\nUsername: {Pages.username}\n\nEmail: {Pages.email}\n\nPlan: {Pages.plan}\n\n'
        information = tk.Message(self.Frame6, text=infoText, width=500, justify='center', bg='DarkGrey')
        information.grid(column=1, row=3)

        # change plan
        changePlanBtn = ttk.Button(self.Frame6, text = "Change Plan", command = lambda : changePlan())
        changePlanBtn.grid(column=1, row=5)

        # change password
        changePwBtn = ttk.Button(self.Frame6, text = "Change Password", command = lambda : controller.show_frame(ChangePasswordPage))
        changePwBtn.grid(column=1, row=6)

        # log out 
        logout_button = ttk.Button(self.Frame6, text="Log out", command = lambda:logout())
        logout_button.grid(column=1, row=7)

        def nextFrame():
            if Pages.loginStatus == True:
                controller.show_frame(SettingsPage)
            else:
                controller.show_frame(LoginPage)

        def logout():
            Pages.loginStatus = False
            controller.show_frame(DashboardPage)

        def changePlan():
            Pages.change = True
            controller.show_frame(PaymentPage)


class ForgotPasswordPage(tk.Frame, Pages):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        # configure the grid
        self.Frame1 = tk.Frame(self, bg="grey")
        self.Frame5 = tk.Frame(self, bg="grey")
        self.Frame6 = tk.Frame(self)
        self.Frame10 = tk.Frame(self, bg="grey")

        self.Frame1.grid(row=0, column=0, rowspan=1, columnspan=2, sticky="nsew")
        self.Frame5.grid(row=0, column=2, rowspan=1, columnspan=7, sticky="nsew")
        self.Frame6.grid(row=1, column=0, rowspan=9, columnspan=10, sticky="nsew")
        self.Frame10.grid(row=0, column=9, rowspan=1, columnspan=1, sticky="nsew")

        for r in range(10):
            self.rowconfigure(r, weight=1)
        for c in range(10):
            self.columnconfigure(c, weight=1)


        # top-left section
        self.Frame1.grid_propagate(False)
        self.Frame1.grid_columnconfigure(0, weight=1)
        self.Frame1.grid_columnconfigure(2, weight=1)
        self.Frame1.grid_rowconfigure(0, weight=1)
        self.Frame1.grid_rowconfigure(2, weight=1)

        b1 = ttk.Button(self.Frame1, text='Dashboard', command = lambda : controller.show_frame(DashboardPage))
        b1.grid(row=1, column=1)


        # title section
        self.Frame5.grid_propagate(False)
        self.Frame5.grid_columnconfigure(0, weight=1)
        self.Frame5.grid_columnconfigure(2, weight=1)
        self.Frame5.grid_rowconfigure(0, weight=1)
        self.Frame5.grid_rowconfigure(2, weight=1)

        title = ttk.Label(self.Frame5, text="Sentiment Dashboard", background="grey")
        title.grid(column=1, row=1)
        title.config(font=('helvetica', 44))


        # user account
        self.Frame10.grid_propagate(False)
        self.Frame10.grid_columnconfigure(0, weight=1)
        self.Frame10.grid_columnconfigure(2, weight=1)
        self.Frame10.grid_rowconfigure(0, weight=1)
        self.Frame10.grid_rowconfigure(2, weight=1)

        l3 = ttk.Button(self.Frame10, text=Pages.getMsg(Pages.loginStatus, Pages.username), command = lambda : nextFrame())
        l3.grid(row=1, column=1)


        # main frame
        self.Frame6.grid_propagate(False)
        for r in range(10):
            self.Frame6.rowconfigure(r, weight=1)
        for c in range(10):
            self.Frame6.columnconfigure(c, weight=1)     

        verificationQ = 'Please verify your identity.\nWhat was your childhood nickname?'

        verification = ttk.Label(self.Frame6, text = verificationQ)
        verification.grid(row=2, column=4, sticky='e', padx=10)

        verificationAns = ttk.Entry(self.Frame6)
        verificationAns.grid(row=2, column=5, sticky='w', padx=10)

        username = ttk.Label(self.Frame6, text = "Username:")
        username.grid(row=3, column=4, sticky='e', padx=10)

        usernameEntry = ttk.Entry(self.Frame6)
        usernameEntry.grid(row=3, column=5, sticky='w', padx=10)

        newPw1 = ttk.Label(self.Frame6, text = "New password:")
        newPw1.grid(row=4, column=4, sticky='e', padx=10)

        newPwEntry1 = ttk.Entry(self.Frame6, show="*")
        newPwEntry1.grid(row=4, column=5, sticky='w', padx=10)

        newPw2 = ttk.Label(self.Frame6, text = "Confirm password:")
        newPw2.grid(row=5, column=4, sticky='e', padx=10)

        newPwEntry2 = ttk.Entry(self.Frame6, show="*")
        newPwEntry2.grid(row=5, column=5, sticky='w', padx=10)

        continueBtn = ttk.Button(self.Frame6, text="Change Password", command=lambda:checkAns())
        continueBtn.grid(row=6, column=5)

        db = sqlManagement()

        def checkAns():
            userAns = verificationAns.get()
            username = usernameEntry.get()
            pw1 = newPwEntry1.get()
            pw2 = newPwEntry2.get()

            if userAns == "" or username == "" or pw1 == "" or pw2 == "":
                tk.messagebox.showinfo("Information", "Please fill in all the required information.")
                return
            
            validUser = db.validate_username(username) 
            if not validUser:
                 tk.messagebox.showerror("Information", "This username does not exists.")
                 return
                            
            Pages.ans = db.getnickname(username)
            if userAns == Pages.ans:
                validPassword = validatePassword(pw1, pw2)
                if not validPassword:
                    tk.messagebox.showerror("Information", "Passwords don't match.")
                
                else:
                    if len(pw2) > 3:
                        db.forget_password(username, userAns, pw2)
                        tk.messagebox.showinfo("Information", "Password successfully changed.")
                        controller.show_frame(DashboardPage)
                    else:
                        tk.messagebox.showerror("Information", "Your password needs to be longer than 3 characters.")
        
        def validatePassword(password, password1):
            if password == password1:
                return True
            return False

        def nextFrame():
            if Pages.loginStatus == True:
                controller.show_frame(SettingsPage)
            else:
                controller.show_frame(LoginPage)


class ChangePasswordPage(tk.Frame, Pages):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        # configure the grid
        self.Frame1 = tk.Frame(self, bg="grey")
        self.Frame5 = tk.Frame(self, bg="grey")
        self.Frame6 = tk.Frame(self)
        self.Frame10 = tk.Frame(self, bg="grey")

        self.Frame1.grid(row=0, column=0, rowspan=1, columnspan=2, sticky="nsew")
        self.Frame5.grid(row=0, column=2, rowspan=1, columnspan=7, sticky="nsew")
        self.Frame6.grid(row=1, column=0, rowspan=9, columnspan=10, sticky="nsew")
        self.Frame10.grid(row=0, column=9, rowspan=1, columnspan=1, sticky="nsew")

        for r in range(10):
            self.rowconfigure(r, weight=1)
        for c in range(10):
            self.columnconfigure(c, weight=1)
 

        # top-left section
        self.Frame1.grid_propagate(False)
        self.Frame1.grid_columnconfigure(0, weight=1)
        self.Frame1.grid_columnconfigure(2, weight=1)
        self.Frame1.grid_rowconfigure(0, weight=1)
        self.Frame1.grid_rowconfigure(2, weight=1)

        b1 = ttk.Button(self.Frame1, text='Dashboard', command = lambda : controller.show_frame(DashboardPage))
        b1.grid(row=1, column=1)


        # title section
        self.Frame5.grid_propagate(False)
        self.Frame5.grid_columnconfigure(0, weight=1)
        self.Frame5.grid_columnconfigure(2, weight=1)
        self.Frame5.grid_rowconfigure(0, weight=1)
        self.Frame5.grid_rowconfigure(2, weight=1)

        title = ttk.Label(self.Frame5, text="Sentiment Dashboard", background="grey")
        title.grid(column=1, row=1)
        title.config(font=('helvetica', 44))


        # user account
        self.Frame10.grid_propagate(False)
        self.Frame10.grid_columnconfigure(0, weight=1)
        self.Frame10.grid_columnconfigure(2, weight=1)
        self.Frame10.grid_rowconfigure(0, weight=1)
        self.Frame10.grid_rowconfigure(2, weight=1)

        l3 = ttk.Button(self.Frame10, text=Pages.getMsg(Pages.loginStatus, Pages.username), command = lambda : nextFrame())
        l3.grid(row=1, column=1)


        # main frame
        self.Frame6.grid_propagate(False)
        for r in range(10):
            self.Frame6.rowconfigure(r, weight=1)
        for c in range(10):
            self.Frame6.columnconfigure(c, weight=1)    

        verificationQ = 'Please verify your identity.\nWhat was your childhood nickname?'

        verification = ttk.Label(self.Frame6, text = verificationQ)
        verification.grid(row=2, column=4, sticky='e', padx=10)

        verificationAns = ttk.Entry(self.Frame6)
        verificationAns.grid(row=2, column=5, sticky='w', padx=10)

        oldPw = ttk.Label(self.Frame6, text = "Old password:")
        oldPw.grid(row=3, column=4, sticky='e', padx=10)

        oldPwEntry = ttk.Entry(self.Frame6, show="*")
        oldPwEntry.grid(row=3, column=5, sticky='w', padx=10)

        newPw1 = ttk.Label(self.Frame6, text = "New password:")
        newPw1.grid(row=4, column=4, sticky='e', padx=10)

        newPwEntry1 = ttk.Entry(self.Frame6, show="*")
        newPwEntry1.grid(row=4, column=5, sticky='w', padx=10)

        newPw2 = ttk.Label(self.Frame6, text = "Confirm password:")
        newPw2.grid(row=5, column=4, sticky='e', padx=10)

        newPwEntry2 = ttk.Entry(self.Frame6, show="*")
        newPwEntry2.grid(row=5, column=5, sticky='w', padx=10)

        continueBtn = ttk.Button(self.Frame6, text="Change Password", command=lambda:checkAns())
        continueBtn.grid(row=6, column=5)

        db = sqlManagement()

        def checkAns():
            userAns = verificationAns.get()
            oldpw = oldPwEntry.get()
            pw1 = newPwEntry1.get()
            pw2 = newPwEntry2.get()

            if userAns == "" or oldpw == "" or pw1 == "" or pw2 == "":
                tk.messagebox.showinfo("Information", "Please fill in all the required information.")
                return
                            
            Pages.ans = db.getnickname(Pages.username)
            if userAns == Pages.ans:
                validPassword = validatePassword(pw1, pw2)
                if not validPassword:
                    tk.messagebox.showerror("Information", "Passwords don't match.")
                
                else:
                    if len(pw2) > 3:
                        db.editpassword(Pages.username, userAns, pw2)
                        tk.messagebox.showinfo("Information", "Password successfully changed.")
                        controller.show_frame(DashboardPage)
                    else:
                        tk.messagebox.showerror("Information", "Your password needs to be longer than 3 characters.")
        
        def validatePassword(password, password1):
            if password == password1:
                return True
            return False

        def nextFrame():
            if Pages.loginStatus == True:
                controller.show_frame(SettingsPage)
            else:
                controller.show_frame(LoginPage)


'''driver code'''
app = tkinterApp()
app.mainloop()
