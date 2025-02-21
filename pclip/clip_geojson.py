import requests,json,re,csv,os,subprocess,urllib3,getpass
from pprint import pprint
from os.path import expanduser
from urllib.request import Request, urlopen
from os.path import expanduser
from retrying import retry
from planet.api.utils import read_planet_json
os.chdir(os.path.dirname(os.path.realpath(__file__)))
planethome=os.path.dirname(os.path.realpath(__file__))
try:
        PL_API_KEY = read_planet_json()['key']
except:
        subprocess.call('planet init',shell=True)

CAS_URL='https://api.planet.com/compute/ops/clips/v1/'
headers = {'Content-Type': 'application/json',}
if not os.path.exists(os.path.join(planethome,'idl.csv')):
        with open(os.path.join(planethome,'idl.csv'),'w') as completed:
            writer=csv.writer(completed,delimiter=',',lineterminator='\n')
with open(os.path.join(planethome,'idl.csv')) as f:
    csv_f = csv.reader(f)
    value = len(list(csv_f))
    value=value-1
def retry_if_rate_limit_error(exception):
    """Return True if we should retry (in this case when it's a rate_limit
    error), False otherwise"""
    return isinstance(exception, RateLimitException)
@retry(
    wait_exponential_multiplier=1000,
    wait_exponential_max=10000,
    retry_on_exception=retry_if_rate_limit_error,
    stop_max_attempt_number=5)
def geojsonc(path=None,item=None,asset=None):
    with open(path) as f, open(os.path.join(planethome,"idl.csv"),'r') as f2,open(os.path.join(planethome,"urllist.csv"),'wb') as csvfile:
        geomloader = json.load(f)
        geom=geomloader['features'][0]['geometry']
        reader = csv.DictReader(f2)
        for i, line in enumerate(reader):
            item_id = line['id_no']
            data = r'{"aoi": '+str(geom)+r',"targets": [{"item_id": '+'"'+item_id+'"'+r',"item_type": '+'"'+item+'"'+r',"asset_type": '+'"'+asset+'"'+r'}]}'
            data2=str(data).replace("'",'"').replace('u"','"')
            try:
                    main=requests.post('https://api.planet.com/compute/ops/clips/v1/', headers=headers, data=data2, auth=(PL_API_KEY, ''))
                    if main.status_code==202:
                        URL=str(main.json()).split('_self')[1].split(',')[0].replace("': u","").replace(" ","").replace("'","")
                        content=main.json()
                        item_id=(content['targets'][0]['item_id'])
                        item_typ=(content['targets'][0]['item_type'])
                        asset_typ=(content['targets'][0]['asset_type'])
                        print("Clipping: "+(item_id+"_"+item_typ+"_"+asset_typ))

                        with open(os.path.join(planethome,"urllist.csv"),'a') as csvfile:
                            writer=csv.writer(csvfile,delimiter=',',lineterminator='\n')
                            writer.writerow([URL])
                    elif main.status_code==429:
                        URL=str(main.json()).split('_self')[1].split(',')[0].replace("': u","").replace(" ","").replace("'","")
                        content=main.json()
                        item_id=(content['targets'][0]['item_id'])
                        item_typ=(content['targets'][0]['item_type'])
                        asset_typ=(content['targets'][0]['asset_type'])
                        print("Clipping: "+(item_id+"_"+item_typ+"_"+asset_typ))
                        with open(os.path.join(planethome,"urllist.csv"),'a') as csvfile:
                            writer=csv.writer(csvfile,delimiter=',',lineterminator='\n')
                            writer.writerow([URL])
                    else:
                        print("Issues with: "+(item_id+"_"+item+"_"+asset)+" has error code "+str(main.status_code))
            except Exception as e:
                print("Could not process "+str(item_id+"_"+item+"_"+asset))
