import click
import json
import py
import systems
import binascii
import requests
from urllib import urlretrieve
from urlparse import urlparse, parse_qs


class Config(dict):
    def __init__(self, *args, **kwargs):
        self.config = py.path.local(
            click.get_app_dir('attract_scrapper')
        ).join('config.json')  # A

        super(Config, self).__init__(*args, **kwargs)

    def load(self):
        """load a JSON config file from disk"""
        try:
            self.update(json.loads(self.config.read()))
        except py.error.ENOENT:
            pass

    def save(self):
        self.config.ensure()
        with self.config.open('w') as f:
            f.write(json.dumps(self))


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@pass_config
def cli(config):
    config.load()


def crc32_from_file(rom):
    buf = rom.open(mode='rb').read()
    buf = (binascii.crc32(buf) & 0xFFFFFFFF)
    return "%08X" % buf


def save_credentials(config):
    config['dev_id'] = click.prompt('Please enter a valid devid for https://www.screenscraper.fr', type=str)
    config['dev_password'] = click.prompt('Please enter password', type=str, hide_input=True)
    config.save()


def create_content_dirs(path):
    folders = ['snap', 'wheel', 'flyer', 'marquee']
    scrap_dir = py.path.local(path)
    if not scrap_dir.check():
        scrap_dir.mkdir()
        click.secho('Creating dir {}'.format(scrap_dir), fg='yellow')

    for f in folders:
        if not scrap_dir.join(f).check():
            scrap_dir.join(f).mkdir()
            click.secho('Creating dir {}'.format(scrap_dir), fg='yellow')


def get_roms(path):
    roms_path = py.path.local(path)
    return roms_path.listdir(sort=True)


def get_game_info(config, rom):
    crc = crc32_from_file(rom)
    payload = {'devid': config.get('dev_id'),
              'devpassword': config.get('dev_password'),
              'softname': 'zzz',
              'output': 'json',
              'crc': crc,
              'romnom': rom.basename
              }
    data = requests.get('https://www.screenscraper.fr/api/jeuInfos.php', params=payload)
    try:

        response = data.json()
        click.secho('Found {}'.format(response['response']['jeu']['nom']), fg='green')
        return response['response']['jeu']
    except ValueError:
        #click.secho('Rom {} not found with crc32, trying by name'.format(rom.basename), fg='magenta', bg='white')
        del payload['crc']
        data = requests.get('https://www.screenscraper.fr/api/jeuInfos.php', params=payload)
        response = data.json()
        click.secho('Found {}'.format(response['response']['jeu']['nom']), fg='green')
        return response['response']['jeu']
    except:
        click.secho('Error getting data for {} from screenscraper'.format(rom.basename), fg='red', blink=True)
        pass


def append_to_romlist(listfile, line, overwrite=False):
    rom_list_path = py.path.local(listfile)
    mode = 'w' if overwrite else 'a'
    list_file = rom_list_path.open(mode=mode, ensure=True)
    list_file.write(line+"\n")
    list_file.close()


def download(url, dest):
    try:
        urlretrieve(url, dest)
    except Exception as e:
        click.secho('An error ocurred to download {}'.format(dest), fg='red')
        pass

@cli.command()
@click.option('--system', default='fba', help='System Name, only tested with fba for now.')
@click.option('--listfile',  default='fba.txt', help='Write the meta data to this gamelist file.')
@click.option('--overwrite', default=False, help='If enabled It will overwrite snaps, marquees, and wheels, if disabled rom will be skipped')
@click.argument('romsdir', type=click.Path(exists=True))
@click.argument('scraperdir', type=click.Path(exists=False))
@pass_config
def scrap(config, system, listfile, overwrite, romsdir, scraperdir):
    """Get requested metadata for all roms"""
    if not config.get('dev_id') or not config.get('dev_password'):
        save_credentials(config)

    create_content_dirs(scraperdir)
    roms = get_roms(romsdir)

    if listfile:
        append_to_romlist(listfile, "#Name;Title;Emulator;CloneOf;Year;Manufacturer;Category;Players;Rotation;Control;Status;DisplayCount;DisplayType;AltRomname;AltTitle;Extra;Buttons", overwrite=True)

    for rom in roms:
        if rom.ext[1:] in systems.systems[system]['exts']:

            click.secho('Procesing ROM {}'.format(rom.basename), fg='cyan')
            data = get_game_info(config, rom)
            if data:
                if listfile:
                    try:
                        category = data.get('genres').get('genres_en')
                        category = category.pop(0)
                    except:
                        category = ''
                        pass

                    try:
                        date = data.get('dates').get('date_wor')
                    except:
                        date = ''
                        pass

                    append_to_romlist(listfile, '{name};{title};{emulator};;{year};{manufacturer};{category};{players};;;;;;;;;'.format(
                        name=rom.purebasename, title=data.get('nom'), emulator=systems.systems[system]['name'],
                        year=date, manufacturer=data.get('developpeur'), category=category,
                        players=data.get('joueurs'), ))

                if data.get('medias').get('media_marquee'):
                    click.secho('Downloading marquee for {}'.format(data.get('nom'), fg='blue'))
                    url_parts = urlparse(data.get('medias').get('media_marquee'))
                    qs = parse_qs(url_parts.query)
                    marquee_path = py.path.local(scraperdir).join('marquee').join(
                        '{}.{}'.format(rom.purebasename, qs.get('mediaformat').pop(0))).realpath()

                    download_or_not = False
                    if overwrite:
                        download_or_not = True
                    elif marquee_path.check():
                        download_or_not = False
                    else:
                        download_or_not = True

                    if download_or_not:
                        download(data.get('medias').get('media_marquee'), str(marquee_path))
                    else:
                        click.secho('Skipping marquee for {} because it already exists'.format(rom.basename), fg='yellow')


                if data.get('medias').get('media_video'):
                    click.secho('Downloading video for {}'.format(data.get('nom'), fg='magenta'))
                    url_parts = urlparse(data.get('medias').get('media_video'))
                    qs = parse_qs(url_parts.query)
                    video_path = py.path.local(scraperdir).join('snap').join(
                        '{}.{}'.format(rom.purebasename, qs.get('mediaformat').pop(0))).realpath()

                    download_or_not = False
                    if overwrite:
                        download_or_not = True
                    elif video_path.check():
                        download_or_not = False
                    else:
                        download_or_not = True

                    if download_or_not:
                        download(data.get('medias').get('media_video'), str(video_path))
                    else:
                        click.secho('Skipping video for {} because it already exists'.format(rom.basename), fg='yellow')

                try:
                    wheels = data.get('medias').get('media_wheels').get('media_wheel_eu')
                except:
                    wheels = False

                if wheels:
                    click.secho('Downloading wheel for {}'.format(data.get('nom'), fg='blue'))
                    url_parts = urlparse(data.get('medias').get('media_wheels').get('media_wheel_eu'))
                    qs = parse_qs(url_parts.query)
                    wheel_path = py.path.local(scraperdir).join('wheel').join(
                        '{}.{}'.format(rom.purebasename, qs.get('mediaformat').pop(0))).realpath()

                    download_or_not = False
                    if overwrite:
                        download_or_not = True
                    elif wheel_path.check():
                        download_or_not = False
                    else:
                        download_or_not = True

                    if download_or_not:
                        download(data.get('medias').get('media_wheels').get('media_wheel_eu'), str(wheel_path))
                    else:
                        click.secho('Skipping wheel for {} because it already exists'.format(rom.basename), fg='yellow')

if __name__ == '__main__':
    cli()
