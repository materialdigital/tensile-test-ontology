"""
This module contains functions for generating and manipulating badges.

Author: Matthias Jung
Date: 2023-12-07

usage: styleguide_checker.py [-h] [-r REPORT_FILE] [-b] 
                             [--badge_cmdfile BADGE_CMDFILE] 
                             [--badge_svgfile BADGE_SVGFILE] 
                             ontology_file

Check compliance of an ontology file with the PMDco style guide.
The results are written to a JSON file. A shell command for
creating a badge is also generated.

positional arguments:
  ontology_file

options:
  -h, --help            show this help message and exit
  -r REPORT_FILE, --report_file REPORT_FILE
                        Specify the file path for the style guide report
  -b, --create_badge    Enable to create a badge based on the style guide report
  --badge_cmdfile BADGE_CMDFILE
                        Specify the file path for the badge command file
  --badge_svgfile BADGE_SVGFILE
                        Specify the file path for the badge SVG file
"""
import argparse
import typing
import json
import re
import rdflib
import numpy as np

OBO = rdflib.Namespace("http://purl.obolibrary.org/obo/")

def get_subj_name(subject: rdflib.term.Literal) -> str:
    """
    Extracts the name of a subject from a given RDFLib Literal.

    Args:
        subject (rdflib.term.Literal): The RDFLib Literal representing the subject.

    Returns:
        str: The extracted name of the subject.

    """
    return str(subject).rsplit('/', maxsplit=1)[-1].split('#')[-1]

def is_upper_camel_case(s: str) -> bool:
    """
    Check if a given string is in upper camel case.

    Args:
        s (str): The string to be checked.

    Returns:
        bool: True if the string is in upper camel case, False otherwise.
    """
    return re.match(r"^([A-Z][a-z]+)*$", s) is not None

def is_lower_camel_case(s: str) -> bool:
    """
    Check if a given string follows the lower camel case naming convention.

    Args:
        s (str): The string to be checked.

    Returns:
        bool: True if the string follows the lower camel case convention, False otherwise.
    """
    return re.match(r"^([a-z]+)([A-Z][a-z]+)*$", s) is not None

def is_capitalized(s: str) -> bool:
    """
    Check if a string is capitalized.

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string is capitalized, False otherwise.
    """
    return re.match(r"^([A-Z][a-z]+\s?)*$", s) is not None

def has_language(
        lit_list: typing.List[rdflib.term.Literal],
        languages: typing.List[str] = None) -> bool:
    """
    Check if all literals in the given list have the specified languages.

    Parameters:
        lit_list (List[rdflib.term.Literal]): A list of RDF literals.
        languages (List[str], optional): A list of languages to check. Defaults to ['en'].

    Returns:
        bool: True if all literals have the specified languages, False otherwise.
    """
    if languages is None:
        languages = ['en']
    langlist = [lit.language for lit in lit_list]
    return all(language in langlist for language in languages) and not None in langlist

def has_curation_status(subject: rdflib.term.Node, graph: rdflib.graph.Graph) -> bool:
    """
    Check if the given subject has a curation status in the graph.

    Parameters:
        subject (rdflib.term.Node): The subject to check.
        graph (rdflib.graph.Graph): The graph to search in.

    Returns:
        bool: True if the subject has a curation status, False otherwise.
    """
    return len(list(graph.objects(subject, OBO.IAO_0000114))) == 1

def has_valid_term_editor(subject: rdflib.term.Node, graph: rdflib.graph.Graph) -> bool:
    """
    Check if the given subject has a valid term editor.

    Args:
        subject (rdflib.term.Node): The subject to check.
        graph (rdflib.graph.Graph): The graph to search in.

    Returns:
        bool: True if the subject has a valid term editor, False otherwise.
    """
    term_editor_list = list(graph.objects(subject, OBO.IAO_0000117))
    return all([re.match(r"^PERSON:(.*)$", str(termEditor)) is not None
                for termEditor in term_editor_list]) and \
           len(term_editor_list) > 0

def check_common(subject: rdflib.term.Node, graph: rdflib.graph.Graph) -> dict[str, bool]:
    """
    Checks the common properties of a subject in an 
    RDF graph and returns a dictionary with the results.

    Parameters:
        subject (rdflib.term.Node): The subject to check.
        graph (rdflib.graph.Graph): The RDF graph to search in.

    Returns:
        dict[str, bool]: A dictionary containing the following boolean properties:
            - 'rdfsLabelExists': Indicates whether the subject has at least one RDFS label.
            - 'rdfsLabelsLang': Indicates whether all RDFS labels have a language tag.
            - 'rdfsLabelsStyle': Indicates whether all RDFS labels are capitalized.
            - 'skosDefinitionExists': Indicates whether the subject has at least one SKOS def.
            - 'skosDefinitionsLang': Indicates whether all SKOS definitions have a language tag.
            - 'oboCurationStatusExists': Indicates whether the subject has an OBO curation status.
            - 'oboTermEditorExistsValid': Indicates whether the subject has a valid OBO term editor.
    """
    labels_list = list(graph.objects(subject, rdflib.RDFS.label))
    skosdef_list = list(graph.objects(subject, rdflib.SKOS.definition))
    return {
        'rdfsLabelExists': len(labels_list) > 0,
        'rdfsLabelsLang': has_language(labels_list),
        'rdfsLabelsStyle': all([is_capitalized(label) for label in labels_list]),
        'skosDefinitionExists': len(skosdef_list) > 0,
        'skosDefinitionsLang': has_language(skosdef_list),
        'oboCurationStatusExists': has_curation_status(subject, graph),
        'oboTermEditorExistsValid': has_valid_term_editor(subject, graph)
    }

def check_class(subject: rdflib.term.Node, graph: rdflib.graph.Graph) -> dict[str, bool]:
    """
    Check the given subject against common checks and class-specific checks.
    
    Args:
        subject (rdflib.term.Node): The subject to check.
        graph (rdflib.graph.Graph): The graph to use for checking.

    Returns:
        dict[str, bool]: A dictionary containing the results of the common checks 
        and the class-specific checks. The keys are the names of the checks and the 
        values are boolean indicating whether the checks passed or not.
    """
    common_checks = check_common(subject, graph)
    class_specific_checks = {
        'classNameStyle': is_upper_camel_case(get_subj_name(subject)),
    }
    return {**common_checks, **class_specific_checks}

def check_object_property(subject: rdflib.term.Node, graph: rdflib.graph.Graph) -> dict[str, bool]:
    """
    Check the property of an object in the graph.

    Args:
        subject (rdflib.term.Node): The subject to check.
        graph (rdflib.graph.Graph): The graph to check.

    Returns:
        dict[str, bool]: A dictionary containing the results of the checks. The keys are the
            names of the checks and the values are boolean values indicating whether the
            checks passed or not.
    """
    common_checks = check_common(subject, graph)
    object_property_specific_checks = {
        'objectPropertyNameStyle': is_lower_camel_case(get_subj_name(subject))
    }
    return {**common_checks, **object_property_specific_checks}

def check_classes(graph: rdflib.graph.Graph) -> dict[str, dict[str, bool]]:
    """
    Generates a dictionary with the classes found in the 
    given graph and their respective boolean values.

    Parameters:
        graph (rdflib.graph.Graph): The graph to search for classes.

    Returns:
        dict[str, dict[str, bool]]: A dictionary containing the classes 
                                    found as keys and their respective boolean values as values.
    """
    return {str(s): check_class(s, graph)
            for s in graph.subjects(predicate=rdflib.RDF.type, object=rdflib.OWL.Class)}

def check_object_properties(graph: rdflib.graph.Graph) -> dict[str, dict[str, bool]]:
    """
    Generate a dictionary containing the properties of all object nodes in the given RDF graph.

    Parameters:
        graph (rdflib.graph.Graph): The RDF graph to check.

    Returns:
        dict[str, dict[str, bool]]: A dictionary where the keys are the string 
        representations of the subject nodes that are of type rdflib.OWL.ObjectProperty, 
        and the values are dictionaries representing the properties of each subject 
        node. Each property is represented by a key-value pair, where the key is a string
        representation of the property name, and the value is a boolean indicating 
        whether the property is present.
    """
    return {str(s): check_object_property(s, graph)
            for s in graph.subjects(predicate=rdflib.RDF.type, object=rdflib.OWL.ObjectProperty)}

def check_graph(graph: rdflib.graph.Graph) -> dict[str, dict[str, dict[str, bool]]]:
    """
    Generate a dictionary containing the results of various 
    checks performed on the given RDFLib graph.

    Parameters:
    - graph (rdflib.graph.Graph): The RDFLib graph to be checked.

    Returns:
    - dict[str, dict[str, dict[str, bool]]]: A dictionary containing the results of the checks. 
                                             The dictionary has the following structure:
        {
            'classes': {
                'check1': {
                    'result1': bool,
                    'result2': bool,
                    ...
                },
                'check2': {
                    'result1': bool,
                    'result2': bool,
                    ...
                },
                ...
            },
            'objectProperties': {
                'check1': {
                    'result1': bool,
                    'result2': bool,
                    ...
                },
                'check2': {
                    'result1': bool,
                    'result2': bool,
                    ...
                },
                ...
            }
        }
    """
    return {
        'classes': check_classes(graph),
        'objectProperties': check_object_properties(graph)
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Check compliance of an ontology file with the PMDco style guide. \
                     The results are written to a JSON file. \
                     A shell command for creating a badge is also generated.')
    parser.add_argument('ontology_file', type=str)
    parser.add_argument('-r', '--report_file', type=str, default='styleguide_report.json',
                        help='Specify the file path for the style guide report')
    parser.add_argument('-b', '--create_badge', action='store_true',
                        help='Enable to create a badge based on the style guide report')
    parser.add_argument('--badge_cmdfile', type=str, default='styleguide_badge.sh',
                        help='Specify the file path for the badge command file')
    parser.add_argument('--badge_svgfile', type=str, default='styleguide_badge.svg',
                        help='Specify the file path for the badge SVG file')
    args = parser.parse_args()

    g = rdflib.Graph()
    g.parse(args.ontology_file)

    report = check_graph(g)

    number_classes = len(report['classes'].keys())
    number_valid_classes = [all(list(cl_res.values()))
                            for _, cl_res in report['classes'].items()].count(True)
    number_object_properties = len(report['objectProperties'].keys())
    number_valid_object_properties = [
        all(list(cl_res.values())) for _, cl_res in report['objectProperties'].items()
    ].count(True)
    number_definitions = number_classes + number_object_properties
    number_valid_definitions = number_valid_classes + number_valid_object_properties

    print('=============== Style guide compliance report ===============')
    print(f'Classes: {number_valid_classes} of {number_classes}',
          'classes comply with the style guide')
    print(f'Object properties: {number_valid_object_properties} of',
          f'{number_object_properties} object properties comply with the style guide')
    print(f'Overall Definitions: {number_valid_definitions} of',
          f'{number_definitions} definitions comply with the style guide')
    print('=============================================================')

    frac_valid = number_valid_definitions/number_definitions
    def badge_color(frac: float) -> str:
        """
        Generates the color for a badge based on a given fraction.

        Parameters:
            frac (float): The fraction value to determine the badge color. 
                          Must be between 0.0 and 1.0.

        Returns:
            str: The color for the badge based on the given fraction value.
        """
        if frac > 1.0 or frac < 0.0:
            raise ValueError('frac_valid must be between 0.0 and 1.0')
        else:
            for frac_thr, b_color in zip(
                np.flip(np.linspace(0.0, 1.0, 6, endpoint=False)),
                ['brightgreen', 'green', 'yellow', 'yellowgreen', 'orange', 'red']
            ):
                if frac >= frac_thr:
                    return b_color

    if args.create_badge:
        with open(args.badge_cmdfile, 'w', encoding='utf8') as f:
            f.write('badge "Styleguide compliance" '+
                    f'"{frac_valid*100.0:.1f}%" '+
                    f':{badge_color(frac_valid)} > {args.badge_svgfile}')

    with open(args.report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4)
