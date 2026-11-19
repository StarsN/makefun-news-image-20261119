# news-image-20261119 — One Image, One Day
[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/StarsN/makefun-news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/StarsN/makefun-news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

[make.fun bounty: Sum up 19 November's world news in one image](https://make.fun/bounty/news-image-20261119)

A newspaper front page for **Thursday 19 November 2026**, drawn entirely
from code by a small Python program — standard library only, no network,
no downloaded assets. Every pixel is computed at run time from a
hand-written 5×7 bitmap font and plain geometry, so the output is fully
deterministic: run it twice, get the same bytes.

## The image

- **Top story:** Trump, Xi Jinping and Putin hold the first-ever
  trilateral summit in Shenzhen, on the sidelines of the APEC summit —
  the leaders of the three biggest nuclear powers meet at Kylin Villa,
  with nuclear arms control, Ukraine and Iran on the agenda.
- **Also in the picture:** three oil tankers catch fire after hitting
  mines in the Strait of Hormuz; the Crimean Bridge is attacked again as
  Russia and Ukraine trade bridge strikes; Grand Theft Auto VI launches
  worldwide after a 13-year wait to near-perfect reviews; a Van Gogh
  sells for a record $190.4 million after a row over its Nazi-era
  history; the World Court rules on Myanmar and the Rohingya; Claude
  maker Anthropic is poised for a $1.4 trillion stock market debut;
  Israeli tanks cross the Gaza ceasefire line in a rare incursion; and
  NASA's Voyager 1 reaches the one light-day milestone.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `entry.png` (1024×1024, about 22 KB) into `MAKEFUN_OUTPUT_DIR`,
or into `/output` when that directory exists, else `./out`.

## How it works

- `main.py` — everything in one file: the 5×7 bitmap font, a tiny
  software rasteriser (rects, lines, circles, polygons, stars), the
  front-page scene (masthead, summit scene, eight news panels) and a
  minimal PNG encoder built on `zlib` and `binascii.crc32`.

Python 3 standard library only; nothing is installed and nothing is
fetched.
