from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import pandas as pd
import dataframe_image as dfi
from pandas.io.formats.style import Styler
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

def imageGen(urllist):
    bustable = []

    for url in urllist:
        errcount = 0
        while errcount<20:
            try:
                html = urlopen(url).read()
            except HTTPError:
                errcount += 1
            else:
                break
        soup = BeautifulSoup(html, features="html.parser")
        name = soup.find_all("div", {"class": "BusStation__name"})[0].text
        list = soup.find("ul")
        bustable.append([' ',name,' '])
        for li in list.find_all("li"):
            Numb=li.find_all("div", {"class": "Bus__number"})[0].text
            StName = li.find_all("div", {"class": "Bus__stopName"})[0].text
            buf = li.find_all("span", {"class": "Arrival__item"})
            ArrTime = []
            for minutes in buf:
                ArrTime.append(minutes.text.replace(' мин',''))
            bustable.append([Numb,StName,', '.join(ArrTime)])
    df = pd.DataFrame(bustable,columns=['№','Кон.','Мин.'])
    dfStyler = df.style.set_properties(**{'text-align': 'left'})\
                       .hide_index()\
                       .apply(highlight_col,axis=None)
    dfi.export(dfStyler,'out2.png')


def highlight_col(x):
    f = 'font-weight: bold'   
    m = x["№"] == ' '
    df1 = pd.DataFrame('', index=x.index, columns=x.columns)
    df1 = df1.mask(m, f)
    return df1