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
                   headers=["Index", "City name"],
                   tablefmt="pretty"))

    val = input("Please select city index / indices: ")
    input_numbers = [int(i) for i in val.split(' ') if i.isdigit()]

    if len(input_numbers) > 1:
        cashe_list = []
        for i in input_numbers:
            cashe_list.append(cities[i][0])
        cities_str = ", ".join(cashe_list)
        print("Chosen cities: " + cities_str)
        return cashe_list

    elif input_numbers == [10]:
        print("All cities were chosen!")
        all_cities = ["Warszawa", "Krakow", "Lodz", "Wroclaw",
                      "Poznan", "Gdansk", "Szczecin", "Bydgoszcz",
                      "Lublin", "Bialystok"]
        return all_cities

    else:
        print("Chosen city: " + cities[int(val)][0])
        i = cities[int(val)]
        return i