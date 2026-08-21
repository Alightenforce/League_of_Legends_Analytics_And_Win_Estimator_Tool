class Champion_Manager:
    def __init__(self, api, version_number):
        self.api = api
        self.version_number = version_number
        self.champion_lookup = None

    def find_champion_ids_to_names(self) -> dict:
        dict_of_champion_ids_to_names = {}
        data = self.api.get_champion_data(self.version_number)
        all_champion_names = data["data"]
        for champion in all_champion_names.values():
            dict_of_champion_ids_to_names[int((champion["key"]))] = champion["name"]
        return dict_of_champion_ids_to_names