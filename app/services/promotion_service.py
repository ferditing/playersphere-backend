class PromotionService:
    
    @staticmethod
    def promote_rules(standings, rules):

        promoted = []
        relegated = []

        promote_count = rules.get("promote", 0)
        relegate_count = rules.get("relegate", 0)

        if promote_count:
            promoted = standings[:promote_count]

        if relegate_count:
            relegated = standings[-relegate_count:]

        return {
            "promoted": promoted,
            "relegated": relegated
        }