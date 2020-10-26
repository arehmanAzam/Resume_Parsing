import docx2txt
from resume_parser import resumeparse
import os


def extract_text_from_pdf(pdf_path):
    try:
        return resumeparse.convert_pdf_to_txt(pdf_path)
    except Exception as e:
        print("Error in extract_text_from_pdf function, Exception: %s"%e)
def extract_text_from_doc(doc_path):
    try:
        return resumeparse.convert_docx_to_txt(doc_path)
    except Exception as e:
        print("Error in extract_text_from_doc function, Exception: %s" % e)
def extract_segments(text_string):
    try:
        result=resumeparse.segment(text_string)
        return result
    except Exception as e:
        print("Error in extract_segments function, Exception: %s" % e)

def load_doc(path):
    try:
        assert path is not str
        assert os.path.exists(path)
        raw_text=''
        assert ('.pdf' in path) or ('.docx' in path) or ('.doc' in path )

        if ('.pdf' in path):
            text,raw_text=extract_text_from_pdf(path)
        elif ('.docx' in path or '.doc' in path):
            text,raw_text= extract_text_from_doc(path)
        # print(text)
        # with open('file_text.txt','w+') as file_out:
        #     file_out.write(text)
        segments_text=extract_segments(text)
        return segments_text,raw_text,text
    except Exception as e:
        print("Error in load_doc function, Exception: %s" % e)



if __name__ == '__main__':
    load_doc('/home/abdulrehman/PycharmProjects/CV_parsing/data/CV_Samples/CV_Samples/Work_Samples/David Curd before.doc')