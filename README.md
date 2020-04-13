NASM Scraper script
===================

A quick and dirty script for extracting contact info from the NASM members list.
We use this script once a year and so it is about as well-maintained as you would expect from that.

This script only runs on a *Mac* running the Safari web browser (which is built into all Mac OS releases).
It has been tested on Mac OS Mojave 10.14.6, with the built-in version of Python (2.7.16).
(The script would need minor adjustments to work with a different OS, browser, or Python 3.)

Installing
----------

First, follow these instructions to download the code and install prerequisites:

1. Open the "Terminal" Application (to find it, you can click the magnifying glass icon in the top right corner of the screen and type "terminal".)
2. Type (or copy & paste) the following lines, with each line followed by the Return/Enter key.
```
     git clone https://github.com/bostonchoral/nasm-spammer.git
     cd nasm-spammer
     ./install
```

> NOTE: You might see the message:
> ```
>      DEPRECATION: Python 2.7 will reach the end of its life on January 1st, 2020.
> ```
> You can ignore this message, even if it's after 2020. (Apple has ignored it for years; why shouldn't you?)


Second, you need to enable remote control for Safari (by default, Safari doesn't allow scripts to control it, which is a good thing). To do it:

1. Open Safari. (If it isn't in your dock, click the magnifying glass icon in the top right corner of the screen and type "safari".)
2. In the "Safari" menu at the top left of the screen, choose "Preferences".
3. Click the "Advanced" tab.
4. Check "Show Develop menu in menu bar".
5. In the "Develop" menu, enable "Allow Remote Automation".


Running
-------

1. Open the "Terminal" application.
2. Type `cd ~/nasm-spammer` and hit Return/Enter. (If you're already in the same terminal window you used before, you don't have to do this.)
3. Type `./run` and hit Return/Enter.

The script will ask you for the NASM username (i.e. the email address associated with the account) and password. Get these from someone who knows them.

Once you have entered the account info, the web scraper will launch a Safari window with an orange title bar (to
indicate that it's being remote controlled). **It's very important for you not to click on or type in this window.** 
You can move the window around, or hide it... but if you try to interact with it, a box will pop up telling you that
the session is remote controlled. You must click "Continue Session" to let the script continue to run - otherwise it
will stop.

The script will take several hours to run. It intentionally pauses after fetching each page, to make sure that it
doesn't overwhelm the NASM web site. During this time, you should leave your Mac plugged in. 
You'll see the script's progress with messages in the Terminal window, and you'll see it fetching new pages in the remote-controlled 
web browser about twice a minute or so.

To stop the script, bring the Terminal window to the front and hold the Control key while pressing "c".
If the script gets interrupted for any reason, just type `./run` in the Terminal window to run it again - it will resume from wherever it left off, so you won't lose progress.

If your Mac gets turned off and you lose the terminal window, just repeat the steps at the top of this section to resume.

**DEALING WITH ERRORS:** If the script stops because of an error, try to run it again using `./run`. Chances are, it was just a blip, and it'll pick up from where it left off.
If the script stopped with the browser window open, you need to close the browser window before it will work again. Safari will ask if you really want to stop the remote-controlled session;
click the "Stop Session" button to confirm.


Output
------

The script's output file is named `contacts.tsv`. It's in TSV (tab-separated values) format, which you can easily import into Excel or Google Sheets.

You can find the file by going to your home folder, then to the `nasm-spammer` folder within it. You should see `contacts.tsv` there.

If you don't know how to get to your home folder:

* Click the Finder icon on your Dock.
* Open the "Go" menu and choose "Home".
* Double-click the "nasm-spammer" folder in that window. The `contacts.tsv` file should be in it.
* You can drag the "contacts.tsv" file into Excel's "Open" dialog box (or Google Sheets' "Upload" dialog box) to open it.

Each row lists the following information in columns (separated by tab characters):

* The name of the institution.
* The URL of the institution's page on the NASM site.
* The URL of the institution's own web page.
* The name of the contact person at the institution.
* The person's title and department (if listed).
* The person's email address.

If there is more than one contact person for a given institution, they will appear in multiple rows for that institution.


Uninstalling
------------

To disable remote control for Safari:

1. Open Safari.
2. In the "Develop" menu, disable "Allow Remote Automation".
3. In the "Safari" menu at the top left of the screen, choose "Preferences".
4. Click the "Advanced" tab.
5. Uncheck "Show Develop menu in menu bar".

To uninstall the script and its folder:

1. Click the Finder icon in your Dock.
2. In the "Go" menu, choose "Home".
3. Among the files, you should see a folder named `nasm-spammer`. Drag it to the trash.




