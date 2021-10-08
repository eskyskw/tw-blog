import twint
import os
import pandas as pd
import datetime
import sys
import time

# 検索するアカウントのIDと期間、2つのファイル名を入力
acount = "Rocomoting"   #ex) @search_id
start = "2021-08-12"  #ex) 2020-08-15
end = "2021-08-13"    #ec) 2021-08-22 04:15:22

csvfile = "tmppp.csv"
htmlfile = "tw-links.txt"

# TWINTに必要な情報を読み込ませる
c = twint.Config()
c.Search = 'from:'+acount
c.Store_csv = True
c.Output = csvfile
c.Since = start
c.Until = end
nowPath = os.getcwd()
tmpPath = nowPath+'/'+csvfile
if(os.path.exists(tmpPath)): os.remove(tmpPath)

def jisa(sd, td):   #時差を計算する関数。多分もっとスマートな方法がある
                    #sd:"0000-00-00 00:00:00", td:"+00:00", JSTの場合td="+09:00"
    if(td[0] != '+' and td[0] != '-'): td = '+'+td
    d = datetime.datetime.strptime(sd+td, "%Y-%m-%d %H:%M:%S%z")
    d_just = d.astimezone(datetime.timezone.utc)
    return d_just.strftime('%Y-%m-%d %H:%M:%S')

hoji = ""   # Twitter社の機嫌によってはスクレイピングが上手くいかないため、その場合の保険として
flag = True # 2連続でhoji != last[1]がFalseでない限りスクレイピングを続ける仕様とした。

# whileループ内でtwintを実行
while(True):
    twint.run.Search(c)
    if(os.path.exists(tmpPath)):
        df = pd.read_csv(tmpPath, header=0, usecols=["created_at", "link"])
        last = df.tail(1).values[0]
        if(flag or hoji != last[1]):
            c.Until = jisa(last[0][0:-4], "09:00")  # csvの末尾の時刻を再度c.Untilに代入
            flag = hoji != last[1]
            hoji = last[1]
            if(not flag): print("try again")
            else: print(df.tail(1).values[0])
        else:
            print("According to Twitter, there are no more tweets.")
            break
    else:   # 初手からTwitter社の機嫌が悪い場合
        if(not flag):   # 初手と二手目にTwitter社の機嫌が悪い場合、スクレイピングを中止
            print("Sorry, this query may be wrong.")
            sys.exit()
        flag = False
        print("try again")
    time.sleep(5)   # 祈りの時間

# csvから必要な情報(url)を抽出
links = pd.read_csv(tmpPath, header=0, usecols=["link"])

# urlをいい感じに整形しhtmlfileに書き込む
str1 = '<!-- wp:embed {"url":"'
str2 = '","type":"rich","providerNameSlug":"twitter","responsive":true,"className":""} --> <figure class="wp-block-embed is-type-rich is-provider-twitter wp-block-embed-twitter"><div class="wp-block-embed__wrapper">'
str3 = '</div></figure> <!-- /wp:embed -->'

f = open(htmlfile, 'w')
for link in reversed(links.values): #最新ツイートから取得されるため、csvの逆順で出力
    f.write(str1+link[0]+str2+link[0]+str3 + '\n')
f.close()
print("\nAll tweet's urls are saved in {}.\n".format(htmlfile))

