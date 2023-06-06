
def get_child_permission(parent_dict, child_list):
    for func in child_list:
        p_id = func["p_id"]
        if parent_dict[p_id].get('children'):
            parent_dict[p_id]["children"].append(func)
        else:
            parent_dict[p_id]["children"] = [func, ]


def get_permission_list(df):
    level_1_dicts = {level_1["code"]: level_1 for level_1 in
                     df[df.menu_level == "1"].sort_values(by='code', ascending=True).to_dict("records")}
    level_2_dicts = {level_2["code"]: level_2 for level_2 in
                     df[df.menu_level == "2"].sort_values(by='code', ascending=True).to_dict("records")}
    level_3_dicts = {level_3["code"]: level_3 for level_3 in
                     df[df.menu_level == "3"].sort_values(by='code', ascending=True).to_dict("records")}
    level_4_list = df[df.menu_level == "4"].sort_values(by='code', ascending=True).to_dict("records")
    get_child_permission(level_3_dicts, level_4_list)
    get_child_permission(level_2_dicts, list(level_3_dicts.values()))
    # get_child_permission(level_2_dicts, level_3_list)
    get_child_permission(level_1_dicts, list(level_2_dicts.values()))
    return list(level_1_dicts.values())


def get_event_list(df):
    level_1_dicts = {level_1["code"]: level_1 for level_1 in
                     df[df.menu_level == "1"].sort_values(by='code', ascending=True).to_dict("records")}
    level_2_dicts = {level_2["code"]: level_2 for level_2 in
                     df[df.menu_level == "2"].sort_values(by='code', ascending=True).to_dict("records")}

    get_child_permission(level_1_dicts, list(level_2_dicts.values()))
    return list(level_1_dicts.values())