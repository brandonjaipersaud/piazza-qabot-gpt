from utils.utils import is_empty

def get_between_characters(text:str, character:str):
  
    start_index = text.index(f'{character}') + 1
    end_index = text.index(f'{character}', start_index)
    
    text_between = text[start_index:end_index]
    return text_between, start_index, end_index

def get_answers(text:str):
    """ Retrieve answers from a list of strings in serialized form.
        Text should be in the format 'sdfasfas', 'afafa',
        Call this with text[1:-1] to strip [] so text[0] refers to the quote token
    """

    if text[0] == '[':
        text = text[1:-1]

    answers = []
    while text != "":

        answer, start_index, end_index = get_between_characters(text, text[0])
        answers.append(answer)
        text = text[end_index+3:]

    return answers


def split_answers(row):
    
    if not is_empty(row["answer(s)"]):
        answers = get_answers(row["answer(s)"])
        row['answer1'] = answers[0]
        row['answer2'] = answers[1]
    return row