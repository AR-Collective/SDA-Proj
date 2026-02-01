import json
with open("config.json") as file_data:
    json_config = json.load(file_data)
    file_data.close()
