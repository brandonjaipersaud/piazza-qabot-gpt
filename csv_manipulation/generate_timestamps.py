import argparse
from io import TextIOWrapper
from utils.utils import is_empty
import pandas as pd

import piazza_api_utils.utils as piazza_utils

import json



def add_human_timestamp(row, course:piazza_utils.Network):
    """Add student/instructor timestamps. Ignore columns that already have timestamps."""
    post_id = row['question_id']
    
    post = piazza_utils.get_question_post(course, post_id, print_info=True)
    answer_timestamps = piazza_utils.get_timestamp(post, course)
 

    if answer_timestamps['i_timestamp'] and not is_empty(row['instructor_answer']) and is_empty(row['instructor_answer_timestamp']):
        row['instructor_answer_timestamp'] = answer_timestamps['i_timestamp']
        

    if answer_timestamps['s_timestamp'] and not is_empty(row['student_answer']) and is_empty(row['student_answer_timestamp']):
        row['student_answer_timestamp'] = answer_timestamps['s_timestamp']


    return row



def add_model_answer_timestamp(row, f:TextIOWrapper):
    question_id = row['question_id']
    if not is_empty(row['model_answer']):
        line = f.readline()
        while line:
            if f'Answering question {question_id}'.lower() in line.lower():
                # seek to line where followup is created
                while line:
                    if 'method=content.create' in line.lower():
                        datetime = line.split(',')[0][1:]
                        row['model_answer_timestamp'] = datetime
                        f.seek(0, 0)
                        return row

                    line = f.readline()
                    
                        
            line = f.readline()
        
        # failed to find line in file
        row['model_answer_timestamp'] = 'N/A'

    f.seek(0, 0)
    return row

    


def add_timestamps(course:piazza_utils.Network, df:pd.DataFrame, course_log_path=None, force=False, model_answer_timestamps=True, human_answer_timestamps=True):
    """Add timestamps to questions in the df. Useful for determining whether TA considered bot answer before leaving their own answer."""
  
    if model_answer_timestamps:
        if 'model_answer_timestamp' in df.columns and not force:
            print(f"Model Timestamp column already added and force={force}. Skipping model timestamps.")
        else:
            if 'model_answer_timestamp' not in df.columns:
                df['model_answer_timestamp'] = ""

            if force:
                print("WARNING: Overwriting model timestamp columns in df")

            if course_log_path:
                print(f"Adding model timestamps based on course log path: {course_log_path}")
                
                with open(course_log_path, 'r') as f:
                    df = df.apply(lambda row: add_model_answer_timestamp(row, f), axis=1)
            
            else:
                print('Please provide a course log path so can find timestamps')
       

    if human_answer_timestamps:
        if 'human_answer_timestamp' in df.columns and not force:
            print(f"Human Timestamp column already added and force={force}. Skipping human timestamps.")
        
        else:

            if 'instructor_answer_timestamp' not in df.columns:
                df['instructor_answer_timestamp'] = ""
                df['student_answer_timestamp'] = ""
        
            if force:
                print("WARNING: Overwriting human timestamp columns in df")

            df = df.apply(lambda row: add_human_timestamp(row, course), axis=1)
    
    return df



def check_columns(df, args):

    missing_columns = []
    if 'question_id' not in df.columns:
        missing_columns.append('question_id')

    if args.model_answer and "model_answer" not in df.columns:
        print('Model_answer timestamps set and model answer not in df!')
        missing_columns.append('model_answer')

        
    if args.human_answer and "instructor_answer" not in df.columns:
        print('Human_answer timestamps set and instructor answer not in df!')
       
    
    if len(missing_columns) > 0:
        print(f'Missing columns {missing_columns}')
        return False
    
    return True



def parse_args(args, df):
    if check_columns(df, args):
        if not args.piazza_creds_file:
            print('Missing piazza creds file!')
            return df
        user_profile, course = piazza_utils.login(args.piazza_creds_file)
        df = add_timestamps(course, df, course_log_path=args.course_log_path, model_answer_timestamps=args.model_answer, human_answer_timestamps=args.human_answer)
    return df
    




