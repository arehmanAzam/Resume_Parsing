from resume_parser import resumeparse
import nltk
import glob
from LoadDocument import load_doc
import json
import os
import re
from datetime import date
import spacy
from spacy.lang.en import English
from spacy import displacy
from find_job_titles import Finder

class Extraction:

    def __init__(self,resume_path):
        self.segmented_text={}
        self.raw_text=''
        self.lines=[]
        self.resume_load(resume_path)
        self.overall_resume=self.summary(resume_path)
        self.nlp = spacy.load('en_core_web_sm')
        self.job_finder=Finder()
    def experience_years(self,resume_text):
        try:

            list_years=[]
            def correct_year(result):
                if len(result) < 2:
                    if int(result) > int(str(date.today().year)[-2:]):
                        result = str(int(str(date.today().year)[:-2]) - 1) + result
                    else:
                        result = str(date.today().year)[:-2] + result
                return result

            # try:
            experience = 0
            start_month = -1
            start_year = -1
            end_month = -1
            end_year = -1

            not_alpha_numeric = r'[^a-zA-Z\d]'
            number = r'(\d{2})'

            months_num = r'(01)|(02)|(03)|(04)|(05)|(06)|(07)|(08)|(09)|(10)|(11)|(12)'
            months_short = r'(jan)|(feb)|(mar)|(apr)|(may)|(jun)|(jul)|(aug)|(sep)|(oct)|(nov)|(dec)'
            months_long = r'(january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december)'
            month = r'(' + months_num + r'|' + months_short + r'|' + months_long + r')'
            regex_year = r'((20|19)(\d{2})|(\d{2}))'
            year = regex_year
            start_date = month + not_alpha_numeric + r"?" + year

            end_date = r'((' + number + r'?' + not_alpha_numeric + r"?" + month + not_alpha_numeric + r"?" + year + r')|(present|current))'
            longer_year = r"((20|19)(\d{2}))"
            year_range = longer_year + r"(" + not_alpha_numeric + r"{1,4}|(\s*to\s*))" + r'(' + longer_year + r'|(present|current))'
            date_range = r"(" + start_date + r"(" + not_alpha_numeric + r"{1,4}|(\s*to\s*))" + end_date + r")|(" + year_range + r")"

            regular_expression = re.compile(date_range, re.IGNORECASE)

            regex_result = re.search(regular_expression, resume_text)

            while regex_result:

                date_range = regex_result.group()
                try:
                    year_range_find = re.compile(year_range, re.IGNORECASE)
                    year_range_find = re.search(year_range_find, date_range)
                    replace = re.compile(r"(" + not_alpha_numeric + r"{1,4}|(\s*to\s*))", re.IGNORECASE)
                    replace = re.search(replace, year_range_find.group().strip())

                    start_year_result, end_year_result = year_range_find.group().strip().split(replace.group())
                    start_year_result = int(correct_year(start_year_result))
                    if end_year_result.lower().find('present') != -1 or end_year_result.lower().find('current') != -1:
                        end_month = date.today().month  # current month
                        end_year_result = date.today().year  # current year
                    else:
                        end_year_result = int(correct_year(end_year_result))


                except:

                    start_date_find = re.compile(start_date, re.IGNORECASE)
                    start_date_find = re.search(start_date_find, date_range)

                    non_alpha = re.compile(not_alpha_numeric, re.IGNORECASE)
                    non_alpha_find = re.search(non_alpha, start_date_find.group().strip())

                    replace = re.compile(start_date + r"(" + not_alpha_numeric + r"{1,4}|(\s*to\s*))", re.IGNORECASE)
                    replace = re.search(replace, date_range)
                    date_range = date_range[replace.end():]

                    start_year_result = start_date_find.group().strip().split(non_alpha_find.group())[-1]

                    # if len(start_year_result)<2:
                    #   if int(start_year_result) > int(str(date.today().year)[-2:]):
                    #     start_year_result = str(int(str(date.today().year)[:-2]) - 1 )+start_year_result
                    #   else:
                    #     start_year_result = str(date.today().year)[:-2]+start_year_result
                    # start_year_result = int(start_year_result)
                    start_year_result = int(correct_year(start_year_result))

                    if date_range.lower().find('present') != -1 or date_range.lower().find('current') != -1:
                        end_month = date.today().month  # current month
                        end_year_result = date.today().year  # current year
                    else:
                        end_date_find = re.compile(end_date, re.IGNORECASE)
                        end_date_find = re.search(end_date_find, date_range)

                        end_year_result = end_date_find.group().strip().split(non_alpha_find.group())[-1]

                        # if len(end_year_result)<2:
                        #   if int(end_year_result) > int(str(date.today().year)[-2:]):
                        #     end_year_result = str(int(str(date.today().year)[:-2]) - 1 )+end_year_result
                        #   else:
                        #     end_year_result = str(date.today().year)[:-2]+end_year_result
                        # end_year_result = int(end_year_result)
                        end_year_result = int(correct_year(end_year_result))

                if (start_year == -1) or (start_year_result <= start_year):
                    start_year = start_year_result
                if (end_year == -1) or (end_year_result >= end_year):
                    end_year = end_year_result
                list_years.append(resume_text[regex_result.span(0)[0]:regex_result.span(0)[1]])
                resume_text = resume_text[regex_result.end():].strip()
                regex_result = re.search(regular_expression, resume_text)
            return list_years
        except Exception as e:
            print("Error in Extraction.experience_years function, Exception: %s" % e)

    def resume_load(self,path):
        try:
            self.segmented_text, self.raw_text, self.lines = load_doc(path)
        except Exception as e:
            print("Error in Extraction.resume_load function, Exception: %s" % e)
    def match_with_summary(self,string):
        try:
            if self.overall_resume !=None:
                values_sum=[*self.overall_resume.values()]
                for value in values_sum:
                    if type(value) == str and value!='':
                        if string in value or value in string:
                            return True
                return False
        except Exception as e:
            print("Error in Extraction.match_with_summary function, Exception: %s" % e)
            return False
    def objective_statement(self):
        try:
            objective_heading = ''
            objective_summary = ''
            if self.segmented_text is not {} and self.segmented_text['objective']!={}:
                objective=self.segmented_text['objective']
                objective_key=[*objective.keys()][0]
                objective_value = [*objective.values()][0]
                if objective_key in objective_value[0].lower():
                    objective_heading=objective_value[0]
                else:
                    objective_heading=objective_key
                objective_summary=' '.join(objective_value[1:])
                print(objective_heading)
                print(objective_summary)
            elif self.segmented_text['contact_info']!={}:
                contact_info = self.segmented_text['contact_info']
                print(contact_info)
                if len(contact_info)>1:
                    counter_index=0
                    for contact_value in contact_info:
                        if self.overall_resume!=None and self.match_with_summary(contact_value):
                            pass
                        elif len(contact_value)>50 and len(contact_value.split())>10:
                            objective_summary+=" "+ contact_value
                    print(objective_summary)
                # if len(contact_info)>4:
                #     for string in contact_info:
                #         if overall
        except Exception as e:
            print("Error in Extraction.objective_statement function, Exception: %s" % e)

    def skills(self):
        try:
            print(self.segmented_text['skills'])
        except Exception as e:
            print("Error in Extraction.skills function, Exception: %s" % e)
    def entity_recognition(self,text):
        try:
            entity=self.nlp(text)
            entities = [(i, i.label_, i.label) for i in entity.ents]
            return entities
        except Exception as e:
            print("Error in Extraction.entity_recognition function, Exception: %s" % e)
    def experience(self):
        try:
            experience_section=''
            employ_chunks=[]
            print(self.segmented_text['work_and_employment'])
            if self.segmented_text['work_and_employment'] != {}:
                employ_chunks=[*self.segmented_text['work_and_employment'].values()][0]
                experience_section=' '.join(employ_chunks)
            if experience_section !=None or experience_section !='':
                service_tenures=self.experience_years(experience_section)
                if len(service_tenures)>0:
                    for tenure in service_tenures:
                        match = [chunk for chunk in employ_chunks if tenure in chunk]
                        job=self.job_finder.findall(" ".join(match))
                        print(job)
                        entities=self.entity_recognition(" ".join(match))

        except Exception as e:
            print("Error in Extraction.experience function, Exception: %s" % e)
    def education(self):
        try:
            print(self.segmented_text['education_and_training'])
        except Exception as e:
            print("Error in Extraction.education function, Exception: %s" % e)
    def accomplishments(self):
        try:
            print(self.segmented_text['accomplishments'])
        except Exception as e:
            print("Error in Extraction.accomplishments function, Exception: %s" % e)

    def summary(self,path):
        try:
            return resumeparse.read_file(path)
        except Exception as e:
            print('Exception occured in Extraction.summary')
if __name__ == '__main__':
    # nltk.download('stopwords')
    # obj1='/home/abdulrehman/PycharmProjects/CV_parsing/data/CV_Samples/CV_Samples/Work_Samples/Ines Before.docx'
    # obj2='/home/abdulrehman/PycharmProjects/CV_parsing/data/CV_Samples/CV_Samples/Work_Samples/Innocent Before.docx'
    # obj3='/home/abdulrehman/PycharmProjects/CV_parsing/data/CV_Samples/CV_Samples/Work_Samples/Loira Before.pdf'
    #
    # obj4='/home/abdulrehman/PycharmProjects/CV_parsing/data/CV_Samples/CV_Samples/Work_Samples/Osita Before.docx'
    # obj5='/home/abdulrehman/PycharmProjects/CV_parsing/data/CV_Samples/CV_Samples/Work_Samples/Jason Before.pdf'
    # obj6='/home/abdulrehman/PycharmProjects/CV_parsing/data/CV_Samples/CV_Samples/Sample_Folder_2/John before.docx.docx'
    # for resume in glob.glob('/home/abdulrehman/PycharmProjects/CV_parsing/data/CV_Samples/CV_Samples/Sample_Folder_2/*before.*'):
    #     print(resume)
    #     ex_obj=Extraction(resume)
    #     # ex_obj.objective_statement()
    #     ex_obj.experience()
        # ex_obj.education()
     for resume in glob.glob('../data/CV_Samples/CV_Samples/Work_Samples/*before.*'):
        # data1= ResumeParser(resume).get_extracted_data()
        # data3= resumeparse.convert_pdf_to_txt(resume)
        print(resume)
        segmented_text,raw_text,lines=load_doc(resume)
        # print(data1)
        file_name=os.path.basename(resume)
        y = json.dumps(segmented_text)
        with open('../data/CV_Samples/CV_Samples/resume_json/'+file_name+'.json','w+') as json_file:
            json_file.write(y)
        print(segmented_text['contact_info'])
    #     print('\n \n')