from jupyter_client import KernelManager


class Kernel:
    def __init__(self, **kwargs):
        self._manager = KernelManager(**kwargs)
        self._manager.start_kernel()
        self._client = self._manager.client()
        self._client.start_channels()
        self._client.wait_for_ready()

    @property
    def manager(self):
        return self._manager

    @property
    def client(self):
        return self._client

    def execute(self, msg):
        self._client.execute(msg)

        status = 'busy'
        result = None

        while status == 'busy':
            msg = self._client.get_iopub_msg(timeout=1)
            content = msg.get('content')
            msg_type = msg.get('msg_type')
            print(msg)

            # 'text/plain' in ['content']['data'] contains results from cells;
            #  'text' in ['content'] contains results from print statements
            if msg_type == 'execute_result':
                data = content.get('data')

                if data is not None:
                    result = data.get('text/plain')

            if 'execution_state' in content:
                status = msg['content']['execution_state']

        return result

    def shutdown(self):
        self._manager.shutdown_kernel()
