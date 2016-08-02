from pyasusdm import TaskManager

# Get manager
manager = TaskManager(user='****', password='****')

# Add task
print 'Adding task...'
debian_magnet = "magnet:?xt=urn:btih:c9654595270296c3c2406386d4cdf4795f04b3f0&dn=debian-7.11.0-amd64-netinst.iso&tr=udp://bttracker.debian.org:6969&tr=http://bttracker.debian.org:6969/announce"
print manager.add_magnet(debian_magnet)

# Get task
print 'Getting tasks...'
task = manager.tasks().next()
print task.title

# Pause task
print 'Pausing...'
print manager.pause_task(task)

# Cancel task
print 'Canceling...'
print manager.cancel_task(task)

# Clear tasks
print manager.clear()

for task in manager.tasks():
    print task.id
