import time
import IBEXMapper


def main() -> None:
    IBEXMapper.generateMapFromLink("t2010_02.txt", 400, 30)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (round(time.time() - start_time, 2)))
