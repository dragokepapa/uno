#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class GameManager:
    def __init__(self):
        # simple storage (UNO bot ke liye basic)
        self.games = {}
        self.userid_current = {}

    def player_for_user_in_chat(self, user, chat):
        # basic safe function (error na aaye)
        if not user or not chat:
            return None

        game = self.games.get(chat.id)
        if not game:
            return None

        for player in game.get("players", []):
            if player.user.id == user.id:
                return player

        return None


# 🔥 IMPORTANT LINE (ye hi missing tha)
gm = GameManager()