
__m = [
    "dataset instance",
    "update storage engine",
    "job default config",
    "update federation engine",
    "update computing engine",
    "engine runtime conf",
    "start destroy manager",
    "query by manager",
    "base_worker.run",
    "task_executor.",
    "_session.",
    "reader.",
    "Data meta",
    "tracker_client.",
    "task_base_worker.",
    "control_client.",
    "pipelined_model.create_component_model",
    "_table.mapPartitions",
    "db_models.init_database_tables",
    "blocks.create_cipher",
    "secure_aggregator.__init__",
    "base_param._warn_to_deprecate_param",
    "one_vs_rest.one_vs_rest_factory",
    "mini_batch.get_batch_generator",
    "hetero_decision_tree_guest.assign_instances_to_new_node",
    "boosting.generate_flowid",
    "decision_tree.set_flowid",
    "table.load",
    "client.init"
]




def log_filter(m):
    for value in __m:
        if m.find(value) >= 0:
            return True

    return False

if __name__ == "__main__":
    flag = log_filter('[INFO] [2023-05-23 02:16:15,644] [202305230215576445560] [3108:140377913743168] - [ecdh_intersect_guest._exchange_id] [line:36]: sent id 1st ciphertext to all host')
    print(flag)
    flag =log_filter('client.init')
    print(flag)