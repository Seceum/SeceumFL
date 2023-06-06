import sys, os
sys.path.append("./")
import wrapper


ROLE = "guest"
PID = 9999

def base(jids):
    j = wrapper.EvaluationWrapper(pid=PID, hosts=[], role=ROLE, guest=9999)
    j.setReader(jids)
    j.exe(asyn=False)

if __name__  ==  "__main__":
    base(["202210111915501709650", "202210111815107453700"])

