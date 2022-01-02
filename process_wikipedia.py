
import pandas as pd
import colorama, re
from colorama import Fore, Style
from typing import Tuple

def split_section(section: str) -> Tuple[str, str]:
    try:
        index = section.index(' ==')
    except ValueError:
        return section.lower(), ''
    
    title, body = section[:index].strip().lower(), section[index+3:].strip()
    return title, body

def main():
    colorama.init()
    print(Fore.MAGENTA + Style.BRIGHT + '\n--- Process Wikipedia Data Script ---\n')

    print(Fore.CYAN + '- Reading raw Wikipedia data file...')
    df = pd.read_json('data/wikipedia_raw.json', orient='records')

    for i in range(len(df)):
        article = df.loc[i, 'wp_article']

        if article:
            sections = list(map(lambda x: x.strip(), article.split('\n\n== ')))
            df.loc[i, 'introduction'] = sections[0]

            sections = dict(map(split_section, sections[1:]))

            # Remove section headers and strip newlines
            process_body = lambda b: re.sub('=== .* ===', '\n', b).strip()

            if 'gameplay' in sections:
                df.loc[i, 'gameplay'] = process_body(sections['gameplay'])

            synopsis = None
            if 'synopsis' in sections:
                synopsis = process_body(sections['synopsis'])
            elif 'plot' in sections:
                synopsis = process_body(sections['plot'])

            df.loc[i, 'synopsis'] = synopsis

    df.drop('wp_article', axis=1, inplace=True)

    print(Fore.CYAN + '- Writing processed data to new JSON file...')
    df.to_json('data/wikipedia.json', orient='records')
    print(Fore.GREEN + '\nDone.\n' + Style.RESET_ALL)

if __name__ == '__main__':
    main()
