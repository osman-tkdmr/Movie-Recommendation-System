import json
import glob

def transform(records):
    output = {}
    for record in records:
        imdb_id = record.pop('imdb_id')
        for section in ['movie_results', 'person_results', 'tv_results', 'tv_episode_results', 'tv_season_results']:
            items = record.get(section, [])
            cleaned = []
            for item in items:
                if 'genre_ids' in item and isinstance(item['genre_ids'], list) and len(item['genre_ids']) == 1:
                    item['genre_ids'] = item['genre_ids'][0]
                for field in ['vote_average', 'vote_count', 'production_code', 'runtime', 'episode_number', 'season_number', 'show_id']:
                    if field in item:
                        val = item[field]
                        if isinstance(val, str) and val.isdigit():
                            item[field] = int(val)
                        elif isinstance(val, float) and val.is_integer():
                            item[field] = int(val)
                cleaned.append(item)
            record[section] = cleaned
        output[imdb_id] = record
    return output

if __name__ == '__main__':
    combined_data = {}

    for filepath in glob.glob('./Moppie*/scrapping/data.json'):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            records = [json.loads(line) for line in lines if line.strip()]
            transformed = transform(records)
            combined_data.update(transformed)
            print(f"Processed: {filepath}")
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    with open('output.json', 'w', encoding='utf-8') as out_f:
        json.dump(combined_data, out_f, ensure_ascii=False, indent=4)

    print("\n✅ All IMDb records successfully written to output.json")
