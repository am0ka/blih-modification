#!/usr/bin/env python3

import os
import sys
import getopt
import hmac
import hashlib
import urllib.request
import urllib.parse
import json
import getpass

version = 1.7

class blih:
    def __init__(self, baseurl='https://blih.epitech.eu/', user=None, token=None, verbose=False, user_agent='blih-' + str(version)):
        self._baseurl = baseurl
        if token:
            # using password as argument
            # password is in style of b'XXXXXXXX', just cut
            self._token = bytes(hashlib.sha512(bytes(str(token)[2:-1], 'utf8')).hexdigest(), 'utf8')
        else:
            self.token_calc()
        if user == None:
            self._user = getpass.getuser()
        else:
            self._user = user
        self._verbose = verbose
        self._useragent = user_agent

    def token_get(self):
        return self._token

    def token_set(self, token):
        self._token = token

    token = property(token_get, token_set)

    def token_calc(self):
        self._token = bytes(hashlib.sha512(bytes(getpass.getpass(), 'utf8')).hexdigest(), 'utf8')

    def sign_data(self, data=None):
        signature = hmac.new(self._token, msg=bytes(self._user, 'utf8'), digestmod=hashlib.sha512)
        if data:
            signature.update(bytes(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')), 'utf8'))

        signed_data = {'user' : self._user, 'signature' : signature.hexdigest()}
        if data != None:
            signed_data['data'] = data

        return signed_data

    def request(self, resource, method='GET', content_type='application/json', data=None, url=None):
        signed_data = self.sign_data(data)

        if url:
            req = urllib.request.Request(url=url, method=method, data=bytes(json.dumps(signed_data), 'utf8'))
        else:
            req = urllib.request.Request(url=self._baseurl + resource, method=method, data=bytes(json.dumps(signed_data), 'utf8'))
        req.add_header('Content-Type', content_type)
        req.add_header('User-Agent', self._useragent)

        try:
            f = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            print ('HTTP Error ' + str(e.code))
            data = json.loads(e.read().decode('utf8'))
            print ("Error message : '" + data['error'] + "'")
            sys.exit(1)

        if f.status == 200:
            try:
                data = json.loads(f.read().decode('utf8'))
            except:
                print ("Can't decode data, aborting")
                sys.exit(1)
            return (f.status, f.reason, f.info(), data)

        print ('Unknown error')
        sys.exit(1)

    def repo_create(self, name, type='git', description=None):
        data = {'name' : name, 'type' : type}
        if description:
            data['description'] = description
        # pylint: disable=unused-variable
        status, reason, headers, data = self.request('/repositories', method='POST', data=data)
        print (data['message'])

    def repo_list(self, search=''):
        # pylint: disable=unused-variable
        status, reason, headers, data = self.request('/repositories', method='GET')
        for i in data['repositories']:
            if str(i).find(search) != -1:
                print(i)

    def repo_delete(self, name):
        # pylint: disable=unused-variable
        status, reason, headers, data = self.request('/repository/' + name, method='DELETE')
        print (data['message'])

    def repo_info(self, name):
        # pylint: disable=unused-variable
        status, reason, headers, data = self.request('/repository/' + name, method='GET')
        print (data['message'])

    def repo_setacl(self, name, acluser, acl):
        data = {'user' : acluser, 'acl' : acl}
        # pylint: disable=unused-variable
        status, reason, headers, data = self.request('/repository/' + name + '/acls', method='POST', data=data)
        print (data['message'])

    def repo_getacl(self, name):
        # pylint: disable=unused-variable
        status, reason, headers, data = self.request('/repository/' + name + '/acls', method='GET')
        for i in data.keys():
            print (i + ':' + data[i])

    def repo_clone(self, name, direction=None):
        # pylint: disable=unused-variable
        status, reason, headers, username = self.request('/whoami', method='GET')
        git_url = 'git@git.epitech.eu:/' + str(username['message']) + '/' + name
        if direction == None:
            os.system("git clone " + git_url)
        else:
            os.system("git clone " + git_url + " " + direction)

    def repo_init(self, name):
        self.repo_create(name)
        self.repo_setacl(name, "ramassage-tek", "r")
        self.repo_clone(name)

    def sshkey_upload(self, keyfile):
        try:
            f = open(keyfile, 'r')
        except (PermissionError, FileNotFoundError):
            print ("Can't open file : " + keyfile)
            return
        key = urllib.parse.quote(f.read().strip('\n'))
        f.close()
        data = {'sshkey' : key}
        # pylint: disable=unused-variable
        status, reason, headers, data = self.request('/sshkeys', method='POST', data=data)
        print (data['message'])

    def sshkey_delete(self, sshkey):
        # pylint: disable=unused-variable
        status, reason, headers, data = self.request('/sshkey/' + sshkey, method='DELETE')
        print (data['message'])

    def sshkey_list(self):
        # pylint: disable=unused-variable
        status, reason, headers, data = self.request('/sshkeys', method='GET')
        for i in data.keys():
            print (data[i] + ' ' + i)

    def whoami(self):
        # pylint: disable=unused-variable
        status, reason, headers, data = self.request('/whoami', method='GET')
        print (data['message'])

def usage_repository():
    print ('Usage: ' + sys.argv[0] + ' [options] repository command ...')
    print ()
    print ('Commands :')
    print ('\tcreate repo (c)\t\t\t-- Create a repository named "repo"')
    print ('\tinfo repo (i)\t\t\t-- Get the repository metadata')
    print ('\tgetacl repo (ga)\t\t-- Get the acls set for the repository')
    print ('\tlist (l)\t\t\t-- List the repositories created')
    print ('\t\t -f | --find [value]\t-- Search specific repositories in the list')
    print ('\tsetacl repo user [acl] (sa)\t-- Set (or remove) an acl for "user" on "repo"')
    print ('\t\t\t\t\tACL format:')
    print ('\t\t\t\t\tr for read')
    print ('\t\t\t\t\tw for write')
    print ('\t\t\t\t\ta for admin')
    print ('\tclone repo (git)\t\t-- Clone repository in <repo_name> directory')
    print ('\tclone repo dest\t\t\t-- Clone repository in any directory')
    print ('\tinit repo \t\t\t-- Create, Set and Clone. 3in1 function')
    sys.exit(1)

def repository(args, baseurl, user, token, verbose, user_agent):
    if len(args) == 0:
        usage_repository()
    if (args[0] == 'create') or (args[0] == 'c'):
        if len(args) != 2:
            usage_repository()
        handle = blih(baseurl=baseurl, user=user, token=token, verbose=verbose, user_agent=user_agent)
        handle.repo_create(args[1])
    elif (args[0] == 'list') or (args[0] == 'l'):
        if (len(args) != 1) and (len(args) != 3):
            usage_repository()
        handle = blih(baseurl=baseurl, user=user, token=token, verbose=verbose, user_agent=user_agent)
        if (len(args) != 1) and ((args[1] == '-f') or (args[1] == '--find')):
            handle.repo_list(args[2])
        else:
            handle.repo_list()
    elif (args[0] == 'info') or (args[0] == 'i'):
        if len(args) != 2:
            usage_repository()
        handle = blih(baseurl=baseurl, user=user, token=token, verbose=verbose, user_agent=user_agent)
        handle.repo_info(args[1])
    elif (args[0] == 'delete') or (args[0] == 'd'):
        if len(args) != 2:
            usage_repository()
        handle = blih(baseurl=baseurl, user=user, token=token, verbose=verbose, user_agent=user_agent)
        handle.repo_delete(args[1])
    elif (args[0] == 'setacl') or (args[0] == 'sa'):
        if len(args) != 4 and len(args) != 3:
            usage_repository()
        if len(args) == 3:
            acl = ''
        else:
            acl = args[3]
        handle = blih(baseurl=baseurl, user=user, token=token, verbose=verbose, user_agent=user_agent)
        handle.repo_setacl(args[1], args[2], acl)
    elif (args[0] == 'getacl') or (args[0] == 'ga'):
        if len(args) != 2:
            usage_repository()
        handle = blih(baseurl=baseurl, user=user, token=token, verbose=verbose, user_agent=user_agent)
        handle.repo_getacl(args[1])
    # git clone function
    elif (args[0] == 'clone') or (args[0] == 'git'):
        if len(args) == 2 or len(args) == 3:
            handle = blih(baseurl=baseurl, user=user, token=token, verbose=verbose, user_agent=user_agent)
            if len(args) == 2:
                handle.repo_clone(args[1])
            elif len(args) == 3:
                handle.repo_clone(args[1], args[2])
        else:
            usage_repository()
    elif (args[0] == 'init'):
        if len(args) != 2:
            usage_repository()
        handle = blih(baseurl=baseurl, user=user, token=token, verbose=verbose, user_agent=user_agent)
        handle.repo_init(args[1])
    else:
        usage_repository()

def usage_sshkey():
    print ('Usage: ' + sys.argv[0] + ' [options] sshkey command ...')
    print ()
    print ('Commands :')
    print ('\tupload [file]\t\t\t-- Upload a new ssh-key')
    print ('\tlist\t\t\t\t-- List the ssh-keys')
    print ('\tdelete <sshkey>\t\t\t-- Delete the sshkey with comment <sshkey>')
    sys.exit(1)

def sshkey(args, baseurl, user, token, verbose, user_agent):
    if len(args) == 0:
        usage_sshkey()
    if args[0] == 'list':
        handle = blih(baseurl=baseurl, user=user, token=token, verbose=verbose, user_agent=user_agent)
        handle.sshkey_list()
    elif args[0] == 'upload':
        key = None
        if len(args) == 1:
            key = os.getenv('HOME') + '/.ssh/id_rsa.pub'
        elif len(args) == 2:
            key = args[1]
        else:
            usage_sshkey()
        handle = blih(baseurl=baseurl, user=user, token=token, verbose=verbose, user_agent=user_agent)
        handle.sshkey_upload(key)
    elif args[0] == 'delete':
        if len(args) != 2:
            usage_sshkey()
        handle = blih(baseurl=baseurl, user=user, token=token, verbose=verbose, user_agent=user_agent)
        handle.sshkey_delete(args[1])
    else:
        usage_sshkey()

def whoami(args, baseurl, user, token, verbose, user_agent):
    handle = blih(baseurl=baseurl, user=user, token=token, verbose=verbose, user_agent=user_agent)
    handle.whoami()

def usage():
    print ('Usage: ' + sys.argv[0] + ' [options] command ...')
    print ()
    print ('Global Options :')
    print ('\t-u user | --user=user\t\t-- Run as user')
    print ('\t-v | --verbose\t\t\t-- Verbose')
    print ('\t-b url | --baseurl=url\t\t-- Base URL for BLIH')
    print ('\t-t | --token\t\t\t-- Specify password in the cmdline')
    print ()
    print ('Commands :')
    print ('\trepository (r)\t\t\t-- Repository management')
    print ('\tsshkey\t\t\t\t-- SSH-KEYS management')
    print ('\twhoami\t\t\t\t-- Print who you are')
    sys.exit(1)

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hvu:b:t:VU:', ['help', 'verbose', 'user=', 'baseurl=', 'token=', 'version', 'useragent='])
    except getopt.GetoptError as e:
        print (e)
        usage()

    verbose = False
    user = None
    baseurl = 'https://blih.epitech.eu/'
    token = None
    user_agent = 'blih-' + str(version)

    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
        elif o in ('-v', '--verbose'):
            verbose = True
        elif o in ('-u', '--user'):
            user = a
        elif o in ('-b', '--baseurl'):
            baseurl = a
        elif o in ('-t', '--token'):
            token = bytes(a, 'utf8')
        elif o in ('-V', '--version'):
            print ('blih version ' + str(version))
            sys.exit(0)
        elif o in ('-U', '--useragent'):
            user_agent = a
        else:
            usage()

    if len(args) == 0:
        usage()

    if (args[0] == 'repository') or (args[0] == 'r'):
        repository(args[1:], baseurl, user, token, verbose, user_agent)
    elif args[0] == 'sshkey':
        sshkey(args[1:], baseurl, user, token, verbose, user_agent)
    elif args[0] == 'whoami':
        whoami(args[1:], baseurl, user, token, verbose, user_agent)
    else:
        usage()
