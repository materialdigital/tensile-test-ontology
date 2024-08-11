"""
Tool for checking a provided ontology for OOPS pitfalls.

Author: Matthias Jung
Date: 2023-12-07

usage: oops_report.py [-h] [-u ONTOLOGY_URL] [-f ONTOLOGY_FILE] 
                      [-t ONTOLOGY_FILE_TYPE] [-r RESTRICTION] 
                      [--timeout TIMEOUT] [-v]

Generates a report using the OOPS API based on the provided ontology 
URL or ontology file. The output is stored in oops_report.json. The 
maximum level of the report is stored in oops_badge.svg. The badge       
command is stored in _oops_badge_command.sh. Use either ontology_file 
or ontology_url, if both are provided only ontology_file is used.

options:
  -h, --help            show this help message and exit
  -u ONTOLOGY_URL, --ontology-url ONTOLOGY_URL
                        The URL of the ontology to be used for generating the report.
  -f ONTOLOGY_FILE, --ontology-file ONTOLOGY_FILE
                        The path to the ontology file to be used for generating the report.
  -t ONTOLOGY_FILE_TYPE, --ontology-file-type ONTOLOGY_FILE_TYPE
                        The format of the input ontology file (default: xml).
  -r RESTRICTION, --restriction RESTRICTION
                        A restriction to be applied during report generation.
  --timeout TIMEOUT     The number of seconds to wait for a response from 
                        the OOPS API (default: 120).
  -v, --verbose         Whether to print verbose output.
"""
import argparse
import json
import xml.etree.ElementTree as ET
import requests
import rdflib

REQ_TIMEOUT = 120
LEVELS = {'Critical': 3, 'Important': 2, 'Minor': 1, 'Pass': 0}
LEVELS_INV = {v: k for k, v in LEVELS.items()}
LEVEL_COLOR = {
    'Critical': 'red',
    'Important': 'orange',
    'Minor': 'yellow',
    'Pass': 'brightgreen'
}

def pitfall_repr(pitfall, namespace, restriction=''):
    """
    Generate a dictionary representing a pitfall's information.

    :param pitfall: The pitfall element to extract information from.
    :type pitfall: Element

    :param namespace: The namespace to use for XML element searching.
    :type namespace: dict

    :param restriction: A restriction to filter affected elements by (optional).
    :type restriction: str

    :return: A dictionary containing the pitfall's name, 
             description, code, importance, and affected elements.
    :rtype: dict
    """
    d = pitfall.find('.//oops:Description', namespace).text
    n = pitfall.find('.//oops:Name', namespace).text
    c = pitfall.find('.//oops:Code', namespace).text
    i = pitfall.find('.//oops:Importance', namespace).text
    affelem_filtered = [
        affelem.text for affelem in pitfall.findall('.//oops:AffectedElement', namespace)
        if affelem.text.startswith(restriction)
    ]
    return {
        'name': n,
        'description': d,
        'code': c,
        'importance': i,
        'affected_elements': affelem_filtered
    }

def suggestion_repr(suggestion, namespace, restriction=''):
    """
    Returns a dictionary representation of a suggestion with the given namespace and restriction.

    Parameters:
        suggestion (Element): The suggestion element.
        namespace (dict): The namespace dictionary.
        restriction (str): The restriction to filter affected elements (default '').

    Returns:
        dict: A dictionary containing the name, description, 
              and affected elements of the suggestion.
    """
    d = suggestion.find('.//oops:Description', namespace).text
    n = suggestion.find('.//oops:Name', namespace).text
    affelem_filtered = [
        affelem.text for affelem in suggestion.findall('.//oops:AffectedElement', namespace)
        if affelem.text.startswith(restriction)]
    return {
        'name': n,
        'description': d,
        'affected_elements': affelem_filtered
    }

def make_report(strdata, restriction=''):
    """
    Generate a report based on the given XML data.

    Parameters:
        strdata (str): The XML data as a string.
        restriction (str, optional): A restriction on the affected elements. Defaults to ''.

    Returns:
        tuple: A tuple containing the report, the maximum level of 
               importance, and the corresponding level name.
    """
    root = ET.fromstring(strdata)
    namespace = {'oops': 'http://www.oeg-upm.net/oops'}

    pitfalls = [
        pitfall for pitfall in root.findall('.//oops:Pitfall', namespace)
        for affelem in pitfall.findall('.//oops:AffectedElement', namespace)
        if affelem.text.startswith(restriction)
    ]
    suggestions = [
        suggestion for suggestion in root.findall('.//oops:Suggestion', namespace)
        for affelem in suggestion.findall('.//oops:AffectedElement', namespace)
        if affelem.text.startswith(restriction)
    ]

    report = {
        'pitfalls': [
            pitfall_repr(pitfall, namespace, restriction) for pitfall in pitfalls
        ],
        'suggestions': [ 
            suggestion_repr(suggestion, namespace, restriction) for suggestion in suggestions
        ]
    }

    maxlevel = 0
    for pf in report['pitfalls']:
        maxlevel = max(maxlevel, LEVELS[pf['importance']])

    return report, maxlevel, LEVELS_INV[maxlevel]

def oops_report(ontology_url=None, ontology_file=None,
                ontology_file_type='xml', restriction='', verbose=False, timeout=REQ_TIMEOUT):
    """
    Generates a report using the OOPS API based on the provided ontology URL or ontology file.
    
    Args:
        ontology_url (str): The URL of the ontology to be used for generating the report.
        ontology_file (str): The path to the ontology file to be used for generating the report.
        restriction (str): A restriction to be applied during report generation.
        verbose (bool): Whether to print verbose output.
        
    Returns:
        int: The maximum level of the report.
        
    Raises:
        ValueError: If neither ontology_file nor ontology_url is specified.
        RuntimeError: If an invalid response is received from the OOPS API.
    """
    if ontology_file is not None:
        ontology = convert_file(ontology_file, ontology_file_type)
        xml_body = '''
        <?xml version="1.0" encoding="UTF-8"?>
        <OOPSRequest>
        <OntologyURI></OntologyURI>
        <OntologyContent>'''+ontology+'''</OntologyContent>
        <Pitfalls></Pitfalls>
        <OutputFormat>XML</OutputFormat>
        </OOPSRequest>
        '''
    elif ontology_url is not None:
        xml_body = '''
        <?xml version="1.0" encoding="UTF-8"?>
        <OOPSRequest>
        <OntologyURI>'''+ontology_url+'''</OntologyURI>
        <OntologyContent></OntologyContent>
        <Pitfalls></Pitfalls>
        <OutputFormat>XML</OutputFormat>
        </OOPSRequest>
        '''
    else:
        raise ValueError('Either ontology_file or ontology_url must be specified')

    url = 'https://oops.linkeddata.es/rest'
    headers = {
        'Content-Type': 'application/xml'
    }
    with open('_oops_badge_command.sh', 'w', encoding='utf8') as f:
        f.write('badge OOPS! Error :blue > oops_badge.svg')

    response = requests.post(url, data=xml_body.encode('utf-8'), headers=headers, timeout=timeout)
    with open('oops_request_raw.txt', 'wb') as f:
        f.write(response.content)

    if verbose:
        print(f'OOPS API answered with status code {response.status_code}')
    if response.status_code == 200:
        report, maxlevel, maxlevel_text = make_report(response.content, restriction)
        with open('_oops_badge_command.sh', 'w', encoding='utf8') as f:
            f.write(f'badge OOPS! {maxlevel_text} :{LEVEL_COLOR[maxlevel_text]} > oops_badge.svg')
    else:
        with open('_oops_badge_command.sh', 'w', encoding='utf8') as f:
            f.write('badge OOPS! Error :blue > oops_badge.svg')
        raise RuntimeError('Invalid response from OOPS API')

    if verbose:
        print(f"Report shows {len(report['pitfalls'])} pitfalls and {len(report['suggestions'])}",
              f"suggestions. Max level is {maxlevel}:{maxlevel_text}")

    with open('oops_report.json', 'w', encoding='utf8') as f:
        json.dump(report, f, indent=4)

def convert_file(file_path, input_type):
    """
    Converts a file to a specified input type.
    
    Args:
        file_path (str): The path to the file to be converted.
        input_type (str): The format of the input file.
        
    Returns:
        str: The serialized XML representation of the converted file.
    """
    graph = rdflib.Graph()
    graph.parse(file_path, format=input_type)
    return graph.serialize(format='xml')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
        'Generates a report using the OOPS API based on the provided ontology \
         URL or ontology file. The output is stored in oops_report.json. \
         The maximum level of the report is stored in oops_badge.svg. \
         The badge command is stored in _oops_badge_command.sh. \
         Use either ontology_file or ontology_url, if both are provided \
         only ontology_file is used.')
    parser.add_argument('-u', '--ontology-url', type=str, default=None,
                        help='The URL of the ontology to be used for generating the report.')
    parser.add_argument('-f', '--ontology-file', type=str, default=None,
                        help='The path to the ontology file to be used for generating the report.')
    parser.add_argument('-t', '--ontology-file-type', type=str, default='xml',
                        help='The format of the input ontology file (default: xml).')
    parser.add_argument('-r', '--restriction', type=str, default='',
                        help='A restriction to be applied during report generation.')
    parser.add_argument('--timeout', type=int, default=REQ_TIMEOUT,
                        help=f'The number of seconds to wait for a \
                               response from the OOPS API (default: {REQ_TIMEOUT}).')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Whether to print verbose output.')
    args = parser.parse_args()

    oops_report(ontology_url=args.ontology_url,
                ontology_file=args.ontology_file,
                ontology_file_type=args.ontology_file_type,
                restriction=args.restriction,
                verbose=args.verbose,
                timeout=args.timeout)
