from notifications.signals import notify

def task_completed(recipient, obj):
    notify.send(obj, recipient=recipient, verb="A task has been completed", target=obj)

def task_failed(recipient, obj):
    notify.send(obj, recipient=recipient, verb="A task has failed", target=obj)
