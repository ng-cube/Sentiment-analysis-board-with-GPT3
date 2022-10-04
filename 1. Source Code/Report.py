import os
import shutil
from PDF import PDF
'''
To call a report, please first construct a report object report = Report(Directory, reportname)

Then, call report.showReport(sentimentreasoning,[percentage of postive tweets, percentage of negative tweets, percentage of neutral tweets, mean, variance])


'''
class Report():
    def __init__(self, storage_dir, report_name): #numbers,reasoning
        self.storageDirectory = storage_dir
        self.reportName = report_name
    
    #construct dir for images
    def constructDir(self):
        try:
            shutil.rmtree(self.storageDirectory)
            os.mkdir(self.storageDirectory)
        except FileNotFoundError:
            os.mkdir(self.storageDirectory)

    #and format numbers right below:
    def displayNumbers(self,paraArray):
        if (len(paraArray)!=5):
            raise Exception("Parameter array must be of length 5 and in the sequence of percentage of positive tweets, percentage of negative tweets, percentage of neutral tweets, mean and variance.")
        stat=[]
        pair1=[]
        pair2=[]
        pair3=[]
        pair4=[]
        pair5=[]
        pair1.append('Percentage of positive tweets')
        pair1.append(str(paraArray[0]))
        pair2.append('Percentage of negative tweets')
        pair2.append(str(paraArray[1]))
        pair3.append('Percentage of neutral tweets')
        pair3.append(str(paraArray[2]))
        pair4.append('Average sentiment')
        pair4.append(str(paraArray[3]))
        pair5.append('Variance')
        pair5.append(str(paraArray[4]))
        stat.append(pair1)
        stat.append(pair2)
        stat.append(pair3)
        stat.append(pair4)
        stat.append(pair5)
        return stat
            

    #show report
    def showReport(self,summary, numbers):
        self.constructDir()
        pdf = PDF(self.storageDirectory,self.reportName, summary, self.displayNumbers(numbers))
        pdf.print_page()
        pdf.output(self.storageDirectory+'/Report.pdf', 'F')