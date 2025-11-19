## Customize Makefile settings for tto
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile


CITATION="'M. Schilling, B. Bayerlein, P. v. Hartrott, J. Waitelonis, H. Birkholz, P. D. Portella, B. Skrotzki, Advanced Engineering Materials 2024, 2400138.'"


ALL_ANNOTATIONS=--ontology-iri https://w3id.org/pmd/tto/ -V https://w3id.org/pmd/tto/$(VERSION) \
	--annotation http://purl.org/dc/terms/created "$(TODAY)" \
	--annotation owl:versionInfo "$(VERSION)" \
	--annotation http://purl.org/dc/terms/bibliographicCitation "$(CITATION)"  \
	--link-annotation owl:priorVersion https://w3id.org/pmd/tto/$(PRIOR_VERSION) \

update-ontology-annotations: 
	$(ROBOT) annotate --input ../../tto.owl $(ALL_ANNOTATIONS) --output ../../tto.owl && \
	$(ROBOT) annotate --input ../../tto.ttl $(ALL_ANNOTATIONS) --output ../../tto.ttl && \
	$(ROBOT) annotate --input ../../tto-simple.owl $(ALL_ANNOTATIONS) --output ../../tto-simple.owl && \
	$(ROBOT) annotate --input ../../tto-simple.ttl $(ALL_ANNOTATIONS) --output ../../tto-simple.ttl && \
	$(ROBOT) annotate --input ../../tto-full.owl $(ALL_ANNOTATIONS) --output ../../tto-full.owl && \
	$(ROBOT) annotate --input ../../tto-full.ttl $(ALL_ANNOTATIONS) --output ../../tto-full.ttl && \
	$(ROBOT) annotate --input ../../tto-base.owl $(ALL_ANNOTATIONS) --output ../../tto-base.owl && \
	$(ROBOT) annotate --input ../../tto-base.ttl $(ALL_ANNOTATIONS) --output ../../tto-base.ttl 




