from typing import List
from datetime import datetime 
import re
from copy import deepcopy

import pandas as pd 
import seaborn as sns

from piazza_api_utils.utils import MyHTMLParser, strip_tags
from utils.parse_answers import *
from custom_exceptions.my_exceptions import *



def add_column(column_name:str, df:pd.DataFrame, force:bool=True):
    should_process = False
    if column_name in df.columns and not force:
        print(f"{column_name} column already added and force={force}. Skipping.")
    else:
        should_process = True
        if column_name not in df.columns:
            df[column_name] = ""

        if force:
            print(f"WARNING: Overwriting {column_name} columns in df")
    
    return (df, should_process)


def check_columns(required_columns:list, df:pd.DataFrame) -> list:
    missing_columns = []
    for r in required_columns:
        if r not in df.columns:
            missing_columns.append(r) 

    if len(missing_columns) > 0:
        raise MissingColumnsError(missing_columns)
        
    return True



def get_folders(data: pd.DataFrame, folder_colname: str ='folders') -> List[str]:
    """ Return folders associated with the posts in `data`
    """
    folders = data[folder_colname].unique()
    return folders


def folder_distribution(data: pd.DataFrame, folder_colname: str ='folders'):
    
    get_folders(data)
    sns.displot(data=data, x=folder_colname, height=20)



def merge_title_and_content(title, content):
    if is_empty(title):
        title = ""
    
    if is_empty(content):
        content = ""
    return title + '. ' + content

def filter_row(row):
    return row


# @|<img|<pre|\.png|def
def filter_csv(data: pd.DataFrame, filter_string:str='<img|@|<pre|\.png|def', contains=True, should_strip_tags=True, return_cols=None):
    """Return data with filtered criteria. Maybe strip tags. """


    filtered_data = data.fillna("", inplace=False)
    if contains:
        filtered_data = filtered_data[filtered_data['question'].str.contains(filter_string, flags=re.IGNORECASE, regex=True)]
    else:
        filtered_data = filtered_data[~filtered_data['question'].str.contains(filter_string, flags=re.IGNORECASE, regex=True)]



    if should_strip_tags:
        filtered_data["question"] = filtered_data["question"].apply(strip_tags)
        filtered_data["student_answer"] = filtered_data["student_answer"].apply(strip_tags)
        filtered_data["instructor_answer"] = filtered_data["instructor_answer"].apply(strip_tags)

    
    if return_cols:
        filtered_data = filtered_data[return_cols]

    return filtered_data



def split_answers_csv(df:pd.DataFrame):

    check_columns(['answer(s)'], df)

    new_df = []

    augment_feedback = False

    if 'feedback' in df.columns:
        augment_feedback = True

    for index, row in df.iterrows():
        if not is_empty(row['answer(s)']):
            answers = get_answers(row['answer(s)'])
            new_row = deepcopy(row)
            row["model_answer"] = answers[0]
            new_row["model_answer"] = answers[1]

            if augment_feedback:
                if not is_empty(row['feedback']):
                    feedback = row['feedback'].split(',')
                    row["feedback"] = feedback[0]
                    new_row["feedback"] = feedback[1]

            new_df.append(row)
            new_df.append(new_row)
        else:
            new_df.append(row)

    new_df = pd.DataFrame(new_df)
    return new_df


def compare_timestamps(row):
    """ i vs m
    2023-02-09T19:33:43Z   
    2023-02-09 13:35:10
    """
    instructor_timestamp = row['instructor_answer_timestamp']
    model_timestamp = row['model_answer_timestamp']

    if not is_empty(instructor_timestamp) and not is_empty(model_timestamp):

        dt1 = datetime.fromisoformat(instructor_timestamp.replace('Z', ''))
        dt2 = datetime.fromisoformat(model_timestamp)

        if dt1 > dt2:
            row['instructor > model'] = True 
        else:
            row['instructor > model'] = False

    return row

def compare_timestamps_csv(df:pd.DataFrame, required_columns=['model_answer_timestamp', 'instructor_answer_timestamp']):
    

    if not check_columns(required_columns, df):
        return df
  
    df = df.apply(lambda row: compare_timestamps(row), axis=1)
    return df



def augment_with_columns(df1:pd.DataFrame, df2:pd.DataFrame, augment_columns:List[str], merge_columns=['question_id']):
    """Add columns in df2 to df1"""

    # print(augment_columns)
   
    # if not check_columns(augment_columns, df2):
    #     raise MissingColumnsError(augment_columns, msg='df2')
        
    # overwrite with force argument?
    # df1 supposed to be missing augment columns. Otherwise overwrite.
    # if check_columns(augment_columns, df1): 
    #     raise ColumnExistsError(augment_columns, msg='df1')

    # if not check_columns(merge_columns, df1) or not check_columns(merge_columns, df2):
    #     raise MissingColumnsError(merge_columns, msg='df1 or df2')

    
    merged_df = df1.merge(df2, how='left')
    return merged_df


def select_columns_df(df, columns):
    if not check_columns(columns, df):
        raise MissingColumnsError(columns, msg="df")

    print(f'Selecting columns: {columns}')
    return df[columns]




def merge_title_and_content_row(row):
    title = row['question_title']
    content = row['question']
    
    row['question'] = merge_title_and_content(title, content)
    return row

def merge_title_and_content_csv(df:pd.DataFrame):
    if not check_columns(['question_title', 'question'], df):
        raise MissingColumnsError(['question_title', 'question'])
    
    df = df.apply(lambda row: merge_title_and_content_row(row), axis=1)
    return df

def main():

    csv = pd.read_csv("data/csc311_all_raw_unfiltered.csv")
    print(csv)




if __name__ == "__main__":
    main()