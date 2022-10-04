from fpdf import FPDF
import os
class PDF(FPDF):
    def __init__(self, storage_directory, report_name, reasoning, numbers):
        super().__init__()
        self.WIDTH = 210
        self.HEIGHT = 297
        self.margin = 10
        self.storageDirectory=storage_directory
        self.reportName=report_name
        self.reasoning=reasoning
        self.numbers=numbers
    
    #customise pdf
        
    def page_body(self):
        #Print report title
        self.set_font('Helvetica','B', 28)
        #report name centered in the middle w/o borders
        self.cell(w=0, h=10, txt=self.reportName, border=0, align='C', ln=1)
        #Second, we display the main plot, followed by plots that cannot be legend
        self.image('Interfaces/fig1.png',w=180)
        
        self.ln(self.font_size * 2.5)
        #Then, we display the reasoning
        self.set_text_color(0,0,0)
        self.set_font('Helvetica',style='',size=14) 
        line_height = self.font_size * 2.5
        
        col_width=(self.WIDTH-self.margin*2)/2
        for row in self.numbers:
            for item in row:
                self.cell(col_width, line_height, item, border=1, ln=3, align='L')
            self.ln(line_height)
        
        #Line break
        self.ln(line_height)
        
        for row in self.reasoning:
            
            self.set_font(style="B")
            self.cell(txt=row[0], align='L',ln=1)
            self.set_font(style="")
            
            self.multi_cell(txt=row[1],w=self.epw,ln=1)
            
            self.multi_cell(txt=row[2],w=self.epw,ln=1)
            self.ln(line_height)
            self.ln(line_height)
            

    def print_page(self):
        self.add_page()
        self.page_body()