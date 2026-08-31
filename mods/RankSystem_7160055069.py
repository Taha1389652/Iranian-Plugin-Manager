# ba_meta require api 9

import os
import json
import babase
import bascenev1 as bs

plugman = dict(
    plugin_name="rank_system",
    description="ranks system for servers or for local players",
    external_url="",
    authors=[
        {"name": "ATD", "email": "anasdhaoidi001@gmail.com", "discord": ""},
    ],
    version="1.0.0",
)

MODS_DIR = os.path.dirname(__file__)
STATS_DIR = os.path.join(MODS_DIR, "stats")
STATS_FILE = os.path.join(STATS_DIR, "ranks.json")


class RankSystem:

    def __init__(self):
        self.data = {}
        self.load()

    def load(self):
        if not os.path.exists(STATS_DIR):
            os.makedirs(STATS_DIR)

        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, "r") as f:
                    self.data = json.load(f)
            except:
                self.data = {}

    def save(self):
        with open(STATS_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    def add_score(self, account_id, score=1):
        if account_id not in self.data:
            self.data[account_id] = {
                "score": 0,
                "rank": 0
            }

        self.data[account_id]["score"] += score
        self.update_ranks()
        self.save()

    def update_ranks(self):
        sorted_players = sorted(
            self.data.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )

        for i, (aid, p) in enumerate(sorted_players):
            p["rank"] = i + 1

    def get_rank(self, account_id):
        return self.data.get(account_id, {}).get("rank")


rank_sys = RankSystem()


class RankTag:
    def __init__(self, node, rank):

        m = bs.newnode(
            "math",
            owner=node,
            attrs={
                "input1": (0, 1.2, 0),
                "operation": "add"
            }
        )

        node.connectattr("torso_position", m, "input2")

        if rank == 1:
            text = "1"
            color = (1, 1, 1)
        elif rank == 2:
            text = "2"
            color = (1, 1, 1)
        elif rank == 3:
            text = "3"
            color = (1, 1, 1)
        else:
            text = f"#{rank}"
            color = (1, 1, 1)

        t = bs.newnode(
            "text",
            owner=node,
            attrs={
                "text": text,
                "in_world": True,
                "color": color,
                "scale": 0.01,
                "h_align": "center"
            }
        )

        m.connectattr("output", t, "position")


# 🔌 plugin
# ba_meta export babase.Plugin
class byATD(babase.Plugin):

    def on_app_running(self):
        print("Rank System Loaded ")

        import bascenev1._gameactivity as ga

        old_spawn = ga.GameActivity.spawn_player_spaz

        def new_spawn(self, player, *args, **kwargs):
            spaz = old_spawn(self, player, *args, **kwargs)

            try:
                aid = player.sessionplayer.get_account_id()

                rank_sys.add_score(aid, 1)

                rank = rank_sys.get_rank(aid)
                if rank:
                    RankTag(spaz.node, rank)

            except Exception as e:
                print("Rank error:", e)

            return spaz

        ga.GameActivity.spawn_player_spaz = new_spawn
