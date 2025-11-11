
![Build Status](https://github.com/materialdigital/tensile-test-ontology/actions/workflows/qc.yml/badge.svg)
# Tensile Test Ontology

This [repository](https://github.com/materialdigital/tensile-test-ontology) comprises the newest version 3.0 of the Tensile Test Ontology (TTO) that is based on the [PMD Core Ontology (PMDco 3.0)](https://github.com/materialdigital/core-ontology) and was developed within the frame of the joint project [Platform MaterialDigital (PMD)](https://materialdigital.de/).
The semantic concepts represented in TTO are in accordance with the associated testing standard [ISO 6892-1:2019-11](https://www.beuth.de/de/norm/iso-6892-1/316885984) for tensile testing of metals at room temperature. 

There is an earlier version 2.0 of the TTO which is still available in a [dedicated repository](https://github.com/materialdigital/application-ontologies/tree/main/tensile_test_ontology_TTO) and used in some demonstrators. The associated information regarding the development of this ontology is also inherently still valid.

## Versions

### Stable release versions

The latest version of the ontology can always be found at:

[https://w3id.org/pmd/tto/tto.owl]([https://w3id.org/pmd/tto/tto.owl)

### Editors' version

Editors of this ontology should use the edit version, [src/ontology/tto-edit.owl](src/ontology/tto-edit.owl) | [Editable version in this GitHub repository](https://github.com/materialdigital/tensile-test-ontology/blob/main/src/ontology/tto-edit.owl).
When editing this verion, a branch can be created that may be further considered by a pull request using the classic workflow applied for collaborative ontology development processes on GitHub.

## Exemplary Dataset

An exemplary dataset ([TTL](https://github.com/materialdigital/tensile-test-ontology/blob/main/tensile_test_data/S355_data_tto.ttl) and [RDF](https://github.com/materialdigital/tensile-test-ontology/blob/main/tensile_test_data/S355_data_tto.rdf) files) is provided in this repository ([data section](https://github.com/materialdigital/tensile-test-ontology/tree/main/tensile_test_data)) which resulted from mapping of typical tensile test data that was published in an open access [Zenodo repository](https://zenodo.org/record/6778336). 
For this data mapping procedure, a simple Python script was used in a Jupyter Notebook environment. This Jupyter Notebook script entitled [PMDCO_3_0_TTO_Data_Mapping](https://github.com/materialdigital/tensile-test-ontology/blob/main/tensile_test_data/PMDCO_3_0_TTO_Data_Mapping.ipynb) can also be found in this repository as well as the data obtained from the test performances (frequently denoted as "raw data"). 

## Scientific Publication

When using the Tensile Test Ontology (TTO), please refer to and cite the following publication which provides in-depth insights into the development of this ontology and the development of such ontologies in general (Ontology Development Path):

*M. Schilling, B. Bayerlein, P. v. Hartrott, J. Waitelonis, H. Birkholz, P. D. Portella, B. Skrotzki, Advanced Engineering Materials 2024, 2400138.*

Bibtex:
```
@article{Schilling2024,
   author = {Schilling, Markus and Bayerlein, Bernd and von Hartrott, Philipp and Waitelonis, Jörg and Birkholz, Henk and Dolabella Portella, Pedro and Skrotzki, Birgit},
   title = {FAIR and Structured Data: A Domain Ontology Aligned with Standard-Compliant Tensile Testing},
   journal = {Advanced Engineering Materials},
   pages = {2400138},
   ISSN = {1438-1656},
   DOI = {https://doi.org/10.1002/adem.202400138},
   url = {https://onlinelibrary.wiley.com/doi/abs/10.1002/adem.202400138},
   year = {2024},
   type = {Journal Article}
}
```
available open access at: [Advanced Engineering Materials](https://doi.org/10.1002/adem.202400138).
  
This publication offers valuable insights into the development process of domain ontologies, illustrated by the example of the tensile test. Starting with the basics of Semantic technologies (ST) and ontologies as well as considerations on mechanical characterization methods, the TTO development process and aspects such as the storage and retrieval of interoperable, FAIR data by means of data mapping and querying are presented in detail. Hence, this pulication may be an essential reference for users and contributors.

## Contact

Please use this GitHub repository's [Issue tracker](https://github.com/materialdigital/tensile-test-ontology/issues) to request new terms/classes or report errors or specific concerns related to the ontology.

## Acknowledgements

This ontology repository was created using the [Ontology Development Kit (ODK)](https://github.com/INCATools/ontology-development-kit).