from tabulate import tabulate

def select_city():
    cities = [["Warszawa"],
              ["Krakow"],
              ["Lodz"],
              ["Wroclaw"],
              ["Poznan"],
              ["Gdansk"],
              ["Szczecin"],
              ["Bydgoszcz"],
              ["Lublin"],
              ["Bialystok"],
              ["ALL"]]

    print(tabulate(cities,
                   showindex="always",
                   headers=["index", "nazwa miasta"],
                   tablefmt="pretty"))

    val = input("Prosze wybrac index miasta / miast: ")
    input_numbers = [int(i) for i in val.split(' ') if i.isdigit()]

    if len(input_numbers) > 1:
        cashe_list = []
        for i in input_numbers:
            cashe_list.append(cities[i][0])
        cities_str = ", ".join(cashe_list)
        print("Wybrane miasta: " + cities_str)
        return cashe_list

    elif input_numbers == [10]:
        print("Wybrane wszystkie miasta")
        all_cities = ["Warszawa", "Krakow", "Lodz", "Wroclaw",
                      "Poznan", "Gdansk", "Szczecin", "Bydgoszcz",
                      "Lublin", "Bialystok"]
        return all_cities

    else:
        print("Wybrane miasto: " + cities[int(val)][0])
        i = cities[int(val)]
        return i