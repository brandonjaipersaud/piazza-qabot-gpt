from collections import namedtuple
from piazza_api import network, rpc

import pandas as pd


class MyNetwork(network.Network):
    def __init__(self, network_id, session):
        self._nid = network_id
        self._rpc = rpc.PiazzaRPC(network_id=self._nid)
        self._rpc.session = session

        ff = namedtuple('FeedFilters', ['unread', 'following', 'folder'])
        self._feed_filters = ff(network.UnreadFilter, network.FollowingFilter, network.FolderFilter)


    def is_responded_to(self, post:dict, piazzabot_id):
        """Has piazzabot already responded to post? If a db is used, this is redundant since we track questions we have responded to in the db."""

        for action in post['log']:
            if action['n'] == 'followup' and action['u'] == piazzabot_id:
                return True

        return False


    def has_instructor_answer(self, post):
        """Can also use has_i to test for this.

        has_s/i won't appear in dict if no s/i response so may get a keyerror
        """

        for action in post["log"]:
            if action["n"] == "i_answer":
                return True 
        return False

    def is_student_endorsed(self, post):
        """Don't respond to questions that have instructor endorsed student answers"""

        if "has_s" in post and post["has_s"] == 1:
            if "tag_endorse_prof" in post and post["tag_endorse_prof"] == 1:
                return True 

        return False
    

    
    def iter_all_posts(self, piazzabot_id=None, limit=500, skip_answered=True, db:pd.DataFrame=None, db_path=None):
        """Get all posts visible to the current user

        This grabs you current feed and ids of all posts from it; each post
        is then individually fetched. This method does not go against
        a bulk endpoint; it retrieves each post individually, so a
        caution to the user when using this.

        :type limit: int|None
        :param limit: If given, will limit the number of posts to fetch
            before the generator is exhausted and raises StopIteration.
            No special consideration is given to `0`; provide `None` to
            retrieve all posts.
        :returns: An iterator which yields all posts which the current user
            can view
        :rtype: generator
        """
        
        
        feed = self.get_feed(limit=limit, offset=0)['feed']
        filtered_feed = []
        for p in feed:

            # print(p.keys())
            # print(p)
            
            if p['type'] != 'question':
                continue

            if not piazzabot_id:
                filtered_feed.append(p)
                continue


            # no filtering if piazzabot_id is not defined -> get all questions
            if piazzabot_id and not self.is_responded_to(p, piazzabot_id):
                if skip_answered and (self.has_instructor_answer(p) or self.is_student_endorsed(p)):
                    #print(f"Skipping {p['nr']}")
                    continue 

                # print(p["nr"])
                #print(f"Answering {p['nr']}")

                filtered_feed.append(p)

        cids = [post['id'] for post in filtered_feed]
        
        for cid in cids:
            yield self.get_post(cid)


    def create_followup(self, post, content, anonymous=False):
        """Create a follow-up on a post `post`.

        It seems like if the post has `<p>` tags, then it's treated as HTML,
        but is treated as text otherwise. You'll want to provide `content`
        accordingly.

        :type  post: dict|str|int
        :param post: Either the post dict returned by another API method, or
            the `cid` field of that post.
        :type  content: str
        :param content: The content of the followup.
        :type  anonymous: bool
        :param anonymous: Whether or not to post anonymously.
        :rtype: dict
        :returns: Dictionary with information about the created follow-up.
        """
        try:
            cid = post["id"]
        except KeyError:
            cid = post

        params = {
            "cid": cid,
            "type": "followup",

            # For followups, the content is actually put into the subject.
            "subject": content,
            "content": "",
            "config": {
                "ionly": "true"
            },
            "anonymous": "yes" if anonymous else "no",
        }
        return self._rpc.content_create(params)