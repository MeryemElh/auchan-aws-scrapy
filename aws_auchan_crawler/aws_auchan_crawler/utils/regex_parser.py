
from re import compile as regex_compile

class RegexParser():
    def __init__(self) -> None:
        self.regex_single_contenance = regex_compile(r'^Contenance : (?P<contenance>\d*(?:|,|.\d*)|)(?:| )(?P<unit>[a-zA-Zéèçàù]*)$')
        self.regex_multiple_contenance = regex_compile(r'^Contenance : (?P<nb>\d*(?:|,|.\d*)|)(?:| )x(?:| )(?P<contenance>\d*(?:|,|.\d*)|)(?:| )(?P<unit>[a-zA-Zéèçàù]*)$')
        self.regex_unknown_contenance = regex_compile(r'^Contenance : (?P<contenance>.*)$')
        self.regex_lot = regex_compile(r'^Lot de (?P<lot>.*)$')


    def parse_additional_info(self, data: list[str]) -> dict:
        additional_info = {
            "single_contenances": [], # Known units are for now : 'l', 'ml', 'cl', 'g', 'kg', 'CL' and 'G'
            "multiple_contenances": [],
            "unkown_contenances": [],
            "lots": [],
            "unknown": [],
        }

        for elem in data:
            elem = elem.strip()
            
            single_cont = self.regex_single_contenance.search(elem)
            multiple_cont = self.regex_multiple_contenance.search(elem)
            unkown_cont = self.regex_unknown_contenance.search(elem)
            lot = self.regex_lot.search(elem)

            if single_cont:
                additional_info['single_contenances'].append(single_cont.groupdict())
            elif multiple_cont:
                additional_info['multiple_contenances'].append(multiple_cont.groupdict())
            elif unkown_cont:
                additional_info['unkown_contenances'].append(unkown_cont.groupdict())
            elif lot:
                additional_info['lots'].append(lot.groupdict())
            else:
                if elem:
                    additional_info['unknown'].append(elem)
        
        return additional_info
        
