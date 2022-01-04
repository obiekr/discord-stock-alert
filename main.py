from bot import Bot
import keep_alive
import chromedriver_autoinstaller
import os, shutil

def installChromeDriver():
    path = chromedriver_autoinstaller.install(cwd=True)
    chromePath = os.path.join(os.path.expanduser("~"), ".tv_datafeed/")
    if not os.path.exists(chromePath):
        os.mkdir(chromePath)
    chromePath = os.path.join(chromePath, "chromedriver" + (".exe" if ".exe" in path else ""))
    shutil.copy(path, chromePath)
    print("Chromedriver Installed")

def main():
    bot = Bot()
    print("launcher# running bot.")
    bot.run()
    

if __name__ == "__main__":
    installChromeDriver()
    keep_alive.keep_alive()
    main()


