import json
import scrap_stores


def main():
    with open('files/clients.json', 'r') as clients_handle:
        clients_data = json.load(clients_handle)

    client_names = clients_data.keys()
    for client in client_names:

        try:
            scrap_stores.main(client)
        except Exception as E:
            print(E)
            continue


if __name__ == '__main__':
    main()
