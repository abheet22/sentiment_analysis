from itertools import groupby 
from string import punctuation
from nltk.tag import pos_tag

import re
import re, collections
# s="Ultra Portable, Small Size Smart and Sturdy Feather and security light Easy transfer of all media files"
# s="power saving mode"
# f=open("review_flipkart_sandisk1.txt","r")
# for i in f:
# 	print pos_tag(i.split())


def func(str1):
	
	re.sub(r'\s*(\.*\s*)', ".", str1)
	if str1[0]=="." or str1[0]=="?" or str1[0]=="!" or str1[0]=="\," or str1[0]=="$":
		
		str1=str1[1:]
		return str1
	else:
		# print str1
		return str1

def remove_rep(str1):
    
    punc=["."]
    punc2=set(punctuation)-set(punc)-set(["/"])
    abrre=["prof", "org", "pvt","dr", "ltd", "gov","mr","mrs","st","ms","sr","jr","est","fig","hrs","inc","mt","no","oz","sq"]

    check_punc=set(punctuation)
    c=0

    ap=1
    str_final=""
    pre=[]
    if not str1.startswith("http:"):
        
        newtext = []
        for k, g in groupby(str1):
            if k in punc:
                
                newtext.append(k)
                
            elif k in punc2:
                if ap==0:
                    newtext.append(" ")
                    ap=1
                else:
                    pass
            else:	
                newtext.extend(g)
                ap=1
        s="".join(newtext)
        if re.findall(r'.*([0-9]\.)[^0-9]',s):
            print "1"
            s=re.sub(r'([0-9]\.)'," ",s)
            if(s[0]==" "):
                s=s[1:]
            # s2=re.sub(r'[mM][bB](\/)\s*[sS]',"MBps",s1)

            #re.findall(r'\w+(\/)\w+',s1,re.I):
        if re.findall(r'([^mM][^bB]\/)',s,re.I):
            print "true"
            s=re.sub(r'([^mM][^bB]\/)'," or ",s)
            pre.append(s)
        else:
            pre.append(s)
        
        # else:
        # 	pre.append(s)
        

        # s2=re.sub(r'(\/)',"p",s1,re.I)
    
        
    else:
        pass
    str_final =" ".join(pre)
    
    str_final=func(str_final)
    return str_final.replace("."," . ")

	# print pre



	# tagged_reviews = pos_tag(list3)
	# print tagged_reviews

		

