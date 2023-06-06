import os, json, sys, re, yaml

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("%s [PARY_ID]"%sys.argv[0])
        sys.exit()
    pwd = os.path.dirname(os.path.abspath(__file__)) + "/"
    pid = sys.argv[1]
    cnf_path = os.path.join(pwd, "eggroll/conf/route_table.json")
    obj = json.load(open(cnf_path, "r"))
    if pid not in obj["route_table"]:
        print(f"[ERROR] {pid} not in {cnf_path}")
        sys.exit()

    MY_IP = obj["route_table"][pid]["default"][0]["ip"]
    print(f"[INFO] My IP: {MY_IP}")

    print("[INFO]Init conf/service_conf.yaml")
    with open(pwd + "conf/service_conf.yaml", "r") as f:
        obj = yaml.safe_load(f)
        obj["fateflow"]["host"] = MY_IP
    with open(pwd + "conf/service_conf.yaml", "w+") as f:
        f.write(yaml.safe_dump(obj, sort_keys=False))
    print("[DONE]")

    print("[INFO]Init ./eggroll/conf/eggroll.properties")
    lines = []
    with open(pwd + "eggroll/conf/eggroll.properties", "r") as f:
        while True:
            l = f.readline()
            if not l:break
            l = l.strip("\n")
            if re.match(r"eggroll\.resourcemanager\.process.tag", l):
                l = f"eggroll.resourcemanager.process.tag={pid}"
            if re.match(r"eggroll\.rollsite\.party.id", l):
                l = f"eggroll.rollsite.party.id={pid}"
            lines.append(l)
    with open(pwd + "eggroll/conf/eggroll.properties", "w+") as f:
        f.write("\n".join(lines))
    print("[DONE]")

    print("[INFO]Init conf/app.config.js")
    lines = []
    with open(pwd + "conf/app.config.js", "r") as f:
        while True:
            l = f.readline()
            if not l:break
            l = l.strip("\n")
            if re.search(r"VITE_GLOB_API_URL\"", l):
                l = f"\"VITE_GLOB_API_URL\":\"http://{MY_IP}:9380\","
            lines.append(l)
    with open(pwd + "conf/app.config.js", "w+") as f:
        f.write("\n".join(lines))
    print("[DONE]")


    print("[INFO]Init fateboard/conf/application.properties")
    lines = []
    with open(pwd + "fateboard/conf/application.properties", "r") as f:
        while True:
            l = f.readline()
            if not l:break
            l = l.strip("\n")
            if re.match(r"fateflow\.url[= ]", l):
                l = f"fateflow.url=http://{MY_IP}:9380"
            lines.append(l)
    with open(pwd + "fateboard/conf/application.properties", "w+") as f:
        f.write("\n".join(lines))
    print("[DONE]")

 
    print("[INFO]Init fate-serving/fate-serving-server/conf/serving-server.properties")
    lines = []
    with open(pwd + "fate-serving/fate-serving-server/conf/serving-server.properties", "r") as f:
        while True:
            l = f.readline()
            if not l:break
            l = l.strip("\n")
            if re.match(r"http\.adapter\.url", l):
                l = f"http.adapter.url=http://{MY_IP}:9380/v1/model_manage/get_feature"
            if re.match(r"model\.transfer\.url", l):
                l = f"model.transfer.url=http://{MY_IP}:9380/v1/model/transfer"
            lines.append(l)
    with open(pwd + "fate-serving/fate-serving-server/conf/serving-server.properties", "w+") as f:
        f.write("\n".join(lines))
    print("[DONE]")

                

