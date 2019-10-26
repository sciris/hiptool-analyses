import sys
import pydoc
import sciris as sc
import scirisweb as sw
import hiptool as hp

sys.modules['hptool'] = hp

usernames = ['civfinal', 'denizhan']

data = sc.odict()

# Load datastore
print('Loading datastore...')
datastore = sw.get_datastore(config=hp.webapp.config)

# List users and projects
userkeys = datastore.keys('user*')
projectkeys = datastore.keys('project*')
print(f'There are {len(userkeys)} users and {len(projectkeys)} projects.')

for username in usernames:
    print(f'Working on {username}...')
    data[username] = sc.odict()
    data[username]['user'] = datastore.loaduser(username)
    data[username]['projects'] = sc.odict()
    for projectname in data[username]['user'].projects:
        print(f'  Working on {projectname}...')
        objstr = datastore.redis.get(projectname)
        prj = sc.loadstr(objstr, die=True)
        data[username]['projects'][projectname] = objstr

sys.modules.pop('hptool')

P = prj.obj
P.__class__ = hp.project.Project
P.__module__ = 'hiptool.project'
for hset in P.burdensets.values() + P.intervsets.values() + P.packagesets.values():
    hset.__module__ = hset.__module__.replace('hptool','hiptool')
#    hset.__class__ = hset.__class__.replace('hptool','hiptool')
prj.obj.save('TEST_HIPTOOL4.prj')

print('Done.')