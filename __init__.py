# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 08:54:43 2018

@author: Tim Campbell

"""

import requests
import json
import math
import time
import os
from pathlib import Path

class PerfMetrics:
    """ Compute performance metrics from task on Wrike's platform. """
    
    def __init__(self):
        self.root = str(Path(__file__).parents[0])        
        
        # Get Wrike credentials. The token must be stored in a JSON-formatted file named 'wrike.credentials'
        with open(os.path.join(self.root,'wrike.credentials'),'r') as f:
            self.__cred = json.load(f)
        
        self.tasks = None
        self.comments = None
        self.attachments = None
        self.combined = None

    def get_tasks(self):
        """ Get the tasks from the Wrike platform. """
        
        # Define the v3 Wrike URI
        urlPrefix = 'https://www.wrike.com/api/v3/'
        # Define the authorization via permanent token. This token (defined in wrike.credentials['token']) links to the account to calculate metrics.
        headers = {'Authorization': 'bearer {}'.format(self.__cred['token'])}        
        
        # Get the task summaries, comments, and attachments and return just the 'data' in JSON format
        r = requests.get(urlPrefix+'tasks',headers=headers)
        self.tasks = r.json()['data']
        
        r = requests.get(urlPrefix+'comments',headers=headers)
        self.comments = r.json()['data']
        
        # Since attachments relies on a specific account, go through each account associated with the tasks and combine into self.attachments
        self.attachments = []
        for accountnum in list(set([task['accountId'] for task in self.tasks])):
            r = requests.get(urlPrefix+'accounts/{actno}/attachments'.format(actno=self.tasks[0]['accountId']),headers=headers)
            self.attachments.append(r.json()['data'])
        # Flatten attachments
        self.attachments = [item for sublist in self.attachments for item in sublist]
        
        # Combine all task summaries, comments, attachments, and task details into one dictionary
        self.combined = [None]*len(self.tasks)
        
        idx = 0
        whileConditions = True
        retryFlag = False
        while whileConditions:
            
            val = self.tasks[idx]
            
            try:
                r = requests.get(urlPrefix+'tasks/{tid}'.format(tid=val['id']),headers=headers)
                self.combined[idx] = r.json()['data'][0]
            
                commentIdx = next(iter(idx for idx,x in enumerate(self.comments) if x['taskId']==val['id']),-1)
                if commentIdx>=0:
                    self.combined[idx]['comments'] = self.comments[commentIdx]    
            except json.JSONDecodeError:        # sometimes there is a mis-read; retry once
                if retryFlag:
                    whileConditions = False
                    raise
                    
                retryFlag = True
                time.sleep(1)
                
            else:
                retryFlag = False
                # If 'hasAttachments', there should be a matching attachment. If the attachment was deleted, this flag is not reset.
                if self.combined[idx]['hasAttachments']:
                    if len(self.attachments)>0:    # account for no attachments
                        attachIdx = next(iter(idx for idx,x in enumerate(self.attachments) if x['taskId']==val['id']),-1)
                        if attachIdx>=0:    # account for no matching attachments
                            self.combined[idx]['attachments'] = self.attachments[attachIdx]
                    
                # Pause briefly so as not to overwhelm Wrike
                time.sleep(0.1)  
                
                idx+=1
                
                # Status indicator
                if idx%math.ceil(len(self.tasks)/10)==0 or idx>=len(self.tasks):
                    print('{0:.0f}% complete'.format(min([100,(idx+1)/len(self.tasks)*100])))    
                    
                if idx>=len(self.tasks):
                    whileConditions = False

    def write_files(self):
        """ Write the Wrike data to files. """
        
        # get_tasks if haven't already
        if self.combined is None:
            self.get_tasks()
        
        for valname in ['tasks','comments','attachments','combined']:
            # Dump the JSON to the specified file in pretty format (4 indents per section)
            with open(os.path.join(self.root,'wrike_files',valname+'.json'),'w+') as fp:
                json.dump(getattr(self,valname),fp,indent=4)

    
if __name__ == '__main__':
    wrikeTasks = PerfMetrics()    