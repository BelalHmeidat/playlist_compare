import sys
import os
import pandas as pd
from enum import Enum, auto
# import xml.etree.ElementTree as ET
import plistlib

pd.set_option('display.max_rows', None)  # No row limit
pd.set_option('display.max_columns', None)  # No column limit
pd.set_option('display.width', None)  # Automatically adjust the width of the output
pd.set_option('display.max_colwidth', None)  # Display full content of each column

class Platform(Enum):
    APPLE = auto()
    SPOTIFY = auto()

class Format(Enum):
    CSV = '.csv'
    XML = '.xml'
    TXT = '.txt'
    # TODO: add more formats

def read_spotify_csv(filepath):
    spotify_df = pd.read_csv(filepath)
    spotify_df = spotify_df.reset_index(drop=True)
    # print(spotify_df[['Track name']])
    return spotify_df

def read_apple_music_xml(filepath):
    file = open(filepath, 'rb')
    pl = plistlib.load(file)
    apple_music_df = pd.DataFrame.from_dict(pl['Tracks'], orient='index')
    # df = df[['Name', 'Artist', 'Play Count']]
    apple_music_df['Play Count'] = apple_music_df['Play Count'].fillna(0)
    apple_music_df = apple_music_df.reset_index(drop=True)
    file.close()
    # print(apple_music_df[['Name']])
    return apple_music_df



def search_duplicate_tracks_apple_music(apple_music_df: pd.DataFrame):
    duplicates = []

    def are_same(row1, row2):
        return row1['Name'] in row2['Name'] and row1['Artist'] in row2['Artist']

    for i, row1 in apple_music_df.iterrows():
        for j, row2 in apple_music_df.iterrows():
            if i != j and are_same(row1, row2):
                if i in duplicates or j in duplicates: 
                    continue
                if apple_music_df.loc[i, 'Play Count'] > apple_music_df.loc[j, 'Play Count'] and j not in duplicates:
                    duplicates.append(j)
                elif apple_music_df.loc[i, 'Play Count'] <= apple_music_df.loc[j, 'Play Count'] and i not in duplicates:
                    duplicates.append(i)
    return duplicates

def search_duplicate_tracks_spotify(spotify_df: pd.DataFrame):
    duplicates= []
    def are_same(row1, row2):
        return row1['Track name'] in row2['Track name'] and row1['Artist name'] in row2['Artist name']
    for i, row1 in spotify_df.iterrows():
        for j, row2 in spotify_df.iterrows():
            if i in duplicates or j in duplicates: continue
            if i != j and are_same(row1, row2):
                if j not in duplicates: 
                    duplicates.append(j)
                else: duplicates.append(i)
    return duplicates

def delete_duplicates(df: pd.DataFrame, duplicates_ix):
    duplicates_ix = list(duplicates_ix)
    df = df.drop(index=duplicates_ix, inplace=True)
    # print(df.count())

def find_and_delete_duplicates(spotify_df, apple_music_df):
    apple_duplicates = search_duplicate_tracks_apple_music(apple_music_df)
    spotify_duplicates = search_duplicate_tracks_spotify(spotify_df)
    delete_duplicates(apple_music_df, apple_duplicates)
    delete_duplicates(spotify_df, spotify_duplicates)

def process_track_name(track_name):
    cut_begin_index = track_name.find('(')
    cut_end_index = track_name.find(')')
    if cut_begin_index != -1 and cut_end_index != -1:
        track_name = track_name[:cut_begin_index] + track_name[cut_end_index+1:]
    dash_cut_index = track_name.find(' - ')
    if dash_cut_index != -1:
        track_name = track_name[:dash_cut_index]
    special_characters = ['?', '!','.', ',' ':', ';', '-', '_', '…']
    for char in special_characters:
        index = track_name.find(char)
        while index != -1:
            if index + 1 == len(track_name):
                track_name = track_name[:index]
            elif index - 1 == 0:
                track_name = track_name[index+1:]
            else: 
                after = track_name[index+1]
                before = track_name[index-1]
                if after == ' ' and before == ' ':
                    track_name = track_name[:index-1] + track_name[index+1:]
                elif after == ' ' or before == ' ':
                    track_name = track_name[:index] + track_name[index+1:]
                else: track_name = track_name[:index] + ' ' + track_name[index+1:]
            index = track_name.find(char)

    # track_name = track_name.replace('?', '').replace('!', '').replace('.', '').replace(',', '').replace(':', '').replace(';', '').replace('-', '').replace('_', '')
    return track_name.strip().lower()

def search_shared_tracks(spotify_df, apple_music_df):
    unique_to_spotify = []
    unique_to_apple = []
    def are_same(spotify_row, apple_music_row):
        spotify_name = process_track_name(spotify_row['Track name'])
        apple_name = process_track_name(apple_music_row['Name'])
        apple_sort_name = process_track_name(apple_music_row['Sort Name'])
        if (spotify_name in apple_name or apple_name in spotify_name) and (spotify_row['Artist name'].strip().lower() in apple_music_row['Artist'].strip().lower() or apple_music_row['Artist'].strip().lower() in spotify_row['Artist name'].strip().lower()):
            return True
        elif (spotify_name in apple_sort_name or apple_sort_name in spotify_name) and (spotify_row['Artist name'].strip().lower() in apple_music_row['Artist'].strip().lower() or apple_music_row['Artist'].strip().lower() in spotify_row['Artist name'].strip().lower()):
            return True
        elif spotify_row['Artist name'].strip().lower() in apple_music_row['Name'].strip().lower() or apple_music_row['Artist'].strip().lower() in spotify_row['Track name'].strip().lower():
            return True
        elif apple_music_row['Artist'].strip().lower() in spotify_row['Album'].strip().lower() or spotify_row['Artist name'].strip().lower() in apple_music_row['Album'].strip().lower():
            return True
        return False

    for i, spotify_row in spotify_df.iterrows():
        for j, apple_music_row in apple_music_df.iterrows():
            if are_same(spotify_row, apple_music_row): break
        else:
            unique_to_spotify.append(spotify_row[['Track name', 'Artist name']])

    for i, apple_music_row in apple_music_df.iterrows():
        for j, spotify_row in spotify_df.iterrows():
            if are_same(spotify_row, apple_music_row): break
        else:
            unique_to_apple.append(apple_music_row[['Name', 'Artist']])
    return unique_to_spotify, unique_to_apple
    
def check_shared(spotify_df: pd.DataFrame, apple_music_df: pd.DataFrame):
    unique_to_spotify , unique_to_apple = search_shared_tracks(spotify_df, apple_music_df)
    print('Unique to Spotify:')
    for i in unique_to_spotify:
        print(i['Track name'], 'by', i['Artist name'])
    print('---------------------------')
    print('Unique to Apple Music:')
    for j in unique_to_apple:
        print(j['Name'], 'by', j['Artist'])
    return []

if len(sys.argv) != 3:
    raise Exception('Usage: command <spotify_playlist_path> <apple_music_playlist_path>')

spotify_playlist_filepath = sys.argv[1]
apple_music_playlist_filepath = sys.argv[2]

# spotify_playlist = open(spotify_playlist_filepath)
if not os.path.exists(spotify_playlist_filepath):
    raise Exception('File not found. Check the path of Spotify playlist file!')

# apple_music_playlist = open(apple_music_playlist_filepath)
if not os.path.exists(apple_music_playlist_filepath):
    raise Exception('File not found. Check the path of the Apple Music playlist file!')

spotify_file_name, spotify_file_extension = os.path.splitext(spotify_playlist_filepath)
apple_file_name, apple_file_extension = os.path.splitext(apple_music_playlist_filepath)

if spotify_file_extension == Format.CSV.value:
    spotify_df = read_spotify_csv(spotify_playlist_filepath)
else:
    raise Exception('Spotify playlist file has to be in csv format.') #TODO: support more 

if apple_file_extension == Format.XML.value:
    apple_music_df = read_apple_music_xml(apple_music_playlist_filepath)
else: 
    raise Exception('Apple Music playlist file has to be in xml format.')



find_and_delete_duplicates(spotify_df, apple_music_df)

shared = check_shared(spotify_df, apple_music_df)