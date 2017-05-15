Changelog

- 1.5.3
    - Added generic delete confirmation view
    - Conceptual Domains improvements:
        - Added value meaning editor, and admin inline editor
        - Improved layout and display of Conceptual Domains
        - Improved search index for Conceptual Domains
    - Improved search index for Value Domains
    - Allow arity of relationships to be blank #652
    - Fix display bug that incorecctly stated how visibility of items would change #648  
    - Fix bug that listed unregistered metadata in downloads #659

- 1.5.2
    - Autocompletes now restrict via UUID 
    - Added `serialize_weak_entities` to ValueDomain and ConceptualDomain allow for codes to be transmitted via API
    - Fix slots in PDFs #635

- 1.5.1
    - Fixed UUID4 transcription error in migrations #625
    - Users can search for all content, not just their own - #626
    - Changelog added