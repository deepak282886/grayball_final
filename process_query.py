def process_json(entity):
    entity = entity.replace('null', '"null"')
    json_entity = eval(entity)
    query_dict = {}
    if len(json_entity):
        for i, j in json_entity.items():
            if "name" in j.keys():
                query_dict[j["name"]] = j["parameter_value"]
            if "range_start" in j.keys():
                query_dict[f"{j['name']}_range_start"] = j["range_start"]

            if "range_end" in j.keys():
                query_dict[f"{j['name']}_range_end"] = j["range_end"]
            if "operator" in j.keys():
                query_dict[f"{j['name']}_operator"] = j["operator"]
    return query_dict

