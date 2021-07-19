#
import os
import fpdf
from fpdf import FPDF

from plotly.offline import init_notebook_mode, plot_mpl , plot
import matplotlib.pyplot as plt

import plotly.express as px
import plotly
import plotly.graph_objects as go
import os
import numpy as np


class PDF(FPDF):
    # def __init__(self):
    #     super().__init__()
    #     self.upFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    def border1(self):
        self.set_line_width(0.0)
        self.line(5.0, 5.0, 205.0, 5.0)  # top one
        self.line(5.0, 292.0, 205.0, 292.0)  # bottom one
        self.line(5.0, 5.0, 5.0, 292.0)  # left one
        self.line(205.0, 5.0, 205.0, 292.0)  # right one

    def border2(self):
        self.rect(5.0, 5.0, 200.0, 287.0)
        self.rect(8.0, 8.0, 194.0, 282.0)

    def border3(self):
        self.set_fill_color(32.0, 47.0, 250.0)  # color for outer rectangle
        self.rect(5.0, 5.0, 200.0, 287.0, 'DF')
        self.set_fill_color(255, 255, 255)  # color for inner rectangle
        # self.rect(8.0, 8.0, 194.0, 282.0, 'FD')

    def border4(self):
        self.rect(5.0, 5.0, 200.0, 287.0)

        # self.set_fill_color(32.0, 47.0, 250.0)  # color for outer rectangle
        self.set_fill_color(0.0, 0.0, 0.0)  # color for outer rectangle
        self.rect(6.0, 6.0, 198.0, 285.0, 'DF')
        self.set_fill_color(255, 255, 255)  # color for inner rectangle
        self.rect(7.0, 7.0, 196.0, 283.0, 'FD')

        self.rect(8.0, 8.0, 194.0, 281.0)

    # Logos
    def imagex(self):
        self.upFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.set_xy(150.0, 9.0)
        self.image(self.upFolder + '/SourceCode/SourceFiles/Logos/Bargh.png', link='', type='', w=1586 / 55, h=1920 / 70)
        self.set_xy(178.0, 9.0)
        self.image(self.upFolder + '/SourceCode/SourceFiles/Logos/Kavan.png', link='', type='', w=1586 / 70, h=1920 / 60)
        self.set_xy(70.0, 19.0)
        self.image(self.upFolder + '/SourceCode/SourceFiles/Logos/titr.png', link='', type='', w=1586 / 25, h=1920 / 200)

    # Title
    def titles(self):
        self.set_xy(0.0, 0.0)
        # self.set_font('Arial', 'B', 16)
        self.set_text_color(220, 50, 50)

    # Save Chart of all points
    def createChart(self,xArray,yArray,mtTitle,AlarmArray,chartName,figNum,OperatorName,ProjectName):
        self.upFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        fig = plt.figure(figNum, figsize=(12, 6))
        # print("\n"+"ZZ"+"\n",xArray,yArray)
        # print(xArray.shape(), yArray.shape())
        plt.plot(xArray, yArray, marker = 'o')
        plt.plot(xArray, AlarmArray)
        plt.legend(["Current Level", "Alarm Level"])
        plt.grid(True)
        step = int((max(xArray)+1 - min(xArray)) / 25)
        if step ==0:
            step =1
#         print(xArray,len(xArray))
        if len(xArray) == 1:
            plt.xticks(np.arange(min(xArray)-2,min(xArray)+2,1))
        else:
#             print("DD",min(xArray), max(xArray)+1, step)
            aa= np.arange(min(xArray), max(xArray)+1, step)
#             print("aa",aa)
            plt.xticks(aa)

        plt.yticks(np.arange(0, 101, 5))
        plt.xticks(rotation=60)

        plt.title(mtTitle, bbox={'facecolor': '0.8', 'pad': 7})
        
        # fig.savefig('plot_101.png',bbox_inches='tight')
        # self.pltx = (os.getcwd() + '/' + "plot_101.png")

        fig.savefig(self.upFolder +'/Users/'+OperatorName+'/'+ProjectName+'/SensorPlots/'+chartName+'.png',bbox_inches='tight')
        # self.pltx = (os.getcwd() + '/SensorCharts/' + chartName+'.png')

        # plt.show()

    # Load Chart to Show Level of all points
    def charts(self,chartName,OperatorName,ProjectName):
        self.upFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.set_xy(12.0, 125.0)

        self.pltx = (self.upFolder + '/Users/' + OperatorName + '/' + ProjectName + '/SensorPlots/' + chartName + '.png')
        # self.pltx = (os.getcwd() + '/Users/'+OperatorName+'/'+ProjectName+'/SensorPlots/'+chartName+'.png')
        self.image(self.pltx, link='', type='', w=180, h=150)

    # Page Number
    def footer(self):
        # Go to 1.5 cm from bottom
        self.set_y(-20)
        # Select Arial italic 8
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page %s' % self.page_no(), 0, 0, 'C')

    # Table For all Points
    def tables1(self,table1,table1Header):
        self.set_xy(75, 40)
        self.set_font('Times', '', 12.0)
        self.set_text_color(0, 0, 20)
        self.cell(50, 10, 'Inspection Information', align='C')
        # pdf.set_fill_color(200, 200, 200)
        self.set_font('Times', '', 10.0)
        self.ln(0.5)

        row_height = 10

        col_width = int(185/13)
        start_X = 15
        start_Y = 150
        Real_cnt_row = 0
        Real_cnt_col = 0
        cnt_row = 0
        cnt_col = 1
        EndPage = 270
        color = 0
        # array = np.arange(3900).reshape(300, 13)
#         AlarmRate = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200,1300]
        # print(array)

        self.set_xy(start_X, start_Y)
        # print("F", type(table1))

        # for row in array:  # df[:,0:2]:
        # print("R", range(table1.rowCount()),range(table1.columnCount()))
        # for row in range(1):

        for row in range(table1.rowCount()):

            # print("B",row)
            alarmCode = int(table1.item(row, 1).text())
            alarmCode2 = table1.item(row, 4).text()
            # print("H",alarmCode2,alarmCode2[0],alarmCode2[1],alarmCode2[2])
            Real_cnt_row += 1
            cnt_row += 1
            cnt_col = 0
            Real_cnt_col = cnt_col

            if row == 0:
                thisHeight = start_Y + (-1) * row_height
                self.set_xy(start_X, thisHeight)
                for colHeader in range(len(table1Header)):
                    self.set_font('Times', '', 10.0)
                    self.set_fill_color(47, 216, 230)
                    col_width = 14
                    if colHeader == 0 or colHeader == 5:
                        col_width = 12
                    elif colHeader == 7 or colHeader == 8 or colHeader == 9:
                        col_width = 12
                    elif colHeader == 6 or colHeader == 10:
                        col_width = 16
                    elif colHeader == 11:
                        col_width = 20
                    else:
                        col_width = 14

                    # if self.set_fill_color(47, 216, 230)
                    self.cell(col_width, row_height, table1Header[colHeader], border=1, fill=True)

                self.ln(row_height)
                thisHeight = start_Y + (0) * row_height
                self.set_xy(start_X, thisHeight)


            for column in range(table1.columnCount()):

                if ((column != 2) and (column != 3)):
                    if column == 4:
                        self.set_font('Times', '', 8.0)
                    else:
                        self.set_font('Times', '', 10.0)
                    cnt_col += 1
                    Real_cnt_col = cnt_col
                    self.set_fill_color(173, 216, 230)

                    if cnt_row % 2 == 1:
                        self.set_fill_color(173, 216, 230)
                    else:
                        self.set_fill_color(255, 255, 255)
                    # table1.item(row, column).text()
                    # Alarm Check
                    if (alarmCode == 9 and column == 9) or (alarmCode == 10 and column == 10) or (alarmCode == 11 and column == 11) or (alarmCode == 12 and column == 12) or (alarmCode == 13 and column == 13) or (alarmCode == 14 and column == 14):
                        self.set_fill_color(255, 105, 97)

                    # print("R1", table1.item(row, 0).text(),table1.item(row, 4).text())
                    # print("W1", alarmCode2[0],alarmCode2[1],alarmCode2[2],alarmCode2[3],alarmCode2[4],alarmCode2[5])
                    if (alarmCode2[0] == '1' and column == 9) or (alarmCode2[1] == '1' and column == 10) or (alarmCode2[2] == '1' and column == 11) or (alarmCode2[3] == '1' and column == 12) or (alarmCode2[4] == '1' and column == 13) or (alarmCode2[5] == '1' and column == 14):
                        self.set_fill_color(255, 105, 97)
                        # print("R2", table1.item(row, 0).text(), table1.item(row, 4).text())
                        # print("W2", alarmCode2[0], alarmCode2[1], alarmCode2[2], alarmCode2[3], alarmCode2[4],alarmCode2[5])

                    col_width = 14
                    if column == 0 or column == 7:
                        col_width = 12
                    elif column == 9 or column == 10 or column == 11:
                        col_width = 12
                    elif column == 8 or column == 12:
                        col_width = 16
                    elif column == 13:
                        col_width = 20
                    else:
                        col_width = 14

                    self.cell(col_width, row_height, table1.item(row,column).text(), border=1, fill=True)

            self.ln(row_height)

            # Next Line
            thisHeight = start_Y + (cnt_row) * row_height
            if thisHeight >= EndPage:
                self.add_page()
                self.border4()
                self.imagex()
                self.titles()
                start_Y = 55
                cnt_row = -1
                thisHeight = start_Y + (cnt_row) * row_height
                self.set_text_color(0, 0, 20)
                self.set_xy(start_X, thisHeight)
                # for column in range(table1.columnCount()):
                for colHeader in range(len(table1Header)):
                    # if ((column != 2) and (column != 3)):
                    self.set_fill_color(47, 216, 230)
                    col_width = 14
                    if colHeader == 0 or colHeader == 5:
                        col_width = 12
                    elif colHeader == 7 or colHeader == 8 or colHeader == 9:
                        col_width = 12
                    elif colHeader == 6 or colHeader == 10:
                        col_width = 16
                    elif colHeader == 11:
                        col_width = 20
                    else:
                        col_width = 14
                    self.cell(col_width, row_height, table1Header[colHeader], border=1, fill=True)
                    # self.cell(col_width, row_height, table1.item(0, column).text(), border=1)
                self.ln(row_height)
                cnt_row += 1
                thisHeight = start_Y + (cnt_row) * row_height
            self.set_xy(start_X, thisHeight)

    # Common Table Every Page
    def tableIntro(self,de):
        self.set_xy(75, 40)
        self.set_font('Times', '', 12.0)
        self.set_text_color(0, 0, 20)
        self.cell(50, 10, 'Inspection Information', align='C')
        self.set_font('Times', '', 10.0)
        self.ln(0.5)

        row_height = 10
        col_width1 = 60
        col_width2 = 30
        start_X = 15
        start_Y = 50
        cnt_row = 0
        cnt_col = 1

        self.set_xy(start_X, start_Y)
        self.set_fill_color(20, 200, 50)
        # for row in df[:,0:2]:
        for row in de:
            cnt_row += 1
            cnt_col = 0
            for datum in row:
                cnt_col += 1
                if cnt_col % 2 == 1:
                    col_width = col_width1
                elif cnt_col % 2 == 0:
                    col_width = col_width2

                self.cell(col_width, row_height, str(datum), border=1)

            self.ln(row_height)
            thisHeight = start_Y + (cnt_row) * row_height
            # print(cnt)
            self.set_xy(start_X, thisHeight)

    def tableAlarm(self, i,SensorData,title):
        self.set_xy(75, 100)
        self.set_font('Times', '', 16.0)
        self.set_text_color(255, 105, 0)
        self.cell(50, 50, title, align='C')
        self.set_font('Times', '', 10.0)
        self.set_text_color(0, 0, 0)
        self.ln(0.5)

        row_height = 10
        col_width = 20
        start_X = 15
        start_Y = 255
        cnt_row = 0
        cnt_col = 1

        self.set_xy(start_X, start_Y)
        self.set_fill_color(20, 200, 50)

        self.cell(col_width, row_height, str("ID"), border=1)
        self.cell(col_width, row_height, str("Time"), border=1)
        self.cell(col_width, row_height, str("Position"), border=1)
        self.cell(col_width, row_height, str("O2"), border=1)
        self.cell(col_width, row_height, str("CO2"), border=1)
        self.cell(col_width, row_height, str("CH4"), border=1)
        self.cell(col_width, row_height, str("Humidity"), border=1)
        self.cell(col_width, row_height, str("Temperature"), border=1)
        self.cell(col_width, row_height, str("Battery"), border=1)
        self.ln(row_height)
        thisHeight = start_Y + (1) * row_height
        self.set_xy(start_X, thisHeight)
        self.cell(col_width, row_height, str(SensorData[i][0]), border=1)
        self.cell(col_width, row_height, str(SensorData[i][8]), border=1)
        self.cell(col_width, row_height, str(SensorData[i][5]), border=1)
#         print("PAL",SensorData[i][4])
#         print("PAL2", SensorData[i][4][1])
#         print("PAL3",SensorData[i][4][1] == '1',type(SensorData[i][4][1]))
        if SensorData[i][4][0] == '1':
#             print("PA0", SensorData[i][4][0] == '1', type(SensorData[i][4][0]))
            self.set_fill_color(255, 105, 97)
        else:
            self.set_fill_color(255, 255, 255)
        self.cell(col_width, row_height, str(SensorData[i][9]), border=1,fill=True)  # Sensor Data
        if SensorData[i][4][1] == '1':
#             print("PA1", SensorData[i][4][1] == '1', type(SensorData[i][4][1]))
            self.set_fill_color(255, 105, 97)
        else:
            self.set_fill_color(255, 255, 255)
        self.cell(col_width, row_height, str(SensorData[i][10]), border=1,fill=True)  # Sensor Data
        if SensorData[i][4][2] == '1':
#             print("PA2", SensorData[i][4][2] == '1', type(SensorData[i][4][2]))
            self.set_fill_color(255, 105, 97)
        else:
            self.set_fill_color(255, 255, 255)
        self.cell(col_width, row_height, str(SensorData[i][11]), border=1,fill=True)  # Sensor Data
        if SensorData[i][4][3] == '1':
#             print("PA3", SensorData[i][4][3] == '1', type(SensorData[i][4][3]))
            self.set_fill_color(255, 105, 97)
        else:
            self.set_fill_color(255, 255, 255)
        self.cell(col_width, row_height, str(SensorData[i][12]), border=1,fill=True)  # Sensor Data
        if SensorData[i][4][4] == '1':
#             print("PA4", SensorData[i][4][4] == '1', type(SensorData[i][4][4]))
            self.set_fill_color(255, 105, 97)
        else:
            self.set_fill_color(255, 255, 255)
        self.cell(col_width, row_height, str(SensorData[i][13]), border=1,fill=True)  # Sensor Data
        if SensorData[i][4][5] == '1':
#             print("PA5", SensorData[i][4][5] == '1', type(SensorData[i][4][5]))
            self.set_fill_color(255, 105, 97)
        else:
            self.set_fill_color(255, 255, 255)
        self.cell(col_width, row_height, str(SensorData[i][14]), border=1,fill=True)  # Sensor Data

    def pageOne(self,de,table1,table1Header):
        self.add_page()
        self.border4()
        self.imagex()
        self.titles()
        self.tableIntro(de)
        self.tables1(table1,table1Header)

    def pageChart(self,de,chartName,OperatorName,ProjectName):
        for i in range(6):
            self.add_page()
            self.border4()
            self.imagex()
            self.titles()
            self.tableIntro(de)
            self.charts(chartName[i],OperatorName,ProjectName)

    def pageAlarm(self,SensorData,de,count_Alarm,OperatorName,ProjectName):
        self.upFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        # numAlarm = SensorData.shape[0] - 1
        numAlarm = count_Alarm
        for i in range(numAlarm):
            self.add_page()
            self.border4()
            self.imagex()
            self.titles()
            self.tableIntro(de)
            self.ID = str(SensorData[i][0])
            
            if self.ID[0]=='2':
                if (SensorData[i][4][0] == '1') or (SensorData[i][4][1] == '1') or (SensorData[i][4][2] == '1') or (SensorData[i][4][3] == '1') or (SensorData[i][4][4] == '1') or (SensorData[i][4][5] == '1'):
                    self.set_xy(15.0, 130.0)
                    self.image(self.upFolder + '/Users/' + OperatorName + '/' + ProjectName + '/Pictures/Alarm/' + str(SensorData[i][0]) + '.jpg', link='', type='', w=180,h=120)
                    self.tableAlarm(i,SensorData,'Alarm')
                    
                if (SensorData[i][4] == '222222'):
                    self.set_xy(15.0, 130.0)
                    self.image(self.upFolder + '/Users/' + OperatorName + '/' + ProjectName + '/Pictures/Motion/' + str(SensorData[i][0]) + '.jpg', link='', type='', w=180,h=120)
                    self.tableAlarm(i,SensorData,'Motion')
                    
                if (SensorData[i][4] == '333333'):
                    self.set_xy(15.0, 130.0)
                    self.image(self.upFolder + '/Users/' + OperatorName + '/' + ProjectName + '/Pictures/Face/' + str(SensorData[i][0]) + '.jpg', link='', type='', w=180,h=120)
                    self.tableAlarm(i,SensorData,'Face')
                    
            elif self.ID[0]=='1':
                if (SensorData[i][1] == 110) or (SensorData[i][1] == 111):
                    self.set_xy(15.0, 130.0)
                    self.image(self.upFolder + '/Users/' + OperatorName + '/' + ProjectName + '/Pictures/AutoPictures/' + str(SensorData[i][0]) + '.jpg', link='', type='', w=180,h=120)
                    self.tableAlarm(i,SensorData,'Auto')
                
            elif self.ID[0]=='3':
                if (SensorData[i][4] == '444444'):
                    self.set_xy(15.0, 130.0)
                    self.image(self.upFolder + '/Users/' + OperatorName + '/' + ProjectName + '/Pictures/Operator/Normal_Camera/' + str(SensorData[i][0]) + '.jpg', link='', type='', w=180,h=120)
                    self.tableAlarm(i,SensorData,'Operator')
