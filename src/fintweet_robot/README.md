# Development

## Prerequisites

* anaconda 3
* chrome

## Setup:

1. `conda env create -f scraping_env.yml`

```yaml
# File contents
name: scraper
channels:
  - defaults
dependencies:
  - ca-certificates=2021.4.13=hecd8cb5_1
  - certifi=2020.12.5=py39hecd8cb5_0
  - libcxx=10.0.0=1
  - libffi=3.3=hb1e8313_2
  - ncurses=6.2=h0a44026_1
  - openssl=1.1.1k=h9ed2024_0
  - pip=21.0.1=py39hecd8cb5_0
  - python=3.9.0=h88f2d9e_2
  - readline=8.1=h9ed2024_0
  - setuptools=52.0.0=py39hecd8cb5_0
  - sqlite=3.35.4=hce871da_0
  - tk=8.6.10=hb0a8c7a_0
  - tzdata=2020f=h52ac0ba_0
  - wheel=0.36.2=pyhd3eb1b0_0
  - xz=5.2.5=h1de35cc_0
  - zlib=1.2.11=h1de35cc_3
  - pip:
    - beautifulsoup4==4.9.3
    - bs4==0.0.1
    - chromedriver-autoinstaller==0.2.2
    - lxml==4.6.3
    - pytz==2021.1
    - schedule==1.1.0
    - selenium==3.141.0
    - soupsieve==2.2.1
    - urllib3==1.26.4
```

2. `conda activate scraper`

## Local Package Install

```bash
python -m pip install fintweet-robot
```
