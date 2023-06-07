import os
import json
import requests
from tqdm import tqdm

class VK:

    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def check_folder(self, path_folder):
        if not os.path.exists(path_folder):
            os.makedirs(path_folder)
            print(f'Папка {path_folder} успешно создана.')
        else:
            print(f'Папка {path_folder} уже существует.')



    def user_info(self):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def save_photo(self, path=None):
        if path is None:
            path = r"{}".format(input("Пожалуйста, введите абсолютный путь папки компьютера, в которую хотите сохранить информацию:"))
            self.check_folder(path)
        id = self.user_info()
        real_id = id['response'][0]['id']
        url = 'https://api.vk.com/method/photos.get'

        photos_place = int(input("""Введите цифру, соответствующую запросу:
        1 - фотографии со стены
        2 фотографии профиля
        3 - сохранненые фотографии\n"""))

        d_number = {1:'wall', 2:'profile', 3:'saved'}

        params = {'owner_id': real_id, "album_id": d_number[photos_place], "extended": '1'}
        response = requests.get(url, params={**self.params, **params})
        info = response.json()['response']['items']
        path_to_file = os.path.join(path, f"{real_id}.json")
        lst = [{i:j for i,j in _.items() if i != 'sizes'} for _ in info]
        if not os.path.exists(path_to_file):  # создаем json файл с информацией о фотографиях
            with open(path_to_file, "w") as file:
                json.dump(lst, file)
                print(f"JSON-файл {path_to_file} успешно создан.")
        else:
            print(f"JSON-файл {path_to_file} уже существует.")
        dct = {x['likes']['count']: x["sizes"][ -1]["url"] for x in info}
        for i, j in tqdm(dct.items(), desc='Загрузка в папку', unit='файл'):  # сохраняем каждую фотографию в папку на локальном компьютере
            response = requests.get(j)
            if response.status_code == 200:
                save_path = os.path.join(path, f'{i}.jpg')
                with open(save_path, 'wb') as file:
                    file.write(response.content)
            else:
                print('Ошибка при загрузке фотографии')

with open('tokenVK.txt', 'r') as f:  # файл с токеном
    access_token = f.readline()
    user_id = input('Введите id пользователя:')
    vk = VK(access_token, user_id)
    vk.save_photo()

class Yandex:

    def __init__(self, token: str, ):
        self.token = token

    def creat_folder(self, folder_path):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {
            'Authorization': f'OAuth {self.token}'
        }
        params = {
            'path': folder_path
        }
        if requests.get(url, headers=headers, params=params).status_code == 200:
            print(f'Папка {folder_path} уже существует на диске, продолжаем загрузку.')
        elif requests.put(url, headers=headers, params=params).status_code == 201:
            print(f'Папка {folder_path} успешно создана!')
        else:
            print(f'Ошибка, папка не создана.')

    def upload(self, created_name=None, folder_path=None):
        if created_name == None:
            created_name = input('Пожалуйста, введите название папки, в которую хотите сохранить файл на YandexDisk:')
        self.creat_folder(created_name)
        if folder_path == None:
            folder_path = r"{}".format(input("Пожалуйста, введите абсолютный путь папки компьютера, файлы которой хотите сохранить:"))
        if os.path.isdir(folder_path):
            lst = os.listdir(folder_path)
            url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            headers = {
                'Authorization': f'OAuth {self.token}'
            }
            for i in tqdm(lst, desc='Загрузка на Яндекс.Диск', unit='файл'):
                params = {
                    'path': f'{created_name}/{i}',
                    "overwrite": 'true'
                }
                response = requests.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    upload_url = response.json()['href']
                    with open(os.path.join(folder_path, i), 'rb') as file:
                        upload_response = requests.put(upload_url, data=file)
                        if upload_response.status_code == 201:
                            continue
                        else:
                            print(f'Ошибка загрузки файла {i} на Яндекс.Диск.')
        print(f'Спасибо за обращение!')

# Пожалуйста, перед использованием приложения, копируйте Ваш токен яндекс диска в файл 'tokenYandexDisk.txt'
with open('tokenYandexDisk.txt', "r") as f1:
    token = f1.readline()
    ya = Yandex(token)
    ya.upload()




