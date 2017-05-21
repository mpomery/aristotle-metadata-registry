Changelog

- 1.5.4
    - Fixes for review requests:
        - Fixed hints on visibiity changes, #664
        - Minor CSS improvements
        - Matched wording around cascade registration to match status changes
        - Fixed bug where review request popover windows wouldn't work, #663
        - Fixed bug where bulk review requests would fail, #662

- 1.5.3
    - Added generic delete confirmation view
    - Conceptual Domains improvements:
        - Added value meaning editor, and admin inline editor
        - Improved layout and display of Conceptual Domains
        - Improved search index for Conceptual Domains
    - Improved search index for Value Domains
    - Allow arity of relationships to be blank #652
    - Improved how value domains are compared using the comparator #655
    - Removed UUIDs from comparator #655
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