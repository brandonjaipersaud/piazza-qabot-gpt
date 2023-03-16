import argparse
from argparse import Namespace, ArgumentParser
import json
import time
import math
from datetime import datetime
import os
from tqdm import trange, tqdm
import re
from copy import deepcopy
import sys

from piazza_api_utils.utils import *

sys.path.append('./piazza_api/')
sys.path.append('../')

import csv

from nptyping import NDArray, Int, Shape
from typing import Dict, List, Tuple, Union


from piazza_api import Piazza
from piazza_api.network import Network

from utils import *


    
def parse_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('creds_file', type=str, help="path to credentials file", default='creds.json')
    # only 1 of -s and -c should be set? setting both might be fine
    parser.add_argument('-s','--scrape-posts', action='store_true', help="scrape piazza posts and save to json file")
    parser.add_argument('-ni','--num-iters', type=int, help="how many posts to scrape. Omit to scrape all posts.", default=-1)
    parser.add_argument('-t','--throttle', type=float, help="rate to fetch posts from piazza due to throttle", default=2.5)
   
    parser.add_argument('-c','--json-to-csv', action='store_true', help="convert json file of piazza posts into a csv file")

    parser.add_argument('-js', '--json-save-path', type=str, help="if scrape-posts is enabled, this option should be set")
    parser.add_argument('-jl', '--json-load-path', type=str, help="if json-to-csv is enabled, this option should be set")
    parser.add_argument('-cp', '--csv-save-path', type=str, help="if json-to-csv is enabled, this option should be set")

    parser.add_argument('-st', '--should_strip_tags', help='', action='store_true')
    parser.add_argument('-f', '--should_filter', help='', action='store_true')



    args = parser.parse_args()
    return args, parser
    


def export_posts_json(path:str, course:Network, max_iters='all', throttle=2.5) -> None:
    """
    Scrape Piazza posts and save to json file

    :param path: Path to save json file. When saving to current directory, prefix with ./
    :param max_iters: How many posts to save due to PiazzaAPI throttling
    """

    print(f'Path is {path}')
    print(f"Max_iters {max_iters}, throttle = {throttle}")

    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

    posts = course.iter_all_posts()
    all_posts = []
    #text = json.dumps(post['children'][1], sort_keys=True, indent=4)
    try:
        iters = 0
        # fetches a post from Piazza
        for p in tqdm(posts):
            time.sleep(throttle)
            all_posts.append(p)
            iters += 1
            if iters == max_iters and max_iters != 'all':
                break
    finally:
        print(f'Saving to {path}')
        with open(path, 'w') as f:
            json.dump(all_posts, f)


def json_to_csv_student(json_file_path: str, csv_filename: str, course: Network, is_overwrite_csv: bool=False, is_old=False, should_strip_tags=False):
    """ Use for accessing the api as a non-instructor. Converts json of piazza posts into a csv with html entities potentially removed.

    """

    print("Permissions = Student")


    schema = ("post_id,question_title,question,folders,student_answer,instructor_answer\n")
    parser = MyHTMLParser()

    with open(json_file_path, 'r') as json_file:
        with open(csv_filename, 'w') as csv_file:
            csv_file.write(schema)
            posts = json.load(json_file)
            num_posts = 0
            for post in tqdm(posts):   
                row = [] 
                if post['type'] == 'question':
                    question = post['history'][0] # newest update of question. Change index to -1 for oldest
                    # question_title = strip_tags(question['subject'])
                    # question_content = strip_tags(question['content'])
                    question_title = question['subject']
                    question_content = question['content']

                    # do img tag filtering here?
                    if re.search('@|<img|<pre|\.png|def', question_title + question_content):
                        continue
                    
                    folders = ','.join(post['folders'])
                
                    answers = get_answers_simple(post)
                    student_answer = answers['s_answer']
                    if student_answer:
                        student_answer = student_answer['text']
                    else:
                        student_answer = 'N/A'

                    instructor_answer = answers['i_answer']
                    if instructor_answer:
                        instructor_answer = instructor_answer['text']
                    else:
                        instructor_answer = 'N/A'

                    if should_strip_tags:
                        question_title, question_content, student_answer, instructor_answer = strip_tags(question_title), strip_tags(question_content), strip_tags(student_answer), strip_tags(instructor_answer)

                    row = [post['nr'], question_title, question_content, folders, student_answer, instructor_answer]


                    post_writer = csv.writer(csv_file)
                    post_writer.writerow(row)
                    
                    csv_file.write('\n')

                    num_posts += 1


def json_to_csv_instructor(json_file_path: str, csv_filename: str, course: Network, is_overwrite_csv: bool=False, is_old=False, should_strip_tags=False, filtered=False) -> None:
    """ Use for accessing the api as an instructor. Converts json of piazza posts into a csv with html entities potentially removed.

    :param json_file_path: Path to json file to convert to csv
    :param csv_filename: Name of csv file to save to cur directory
    :param course: Used to extract student profile to determine whether they are endorsed. **Actually not a valid way of checking**
    :param is_old: Toggle to true if course instance is 2019 or earlier. These posts use the 'status' field to determine whether
    a post is private
    """

    print("Permissions = Instructor")

    schema = ("post_id,is_private,question_title,question,folders,student_poster_name,date_question_posted," 
    "student_answer,student_answer_name,date_student_answer_posted,is_student_endorsed,is_student_helpful,"
    "instructor_answer,instructor_answer_name,date_instructor_answer_posted,is_instructor_helpful," 
    "is_followup\n")


    parser = MyHTMLParser()

    endorsed_students = get_endorsed_students(course)[0] # *


    with open(json_file_path, 'r') as json_file:
        with open(csv_filename, 'w') as csv_file:
            csv_file.write(schema)
            posts = json.load(json_file)
            num_posts = 0
            for post in tqdm(posts):   
                row = [] 
                if post['type'] == 'question':
                    question = post['history'][0] # newest update of question. Change index to -1 for oldest
                    question_title = question['subject']
                    question_content = question['content']

                    # img tag filtering
                    if filtered and re.search('@|<img|<pre|\.png|def', question_title + question_content):
                        continue


                    folders = ','.join(post['folders'])
                    
                    date_created = get_post_created(post)

                    answers = get_answers(post, endorsed_students) # *
                    student_answer = answers['s_answer']
                    instructor_answer = answers['i_answer']

                
                    if should_strip_tags:
                        question_title, question_content = strip_tags(question_title), strip_tags(question_content)

                  
                    row = [post['nr'], is_private(post, is_old), question_title, question_content, folders, get_post_creator(post), date_created]
                    s_row, i_row = [], []
                    if student_answer['text'] != '':
                        print(student_answer)
                        student_answer_text = student_answer['text']
                        if should_strip_tags:
                            student_answer_text = strip_tags(student_answer_text)
                        s_row = [student_answer_text, student_answer['poster'], student_answer['date'], str(student_answer['is_endorser']), str(student_answer['is_helpful'])] 
                    else:
                        s_row = [None, None, None, None, None]

                    if instructor_answer['text'] != '':
                        instructor_answer_text = instructor_answer['text']
                        if should_strip_tags:
                            instructor_answer_text = strip_tags(instructor_answer_text)
                        i_row = [instructor_answer_text, instructor_answer['poster'], instructor_answer['date'], str(instructor_answer['is_helpful'])] 
                    else:
                        i_row = [None, None, None, None]
                    
                    # student and instructor answer kept on same row
                    row = row + s_row + i_row

                    is_followup = 'False'

                    for c in post['children']:
                        if c['type'] == 'followup':
                            is_followup = 'True'
                    
                    row += [is_followup]

                    post_writer = csv.writer(csv_file)
                    post_writer.writerow(row)
                    
                    csv_file.write('\n')

                    num_posts += 1


def main():
    args:Namespace = None
    parser:ArgumentParser = None
    args, parser = parse_args()
    
    if not args.scrape_posts and not args.json_to_csv:
        parser.print_help()
        print("Need to specify either -s or -c")
        return
    
    if args.scrape_posts and not args.json_save_path:
        parser.print_help()
        print("Need to enable -js option with --scrape-posts")
        return

    if args.json_to_csv and (not args.json_load_path or not args.csv_save_path):
        parser.print_help()
        print("Need to specify both -jl and -cp with --json-to-csv")
        return


    user_profile, course = login(args.creds_file)
    print(f"Course id is {course._nid}")
  

    if not course:
        return

    if args.scrape_posts:
        if args.num_iters < 0:
            args.num_iters = 'all'
        export_posts_json(args.json_save_path, course, max_iters=args.num_iters, throttle=args.throttle)

    

    if args.json_to_csv:
        is_instructor = check_privileges(course)

        csv_save_path = args.csv_save_path
        filename = os.path.basename(csv_save_path).split('.')[0]
        dirname = os.path.dirname(csv_save_path)

        csv_save_path = f'{dirname}/{filename}'
        suffix = ''

        if args.should_strip_tags:
            suffix += '_strip'
            print('Stripping tags')
        else:
            suffix += '_no_strip'
            print('Not stripping tags')

        if args.should_filter:
            suffix += '_filter'
            print('Filtering')
        else:
            suffix += '_no_filter'
            print('Not filtering')

        csv_save_path += suffix + '.csv'
       


        if is_instructor:
            print("Accessing Piazza api as an instructor")
            json_to_csv_instructor(args.json_load_path, csv_save_path, course, should_strip_tags=args.should_strip_tags, filtered=args.should_filter)
        else:
            print("Accessing Piazza api as a student")
            json_to_csv_student(args.json_load_path, csv_save_path, course, should_strip_tags=args.should_strip_tags, filtered=args.should_filter)


   

if __name__ == "__main__":
    main()