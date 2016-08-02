import requests
import json


class TaskManager():
    def __init__(self, host='router.asus.com', port=8081,
                 user=None, password=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def _dm_request(self, action, params):
        return requests.get(
            "http://%s:%d/downloadmaster/%s" % (self.host, self.port, action),
            params=params,
            auth=(self.user, self.password)
        )

    def _dm_request_successful(self, request):
        if request.ok:
            return (request.text == 'ACK_SUCESS')
        return False

    def tasks(self):
        request = self._dm_request(
            'dm_print_status.cgi',
            {'action_mode': 'All'}
        )

        if request.ok:
            for line in request.iter_lines():
                task = Task()

                try:
                    parsed = json.loads(line)
                except ValueError:
                    parsed = json.loads(line.strip(','))

                args = [
                    'id',
                    'title',
                    'download_ratio',
                    'size',
                    'status',
                    'provider',
                    'time',
                    'download_speed',
                    'upload_speed',
                    'peers',
                    'trash_1',
                    'trash_2',
                    'path'
                ]

                for i, value in enumerate(parsed):
                    setattr(task, args[i], value)

                yield task

    def paused_tasks(self):
        return filter(lambda x: x.is_paused(), self.tasks())

    def downloading_tasks(self):
        return filter(lambda x: x.is_downloading(), self.tasks())

    def finished_tasks(self):
        return filter(lambda x: x.is_finished(), self.tasks())

    def task_info(self, task):
        request = self._dm_request(
            'dm_print_status.cgi',
            {
                'action_mode': 'show_single_task',
                'task_id': task.id,
                'logTab': 0
            }
        )

        args = [
            'id',
            'pieces',
            'hash',
            'secure',
            'comment',
            'creator',
            'created',
            'path'
        ]

        for i, value in enumerate(request.json()):
            setattr(task, args[i], value)

    def clear(self):
        request = self._dm_request(
            'dm_apply.cgi',
            {
                'action_mode': 'DM_CTRL',
                'dm_ctrl': 'clear',
            }
        )

        return self._dm_request_successful(request)

    def add_magnet(self, link):
        request = self._dm_request(
            'dm_apply.cgi',
            {
                'action_mode': 'DM_ADD',
                'download_type': 5,
                'again': 'no',
                'usb_dm_url': link
            }
        )

        return self._dm_request_successful(request)

    def cancel_task(self, task):
        request = self._dm_request(
            'dm_apply.cgi',
            {
                'action_mode': 'DM_CTRL',
                'dm_ctrl': 'cancel',
                'task_id': task.id,
            }
        )

        return self._dm_request_successful(request)

    def pause_task(self, task):
        request = self._dm_request(
            'dm_apply.cgi',
            {
                'action_mode': 'DM_CTRL',
                'dm_ctrl': 'paused',
                'task_id': task.id,
            }
        )

        return self._dm_request_successful(request)

    def resume_task(self, task):
        request = self._dm_request(
            'dm_apply.cgi',
            {
                'action_mode': 'DM_CTRL',
                'dm_ctrl': 'start',
                'task_id': task.id,
            }
        )

        return self._dm_request_successful(request)

    def pause_all(self):
        request = self._dm_request(
            'dm_apply.cgi',
            {
                'action_mode': 'DM_CTRL',
                'dm_ctrl': 'pause_all',
                'download_type': 'ALL',
            }
        )

        return self._dm_request_successful(request)

    def resume_all(self):
        request = self._dm_request(
            'dm_apply.cgi',
            {
                'action_mode': 'DM_CTRL',
                'dm_ctrl': 'start_all',
                'download_type': 'ALL',
            }
        )

        return self._dm_request_successful(request)


class Task():
    PAUSED_STATE = 'Paused'
    WAITING_STATE = 'notbegin'
    DOWNLOAD_STATE = 'Downloading'
    FINISHED_STATE = 'Finished'

    def is_paused(self):
        return getattr(self, 'status', None) == self.PAUSED_STATE

    def is_waiting(self):
        return getattr(self, 'status', None) == self.WAITING_STATE

    def is_downloading(self):
        return getattr(self, 'status', None) == self.DOWNLOAD_STATE

    def is_finished(self):
        return getattr(self, 'status', None) == self.FINISHED_STATE
