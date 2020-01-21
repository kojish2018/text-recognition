
import requests, pdf2image
import base64
import json
from requests import Request, Session
from io import BytesIO
from PIL import Image, ImageEnhance
from pdf2image import convert_from_bytes
from google.cloud import storage
from googleapiclient.discovery import build


def visionapi(request):
    request_json = request.get_json()
    return request_json

def getCloudPdf(request):
    
    client = storage.Client()
    bucket = client.get_bucket('bucketName')
    global blob
    blob = bucket.get_blob(visionapi(request))
    global bytes
    bytes = blob.download_as_string()
    global pngFile
    pngFile = convert_from_bytes(bytes)

def implicit():
    from google.cloud import storage
    storage_client = storage.Client()
    buckets = list(storage_client.list_buckets())
    print(buckets)

def to_Png(request):
    global file
    file = visionapi(request)
    global count
    count = len(pngFile)
  

def pil_image_to_base64(pil_image):
    buffered = BytesIO()
    pil_image.save(buffered, format="PNG")
    str_encode_file = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return str_encode_file

#PILで開いた画像をCloud Vision APIに投げます
def recognize_image(pil_image,lang):
        str_encode_file = pil_image_to_base64(pil_image)
        str_url = "https://vision.googleapis.com/v1/images:annotate?key="
        str_api_key = "apiKey"
        str_headers = {'Content-Type': 'application/json'}
        str_json_data = {
            'requests': [
                {
                    'image': {
                        'content': str_encode_file
                    },
                    'features': [
                        {
                            'type': "DOCUMENT_TEXT_DETECTION",
                            'maxResults': 10
                        }
                    ],
                    'imageContext':{
                            'languageHints': lang
                    }
                }
            ]
        }

        obj_session = Session()
        obj_request = Request("POST",
                              str_url + str_api_key,
                              data=json.dumps(str_json_data),
                              headers=str_headers
                              )
        obj_prepped = obj_session.prepare_request(obj_request)
        obj_response = obj_session.send(obj_prepped,
                                        verify=True,
                                        timeout=60
                                        )
        
        print(str_encode_file)

        if obj_response.status_code == 200:
            jsonFile.append(obj_response.json())
            text = get_fullTextAnnotation(obj_response.text)
            return text

        else:
            return "error"

#返ってきたjsonデータの"fullTextAnnotation"部分のテキストを抽出します。
def get_fullTextAnnotation(json_data):
    text_dict = json.loads(json_data)
    try:
        text = text_dict["responses"][0]["fullTextAnnotation"]["text"]
        return text
    except:
        print(None)
        return None

def first_ocr():
    for num in range(0, count):
        global jsonFile 
        jsonFile = []
        pil_image = pngFile[num]
        print(recognize_image(pil_image,'ja'))    

       
    
def image_cut():

    def get_list(emlist):
        emlist = ['']*count
        for i in range(0,count):
            emlist[i] = []
        return emlist

    global List
    List = get_list("List")

    for num in range(0, count):
        image = pngFile[num]
        data = jsonFile[num]
        for text in data['responses'][0]['textAnnotations']:
            if text['description']== 'location1':
                x_sign = min([text['boundingPoly']['vertices'][0]['x'],text['boundingPoly']['vertices'][3]['x']])
                y_sign = min([text['boundingPoly']['vertices'][0]['y'],text['boundingPoly']['vertices'][1]['y']])
            elif text['description']== 'location2':
                x_tab = min([text['boundingPoly']['vertices'][0]['x'],text['boundingPoly']['vertices'][3]['x']])
                y_tab = min([text['boundingPoly']['vertices'][0]['y'],text['boundingPoly']['vertices'][1]['y']])


        List[num].append(image.crop((x_sign-285, y_sign-699, x_sign-180, y_sign-645))) 
        List[num].append(image.crop((x_sign-174, y_sign-709, x_sign+80, y_sign-645)))

        List[num].append(image.crop((x_sign-320, y_sign-640, x_sign-190, y_sign-580)))
        List[num].append(image.crop((x_sign-108, y_sign-311, x_sign+70, y_sign-247)))
        List[num].append(image.crop((x_sign-108, y_sign-244, x_sign+70, y_sign-180)))
        List[num].append(image.crop((x_sign-108, y_sign-177, x_sign+70, y_sign-113)))

        List[num].append(image.crop((x_tab-260, y_tab+260, x_tab-157, y_tab+295)))
        List[num].append(image.crop((x_tab-152, y_tab+260, x_tab-47, y_tab+295)))
        for i,z in enumerate(range(0,121,30),1):
            List[num].append(image.crop((x_tab+451, y_tab+260+z, x_tab+813, y_tab+295+z)))
            List[num].append(image.crop((x_tab+70, y_tab+260+z, x_tab+173, y_tab+295+z)))
            List[num].append(image.crop((x_tab+183, y_tab+260+z, x_tab+383, y_tab+295+z)))


        for i in range(0,len(List[num])):
            List[num][i] = ImageEnhance.Contrast(List[num][i]).enhance(2.0)
        
        
        
def second_ocr():
    List2 = []
    def get_list(emlist):
        emlist = ['']*count
        for i in range(0,count):
            emlist[i] = []
        return emlist

    List2 = get_list("List2")

    for i in range(0, len(List)):
        for z in range(0, len(List[i])):
            pil_image = List[i][z]
            List2[i].append(recognize_image(pil_image,""))

    return List2
  
    
def ocr_functions(requests):
    getCloudPdf(requests)
    implicit()
    to_Png(requests)
    first_ocr()
    image_cut()
    second_ocr()
    
    