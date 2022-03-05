import sys
import json
from rdflib import Graph, URIRef, BNode, Literal
from typing import Union, IO
from codemeta.common import AttribDict, REPOSTATUS, license_to_spdx, SDO, SCHEMA_SOURCE, CODEMETA_SOURCE, CONTEXT, DUMMY_NS

#pylint: disable=W0621
#ef fixcodemeta() -> dict:
#   """There may be certain errors in codemeta data we want to fix before using rdflib on it"""
#   g.parse(file=file_descriptor, format="jsonld")
#
#   """Parses a codemeta.json file (json-ld)"""
#   data = json.load(file_descriptor)
#   for key, value in data.items():
#       if key == "developmentStatus":
#           if args.with_repostatus and value.strip().lower() in REPOSTATUS:
#               #map to repostatus vocabulary
#               data[key] = "https://www.repostatus.org/#" + REPOSTATUS[value.strip().lower()]
#       elif key == "license":
#           data[key] = license_to_spdx(value, args)
#   return data

def parse_jsonld(g: Graph, res: Union[BNode, URIRef,None], file_descriptor: IO, args: AttribDict) -> Union[str,None]:
    data = json.load(file_descriptor)

    #preprocess json
    if '@context' not in data:
        raise Exception("Not a valid JSON-LD document, @context missing!")

    #rewrite context using the sources we know that work (schema.org doesn't do proper content negotation):
    if isinstance(data['@context'], list):
        for i, v in enumerate(data['@context']):
            if isinstance(v, str):
                if v.startswith("https://schema.org") or v.startswith("http://schema.org"):
                    data['@context'][i] = SCHEMA_SOURCE
                elif v.startswith("https://doi.org/10.5063/schema"):
                    data['@context'][i] = CODEMETA_SOURCE



    prefuri = None
    if isinstance(res, URIRef):
        if '@graph' in data and len(data['@graph']) == 1:
            #force same ID as the resource (to facilitate merging), but return the preferred URI to be used on serialisation again
            for k in ('id','@id'):
                if k in data['@graph'][0]:
                    prefuri = data['@graph'][0][k]
            data['@graph'][0]["@id"] = str(res)
            if 'id' in data['@graph'][0]: del data['@graph'][0]['id'] #prefer @id over id
        elif '@id' in data or 'id' in data:
            #force same ID as the resource (to facilitate merging), but return the preferred URI to be used on serialisation again
            for k in ('id','@id'):
                if k in data:
                    prefuri = data[k]
            data["@id"] = str(res)
            if 'id' in data: del data['id'] #prefer @id over id
        elif '@graph' not in data:
            data["@id"] = str(res)

    #reserialize
    data = json.dumps(data, indent=4)

    #and parse with rdflib
    g.parse(data=data, format="json-ld", context=CONTEXT, publicID=DUMMY_NS)

    # ^--  We assign an u

    return prefuri
