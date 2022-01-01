from bot import Bot
import keep_alive

def main():
    bot = Bot()
    print("launcher# running bot.")
    bot.run()
    

if __name__ == "__main__":
    keep_alive.keep_alive()
    main()