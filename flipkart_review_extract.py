import requests
import sys
import urllib2
import httplib
import re
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import urllib2
import bs4
from bs4 import BeautifulSoup


def findItem(itemName):
    #itemName=itemName.replace(" ", "+")
    itemName=urllib2.quote(itemName)
    print itemName
    link = 'http://www.flipkart.com/search?q={0}&as=off&as-show=off&otracker=start'.format(
        itemName)
    print link
    r = urllib2.Request(link, headers={"User-Agent": "Python-urlli~"})
    try:
        response = urllib2.urlopen(r)
    except:
        print "Internet connection error"
        return
    thePage = response.read()
    soup = bs4.BeautifulSoup(thePage)
    
    firstBlockSoup = soup.find('div', attrs={'class': 'product-unit unit-4 browse-product new-design  quickview-required'})

    if not firstBlockSoup:
        firstBlockSoup = soup.find('div', attrs={'class': 'product-unit unit-4 browse-product new-design  quickview-required'})
        if not firstBlockSoup:
            print "Item Not Found"
            return

    print "Item found"
    return 1

def scrap_item(itemName):
   
    if(findItem(itemName)!=1):
        return False
    else:
        itemName.replace(" ", "+")
        link = 'http://www.flipkart.com/search?q={0}&as=off&as-show=off&otracker=start'.format(
                itemName)
        r = requests.get(link)
        soup = BeautifulSoup(r.text)
        divs=soup.find('div',{'class':'pu-visual-section'})
        product_link=divs.find('a').get('href')
        main_product_link='http://www.flipkart.com{}'.format(product_link)
        return main_product_link
def scrap_reviews(main_product_link):
    url=main_product_link
    r1 = requests.get(url)
    soup = BeautifulSoup(r1.text)
    divs=soup.find('div',{'class':'reviewListBottom'})
    if not divs:
        divs=soup.find_all('div',{'class':'bigReview'})
        for div in divs:
            n=div.find('span',{'class':'review-text'}).text.encode('utf-8')
    
    # print "Name of reviewer : "+str(name)+"\n"+"Review : "+str(n)
            print str(n)+"\n"
    
    else:
        more_reviews(divs)


def more_reviews(divs):
    url_to_all_reviews=divs.find('a').get('href')
    visit_url='http://www.flipkart.com{}'.format(url_to_all_reviews)
    flag=1
    visit_url=visit_url[:len(visit_url)]
    
    k=0
    while(flag==1):
        
        # visit_url=visit_url+str(k)
        r = requests.get(visit_url)
        soup = BeautifulSoup(r.text)
        divs=soup.find_all('div',{'class':'fclear fk-review fk-position-relative line '})
    
        for div in divs:
    
    # name=div.find('div',{'class':'userimg'}).find('span',{'class':'reviewUserName'})
            n=div.find('div',{'class':'lastUnit size4of5 section2'}).find('span',{'class':'review-text'}).text.encode('utf-8')
    
    # print "Name of reviewer : "+str(name)+"\n"+"Review : "+str(n)
            print str(n)+"\n"
        div2=soup.find_all('div',{'class':'fk-navigation fk-text-center tmargin10'})

        #print div2
        if k==0:
            for div in div2:
                div3=div.find('span',{'class':'nav_bar_result_count'}).text.encode('utf-8')
                visit_url=div.find('a').get('href')
                visit_url='http://www.flipkart.com{}'.format(visit_url)
            num=int(div3.split()[0].replace(",",""))
            n2=num%10
            num=num-n2
            # print num
            # print visit_url
        
        # print num
        elif k>100 and k<=1000:
            
            visit_url=visit_url[:len(visit_url)-3]

            # print visit_url
        elif k>1000 and k<=10000:
            visit_url=visit_url[:len(visit_url)-4]    
        elif k>10000 and k<=100000:
            visit_url=visit_url[:len(visit_url)-5]
        else:
            visit_url=visit_url[:len(visit_url)-2]
        # print div2
        if k<=num and k!=0:
            visit_url=visit_url+str(k)
            k=k+10
            # print visit_url
        elif(k==0):
            k=k+10
            pass
        else:
            flag=0


def main():
    #Enter the product name
    link=scrap_item("dgb wireless mouse")
    # print link
    scrap_reviews(link)

if __name__ == '__main__':
    main()







