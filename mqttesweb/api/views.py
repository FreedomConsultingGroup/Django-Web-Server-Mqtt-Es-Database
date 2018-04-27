from django.shortcuts import render
from requests_aws4auth import AWS4Auth
from django.http import HttpRequest, QueryDict, Http404, HttpResponseForbidden
from requests import HTTPError
from elasticsearch import Elasticsearch, RequestsHttpConnection

# Create your views here.


def esGET(request: HttpRequest):
    """
    Returns JSON data from the elasticsearch instance on AWS

    Required GET query parameters:

        key: STRING, API key, assigned by IP address via a call to api/get-key


    Possible GET query parameters:

        tmin: NUMBER, specifies minimum time to search from, in epoch time ms

        tmax: NUMBER, specifies maximum time to search to, in epoch time ms

        searchby: STRING, can be one of:

            "point", searches by distance from a point, ES Geo Distance Query:
            https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-geo-distance-query.html

            EXAMPLE: https://cgood.fcgit.net/api/es-data?tmin=1524851780&searchby=point&latlon=39,-76&rad=200

            Expects the following extra parameters:

                    latlon: 2 NUMBERS, lat lon pair, separated by a comma ','

                    rad: NUMBER, distance from point specified by latlon, in km

            "box", searches for points within a specified rectangle, ES Geo Bounding Box Query:
            https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-geo-bounding-box-query.html

            EXAMPLE: https://cgood.fcgit.net/api/es-data?tmin=1524851780&searchby=box&tl=40,-77&br38,-75

            Expects the following extra parameters:

                    tl: 2 NUMBERS, top left of box,
                        lat lon pair, separated by a comma ','

                    br: 2 NUMBERS, bottom right of box,
                        lat lon pair, separated by a comma ','

            "poly", searches for points within a specified polygon, ES Geo Polygon Query:
            https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-geo-polygon-query.html

            EXAMPLE: https://cgood.fcgit.net/api/es-data?tmin=1524851780&searchby=poly&latlon=39.596,-76.851&latlon=38.489,-77.939&latlon=38.635,-76.195

            Expects the following extra parameters:

                    latlon: ARRAY, multiple lat lon pairs, lat and lon separated by a comma ','

    :param request: request body
    :return: HttpResponse
    """

    keys = open("/home/ubuntu/keys/api-keys.txt", 'r')
    aws_key = keys.readline().replace('\n', '')
    aws_secret = keys.readline().replace('\n', '')
    keys.close()

    region = "us-east-1"
    service = "es"
    aws_auth = AWS4Auth(aws_key, aws_secret, region, service)
    endpoint = "search-chriswillelasticsearch-sbzs5dhk3efss3t4bidlxmym7u.us-east-1.es.amazonaws.com"
    esnode = Elasticsearch(
        hosts=[{'host': endpoint, 'port': 443}],
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    key = None
    tmin = 0
    tmax = None

    if "key" in request.GET:
        if invalidKey(request.GET["key"]):
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()

    if "tmin" in request.GET:
        tmin = request.GET["tmin"]

    if "tmax" in request.GET:
        tmax = request.GET["tmax"]

    if "searchby" in request.GET:
        searchby = request.GET["searchby"]

        if searchby == "point":
            latlon = rad = None
            if "latlon" in request.GET:
                latlon = request.GET["latlon"]
            if "rad" in request.GET:
                ras = request.GET["rad"]

        elif searchby == "box":
            tl = br = None
            if "tl" in request.GET:
                tl = request.GET["tl"]
            if "br" in request.GET:
                br = request.GET["br"]

        elif searchby == "poly":
            latlons

        else:
            searchby = None

    else:
        searchby = None

    query = {"size": 100,
             "query":
                 {"bool":
                      {"must":
                           {"match_all": {}},
                       "filter":
                           {"geo_distance":
                                {"distance": "200km",
                                 "pin.location":
                                     {"lat": 39,
                                      "lon": -76}
                                 }
                            }
                       }
                  }
             }
    es_resp = esnode.search('gpsd_cgood', body=str(query).replace('\'', '\"'))

    i = 0
    response = "{\"hits\": ["
    for hit in es_resp["hits"]["hits"]:
        hit_str = str(hit['_source'])
        hit_str = hit_str.replace('\'', '\"')
        print(hit_str)
        response += hit_str + ", "
        i += 1
    response += "]}"
    return response


def invalidKey(key: str):
    return False