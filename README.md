## Dumb Apple Music - Spotify playlist comparer script. 
Idea is to find songs unique to each platform and not ending up with tons of duplicates as is the case using apps like _Soundiiz_ to do so.

Dependencies:
- pandas
- plistlib

Apple music file needs to be exported as .xml file. Spotfity needs to be exported as .csv using apps like _Soundiiz_ and _Tune My Music_.


### Steps needed to run:
- create python virtual env (optional):
`` python -m venv playlist_compare ``
`` source playlist_compare/bin/activate ``
`` source playlist_compare/bin/activate ``
- install dependencies:
`` pip install pandas plistlib ``
- run script:
`` python3 compare_playlists.py <spotify_playlist_filepath.csv> <apple_playlist_filepath.xml> ``


### Ways to improve (might do but not promised):
- Support for more file types
- Songs similarity ratio
- Direct API connection
- GUI
- Binary packages
- Automatically adding new songs to account

<img width="458" alt="Screenshot 2025-02-09 at 5 57 07 PM" src="https://github.com/user-attachments/assets/97c6024f-c443-48a7-b83e-eab2d1fee8a4" />
