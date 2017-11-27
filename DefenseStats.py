import nflgame
import pandas as pd
import numpy as np

class defense_stats():
    def __init__(self, year=2016, window=4):
        # Get All Teams
        self.teams_map = {}
        teams = []
        for team in nflgame.teams:
            teams.append(team[0])
            for i in range(len(team)):
                self.teams_map[team[i]] = team[0]
        teams.remove('STL')

        # Build DataFrame - Index for Player name and week #
        wks = range(1,18)
        idxs = [teams, wks]

        idx = pd.MultiIndex.from_product(idxs, names=['name', 'week'])
        columns = [
            'rushing_att', 
            'rushing_yds', 
            'rushing_tds', 
            'fumbles_tot',
            'home',
            'DNP',
            'fantasy_points'
        ]
        df = pd.DataFrame(data=None, index=idx, columns=columns)

        # Get Data
        games = nflgame.games(year)
        for g in games:
            wk = g.schedule['week']
            rushing_att_h = 0
            rushing_yds_h = 0
            fumbles_tot_h = 0
            rushing_tds_h = 0
            
            rushing_att_a = 0
            rushing_yds_a = 0
            fumbles_tot_a = 0
            rushing_tds_a = 0
            for p in g.players.rushing():
                if p.home:
                    rushing_att_h += p.rushing_att
                    rushing_yds_h += p.rushing_yds
                    fumbles_tot_h += p.fumbles_tot
                    rushing_tds_h += p.rushing_tds
                else:
                    rushing_att_a += p.rushing_att
                    rushing_yds_a += p.rushing_yds
                    fumbles_tot_a += p.fumbles_tot
                    rushing_tds_a += p.rushing_tds
            
            # Home Defense accumulates Away Offense
            home = self.teams_map[g.home]
            df.loc[(g.home, wk), 'home'] = 1
            df.loc[(home, wk), 'rushing_att'] = rushing_att_a
            df.loc[(home, wk), 'rushing_yds'] = rushing_yds_a
            df.loc[(home, wk), 'fumbles_tot'] = fumbles_tot_a
            df.loc[(home, wk), 'rushing_tds'] = rushing_tds_a
            
            # Away Defense accumulates Home Offense
            away = self.teams_map[g.away]
            df.loc[(g.away, wk), 'home'] = 0
            df.loc[(away, wk), 'rushing_att'] = rushing_att_h
            df.loc[(away, wk), 'rushing_yds'] = rushing_yds_h
            df.loc[(away, wk), 'fumbles_tot'] = fumbles_tot_h
            df.loc[(away, wk), 'rushing_tds'] = rushing_tds_h

        # Calculate Fantasy Points
        df['fantasy_points'] = df['rushing_yds'] * .1 + df['rushing_tds'] * 6 - df['fumbles_tot'] * 2

        # DNP
        df.loc[df['fantasy_points'].isnull(), 'DNP'] = True
        df.loc[df['fantasy_points'].notnull(), 'DNP'] = False

        # Fill NaNs
        df = df.fillna(0)

        # Boolean Values to int
        df['DNP'] = df['DNP'].astype('int')

        self.df = df
        self.df_mean = df[df['DNP'] == 0].rolling(window=window, min_periods=1).mean().astype(int)

    def getDefenseStatsPerWeek(self, team, week):
        team = self.teams_map[team]

        # If week 0 return average NFL Defense stats
        if week == 0:
            return self.df.mean().astype(int)

        DNP = 0
        if (team, week) not in list(self.df_mean.index.values):
            DNP = 1
            week -= 1

        def_row = self.df_mean.loc[team, week].astype(int)
        def_row['home'] = self.df.loc[team, week]['home']
        def_row['home'] = DNP
        
        return def_row












