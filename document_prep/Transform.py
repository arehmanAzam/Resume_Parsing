from docx import Document
from docx.shared import Inches
from extract_fields.Extraction import Extraction
import glob

class Transform:
    def __init__(self):
        pass

    def doc_prep(self):
        f = open('/home/abdulrehman/PycharmProjects/CV_parsing/data/CV_Samples/CV_Samples/Work_Samples/Ciaran After.docx', 'rb')
        self.doc = Document(f)
        self.doc.add_heading('Document Title', 0)

if __name__ == '__main__':
    # for resume in glob.glob('/home/abdulrehman/PycharmProjects/CV_parsing/data/CV_Samples/CV_Samples/Sample_Folder_2/*before*'):
    #     print(resume)
    #     ex_obj=Extraction(resume)
    #     objective=ex_obj.objective_statement()
    #     experience=ex_obj.experience()
    #     education = ex_obj.education()
    #     skills=ex_obj.skills()
    #     summary=ex_obj.overall_resume
    #     print('\n \n')

    ins_transform=Transform()
    ins_transform.doc_prep()