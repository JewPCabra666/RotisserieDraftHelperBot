import json

with open('people.json', 'r') as jsonfile:
    people = json.load(jsonfile)
    # print(people)


class Person(object):
    def __init__(self, name):
        self.name = name
        self.column = people[name]["column"]
        self.alias = people[name]["alias"]
        self.id = people[name]['id']

    def __str__(self):
        return f'[\n  name - {self.name}\n  alias - {self.alias}\n  id - {self.id}\n  column - {self.column}\n]'


def get_people():
    people_list = []
    for name in people:
        people_list.append(Person(name))
    return people_list


def get_cards():
    cards = []
    with open('CommanderCubeRotisserie.txt', 'r') as readfile:
        for line in readfile:
            cards.append(line.strip())
    return cards


def main():
    for person in get_people():
        print(person)


if __name__ == '__main__':
    main()
