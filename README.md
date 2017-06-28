# Another attract mode scrapper
I wanted to update the artwork in my attract mode install but 
i didnt found a reliable scrapper that got me the snaps and marquee
so I wrote one that uses http://screenscraper.fr api.


# Install Instructions
```bash
sudo easy_install virtualenv
```
or even better:
```bash
$ sudo pip install virtualenv
```
One of these will probably install virtualenv on your system. Maybe it’s even in your package manager. If you use Ubuntu, try:

```bash
$ sudo apt-get install python-virtualenv
```

Once you have virtualenv installed, just fire up a shell and create your own environment:

```bash
$ mkdir at_scrapper
$ cd myproject
$ virtualenv venv
```

Now we just need to activate the new env.

```bash
$ . venv/bin/activate
```

Once in the new environment we can install the scrapper

```bash
at_scrapper $ git clone repo app
at_scrapper $ cd app
at_scrapper $ pip install -e
```

And thats it!

Now you can start using the scrapper, remember that you need to activate your environment
or you need to call the scrapper bin that is installed in the venv/bin folder

# Usage

```bash
Usage: attract_scrapper scrap [OPTIONS] ROMSDIR SCRAPERDIR

  Get requested metadata for all roms

Options:
  --system TEXT     System Name, default fba.
  --listfile TEXT   Write the meta data to this gamelist file. (Should be something like ~/.attract/romlist/Final Burn Alpha.txt)
  --overwrite TEXT  If enabled It will overwrite snaps, marquees, and wheels,
                    if disabled only listfile will be updated
  --help            Show this message and exit.
```

# Example

```bash
(venv) ivan@taco:~ $ attract_scrapper scrap --listfile ~/.attract/romlists/Final\ Burn\ Alpha.txt ~/roms/fba/ ~/roms/fba/
Procesing ROM 1944.zip
Found 1944: The Loop Master
Downloading marquee for 1944: The Loop Master
Downloading video for 1944: The Loop Master
Downloading wheel for 1944: The Loop Master
Procesing ROM armwaru.zip
Found Armored Warriors
Downloading marquee for Armored Warriors
Downloading video for Armored Warriors
Downloading wheel for Armored Warriors
```