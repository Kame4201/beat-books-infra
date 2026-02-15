# Database Schema

## Overview

PostgreSQL database hosted on Neon.tech. Schema is owned and managed exclusively by `beat-books-data` via Alembic migrations.

## Tables

### Team-Level Statistics

#### team_offense
| Column | Type | Description |
|--------|------|-------------|
| id | serial PK | Auto-increment ID |
| season | integer | NFL season year |
| tm | varchar(64) | Team abbreviation (e.g., "KC") |
| games_played | integer | Games played |
| points_scored | integer | Total points scored |
| total_yards | integer | Total offensive yards |
| plays | integer | Total offensive plays |
| yards_per_play | numeric(5,2) | Yards per offensive play |
| turnovers | integer | Total turnovers committed |
| fumbles_lost | integer | Fumbles lost |
| first_downs | integer | Total first downs |
| pass_completions | integer | Pass completions |
| pass_attempts | integer | Pass attempts |
| pass_yards | integer | Passing yards |
| pass_touchdowns | integer | Passing touchdowns |
| interceptions | integer | Interceptions thrown |
| rush_attempts | integer | Rushing attempts |
| rush_yards | integer | Rushing yards |
| rush_touchdowns | integer | Rushing touchdowns |
| penalties | integer | Total penalties |
| penalty_yards | integer | Penalty yards |

#### team_defense
Same structure as team_offense but tracks defensive statistics (yards allowed, points allowed, etc.).

### Player-Level Statistics

#### passing_stats
| Column | Type | Description |
|--------|------|-------------|
| id | serial PK | |
| season | integer | NFL season year |
| player_name | varchar(128) | Player name |
| tm | varchar(64) | Team abbreviation |
| age | integer | Player age |
| position | varchar(16) | Position (QB) |
| games_played | integer | Games played |
| games_started | integer | Games started |
| completions | integer | Pass completions |
| attempts | integer | Pass attempts |
| completion_pct | numeric(5,2) | Completion percentage |
| yards | integer | Passing yards |
| touchdowns | integer | Passing TDs |
| interceptions | integer | Interceptions thrown |
| passer_rating | numeric(6,2) | Passer rating |
| sacks | integer | Times sacked |
| sack_yards | integer | Yards lost to sacks |

#### rushing_stats
Columns: id, season, player_name, tm, age, position, games_played, games_started, attempts, yards, touchdowns, yards_per_attempt, fumbles.

#### receiving_stats
Columns: id, season, player_name, tm, age, position, games_played, games_started, targets, receptions, yards, touchdowns, yards_per_reception.

#### defense_stats
Individual defensive player statistics (tackles, sacks, interceptions, etc.)

#### kicking_stats
Field goals, extra points, kickoffs.

#### punting_stats
Punts, punt yards, inside-20 punts.

#### return_stats
Kick returns, punt returns, yards, touchdowns.

#### scoring_stats
Individual scoring breakdown (TDs, FGs, XPs, 2PTs, safeties).

### Game & Season Data

#### games
| Column | Type | Description |
|--------|------|-------------|
| id | serial PK | |
| season | integer | |
| week | integer | Week number (1-22) |
| game_date | date | Date of game |
| home_team | varchar(64) | Home team |
| away_team | varchar(64) | Away team |
| home_score | integer | Home team score |
| away_score | integer | Away team score |

#### standings
| Column | Type | Description |
|--------|------|-------------|
| id | serial PK | |
| season | integer | |
| tm | varchar(64) | |
| wins | integer | |
| losses | integer | |
| ties | integer | |
| win_pct | numeric(4,3) | Win percentage |
| division | varchar(32) | Division name |
| conference | varchar(8) | AFC/NFC |

### Metadata

#### scraped_data
Stores raw scraped HTML/data for reference and reprocessing.

#### scraped_data_metadata
Tracks scraping jobs: URL, timestamp, status, row count.

### Future Tables (via Alembic migration)

#### odds (Phase 2)
Opening/closing lines, moneylines, over/unders from multiple sportsbooks.

#### injury_reports (Phase 4)
Weekly injury designations (Questionable/Doubtful/Out).

#### game_weather (Phase 4)
Temperature, wind speed, precipitation for outdoor games.

## Recommended Indexes

~~~sql
CREATE INDEX idx_passing_stats_season ON passing_stats(season);
CREATE INDEX idx_passing_stats_player ON passing_stats(player_name);
CREATE INDEX idx_passing_stats_team ON passing_stats(tm);
CREATE INDEX idx_team_offense_season ON team_offense(season);
CREATE INDEX idx_rushing_stats_season ON rushing_stats(season);
CREATE INDEX idx_receiving_stats_season ON receiving_stats(season);
CREATE INDEX idx_games_season_week ON games(season, week);
CREATE INDEX idx_standings_season ON standings(season);
~~~

## Access Control

| Repo | Access Level | Can Create Tables? |
|------|--------------|--------------------|
| beat-books-data | READ/WRITE | YES (via Alembic) |
| beat-books-model | READ ONLY | NO |
| beat-books-api | NONE (routes through services) | NO |
