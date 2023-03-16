import json
import time
import math
from datetime import datetime
import os
from tqdm import trange, tqdm
import re
from copy import deepcopy
import sys

import datetime

from io import StringIO
from html.parser import HTMLParser

import getpass

from nptyping import NDArray, Int, Shape
from typing import Dict, List, Tuple, Union

from piazza_api import Piazza
from piazza_api.network import Network
from piazza_api import exceptions

from piazza_api_utils.my_piazza_api import MyNetwork

# from piazza_api_utils.csv_utils import merge_title_and_content

import pandas as pd

"""Custom Types"""
Answer = Dict[str,Dict[str,Union[str,int]]]
Post = Dict[str,Union[str, Union[str,int,List]]]

"""Macros"""
# who the answer is coming from
STUDENT, INSTRUCTOR, STUDENT_ENDORSED_ANSWERER = 0, 1, 2
EPSILON = 1e-05



class MyHTMLParser(HTMLParser):
    """taken from: [1]"""
    
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    """strips html tags and substitutes html entities """
    #html = html.unescape(html)
    s =  MyHTMLParser()
    s.feed(html)
    return s.get_data()




def check_image(question_content, filter='<img'):
    if re.search(filter, question_content):
        return True 
    return False
    

def get_id_from_question(df:pd.DataFrame, course:MyNetwork):
    """
    iterate through all q's. if q matches a q in df, then augment.
    """
    p = get_question_post(course, 254)
    title, content = get_question_content(p, should_strip_tags=True)
    question = merge_title_and_content(title, content)
    print(question)
    find_question = df.loc[df["question"] == question, "question"]
    print(find_question)

    raise AssertionError

    posts = course.iter_all_posts(limit=None)
  
    for p in posts:
        title, content = get_question_content(p, should_strip_tags=True)
        question = merge_title_and_content(title, content)

        print(question)
       
        # get df['question'] == question and update post id
        find_question = df.loc[df["question"] == question, "question"]
       
        if len(find_question) == 1:
            print('found')
            # set value
            raise AssertionError 

        time.sleep(1)
        
    raise AssertionError

    return df

def get_question_post(course:Network, question_id, throttle_interval=45, print_info=False):
    """Retrieve and return question post"""
    full_question = None
    retrying = False
    while(not full_question):
        try:
            if retrying:
                print(f"retrying question: {question_id}")
            full_question = course.get_post(question_id)
            if print_info:
                print(f'Fetched question {question_id}')
            retrying = False
        except exceptions.RequestError as err:
            print(f"Request Error for {question_id}. Sleeping for {throttle_interval}")
            time.sleep(throttle_interval) 
            retrying = True
        
    
    return full_question


def merge_title_and_content(title, content, sep=' '):
    """Also defined in csv_utils. Remove from that file."""
    return title + sep + content

def get_question_content(post, should_strip_tags=False):
    """Retrieve and return question content from a question post"""
    question = post['history'][0] # newest update of question. Change index to -1 for oldest
    question_title = question['subject']
    question_content = question['content']

    if should_strip_tags:
        question_title = strip_tags(question_title)
        question_content = strip_tags(question_content)

    return question_title, question_content



def get_timestamp_within_range(course:Network, df:pd.DataFrame):

    start_post = get_question_post(course, int(df["question_id"].min()))
    end_post = get_question_post(course, int(df["question_id"].max()))

    start_time = datetime.datetime.strptime(start_post['created'], '%Y-%m-%dT%H:%M:%SZ')
    end_time = datetime.datetime.strptime(end_post['created'], '%Y-%m-%dT%H:%M:%SZ')

    return start_time, end_time



def get_images(course:Network, df:pd.DataFrame):
    """what % of questions in df have images"""
    question_ids = df["question_id"].astype(int)
    questions_with_imgs = []
    questions_without_imgs = []
    for id in question_ids:
    
        # get question content
        full_question = get_question_post(course, id)
        question_title, question_content = get_question_content(full_question)
        question_content = merge_title_and_content(question_title, question_content)
        if check_image(question_content, filter='<img'):
            questions_with_imgs.append(question_content)
        else:
            questions_without_imgs.append(question_content)

    return questions_with_imgs, questions_without_imgs


        
  
def check_question(post, min, max):
    """Check if question post id is b/w min and max"""
    if post["type"] == 'question' and (post["nr"] >= min and post["nr"] <= max):
        return True
    return False


def get_questions_in_range(course:Network, df:pd.DataFrame):
    min = int(df["question_id"].min())
    max = int(df["question_id"].max())
    print(f'Min = {min} Max = {max}')
    feed:list = course.get_feed()["feed"]
    questions = list(filter(lambda p: check_question(p, min, max), feed))

    return questions
    


def check_privileges(course:Network):
    """Return True if user has necessary privileges to access piazza api"""
    try:
        course.get_all_users()
    except exceptions.RequestError:
        return False 
    return True
    

def login(cred_filepath: str=None, email=None, password=None, courseid=None, echo=False) -> Tuple[dict, Network]:
    """logs user into Piazza"""

    email:str 
    password:str 
    courseid:str 

    if cred_filepath:
        with open(cred_filepath) as f:
            creds = json.load(f)
            email, password, courseid = creds['email'], creds['password'], creds['courseid']

    else:
        if email == None or courseid == None:
            print("No cred_filepath provided. Need to specify email, courseid and optionally a password.")
            return None, None

    if not password or password == "":
        password = getpass.getpass()
        
    
    if echo:     
        print(f"email: {email}\ncourseid: {courseid}")

    p: Piazza = Piazza()
    try:
        p.user_login(email, password)
    except exceptions.AuthenticationError:
        print("PiazzaAuthenticationError: Invalid email or password")
        return None, None
    
    user_profile: dict = p.get_user_profile()
    course: Network = p.network(courseid)
    return user_profile, MyNetwork(course._nid, course._rpc.session)


def get_post_creator(post: Post):
    for entry in post['change_log']:
        if entry['type'] == 'create':
            if 'uid' in entry:
                return entry['uid']
            else:
                return None


def get_post_created(post: Post):
    """get time post was created"""
    for entry in post['change_log']:
        if entry['type'] == 'create':
            return entry['when']


def get_posts_by_student(filename:str, student_id:str) -> List[Post]:
    student_posts = []
    with open(filename, 'r') as f:
        all_posts = json.load(f)
        for p in all_posts:
            if get_post_creator(p) == student_id:
                student_posts.append(p)
    return student_posts


def get_endorsed_students(course: Network) -> Tuple[Dict, Dict]:
    endorsed_users = {}
    non_endorsed_users = {}
    users = course.get_all_users()
    for u in users:
        if u['endorser']:
            endorsed_users[u['id']] = u['name']
        else:
            non_endorsed_users[u['id']] = u['name']


    return endorsed_users, non_endorsed_users


def is_private(post: Post, is_old=False) -> bool:
    """ Return true if post is private """
    if is_old: # use 'status' field of post to determine whether post is Private
        return True if post['status'] == 'private' else False

    #print(json.dumps(post['change_log'], indent=4, sort_keys=True))
    for entry in post['change_log']:
        # print(entry)
        if entry['type'] == 'create':
            return True if entry['v'] == 'private' else False





def get_timestamp(post:Post, course:Network):
    timestamps = {}
    answers = get_answers(post, course=course, should_strip_tags=True)
    if 'timestamp' in answers['s_answer']:
        timestamps['s_timestamp'] = answers['s_answer']['timestamp']
    else:
         timestamps['s_timestamp'] = None

    
    if 'timestamp' in answers['i_answer']:
        timestamps['i_timestamp'] = answers['i_answer']['timestamp']
    else:
         timestamps['i_timestamp'] = None


    return timestamps
   


def get_followups(post:Post, should_strip_tags=False):
    print(post)




def get_answers_simple(post:Post, should_strip_tags=False):
    """Only return answers and nothing else. No need for this function anymore."""
    answers = {}
    answers['s_answer'] = {}
    answers['i_answer'] = {}

    for t in answers.keys():
        for ans in post['children']:
            if ans['type'] == t:      
                vals = answers[t]
                text = ans['history'][0]['content']
                if should_strip_tags:
                    text = strip_tags(text)
                vals['text'] = text

    if "text" not in answers['s_answer']:
        answers['s_answer']["text"] = ""

    if "text" not in answers['i_answer']:
        answers['i_answer']["text"] = ""


    return answers



def get_answers(post:Post, endorsed_students: Dict=None, course:Network=None, should_strip_tags=False, is_instructor=True) -> List[Dict[str, Answer]]:
    """ Get student and instructor answers """

    answers = {}
    answers['s_answer'] = {}
    answers['i_answer'] = {}

    for t in answers.keys():
        for ans in post['children']:
            if ans['type'] == t:      
                vals = answers[t]
                text = ans['history'][0]['content']

                if should_strip_tags:
                    text = strip_tags(text)
                vals['text'] = text

                vals['timestamp'] = ans['created']

                
                if 'uid' in ans['history'][0]:
                    vals['poster'] = ans['history'][0]['uid']
                else:
                     vals['poster'] = None
                vals['date'] = ans['history'][0]['created']
                vals['num_helpful'] = len(ans['tag_endorse_arr'])
                # post creator is same student that liked response
                if get_post_creator(post) in ans['tag_endorse_arr']:
                    vals['is_helpful'] = True 
                else:
                    vals['is_helpful'] = False

                if ans['type'] == "s_answer":
                    
                    if 'uid' in ans['history'][0]:
                        student_poster_id = ans['history'][0]['uid'] # id of the most recent student answer editor
                    else:
                        student_poster_id = None

                    if not is_instructor:
                        continue

                    # below are privledged operations

                    # check if student is endorsed (actually not a valid way of checking)
                    if course and not endorsed_students:
                        endorsed_students = get_endorsed_students(course)

                    

                    vals['is_endorser'] = False
                    if student_poster_id in endorsed_students:
                        vals['is_endorser'] = True
                   
                break

    if "text" not in answers['s_answer']:
        answers['s_answer']["text"] = ""

    if "text" not in answers['i_answer']:
        answers['i_answer']["text"] = ""
    
    return answers