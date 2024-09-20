import json

def cyrillic_to_latin(text, osisana=False):
    transliteration_map = {
        '\u0410': 'A', '\u0411': 'B', '\u0412': 'V', '\u0413': 'G', '\u0414': 'D', '\u0402': 'Đ',
        '\u0415': 'E', '\u0416': 'Ž', '\u0417': 'Z', '\u0418': 'I', '\u0408': 'J', '\u041A': 'K',
        '\u041B': 'L', '\u0409': 'Lj', '\u041C': 'M', '\u041D': 'N', '\u040A': 'Nj', '\u041E': 'O',
        '\u041F': 'P', '\u0420': 'R', '\u0421': 'S', '\u0428': 'Š', '\u0422': 'T', '\u040B': 'Ć',
        '\u0423': 'U', '\u0424': 'F', '\u0425': 'H', '\u0426': 'C', '\u0427': 'Č', '\u040F': 'Dž',

        '\u0430': 'a', '\u0431': 'b', '\u0432': 'v', '\u0433': 'g', '\u0434': 'd', '\u0452': 'đ',
        '\u0435': 'e', '\u0436': 'ž', '\u0437': 'z', '\u0438': 'i', '\u0458': 'j', '\u043A': 'k',
        '\u043B': 'l', '\u0459': 'lj', '\u043C': 'm', '\u043D': 'n', '\u045A': 'nj', '\u043E': 'o',
        '\u043F': 'p', '\u0440': 'r', '\u0441': 's', '\u0448': 'š', '\u0442': 't', '\u045B': 'ć',
        '\u0443': 'u', '\u0444': 'f', '\u0445': 'h', '\u0446': 'c', '\u0447': 'č', '\u045F': 'dž',
    }
    osisana_transliteration_map = {
        '\u0410': 'A', '\u0411': 'B', '\u0412': 'V', '\u0413': 'G', '\u0414': 'D', '\u0402': 'Dj',
        '\u0415': 'E', '\u0416': 'Z', '\u0417': 'Z', '\u0418': 'I', '\u0408': 'J', '\u041A': 'K',
        '\u041B': 'L', '\u0409': 'Lj', '\u041C': 'M', '\u041D': 'N', '\u040A': 'Nj', '\u041E': 'O',
        '\u041F': 'P', '\u0420': 'R', '\u0421': 'S', '\u0428': 'S', '\u0422': 'T', '\u040B': 'C',
        '\u0423': 'U', '\u0424': 'F', '\u0425': 'H', '\u0426': 'C', '\u0427': 'C', '\u040F': 'Dz',

        '\u0430': 'a', '\u0431': 'b', '\u0432': 'v', '\u0433': 'g', '\u0434': 'd', '\u0452': 'dj',
        '\u0435': 'e', '\u0436': 'z', '\u0437': 'z', '\u0438': 'i', '\u0458': 'j', '\u043A': 'k',
        '\u043B': 'l', '\u0459': 'lj', '\u043C': 'm', '\u043D': 'n', '\u045A': 'nj', '\u043E': 'o',
        '\u043F': 'p', '\u0440': 'r', '\u0441': 's', '\u0448': 's', '\u0442': 't', '\u045B': 'c',
        '\u0443': 'u', '\u0444': 'f', '\u0445': 'h', '\u0446': 'c', '\u0447': 'c', '\u045F': 'dz',
    }
    if not osisana:
        return ''.join(transliteration_map.get(char, char) for char in text)
    return ''.join(osisana_transliteration_map.get(char, char) for char in text)

db = None

with open("db.json", 'r') as f:
    data = json.loads(f.read())
    default = data['_default']
    for i in range(len(default.keys())):
        curr = default[f'{i+1}']
        curr['category'] = cyrillic_to_latin(curr['category'])

    db = data

with open("db.json", 'w') as f:
    f.write(json.dumps(data))