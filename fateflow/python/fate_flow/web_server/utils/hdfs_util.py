import io
import pandas as pd
from pyarrow import fs


# class HDFSUtil:
#     def __init__(self, node_name):
#         self.client = Client(node_name, session=False, timeout=20)
#
#     def read_hdfs(self, file_path):
#         with self.client.read(file_path) as f:
#             df = pd.read_csv(f, nrows=5)
#         return df

class HDFSUtil:
    def __init__(self, node_name, path):
        self.path = f'{node_name}/{path}'
        self.file_path = path
        self.fs_client = fs.HadoopFileSystem.from_uri(self.path)

    def _exist(self):
        print(self.path)
        info = self.fs_client.get_file_info([self.file_path])[0]
        return info.type != fs.FileType.NotFound

    def read_hdfs(self):
        if not self._exist():
            return False, 'HDFS 找不到 {}文件'.format(self.path)
        index = 0
        data = []
        columns = []
        with io.TextIOWrapper(buffer=self.fs_client.open_input_stream(self.path), encoding="utf-8") as reader:
            for line in reader:
                if index > 5:
                    break
                msg = line.strip()
                line_data = msg.split(',')
                if index == 0:
                    columns = line_data
                else:
                    data.append(line_data)
                index += 1
        df = pd.DataFrame(data, columns=columns)
        return True, df

    def get_count(self):
        if not self._exist():
            return False, 'HDFS 找不到 {}文件'.format(self.path)
        count = 0
        with io.TextIOWrapper(buffer=self.fs_client.open_input_stream(self.path), encoding="utf-8") as reader:
            for line in reader:
                count += 1
        data_count = count - 1 if count else count
        return True, data_count
