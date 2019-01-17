Modified BLIH
=============

Installation
------------

1) Clone or download this repository
2) Replace `blih_mod.py` with `/usr/bin/blih`

    If you have cloned the repository, you can do the following:
    1) `$ cd blih-modification`
    2) `$ sudo chmod a+x blih_mod.py`
    3) `$ sudo cp blih_mod.py /usr/bin/blih`
3) Try out one of the new functions ;-)

What is new?
------------

1) New 3-in-1 function, which creates, set permission `r` to `ramassage-tek` and downloads (clones) your new repository using just one line. Usage: `blih repository init <repository_name>` or `blih r init <repository_name>`. **(17.01.2019)**

1) Easier way to clone repository for Epitech git is just `$ blih repository clone <repository_name>` or `$ blih repository clone <repository_name> directory` - where `directory` is where you would like to put your repository. **(9.10.2018)**

    Example: `$ blih repository clone <repository_name> directory` will do the same as `$ git clone git@git.epitech.eu:/<username_name>/<repository_name>` directory. For more information read the git manual.

2) If you don't want to write your password all the time, you can use `-t` or `--token`. In this modification, you are able to write your password and BLIH will not ask it. **(9.10.2018)**

    Example: `$ blih -u <user_name> -t "password" ...` your password **must** be in single (`'`) **or** double quotes (`"`). 

3) Added shortcuts for most used commands. **(9.10.2018)**

    1) `blih repository ...` = `blih r`
    2) `blih r create ...` = `blih r c`
    2) `blih r info ...` = `blih r i`
    2) `blih r getacl ...` = `blih r ga`
    2) `blih r list ...` = `blih r l`
    2) `blih r setacl ...` = `blih r sa`
    2) `blih r clone ...` = `blih r git`

Reverting changes
-----------------

If something got wrong, or you want to go back to the original one just do the following:
1) `$ cd blih-modification`
2) `$ sudo chmod a+x blih_orig.py`
3) `$ sudo cp blih_orig.py /usr/bin/blih`

Post Scriptum
-------------

If you have any ideas to make this tool better and more convenient, do not hesitate to send your pull requests or open "New issue" tickets!

Post Post Scriptum
-------------

I am trying and experimenting with different opensource programs. I have 0 knowledge Python. But it is very interesting to learn in practice. Try once. 