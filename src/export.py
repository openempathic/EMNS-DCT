import pandas as pd

class Exporter():
    def __init__(self, data):
        self.df = pd.DataFrame(data)
    
    def to_csv(self, directory):
        self.df.to_csv(directory, index=False, header=False)

if __name__ == '__main__':
    data = [[1,2,3], [4,5,6]]
    exporter = Exporter(data)
    print(exporter.df)
    exporter.to_csv("/home/docker/data/exported.csv")