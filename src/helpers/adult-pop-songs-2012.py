# Processing by hand for manual list

output_file = 'adult-pop-songs-2012.json'
genre_data = {}
genre = 'pop'
cntr = 0
with open('adult-pop-songs-2012.txt') as f:
    for line in f:
        line = line.strip()
        idx, name = line.split('.', maxsplit=1)
        artist, song = name.replace(' f/', ' Featuring ').split(':')

        genre_data[str(cntr)] = [artist.strip(), song.strip(), genre]
        cntr += 1

import json
print('Len: ', len(genre_data))
json.dump(genre_data, open(output_file, 'w'), indent=4)
print('Writing to: "{}"'.format(output_file))