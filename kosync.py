import json
import urllib.request


class KoreaderSync:
    def __init__(self, user, hashed_key,
                 server='https://sync.koreader.rocks:443'):
        self.user = user
        self.hashed_key = hashed_key
        self.server = server

    def healthcheck(self):
        request = urllib.request.Request(
            url=self.server + '/healthcheck',
            headers={
                'accept': 'application/vnd.koreader.v1+json',
            },
            method='GET'
        )

        opened_request = urllib.request.urlopen(request)
        response = json.loads(opened_request.read())

        return response

    def authorize(self):
        request = urllib.request.Request(
            url=self.server + '/users/auth',
            headers={
                'accept': 'application/vnd.koreader.v1+json',
                'x-auth-user': self.user,
                'x-auth-key': self.hashed_key,
            },
            method='GET'
        )

        opened_request = urllib.request.urlopen(request)
        response = json.loads(opened_request.read())

        return response

    def get_progress(self, document_hash):
        request = urllib.request.Request(
            url=self.server + '/syncs/progress/' + document_hash,
            headers={
                'accept': 'application/vnd.koreader.v1+json',
                'x-auth-user': self.user,
                'x-auth-key': self.hashed_key,
            },
            method='GET'
        )

        opened_request = urllib.request.urlopen(request)
        response = json.loads(opened_request.read())

        return response


if __name__ == '__main__':
    with open('KOReader Sync.json', mode='r') as config_file:
        config = json.load(config_file)

    koreader_sync = KoreaderSync(
        config['user'],
        config['hashed_key'],
        config['server']
    )

    print('healthcheck:')
    print(koreader_sync.healthcheck())
    print()
    print('authorize:')
    print(koreader_sync.authorize())
    print()
    print('get_progress:')
    # This is the MD5 hash of an actual EPUB I have synced:
    print(koreader_sync.get_progress('17d3391d853ede55f8bc597d548df734'))
    print()
