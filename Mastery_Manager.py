class Mastery_Manager:
    def __init__(self, api, region_code, puuid, champion_manager):
        self.api = api
        self.region_code = region_code
        self.puuid = puuid
        self.champion_manager = champion_manager

    def get_all_champion_masteries(self) -> list:
        list_of_champion_masteries = []
        data = self.api.get_mastery_data(self.region_code, self.puuid)
        for champion in data:
            id_to_mastery = ((champion["championId"]), (champion["championPoints"]))
            list_of_champion_masteries.append(id_to_mastery)
        return list_of_champion_masteries

    def match_champion_name_to_champion_mastery(self, list_of_champion_masteries : list, dict_of_champion_ids_to_names : dict) -> dict:
        champion_name_to_champion_mastery = {}
        for champion_id_mastery, mastery_points in list_of_champion_masteries:
            if champion_id_mastery in dict_of_champion_ids_to_names:
                champion_name = (dict_of_champion_ids_to_names[champion_id_mastery])
                champion_name_to_champion_mastery[champion_name] = mastery_points
        return champion_name_to_champion_mastery

    def get_champion_name_to_champion_mastery(self) -> dict:
        list_of_champion_masteries = self.get_all_champion_masteries()
        dictionary_of_champion_ids_and_names = self.champion_manager.find_champion_ids_to_names()
        name_to_mastery_points = self.match_champion_name_to_champion_mastery(list_of_champion_masteries, dictionary_of_champion_ids_and_names)
        return name_to_mastery_points